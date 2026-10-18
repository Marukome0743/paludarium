# U9 境界と順序

## 端末の型と優先順位

ドキュメント根拠：FR4.1/4.2、C2/C8/C10/C11。HostへStreamIdごとのterminal_infoを追加する。端末状態はLinux guest向けのtermios flags/line/19 control charsとrows/columns/pixel寸法を持ち、非端末はNone。既定HostとRecordingHostは非端末。native Linux照会はHost内で固定TCGETS/TIOCGWINSZだけを使い、guest request番号は渡さない。非Linux native端末実機は未検証で、fake Hostで境界を確認する。

Config.tty=NoneならHostのstream別状態を使う。Someなら明示的仮想端末を全標準streamへ指定し、その寸法が優先する。Hostの既存termiosは保持し、Hostが非端末なら決定的Linux端末既定値を使う。dupされた標準FDは元のstdio_channelを追跡し、通常file・closedFDと区別する。argv/envp・read/writeの既存接続を維持する。

## 実装前のnative期待結果

検証済み：Docker VMMのLinuxcargo diff_u9 --listはexit0、14 tests/0benchmarks。これは検出の確認だけで意味論native実機証拠ではない。guest io.c/build.sh/oracle.pyを製品実装前に準備し、rootがfork nativeCIで実行する。native oracleログ確認前にHost/Kernel/Runtime製品を変更しない。

Linux ABI根拠：[Linux UAPI termbits.h](https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/asm-generic/termbits.h) はu32 flags4個、u8 line、19 control chars、TCGETS旧ABI36 bytes。[ioctls.h](https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/asm-generic/ioctls.h) のTCGETS0x5401/TIOCGWINSZ0x5413を採用し、実際のLinux期待結果と照合する。
