## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-04T09:07:31Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/entities.md > entity ExitReason、aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/functional-spec.md > W3 | 設計の ExitReason は kind に budget-exhausted を持ち Halt を持たない。共有契約 contract-summary.md の C1 は Syscall、PageFault、InvalidOpcode、Halt の 4 つで、予算切れの値がない。C5 の run(state, mem, budget) は ExitReason を返すだけなので、W3 と BR4.3 の予算切れの止まり方を契約の型で表せない。InvalidOpcode は rip を持つが、設計は instructionBytes と faultIsWrite を別に持つ。Halt の扱い（hlt 命令）も設計にない。U1 は C1・C5 の提供者なので、どちらかを直さないと Cpu と Runtime の実装者が食い違う。 | ExitReason を C1 に合わせるか、予算切れ（BudgetExhausted）と Halt の扱いを U1 の設計として明示し、C1 の変更点として contract-summary に反映する前提を書く。ExitReason の持ち主を Cpu とするか paludarium-types とするかも C1 と揃える。 | New |
| R-02 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/rules.md > BR4.1、BR3.3、aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/entities.md > entity CpuState | Q1 で U1 の中に Rust の static-musl hello world を通すと決めているのに、U1 で実装する命令の一覧がない（BR4.1 は「U1 で実装した命令だけ」とあるだけ）。BR3.3 の syscall は strace で一覧を確かめる手順があるが、命令には同等の手順がない。Rust の x86_64 ターゲットは SSE2 が基準なので、Rust の hello world は xmm レジスタの命令を含む可能性が高い（推測。未検証）。C5 の CpuState は SSE レジスタを持つが、entities.md の CpuState は rax〜r15・rip・flags・fsBase・gsBase だけで xmm がない。SSE は U3 に繰り延べ（traceability の FR1.4）なので、Q1 の約束が U1 で満たせない恐れがある。 | 命令の一覧を、BR3.3 と同じように「ネイティブのバイナリを逆アセンブルして確かめ、一覧を直してから実装する」ルールとして定める。Rust の hello world に SSE 命令が要る場合は、xmm の状態と最小限の SSE 命令を U1 に含めるか、Q1 の A を U3 以降へ移す決定を人に諮る。 | New |
| R-03 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/rules.md > BR1.1、BR1.2、BR1.3 | BR1.1 は ELF の識別子・クラス・機械・PT_INTERP だけを確かめ、e_type（ET_EXEC か ET_DYN）に触れない。Rust の x86_64-unknown-linux-musl は既定で static-pie（ET_DYN）を作る可能性が高い（推測。未検証）。その場合は読み込みの基準アドレス（バイアス）、AT_PHDR・AT_ENTRY の補正、プログラム自身による再配置が要る。BR1.2 の「フラグどおりに 4096 バイト境界に置く」と LoadedImage の entryPoint・programHeaderAddress にバイアスの扱いがなく、実装者が推測せざるを得ない。 | ET_EXEC と ET_DYN（static-pie）のどちらを受け入れるかを BR1.1 に書く。ET_DYN を受けるなら基準アドレスの決め方（固定にして差分テストが決定的になるようにする）と補助ベクタへの反映を BR1.2・BR1.3 に足す。受けないなら、Rust のゲストを非 PIE でビルドする指定を BR7.2 に足す。 | New |
| R-04 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/entities.md > entity SessionConfig、GuestFile、aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/functional-spec.md > W1 | C10 の Config は program、args、env、files（パスと中身の組）、mounts、tty、jit を持つ。設計の SessionConfig は instructionBudget と GuestFile.mode を足し、mounts・tty・jit を持たない。C11 の --mount、--env、--no-jit の扱いが W1 にない（[options] とあるだけ）。また W1 の手順 2 は「ホストのファイルを読んで GuestFile にする」とあるが、<program> のホスト側のパスからゲスト内の programPath をどう決めるかが書かれていない。U1 は C10・C11 の提供者なので、Cli と Runtime で実装が分かれる。 | SessionConfig と C10 の差を一覧にして、U1 が持つ属性と持たない属性（U7・U9 以降へ送るもの）を明記する。W1 に、<program> の解釈（ホストのパスか、ゲストのパスか）、programPath の決め方、U1 で受け付けるオプションと、受け付けないオプションを渡されたときの振る舞いを足す。 | New |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/functional-spec.md > 状態の移り変わり、W3 | スレッドの状態表に、フォールトや invalid-opcode でシグナル終了する遷移と、止める要求（kill、BR4.3）による遷移がない。プロセスの Loading は W2 の手順 5 で Process を作る前の状態で、Process エンティティの生成時点と合わない。Rust の std は SIGSEGV のハンドラを rt_sigaction で登録する（BR3.3 に登録が含まれる）ので、「ハンドラがない（U1 では常に）」は事実と合わない。配送しないので終了するという意図なら、その旨に書き直す。 | スレッドに Signaled と kill の遷移を足し、プロセスの Loading と生成の順序を揃え、「ハンドラの登録はあるが U1 では配送しない」と表現を直す。 | New |
| R-06 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/rules.md > BR1.3 | AT_RANDOM の 16 バイトの出どころが決まっていない。C2 の Host trait に乱数の関数はない。差分テストはネイティブと標準出力が一致する必要があるので、決定的な値にするのか、Host に足すのかを決めておく必要がある。AT_RANDOM 以外の補助ベクタ（AT_SECURE、AT_UID、AT_EXECFN、AT_HWCAP など）で musl が読むものも書かれていない。 | AT_RANDOM の出どころ（U1 では固定値など）と、積む補助ベクタの一覧を BR1.3 に明示する。 | New |
| R-07 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/functional-spec.md > W6、aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/rules.md > BR6.1、BR8.1、BR8.2 | unit-of-work.md は wasm のスレッドの確認を「Host の trait を通したまま」行うとするが、BR6.1 は U1 の Host の実装をネイティブの Linux 用だけとし、W6 は確認用プログラムが trait を通すのか単独なのかを書いていない。Chromium 系・Firefox・Safari のテストページに COOP/COEP の見出しが要る（team.md の Testing Posture）が、W6 に配信の手順がない。BR8.1 の不合格と BR8.2 の「報告がなければ完了にしない」の関係も曖昧で、不合格の環境があるまま U1 を完了できるかが読み取れない。 | W6 に、確認用プログラムの構成（Host の trait との関係）、ページの配信と COOP/COEP、ブラウザの実行環境（Safari は macOS の CI）を足す。不合格のときの U1 の完了の扱いを一文で定める。 | New |
| R-08 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/functional-design/traceability.json > coverage、upstream_ids | FR1、FR2、FR5 は OK だが、子の FR1.3・FR1.4・FR1.6、FR2.2 以降、FR5.3・FR5.4 は Deferred で、親の状態が部分的な担当であることを表していない。rules.md は NFR2 を source に挙げるが、NFR は upstream_ids にも coverage にもない。 | 親の FR は Partial など実態に合う状態にするか、備考で子の繰り延べを示す。NFR2（と関連する NFR）を coverage に足す。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| 検証ツールなし（ステージ定義に宣言なし） | 該当なし | traceability の sensor は通過済みと指示にあったので、ここでは再実行していない。契約との照合は手作業（contract-summary.md の C1、C5、C7、C8、C10、C11 と components.md を読み比べた）で行った。 |

### Summary

U1 が提供者となる契約（C1 の ExitReason、C10・C11 の Config とコマンド）と設計がずれており、Q1 で約束した Rust の hello world を通すのに必要な命令の範囲（SSE の可能性）と ELF の種類（static-pie の可能性）が設計で決まっていない。Major が 4 件あるため NOT-READY。R-02 と R-03 は推測を含むので、修正時に実物のバイナリで確かめて根拠を示すこと。
