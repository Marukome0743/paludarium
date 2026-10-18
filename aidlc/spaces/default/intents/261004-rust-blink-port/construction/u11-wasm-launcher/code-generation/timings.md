# U11 aube wall time

署名head7eb1819fのfresh CI38021278452はattempt3で全jobs成功。Node/Chromium/Firefoxと本物Safariの成功生結果を取得済み。先行するSafari準備失敗は別証拠として保持する。

## 現在の観測（検証済み）

| 環境 | version | 初回install | frozen | list |
|---|---:|---:|---:|---:|
| Node v24.21.0 / Linux | 0.874646 s | 3.421152 s | 2.218349 s | 0.609825 s |
| Chromium153.0.8010.12 / Linux | 0.871365 s | 3.033300 s | 2.030520 s | 0.639520 s |
| Firefox155.0 / Linux | 1.159580 s | 3.369620 s | 2.289360 s | 0.967840 s |
| Safari26.6.2 / macOS | 0.664300 s | 1.987220 s | 1.412220 s | 0.370660 s |

生結果はverification/final-7eb-ci/u11-{node,chromium,firefox}/observations.json。各14ケース完了・exit0。sourceは`7eb1819f52acede33e83775374dd4ee93edf643b`、module SHA256は`f459285f6bdc6f282d409533cc3daf25af3d46860a6cb86adb074f93fd242d1f`、oracle SHA256は`6df71b705f1826a5e6bd65bd7233a989f2911ff964d016b1ac28824bee81ac60`。probe SHA256は`3e2a3c772017bfc6cb5dd275c83b6d4f730bc7f219bfad8b1266f0a4cb66b5a9`、aube SHA256は`260573ab256e4e32e8664871306e21715678bebcad9e7ce941502a566676021f`。旧47a/b6の観測はそれぞれ旧証拠ディレクトリに保持し、この表へ混ぜない。

## 計測方法と負荷条件

Safariの成功生結果はverification/final-7eb-safari-attempt3/observations.json（job114126928791、artifact11658649218、created04:03:54）。旧final-7eb-ci/u11-safariは準備失敗の証拠であり、この表へ用いない。Safariも他3環境と同じmodule/oracle/guest hashを照合済み、14ケース完了・exit0。

`observeProgram`の`performance.now()`でrun開始からexit・stdout/stderr回収までを秒で記録する。各環境のversion→install→frozen→listは逐次実行する。nativeとproduction wasmのビルド、browser install、C12内部試験は受入コマンドより前に終了する。既知のバックグラウンドビルドを受入実行と重ねない。別CIジョブは別runner上で実行される。OS内部の背景負荷が完全にゼロであるとは主張しない。

同一固定guestとmodule/oracleのSHA256、source署名コミット、runner/browserバージョン、raw秒数は観測JSONに保持する。1回の逐次実行を記録するものであり、分布や速度保証ではない。初期fixtureはepoch0、nativeと同じcwd/HOME/TMPDIR、同じofficial append-only reporterを使う。install後のnode_modulesを除き、frozenとlistを同じprivate VFSで実行する。

## 背景資料値（ドキュメント根拠）

| 環境 | version | 初回install | frozen | list |
|---|---:|---:|---:|---:|
| CheerpX1.3.9 | 0.3–0.7 s | 1.8–5.7 s | 1.3–3.6 s | 0.17–0.65 s |

根拠は`aidlc/spaces/default/knowledge/documents/research/cheerpx-oss.md`の「On CheerpX 1.3.9」。2026-10-03のlocalhost、WebVM Debian buster、i586 glibc2.28版aube、statxをENOSYSへ変換するLD_PRELOAD shim、4回のhidden page loadという条件。初回install62秒という再現しなかった別観測も資料に残る。今回はx86-64 static-musl版・private VFS・公式reporterで条件が異なるため、速度比と合否閾値を作らない。
