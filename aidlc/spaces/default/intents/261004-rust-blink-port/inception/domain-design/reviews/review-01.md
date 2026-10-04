## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-04T07:47:30Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/inception/domain-design/components.md > Host（behaviour・external_dependencies）と Launcher（responsibilities）、Runtime の依存 | wasm の Worker の作成・管理が Host（wasm 実装）と Launcher（JS）の両方の責任として書かれている。Rust 側の wasm コードは JS の Worker を単独で作れないため、Host の wasm 実装は Launcher の JS に頼るはずだが、この依存は宣言されていない。宣言すると Runtime → Host → Launcher → Runtime の循環になる。さらに Jit が生成した wasm を実行するには WebAssembly の instantiate が要るが、Host の trait（スレッド・待機・時刻・入出力・端末・ファイル）に含まれていない。well-formedness の「循環しない」は、隠れた依存のため成り立っていない。 | Worker 作成・メッセージ受け渡し・wasm の instantiate を担う側（Host か Launcher か）を 1 つに決め、Host の trait に含める。Host の wasm 実装と Launcher の関係（JS 側の import として注入する等）を depends_on か external_dependencies に明記し、循環がないことを Rationale に書く。 | New |
| R-02 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/inception/domain-design/components.md > Mmu・Kernel・Cpu・Jit の behaviour と、Assumptions & Open Questions | wasm で複数の Worker が動くとき、共有される状態の置き場所が決まっていない。Mmu のアドレス空間は SharedArrayBuffer に置く前提（未検証の assumption）だが、Kernel の状態（Process・FileDescription・FutexWaitQueue・Vfs の Inode）が Worker 間でどう共有されるかが書かれていない。lock 接頭辞付き命令や xchg などの原子的な命令を Cpu と Mmu のどちらが担うかも責任に無い（FR2.3 の futex は原子性に依存する）。Jit の CompiledBlock をページ書き換えで破棄する際の、他の Worker への伝え方も無い。ADR-003 は競合の不具合を認めているが、共有状態のモデルが無いと実装者が推測で決めることになる。 | 共有状態のモデル（どの状態を SharedArrayBuffer に置き、どれを 1 つの Worker だけが持ってメッセージで頼むか）と、原子命令の担当、Jit の他 Worker への無効化の伝え方を ADR にする。Mmu に「実行可能ページへの書き込みの通知」を責任として加え、通知の向き（Mmu が Jit に依存しない形）を示す。 | New |
| R-03 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/inception/domain-design/decisions.md > ADR-001〜005、007、008 | active rule（phases/inception.md の Architecture Standards）は「少なくとも 2 つの代替案」と「主要な決定ごとの security の検討」を求めている。ADR-001〜005・007 は Alternatives Rejected が 1 件だけで、ADR-008 は 2 件、ADR-006 は 2 件。security への言及は ADR-001（外へ出さない）にしか無く、ADR-005（JIT が生成するコードの境界検査）、ADR-007（unsafe の範囲）、ADR-003（待機の資源枯渇）には無い。 | 1 件しかない ADR に 2 件目の代替案を足す。ADR ごとに Security の項（影響が無ければ「影響なし」と理由）を加え、JIT の境界検査と unsafe の範囲を明記する。 | New |
| R-04 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/inception/domain-design/traceability.json > upstream_ids・coverage | FR だけが載り、NFR1〜NFR9 が無い。components.md は NFR2・NFR4・NFR5 などを参照しているが、設計への対応が追跡できない（NFR2 のファジング、NFR4 の隔離は Loader・Vfs・Kernel の振る舞いに直結する）。 | 設計に影響する NFR（NFR1、NFR2、NFR4、NFR5、NFR7）を upstream_ids と coverage に加える。 | New |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/inception/domain-design/components.md > entities（FileDescription、EpollInstance、EventCounter、SocketPairEnd、Mapping、DecodedInstruction、CompiledBlock） | identifier が一意でない。descriptor（fd 番号）はプロセスごとの値で、dup や fork で共有される open file description の identifier にならない（offset を持つ FileDescription は特に）。Mapping の start、DecodedInstruction と CompiledBlock の guestRip は、複数のアドレス空間（fork・execve）や書き換えをまたぐと衝突する。Thread には Process への references が無い。 | identifier を一意になる形（例：descriptionId、addressSpaceId を含む複合キー）にし、Thread → Process、CompiledBlock・Mapping → AddressSpace の references を足す。詳細は Functional Design に回してもよいが、ownership の段階で一意性は決めておく。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| なし（stage に宣言された検証ツールは無い） | 目視で確認 | depends_on と dependents の対称性：全 12 部品で一致。自己依存なし。宣言された依存だけなら循環なし（ただし R-01 の未宣言の依存は含まない）。entity の所有は 21 件すべてが 1 部品で、references の owned_by も宣言済みの部品と entity を指す。 |

### Summary

宣言された catalogue の構造は整っているが、wasm の Worker 周りの責任の重複と、Worker 間の共有状態のモデルの欠落（R-01、R-02）が、実装者の推測を要する最大の問題である。ADR が active rule の代替案・security の基準を満たしていない点（R-03）も、承認前に確認してほしい。
