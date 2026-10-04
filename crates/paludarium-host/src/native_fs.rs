//! Native filesystem operations relative to a retained directory capability.
use crate::{DirectoryEntry, FileHandle, FileStat, HostFs};
use cap_fs_ext::{FollowSymlinks, OpenOptionsFollowExt};
use cap_std::fs::{Dir, OpenOptions};
use fs2::FileExt;
use paludarium_types::Errno;
use std::{
    io::{Read, Seek, SeekFrom, Write},
    path::{Path, PathBuf},
    sync::{Arc, Mutex, PoisonError},
};
fn err(e: std::io::Error) -> Errno {
    e.raw_os_error()
        .map(Errno)
        .unwrap_or_else(|| crate::errno_from_io(&e))
}
fn path(b: &[u8]) -> Result<PathBuf, Errno> {
    if b.contains(&0) {
        return Err(Errno::EINVAL);
    }
    #[cfg(unix)]
    {
        use std::os::unix::ffi::OsStrExt;
        Ok(PathBuf::from(std::ffi::OsStr::from_bytes(b)))
    }
    #[cfg(not(unix))]
    {
        Ok(PathBuf::from(
            std::str::from_utf8(b).map_err(|_| Errno::EINVAL)?,
        ))
    }
}
fn bytes(p: &Path) -> Vec<u8> {
    #[cfg(unix)]
    {
        use std::os::unix::ffi::OsStrExt;
        p.as_os_str().as_bytes().to_vec()
    }
    #[cfg(not(unix))]
    {
        p.to_string_lossy().as_bytes().to_vec()
    }
}
fn stat(m: std::fs::Metadata) -> FileStat {
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        FileStat {
            inode: m.ino(),
            size: m.len(),
            mode: m.mode(),
            links: m.nlink(),
        }
    }
    #[cfg(not(unix))]
    {
        FileStat {
            inode: 0,
            size: m.len(),
            mode: if m.is_dir() {
                0o040755
            } else if m.is_symlink() {
                0o120777
            } else {
                0o100644
            },
            links: 1,
        }
    }
}
/// Ambient authority is used only to acquire the explicitly configured root.
pub struct NativeFs {
    root: Dir,
}
impl NativeFs {
    pub fn new(root: &Path) -> Result<Self, Errno> {
        Ok(Self {
            root: Dir::open_ambient_dir(root, cap_std::ambient_authority()).map_err(err)?,
        })
    }
}
struct NativeFile {
    file: Mutex<std::fs::File>,
    flags: Mutex<u32>,
}
impl FileHandle for NativeFile {
    fn read(&self, b: &mut [u8]) -> Result<usize, Errno> {
        if self.flags() & 3 == 1 {
            return Err(Errno::EBADF);
        }
        self.file
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .read(b)
            .map_err(err)
    }
    fn write(&self, b: &[u8]) -> Result<usize, Errno> {
        if self.flags() & 3 == 0 {
            return Err(Errno::EBADF);
        }
        self.file
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .write(b)
            .map_err(err)
    }
    fn seek(&self, o: i64, w: u32) -> Result<u64, Errno> {
        let s = match w {
            0 => SeekFrom::Start(u64::try_from(o).map_err(|_| Errno::EINVAL)?),
            1 => SeekFrom::Current(o),
            2 => SeekFrom::End(o),
            _ => return Err(Errno::EINVAL),
        };
        self.file
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .seek(s)
            .map_err(err)
    }
    fn stat(&self) -> Result<FileStat, Errno> {
        self.file
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .metadata()
            .map(stat)
            .map_err(err)
    }
    fn truncate(&self, n: u64) -> Result<(), Errno> {
        self.file
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .set_len(n)
            .map_err(err)
    }
    fn flock(&self, o: u32) -> Result<(), Errno> {
        let f = self.file.lock().unwrap_or_else(PoisonError::into_inner);
        match o & !4 {
            1 => FileExt::try_lock_shared(&*f),
            2 => FileExt::try_lock_exclusive(&*f),
            8 => FileExt::unlock(&*f),
            _ => return Err(Errno::EINVAL),
        }
        .map_err(err)
    }
    fn flags(&self) -> u32 {
        *self.flags.lock().unwrap_or_else(PoisonError::into_inner)
    }
    fn set_flags(&self, f: u32) -> Result<(), Errno> {
        #[cfg(unix)]
        {
            let file = self.file.lock().unwrap_or_else(PoisonError::into_inner);
            let current = rustix::fs::fcntl_getfl(&*file).map_err(|e| Errno(e.raw_os_error()))?;
            let mutable = rustix::fs::OFlags::APPEND | rustix::fs::OFlags::NONBLOCK;
            let flags = (current & !mutable) | (rustix::fs::OFlags::from_bits_retain(f) & mutable);
            rustix::fs::fcntl_setfl(&*file, flags).map_err(|e| Errno(e.raw_os_error()))?;
            let mut saved = self.flags.lock().unwrap_or_else(PoisonError::into_inner);
            *saved = (*saved & !3072) | (f & 3072);
            Ok(())
        }
        #[cfg(not(unix))]
        {
            let _ = f;
            Err(Errno::ENOSYS)
        }
    }
}
impl HostFs for NativeFs {
    fn open(&self, p: &[u8], f: u32, m: u32) -> Result<Arc<dyn FileHandle>, Errno> {
        if f & (64 | 65536) == 64 | 65536 {
            return Err(Errno::EINVAL);
        }
        let mut o = OpenOptions::new();
        #[cfg(unix)]
        {
            use cap_std::fs::OpenOptionsExt;
            o.mode(m);
        }
        #[cfg(not(unix))]
        let _ = m;
        o.read(f & 3 != 1)
            .write(f & 3 != 0)
            .create(f & 64 != 0)
            .create_new(f & 192 == 192)
            .truncate(f & 512 != 0)
            .append(f & 1024 != 0);
        if f & 131072 != 0 {
            o.follow(FollowSymlinks::No);
        }
        let relative = path(p)?;
        let readonly_create = f & 3 == 0 && f & 64 != 0 && f & (128 | 512) == 0;
        if readonly_create {
            o.create(false);
        }
        if f & 3 == 0 && f & (128 | 512) != 0 {
            o.write(true);
        }
        let file = match self.root.open_with(&relative, &o) {
            Ok(file) => file,
            Err(e) if readonly_create && e.kind() == std::io::ErrorKind::NotFound => {
                let mut create = o.clone();
                create.write(true).create_new(true);
                match self.root.open_with(&relative, &create) {
                    Ok(file) => file,
                    Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {
                        self.root.open_with(&relative, &o).map_err(err)?
                    }
                    Err(e) => return Err(err(e)),
                }
            }
            Err(e) => return Err(err(e)),
        }
        .into_std();
        if f & 65536 != 0 && !file.metadata().map_err(err)?.is_dir() {
            return Err(Errno::ENOTDIR);
        }
        Ok(Arc::new(NativeFile {
            file: Mutex::new(file),
            flags: Mutex::new(f),
        }))
    }
    fn metadata(&self, p: &[u8], follow: bool) -> Result<FileStat, Errno> {
        let p = path(p)?;
        let m = if follow {
            self.root.metadata(p)
        } else {
            self.root.symlink_metadata(p)
        }
        .map_err(err)?;
        Ok(cap_stat(m))
    }
    fn mkdir(&self, p: &[u8], m: u32) -> Result<(), Errno> {
        let mut builder = cap_std::fs::DirBuilder::new();
        #[cfg(unix)]
        {
            use cap_std::fs::DirBuilderExt;
            builder.mode(m);
        }
        #[cfg(not(unix))]
        let _ = m;
        self.root.create_dir_with(path(p)?, &builder).map_err(err)
    }
    fn unlink(&self, p: &[u8], d: bool) -> Result<(), Errno> {
        if d {
            self.root.remove_dir(path(p)?)
        } else {
            self.root.remove_file(path(p)?)
        }
        .map_err(err)
    }
    fn link(&self, a: &[u8], b: &[u8]) -> Result<(), Errno> {
        self.root
            .hard_link(path(a)?, &self.root, path(b)?)
            .map_err(err)
    }
    fn symlink(&self, a: &[u8], b: &[u8]) -> Result<(), Errno> {
        #[cfg(not(windows))]
        {
            self.root.symlink(path(a)?, path(b)?).map_err(err)
        }
        #[cfg(windows)]
        {
            self.root.symlink_file(path(a)?, path(b)?).map_err(err)
        }
    }
    fn readlink(&self, p: &[u8]) -> Result<Vec<u8>, Errno> {
        self.root
            .read_link_contents(path(p)?)
            .map(|p| bytes(&p))
            .map_err(err)
    }
    fn rename(&self, a: &[u8], b: &[u8]) -> Result<(), Errno> {
        self.root
            .rename(path(a)?, &self.root, path(b)?)
            .map_err(err)
    }
    fn read_dir(&self, p: &[u8]) -> Result<Vec<DirectoryEntry>, Errno> {
        self.root
            .read_dir(path(p)?)
            .map_err(err)?
            .map(|entry| {
                let e = entry.map_err(err)?;
                let m = e.metadata().map_err(err)?;
                let s = cap_stat(m);
                Ok(DirectoryEntry {
                    name: bytes(Path::new(&e.file_name())),
                    inode: s.inode,
                    kind: if s.mode & 0o170000 == 0o040000 {
                        4
                    } else if s.mode & 0o170000 == 0o120000 {
                        10
                    } else {
                        8
                    },
                })
            })
            .collect()
    }
}
fn cap_stat(m: cap_std::fs::Metadata) -> FileStat {
    #[cfg(unix)]
    {
        use cap_std::fs::MetadataExt;
        FileStat {
            inode: m.ino(),
            size: m.len(),
            mode: m.mode(),
            links: m.nlink(),
        }
    }
    #[cfg(not(unix))]
    {
        FileStat {
            inode: 0,
            size: m.len(),
            mode: if m.is_dir() {
                0o040755
            } else if m.is_symlink() {
                0o120777
            } else {
                0o100644
            },
            links: 1,
        }
    }
}
#[cfg(test)]
mod u7_tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};
    static SEQ: AtomicU64 = AtomicU64::new(0);
    struct Fixture {
        base: PathBuf,
        fs: NativeFs,
    }
    impl Fixture {
        fn new() -> Self {
            let base = std::env::temp_dir().join(format!(
                "paludarium-u7-{}-{}",
                std::process::id(),
                SEQ.fetch_add(1, Ordering::Relaxed)
            ));
            std::fs::create_dir_all(base.join("root")).unwrap();
            std::fs::write(base.join("sentinel"), b"outside").unwrap();
            let fs = NativeFs::new(&base.join("root")).unwrap();
            Self { base, fs }
        }
    }
    impl Drop for Fixture {
        fn drop(&mut self) {
            std::fs::remove_dir_all(&self.base).unwrap();
        }
    }
    #[test]
    fn u7_native_io() {
        let x = Fixture::new();
        let f = x.fs.open(b"a", 66, 0o600).unwrap();
        assert_eq!(f.write(b"abc"), Ok(3));
        f.seek(0, 0).unwrap();
        let mut b = [0; 3];
        assert_eq!(f.read(&mut b), Ok(3));
        assert_eq!(&b, b"abc");
    }
    #[test]
    fn u7_native_links() {
        let x = Fixture::new();
        x.fs.open(b"a", 66, 0o600).unwrap();
        x.fs.link(b"a", b"b").unwrap();
        assert_eq!(x.fs.metadata(b"a", true).unwrap().links, 2);
        x.fs.unlink(b"a", false).unwrap();
        assert_eq!(x.fs.metadata(b"b", true).unwrap().links, 1);
    }
    #[test]
    fn u7_native_rename() {
        let x = Fixture::new();
        x.fs.open(b"a", 66, 0o600).unwrap().write(b"data").unwrap();
        x.fs.rename(b"a", b"b").unwrap();
        assert_eq!(x.fs.metadata(b"a", true), Err(Errno::ENOENT));
        assert_eq!(x.fs.metadata(b"b", true).unwrap().size, 4);
    }
    #[test]
    fn u7_native_directory() {
        let x = Fixture::new();
        x.fs.mkdir(b"d", 0o700).unwrap();
        x.fs.open(b"d/a", 66, 0o600).unwrap();
        assert_eq!(x.fs.read_dir(b"d").unwrap().len(), 1);
        assert!(x.fs.unlink(b"d", true).is_err());
        x.fs.unlink(b"d/a", false).unwrap();
        x.fs.unlink(b"d", true).unwrap();
    }
    #[test]
    fn u7_native_parent_escape() {
        let x = Fixture::new();
        assert!(x.fs.open(b"../sentinel", 2, 0).is_err());
        assert!(x.fs.rename(b"../sentinel", b"stolen").is_err());
        assert!(x.fs.link(b"../sentinel", b"stolen").is_err());
        assert_eq!(std::fs::read(x.base.join("sentinel")).unwrap(), b"outside");
    }
    #[test]
    fn u7_native_symlink_escape() {
        let x = Fixture::new();
        #[cfg(unix)]
        {
            std::os::unix::fs::symlink("../sentinel", x.base.join("root/escape")).unwrap();
            assert!(x.fs.open(b"escape", 2, 0).is_err());
            assert!(x.fs.metadata(b"escape", true).is_err());
            assert_eq!(x.fs.readlink(b"escape").unwrap(), b"../sentinel");
            assert_eq!(std::fs::read(x.base.join("sentinel")).unwrap(), b"outside");
        }
    }
    #[test]
    fn u7_native_lock() {
        let x = Fixture::new();
        let a = x.fs.open(b"a", 66, 0o600).unwrap();
        let b = x.fs.open(b"a", 2, 0).unwrap();
        a.flock(2 | 4).unwrap();
        assert_eq!(b.flock(2 | 4), Err(Errno::EAGAIN));
        a.flock(8).unwrap();
        b.flock(2 | 4).unwrap();
    }
    #[test]
    fn u7_native_nofollow() {
        let x = Fixture::new();
        x.fs.open(b"a", 66, 0o600).unwrap();
        x.fs.symlink(b"a", b"s").unwrap();
        assert!(x.fs.open(b"s", 131072, 0).is_err());
        assert_eq!(
            x.fs.metadata(b"s", false).unwrap().mode & 0o170000,
            0o120000
        );
    }
    #[test]
    fn u7_native_symlink_rename_race() {
        #[cfg(unix)]
        {
            const NAME: &str = "native_fs::u7_tests::u7_native_symlink_rename_race";
            if std::env::var_os("PALUDARIUM_U7_RACE_CHILD").is_none() {
                let mut child = std::process::Command::new(std::env::current_exe().unwrap())
                    .args(["--exact", NAME, "--nocapture"])
                    .env("PALUDARIUM_U7_RACE_CHILD", "1")
                    .spawn()
                    .unwrap();
                let start = std::time::Instant::now();
                loop {
                    if let Some(status) = child.try_wait().unwrap() {
                        assert!(status.success());
                        break;
                    }
                    if start.elapsed() > std::time::Duration::from_secs(30) {
                        child.kill().unwrap();
                        child.wait().unwrap();
                        panic!("U7 race exceeded 30 seconds")
                    }
                    std::thread::sleep(std::time::Duration::from_millis(10));
                }
                return;
            }
            let x = Fixture::new();
            std::fs::create_dir(x.base.join("outside")).unwrap();
            std::fs::write(x.base.join("outside/sentinel"), b"outside").unwrap();
            x.fs.mkdir(b"pivot", 0o700).unwrap();
            x.fs.open(b"pivot/sentinel", 66, 0o600)
                .unwrap()
                .write(b"inside")
                .unwrap();
            let root = x.base.join("root");
            let outside = x.base.join("outside");
            let stop = Arc::new(std::sync::atomic::AtomicBool::new(false));
            let done = Arc::clone(&stop);
            let attacker = std::thread::spawn(move || {
                while !done.load(Ordering::Relaxed) {
                    std::fs::rename(root.join("pivot"), root.join("held")).unwrap();
                    std::os::unix::fs::symlink(&outside, root.join("pivot")).unwrap();
                    std::fs::remove_file(root.join("pivot")).unwrap();
                    std::fs::rename(root.join("held"), root.join("pivot")).unwrap();
                }
            });
            for _ in 0..1000 {
                if let Ok(f) = x.fs.open(b"pivot/sentinel", 2, 0) {
                    let _ = f.write(b"inside");
                }
                let _ = x.fs.metadata(b"pivot/sentinel", true);
                let _ = x.fs.read_dir(b"pivot");
                let _ = x.fs.open(b"pivot/new", 66, 0o600);
                let _ = x.fs.link(b"pivot/sentinel", b"pivot/link");
                let _ = x.fs.rename(b"pivot/new", b"pivot/renamed");
                let _ = x.fs.unlink(b"pivot/renamed", false);
                let _ = x.fs.unlink(b"pivot/link", false);
            }
            stop.store(true, Ordering::Relaxed);
            attacker.join().unwrap();
            assert_eq!(
                std::fs::read(x.base.join("outside/sentinel")).unwrap(),
                b"outside"
            );
            assert_eq!(
                std::fs::read_dir(x.base.join("outside")).unwrap().count(),
                1
            );
        }
    }
}
