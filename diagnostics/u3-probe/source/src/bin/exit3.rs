//! ランナーのテスト用ゲスト。stderr に 1 行出して終了コード 3 で終わる。
fn main() {
    eprintln!("exiting with status 3");
    std::process::exit(3);
}
