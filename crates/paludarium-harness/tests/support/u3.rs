use std::os::unix::process::CommandExt;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

/// Bound the whole test, including fixture generation and process cleanup.
pub fn bounded(name: &str, run: impl FnOnce()) {
    if std::env::var("PALUDARIUM_U3_CHILD").as_deref() == Ok(name) {
        run();
        return;
    }
    let mut child = Command::new(std::env::current_exe().expect("test executable"))
        .args(["--exact", name, "--nocapture"])
        .env("PALUDARIUM_U3_CHILD", name)
        .process_group(0)
        .stdin(Stdio::null())
        .spawn()
        .expect("start isolated U3 test");
    let start = Instant::now();
    loop {
        if let Some(status) = child.try_wait().expect("poll isolated U3 test") {
            assert!(status.success(), "isolated {name}: {status}");
            return;
        }
        if start.elapsed() >= Duration::from_secs(30) {
            let group = format!("-{}", child.id());
            let killed = Command::new("kill").args(["-KILL", "--", &group]).status();
            let _ = child.kill();
            let _ = child.wait();
            assert!(
                killed.is_ok_and(|s| s.success()),
                "whole U3 process-group cleanup failed"
            );
            panic!("{name}: outer 30-second watchdog expired");
        }
        std::thread::sleep(Duration::from_millis(5));
    }
}
