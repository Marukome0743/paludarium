# U4 メモリ・時刻・シグナルの現在source確認

## 今回の結果

承認済み復旧Step15〜18を実行した。検証済み：U4 manifest107claimsは欠落0、現在bytesが署名済みproduction `4d52be0a6f3b11d6c11a62f96196985c9c280fdc` のCI対象に全一致。製品source・テスト・U1/U2凍結成果物を変更せず、既存実機CI証拠を再利用した。新しいテスト実行として数えない。

[CI37695518838](https://github.com/Marukome0743/paludarium/actions/runs/37695518838) の7jobsと [native37695518927](https://github.com/Marukome0743/paludarium/actions/runs/37695518927) の4jobsは全成功。U4差分44件、内部6層76件（MMU10/Host8/Kernel37/Runtime11/Cpu5/Types5）、3OS既存suite、lint/依存、全体行coverage92.57%を確認。親summaryとchild重複を区別した。80%下限を保持する。

## 実装・契約の現在値

既存anonymous mmap/munmap/mprotect/brk、typed Host clock/cancellable wait、signal action/mask/altstack、Linux x86-64 frame/returnと単一process/thread配送を確認。C1/C4のfault metadata、C2 Host clock/wait、C8 dispatcherとchecked signal codecの責任を保持する。CPUはHost/Kernelへ依存せず、MMU共通同期の中でHost waitを呼ばない。

signal frameはguest memoryへchecked codecで書き、REP continuationはhandlerから切り離して一致するreturn contextで復元する。target別pending/coalesceとThread/Process優先はlive oracleを含む既存native回帰で確認する。file-backed mmap、guest clone/futex、wasm/JIT統合は後続unitの境界として保持する。

計画Sourcesの「Host未実装」「配送しない」、Step1〜14の未作成説明は先行実装前のbaseline。現在値とは区別する。U4の個別functional/NFR/infra設計directoryは不存在で、共有requirements/components/contracts/units/story-mapを根拠にする。ストーリーを捏造しない。

## 更新した成果物

code-summary/evidence-current/traceability/source-manifest、現在snapshot source-hashes-current.json、validation-current.json、reviewed-source-4d52be0a-current.tsvを整合した。manifestはstrict version1 schema、107 owning pathsを保持。今回新application-sourceなし。旧summary/source-hashes/validation/traceabilityはhistorical-*へ保存し、evidence.mdとdocs/u4の先行raw/validationを改変していない。独立レビュー用ログはU4 verificationへコピーした。

## 残る品質GAP

未検証：現在sourceのsyscall_args/mmu_ops各600秒ASan。旧37paths snapshotから15pathsが変わり、syscall_args target自身とKernel/MMU/Host/Runtime/CPUなどの依存sourceが異なる。mmu_ops target単体が同じでも旧完走を現在プログラムへ転用しない。FR9.3/NFR2/NFR3はGAP。旧317件/93.70%とfuzz1136975/1564316各601秒は履歴。

既存nightly-2026-10-01、各600秒ASan、30秒watchdog、flags mask、coverage80%を保持し、Build and Testへ現在sourceでのfuzz確認を渡す。全任意入力、probe/aube emulator全program、wasm/browser、handler内FS/GS変更の追加native比較は未検証。性能測定なし。製品修正を必要とする新しい不具合は今回見つからなかった。
