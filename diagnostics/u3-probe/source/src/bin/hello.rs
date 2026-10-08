//! ランナーのテスト用ゲスト。決まった文字列を stdout に出して終了コード 0 で終わる。
//! 引数があれば、それも 1 行ずつ出力する（引数の受け渡しの確認用）。
fn main() {
    println!("hello from formicarium guest");
    for arg in std::env::args().skip(1) {
        println!("arg: {arg}");
    }
}
