//! AF_UNIX stream endpoints. Buffers and peer lifetime belong to the Kernel.
use crate::events::{CLOEXEC, IN, NONBLOCK, OUT, ReadinessHub};
use crate::syscalls::{Context, Outcome};
use paludarium_host::{FileHandle, FileStat};
use paludarium_types::Errno;
use paludarium_types::GuestAddr;
use std::collections::VecDeque;
use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::{Arc, Mutex, PoisonError};

// Per-stream flow-control window, not a per-guest memory/fd quota. Native
// queue capacity and packet accounting depend on the host; the oracle compares
// saturation, partial success and readiness transitions instead of byte counts.
pub(crate) const SEND_WINDOW: usize = 212_992;

pub(crate) fn dispatch(c: &mut Context<'_>, a: [u64; 6]) -> Outcome {
    let result = (|| match c.cpu.gpr[paludarium_cpu::reg::RAX] {
        41 => Err(Errno(97)),
        53 => {
            if a[0] != 1 {
                return Err(Errno(97));
            }
            if a[2] != 0 {
                return Err(Errno(93));
            }
            c.mem
                .check_write(GuestAddr(a[3]), 8)
                .map_err(|_| Errno::EFAULT)?;
            let kind = u32::try_from(a[1]).map_err(|_| Errno::EINVAL)?;
            let [first, second] = SocketPairEnd::pair(kind, Arc::clone(&c.files.readiness))?;
            let fd0 = c.files.install(first, kind & CLOEXEC != 0)?;
            let fd1 = c.files.install(second, kind & CLOEXEC != 0)?;
            let mut bytes = [0; 8];
            bytes[..4].copy_from_slice(&fd0.to_le_bytes());
            bytes[4..].copy_from_slice(&fd1.to_le_bytes());
            c.mem
                .write(GuestAddr(a[3]), &bytes)
                .map_err(|_| Errno::EFAULT)?;
            Ok(0)
        }
        48 => {
            let d = c.files.descriptor(a[0])?;
            let socket = d
                .file
                .as_any()
                .and_then(|v| v.downcast_ref::<SocketPairEnd>())
                .ok_or(Errno(88))?;
            socket.shutdown(a[1])?;
            Ok(0)
        }
        45 => {
            let d = c.files.descriptor(a[0])?;
            if !d.file.as_any().is_some_and(|v| v.is::<SocketPairEnd>()) {
                return Err(Errno(88));
            }
            if a[3] != 0 {
                return Err(Errno(95));
            }
            crate::files::run(c, 0, a)
        }
        44 => {
            let d = c.files.descriptor(a[0])?;
            if !d.file.as_any().is_some_and(|v| v.is::<SocketPairEnd>()) {
                return Err(Errno(88));
            }
            if a[3] & !0x4000 != 0 || a[4] != 0 || a[5] != 0 {
                return Err(Errno(95));
            }
            let len = usize::try_from(a[2].min(0x7fff_f000)).map_err(|_| Errno::EINVAL)?;
            c.mem
                .check_read(GuestAddr(a[1]), len)
                .map_err(|_| Errno::EFAULT)?;
            let mut bytes = Vec::new();
            bytes.try_reserve(len).map_err(|_| Errno::ENOMEM)?;
            bytes.resize(len, 0);
            c.mem
                .read(GuestAddr(a[1]), &mut bytes)
                .map_err(|_| Errno::EFAULT)?;
            crate::files::write_io(c, &d.file, &bytes, a[3] & 0x4000 != 0)
        }
        _ => Err(Errno::ENOSYS),
    })();
    Outcome::Return(result.unwrap_or_else(Errno::to_syscall_return))
}

