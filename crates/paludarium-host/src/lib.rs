//! Host abstraction for paludarium (contract C2, U1 subset).
//!
//! Every host facility the emulator uses goes through the [`Host`] trait
//! (BR6.1, ADR-007), so that the native and wasm implementations differ only
//! here. U1 provides standard I/O and randomness (for `AT_RANDOM`); threads,
//! time and host files are added by later units.
//!
//! This is the only crate where `unsafe` is permitted (NFR3.1). The U1
//! implementation does not need any.

#![cfg_attr(windows, feature(windows_by_handle))]

use std::io::{self, Read, Write};
use std::path::Path;

use paludarium_types::{Errno, Error, ErrorKind};

mod clock;
pub mod fs;
mod native_fs;
pub use fs::{DirectoryEntry, FileHandle, FileStat, HostFs};
pub use native_fs::NativeFs;
pub mod testing;
pub use clock::{ClockId, WaitOutcome};

/// Facilities the emulator needs from its host.
pub trait Host: Send + Sync {
    fn mount_fs(&self, _root: &Path) -> Result<std::sync::Arc<dyn HostFs>, Errno> {
        Err(Errno::ENOSYS)
    }
    /// Reads from the host's standard input; `Ok(0)` at end of input.
    fn read_stdin(&self, buf: &mut [u8]) -> Result<usize, Errno>;
    /// Writes to the host's standard output; returns the bytes written.
    fn write_stdout(&self, buf: &[u8]) -> Result<usize, Errno>;
    /// Writes to the host's standard error; returns the bytes written.
    fn write_stderr(&self, buf: &[u8]) -> Result<usize, Errno>;
    /// Fills `buf` with cryptographically secure random bytes.
    fn random_bytes(&self, buf: &mut [u8]) -> Result<(), Error>;
    /// Nanoseconds since the selected clock's epoch.
    fn clock(&self, _clock: ClockId) -> Result<u64, Errno> {
        Err(Errno::ENOSYS)
    }
    /// Waits until a deadline while polling cancellation outside guest memory locks.
    fn wait_until(
        &self,
        _clock: ClockId,
        _deadline: u64,
        _cancel: &std::sync::atomic::AtomicBool,
    ) -> Result<WaitOutcome, Errno> {
        Err(Errno::ENOSYS)
    }
}

/// Maps a host I/O error to the errno the guest sees.
#[must_use]
pub fn errno_from_io(err: &io::Error) -> Errno {
    match err.kind() {
        io::ErrorKind::BrokenPipe => Errno::EPIPE,
        io::ErrorKind::WouldBlock => Errno::EAGAIN,
        io::ErrorKind::InvalidInput => Errno::EINVAL,
        _ => Errno::EIO,
    }
}

fn write_through(out: &mut dyn Write, buf: &[u8]) -> Result<usize, Errno> {
    out.write_all(buf).map_err(|e| errno_from_io(&e))?;
    out.flush().map_err(|e| errno_from_io(&e))?;
    Ok(buf.len())
}

/// The native host (Linux, and the portable parts for macOS and Windows).
/// Writes are unbuffered from the guest's point of view: every guest
/// `write` is flushed before it returns.
#[derive(Debug, Default, Clone, Copy)]
pub struct NativeHost;

impl NativeHost {
    /// Creates the native host.
    #[must_use]
    pub fn new() -> Self {
        NativeHost
    }
}

impl Host for NativeHost {
    fn mount_fs(&self, root: &Path) -> Result<std::sync::Arc<dyn HostFs>, Errno> {
        Ok(std::sync::Arc::new(NativeFs::new(root)?))
    }
    fn clock(&self, clock: ClockId) -> Result<u64, Errno> {
        clock::native_clock(clock)
    }
    fn wait_until(
        &self,
        clock: ClockId,
        deadline: u64,
        cancel: &std::sync::atomic::AtomicBool,
    ) -> Result<WaitOutcome, Errno> {
        clock::native_wait(clock, deadline, cancel)
    }
    fn read_stdin(&self, buf: &mut [u8]) -> Result<usize, Errno> {
        io::stdin().lock().read(buf).map_err(|e| errno_from_io(&e))
    }

    fn write_stdout(&self, buf: &[u8]) -> Result<usize, Errno> {
        write_through(&mut io::stdout().lock(), buf)
    }

    fn write_stderr(&self, buf: &[u8]) -> Result<usize, Errno> {
        write_through(&mut io::stderr().lock(), buf)
    }

    fn random_bytes(&self, buf: &mut [u8]) -> Result<(), Error> {
        getrandom::fill(buf)
            .map_err(|_| Error::new(ErrorKind::Host, "host randomness is unavailable"))
    }
}

/// Reads a program file from the host file system for the command line
/// (BR5.4). Kept here so that no other crate touches `std::fs` (BR6.1).
pub fn read_program_file(path: &Path) -> Result<Vec<u8>, Error> {
    std::fs::read(path).map_err(|_| Error::new(ErrorKind::Host, "cannot read the program file"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn native_random_bytes_fill_the_buffer() {
        let host = NativeHost::new();
        let mut a = [0u8; 32];
        let mut b = [0u8; 32];
        host.random_bytes(&mut a).unwrap();
        host.random_bytes(&mut b).unwrap();
        // Two 256-bit draws are equal with negligible probability.
        assert_ne!(a, b);
    }

    #[test]
    fn write_through_reports_full_length() {
        let mut sink = Vec::new();
        assert_eq!(write_through(&mut sink, b"abc"), Ok(3));
        assert_eq!(sink, b"abc");
    }

    #[test]
    fn io_errors_map_to_errno() {
        let pipe = io::Error::from(io::ErrorKind::BrokenPipe);
        assert_eq!(errno_from_io(&pipe), Errno::EPIPE);
        let other = io::Error::other("x");
        assert_eq!(errno_from_io(&other), Errno::EIO);
        struct Broken;
        impl Write for Broken {
            fn write(&mut self, _: &[u8]) -> io::Result<usize> {
                Err(io::Error::from(io::ErrorKind::BrokenPipe))
            }
            fn flush(&mut self) -> io::Result<()> {
                Ok(())
            }
        }
        assert_eq!(write_through(&mut Broken, b"x"), Err(Errno::EPIPE));
    }

    #[test]
    fn missing_program_file_is_a_host_error_without_path() {
        let dir = std::env::temp_dir().join("paludarium-host-test-missing-file");
        let err = read_program_file(&dir).unwrap_err();
        assert_eq!(err.kind, ErrorKind::Host);
        assert!(!err.to_string().contains("paludarium-host-test"));
    }

    #[test]
    fn program_file_is_read_whole() {
        let path =
            std::env::temp_dir().join(format!("paludarium-host-test-{}", std::process::id()));
        std::fs::write(&path, b"\x7fELF-test").unwrap();
        let content = read_program_file(&path).unwrap();
        std::fs::remove_file(&path).unwrap();
        assert_eq!(content, b"\x7fELF-test");
    }

    #[test]
    fn recording_host_captures_streams() {
        let host = testing::RecordingHost::new();
        host.write_stdout(b"out").unwrap();
        host.write_stderr(b"err").unwrap();
        let mut r = [0u8; 4];
        host.random_bytes(&mut r).unwrap();
        assert_eq!(host.stdout(), b"out");
        assert_eq!(host.stderr(), b"err");
        assert_eq!(r, [testing::RecordingHost::RANDOM_BYTE; 4]);
        let mut buf = [0u8; 4];
        assert_eq!(host.read_stdin(&mut buf), Ok(0));
    }
}

#[cfg(test)]
mod u4_tests;
