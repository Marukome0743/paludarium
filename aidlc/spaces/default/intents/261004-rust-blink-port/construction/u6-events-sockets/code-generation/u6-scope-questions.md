# U6 範囲の確認

## 上流の範囲

unit-of-work.mdはeventfd2、自前edge-triggered epoll、AF_UNIX socketpair、タイマーとネットワーク拒否をU6へ割り当てている。requirements.mdのFR2.4〜FR2.7はmulti-thread tokio timerとUnixStream::pairの合格を要求する。Kernelがイベント状態を所有し、Hostは時刻と待機の道具を提供する。U5のThread/futex/signal通知、U7のfd共有・dup/close/fcntl、U9の標準入出力との境界を保持する。

以下は上流で具体化されていない判断である。回答後に実装範囲のsummaryを確認し、計画を作る。製品・fixtureはまだ変更しない。

## Q1. U6のタイマー範囲をどうしますか？

上流の「タイマー」はAPI全量を指定していない。目的はtokio timerの合格であり、既存Host clockとepollの待機期限を使える。

A. 既存clockとepoll期限でtokio timerを支え、timerfdはprobeで実使用が判明した場合に追加する（推奨）
B. timerfd_create/settime/gettimeも今回の必須範囲に含める
X. Other（具体的な範囲を記入）

[Answer]: A. 既存clockとepoll期限でtokio timerを支え、timerfdはprobeで実使用が判明した場合に追加する（推奨）

## Q2. AF_UNIX socketpairの対応型をどうしますか？

合格条件はUnixStream::pair。SOCK_STREAMは直接必要だが、DGRAM/SEQPACKETを必須とする上流指定はない。

A. SOCK_STREAMとNONBLOCK/CLOEXECを対応し、その他はnative観測に基づく明示エラーにする（推奨）
B. SOCK_DGRAMとSOCK_SEQPACKETも今回対応する
X. Other（具体的な型を記入）

[Answer]: A. SOCK_STREAMとNONBLOCK/CLOEXECを対応し、その他はnative観測に基づく明示エラーにする（推奨）

## Q3. 禁止ネットワークのerrnoをどうしますか？

FR2.7と要件分析Q9は全ホストで通信・名前解決を拒否すると決めているが、errno値は未指定。AF_INET/AF_INET6の作成等を全ホスト同じ方針で拒否する。nativeで成功する通信との不一致は製品ポリシーの例外として明示し、拒否テストで確認する。

A. EAFNOSUPPORTで統一する（推奨）
B. EPERMで統一する
X. Other（errnoと適用範囲を記入）

[Answer]: A. EAFNOSUPPORTで統一する（推奨）

## Consolidated Summary Confirmation

FR2.4〜FR2.7のeventfd2、自前edge-triggered epoll、AF_UNIX SOCK_STREAM socketpairをKernelに実装する。NONBLOCK/CLOEXEC、read/write、readiness、dup/closeと共有fdの寿命、timeout・signal・killによる待機解除を既存境界へ接続する。epollのinterest/ready状態、eventfd counter、socketpair双方のbufferとpeer状態はKernelが所有し、ホストのepollやネットワークへsyscallを転送しない。具体的なLinux flags・errno・イベント遷移はnative観測から確定する。

タイマーは既存Host clockとepoll期限でtokio timerを支える。timerfdは対象probeの実使用が確認された場合だけ追加する。AF_INET/AF_INET6はどのホストでもEAFNOSUPPORTで拒否する。これはnativeで通信可能な環境との差分例外として明示し、拒否の専用テストで検証する。DGRAM/SEQPACKETは今回の必須対応型に含めず、native観測に基づく明示エラーを扱う。

C2 Hostの時刻・待機、C4 MMUの検査付きguest memory、C6 VFS/共通fd、C8 Kernel syscall dispatchへ接続する。U5のThread/futex/signal owner receipt、U7のfd共有・dup/close/fcntl、U9の標準入出力の契約を維持する。主な変更候補はpaludarium-kernelのevent状態・files/syscallsとU6 guest/harness、必要な共通fd接続とCIである。wasm guest Worker接続はU11、probe全量統合はU10の境界として区別する。

テストrunnerを先に用意し、guest/syscallケースは製品変更前にx86-64 Linuxでnative期待を取得する。実装後に内部部品の単体テストを各5〜8件以上と境界統合テストを実施する。待機競合はchannel/barrierで同期し、有限timeout・watchdog・kill/reap・raw観測を保持する。毎CI fresh native差分、Linux行coverage80%以上、3OS fmt/clippy/tests/依存検査、対象fuzzのASan/LSan各600秒、現production moduleのNode/実Safari回帰を確認し、先行Unit証拠を保持する。有限ケース成功から全入力やprobe全量達成を推測しない。

Does this all look correct before I generate the artifact?

Looks correct
Request changes

[Answer]: Looks correct