#[derive(Default)]
struct Side {
    bytes: VecDeque<u8>,
    closed: bool,
    read_shutdown: bool,
    write_shutdown: bool,
    input_epoch: u64,
    output_epoch: u64,
}
struct Pair {
    sides: Mutex<[Side; 2]>,
    hub: Arc<ReadinessHub>,
}
pub(crate) struct SocketPairEnd {
    pair: Arc<Pair>,
    side: usize,
    flags: AtomicU32,
}
impl SocketPairEnd {
    pub fn pair(kind: u32, hub: Arc<ReadinessHub>) -> Result<[Arc<Self>; 2], Errno> {
        if kind & !(NONBLOCK | CLOEXEC | 0xf) != 0 {
            return Err(Errno::EINVAL);
        }
        if kind & 0xf != 1 {
            return Err(Errno(94));
        }
        let pair = Arc::new(Pair {
            sides: Mutex::new(std::array::from_fn(|_| Side {
                output_epoch: 1,
                ..Side::default()
            })),
            hub,
        });
        Ok(std::array::from_fn(|side| {
            Arc::new(Self {
                pair: Arc::clone(&pair),
                side,
                flags: AtomicU32::new(2 | kind & NONBLOCK),
            })
        }))
    }
    pub fn shutdown(&self, how: u64) -> Result<(), Errno> {
        if how > 2 {
            return Err(Errno::EINVAL);
        }
        let mut sides = self
            .pair
            .sides
            .lock()
            .unwrap_or_else(PoisonError::into_inner);
        if how == 0 || how == 2 {
            sides[self.side].read_shutdown = true;
            sides[self.side].input_epoch = sides[self.side].input_epoch.wrapping_add(1);
        }
        if how == 1 || how == 2 {
            sides[self.side].write_shutdown = true;
            sides[1 - self.side].input_epoch = sides[1 - self.side].input_epoch.wrapping_add(1);
        }
        self.pair.hub.changed();
        Ok(())
    }
}
impl Drop for SocketPairEnd {
    fn drop(&mut self) {
        let mut sides = self
            .pair
            .sides
            .lock()
            .unwrap_or_else(PoisonError::into_inner);
        sides[self.side].closed = true;
        sides[1 - self.side].input_epoch = sides[1 - self.side].input_epoch.wrapping_add(1);
        self.pair.hub.changed();
    }
}
impl FileHandle for SocketPairEnd {
    fn as_any(&self) -> Option<&dyn std::any::Any> {
        Some(self)
    }
    fn readiness(&self) -> Result<(u32, u64, u64), Errno> {
        let sides = self
            .pair
            .sides
            .lock()
            .unwrap_or_else(PoisonError::into_inner);
        let own = &sides[self.side];
        let peer = &sides[1 - self.side];
        let eof = own.read_shutdown || peer.closed || peer.write_shutdown;
        let mask = (u32::from(peer.bytes.len() < SEND_WINDOW || peer.closed) * OUT)
            | (u32::from(!own.bytes.is_empty() || eof) * IN)
            | if peer.closed {
                0x2010
            } else if peer.write_shutdown {
                0x2000
            } else {
                0
            };
        Ok((mask, own.input_epoch, own.output_epoch))
    }
    fn read(&self, buf: &mut [u8]) -> Result<usize, Errno> {
        if buf.is_empty() {
            return Ok(0);
        }
        let mut sides = self
            .pair
            .sides
            .lock()
            .unwrap_or_else(PoisonError::into_inner);
        let eof = sides[self.side].read_shutdown
            || sides[1 - self.side].closed
            || sides[1 - self.side].write_shutdown;
        let full = sides[self.side].bytes.len() == SEND_WINDOW;
        let own = &mut sides[self.side];
        if own.read_shutdown {
            return Ok(0);
        }
        if own.bytes.is_empty() {
            return if eof { Ok(0) } else { Err(Errno::EAGAIN) };
        }
        let count = buf.len().min(own.bytes.len());
        for byte in &mut buf[..count] {
            *byte = own.bytes.pop_front().ok_or(Errno::EIO)?;
        }
        if full {
            sides[1 - self.side].output_epoch = sides[1 - self.side].output_epoch.wrapping_add(1);
        }
        self.pair.hub.changed();
        Ok(count)
    }
    fn write(&self, buf: &[u8]) -> Result<usize, Errno> {
        let mut sides = self
            .pair
            .sides
            .lock()
            .unwrap_or_else(PoisonError::into_inner);
        if sides[self.side].write_shutdown
            || sides[1 - self.side].closed
            || sides[1 - self.side].read_shutdown
        {
            return Err(Errno(32));
        }
        let peer = &mut sides[1 - self.side];
        let count = buf.len().min(SEND_WINDOW.saturating_sub(peer.bytes.len()));
        if count == 0 && !buf.is_empty() {
            return Err(Errno::EAGAIN);
        }
        peer.bytes.try_reserve(count).map_err(|_| Errno::ENOMEM)?;
        if peer.bytes.is_empty() && !buf.is_empty() {
            peer.input_epoch = peer.input_epoch.wrapping_add(1);
        }
        peer.bytes.extend(buf[..count].iter().copied());
        self.pair.hub.changed();
        Ok(count)
    }
    fn seek(&self, _: i64, _: u32) -> Result<u64, Errno> {
        Err(Errno::ESPIPE)
    }
    fn stat(&self) -> Result<FileStat, Errno> {
        Ok(FileStat {
            mode: 0o140777,
            links: 1,
            ..FileStat::default()
        })
    }
    fn truncate(&self, _: u64) -> Result<(), Errno> {
        Err(Errno::EINVAL)
    }
    fn flock(&self, _: u32) -> Result<(), Errno> {
        Err(Errno::ENOSYS)
    }
    fn flags(&self) -> u32 {
        self.flags.load(Ordering::SeqCst)
    }
    fn set_flags(&self, flags: u32) -> Result<(), Errno> {
        self.flags.store(2 | flags & NONBLOCK, Ordering::SeqCst);
        Ok(())
    }
}
#[cfg(test)]
mod u6_tests {
    use super::*;
    fn pair() -> [Arc<SocketPairEnd>; 2] {
        SocketPairEnd::pair(1, Arc::default()).unwrap()
    }
    #[test]
    fn u6_socket_backpressure_partial_write_and_out_edge() {
        let [a, b] = pair();
        let bytes = vec![7; SEND_WINDOW + 1];
        assert_eq!(a.write(&bytes), Ok(SEND_WINDOW));
        assert_eq!(a.write(&[1]), Err(Errno::EAGAIN));
        let full = a.readiness().unwrap();
        assert_eq!(full.0 & OUT, 0);
        assert_eq!(b.read(&mut [0; 1]), Ok(1));
        let ready = a.readiness().unwrap();
        assert_ne!(ready.0 & OUT, 0);
        assert_eq!(ready.2, full.2 + 1);
        assert_eq!(a.write(&[1]), Ok(1));
    }
    #[test]
    fn u6_socket_empty() {
        assert_eq!(pair()[0].read(&mut [0]), Err(Errno::EAGAIN));
    }
    #[test]
    fn u6_socket_transfer() {
        let [a, b] = pair();
        a.write(b"hi").unwrap();
        let mut bytes = [0; 2];
        assert_eq!(b.read(&mut bytes), Ok(2));
        assert_eq!(&bytes, b"hi");
    }
    #[test]
    fn u6_socket_bidirectional() {
        let [a, b] = pair();
        a.write(b"a").unwrap();
        b.write(b"b").unwrap();
        let mut byte = [0];
        a.read(&mut byte).unwrap();
        assert_eq!(byte, [b'b']);
        b.read(&mut byte).unwrap();
        assert_eq!(byte, [b'a']);
    }
    #[test]
    fn u6_socket_partial() {
        let [a, b] = pair();
        a.write(b"abc").unwrap();
        assert_eq!(b.read(&mut [0; 2]), Ok(2));
        assert_eq!(b.read(&mut [0; 2]), Ok(1));
    }
    #[test]
    fn u6_socket_peer_lifetime() {
        let [a, b] = pair();
        let copy = Arc::clone(&a);
        drop(a);
        assert_eq!(b.read(&mut [0]), Err(Errno::EAGAIN));
        drop(copy);
        assert_eq!(b.read(&mut [0]), Ok(0));
        assert_eq!(b.write(b"x"), Err(Errno(32)));
    }
    #[test]
    fn u6_socket_shutdown() {
        let [a, b] = pair();
        a.shutdown(1).unwrap();
        assert_eq!(b.read(&mut [0]), Ok(0));
        assert_eq!(a.write(b"x"), Err(Errno(32)));
        assert_eq!(a.shutdown(3), Err(Errno::EINVAL));
    }
    #[test]
    fn u6_socket_edges() {
        let [a, b] = pair();
        a.write(b"abc").unwrap();
        let e = b.readiness().unwrap().1;
        b.read(&mut [0]).unwrap();
        assert_eq!(b.readiness().unwrap().1, e);
        b.read(&mut [0; 2]).unwrap();
        a.write(b"d").unwrap();
        assert_eq!(b.readiness().unwrap().1, e + 1);
    }
    #[test]
    fn u6_socket_flags() {
        let [a, _b] = SocketPairEnd::pair(1 | NONBLOCK | CLOEXEC, Arc::default()).unwrap();
        assert_eq!(a.flags(), 2 | NONBLOCK);
        a.set_flags(0).unwrap();
        assert_eq!(a.flags(), 2);
        assert!(SocketPairEnd::pair(1 | 0x4000, Arc::default()).is_err());
    }
}
