# U1 現行共有 source の完了確認に残る検証

今回の作業は U1 Step39〜40 の証拠照合のみ。U1 の4成果物と manifest、先行 U1/U2/U4/U7/U9 の25成果物、製品 source を変更していない。旧証拠を現行合格へ読み替えず、新しい成功 checker は作成しない。

## 保存と限定検査

25 files の size/SHA256 は `u1-current-source-artifact-preservation.json` に全行を保存し、基準 `construction/u3-sse/code-generation/verification/preceding-unit-artifact-baseline.json` と照合した。これは文書保存の証拠であり、アプリケーション source の検証ではない。

今回 root が実行した U1 sensor-traceability は findings0、sensor-required-sections は h2_count11/findings0 で PASS と通知された。ここでは反復していない。限定 sensor の通過は下記実行証拠不足の解消を意味しない。

## 現行 bytes と一致する7対象 ASan/LSan

以下は署名 Verified CI の実測。全対象は seed1、address sanitizer、detect_leaks1、既存 `/work/fuzz/lsan.supp`、timeout30、rss2048 を保持し、各601秒/exit0、最小C2回exit0、ASan symbol有、LSan fatal無し。各 artifact の source 前後178 pathsおよび現在 host SHA が一致した。

| run / head | target と runs | 証拠 |
| --- | --- | --- |
| 37807689270 / 3b909a7cfb141c61aa0363a933b0558e7860bfa2 | cpu_u2 2099726、decode 79256799、mmu_u2 3696095、load_elf 18365385 | U3 verification/step8-final-four-sanitizers-observations.json、step8-final-four-source-proof.json、step8-final-four-sanitizers/ |
| 37809027345 / 27637cee72ebf388dd4d105df9faafb501d70b24 | syscall_args 1287413、vfs_paths 3128281、mmu_ops 2573125 | U3 verification/step8-final-three-sanitizers-proof.json、step8-final-three-sanitizers/ |

U3 verification は `construction/u3-sse/code-generation/verification/`。各 run/jobs/artifacts connector metadata、raw target logs、binary/symbols、corpus/archive SHA、環境、時刻、exit、source inventory を同ディレクトリに保存済み。これは固定有限時間の実測であり、任意入力の完全保証ではない。

## 完了確認を阻害する現行証拠の不足

1. CI37806377396 の workspace93.14%は記録済みだが、U1 package coverage は76.51%で80% gateに失敗した。CI37807689163 は SHA256RNDS2 の非整列跨ページ native #GP と emulator #PF の相違により coverage の実行途中で失敗した。修正版 command の80%以上を示す現行成功証拠はない。U3を未完扱いにしてこの共有 package floor を外すことはできない。
2. CI37807689163 の新 production wasm job は成功した。fixtureは旧6件にU3の7件を加えた13件、launcher側の予定検査は21件だが、ここで新しい artifact JSON/moduleを回収・全行検査していない。同一新 module の実Safari検証は未実行。旧14件の Safari 成功を現行新 module の成功へ転用できない。
3. 旧 Windows成功run37765054790 の NativeFs fixture bytes は保持されているが、共有types/CPU/kernel等はその後変更された。旧154 paths 全一致という主張は現行 source へ適用できない。新しい3OS unit job成功はあるが、現行依存 closure と Windows隔離回帰の raw metrics を厳密照合した新証拠は未取得。
4. 現行CIのSHA相違は再現済み。run37809419737 の同一 observer を3 runner×3反復で動かし、AMD EPYC7763 は非整列 accessible成功/跨ページ#PF、Intel Xeon8573C は双方#GPだった。Intel SDM Table2-21 の16-byte alignment契約を採用する人の選択と内容確認は root が記録したが、今回U1の範囲では修正実装しない。詳細は U3 verification/step8-sha-memory-proof.json と step8-sha-memory-contract-decision.md。

## 必要な後続作業

U3の正式な実行指示に従い、既に選択されたSHA3形式のalignment契約を実装し、比較対象と独立state不変テストを更新する。その最終 source で fresh native CI、workspace/U1 package両80% gate、必要な現行closureの600秒ASan/LSan、本番moduleのNode/実Safari、Windows回帰source/metricsを取得する。先行25成果物は維持する。

その後、全旧検査を維持しつつ新sourceと署名CI・artifactを厳密に結び付ける別pathの checker を具体化し、人の新command承認を受ける。現時点では既存checkerを変更せず、未達項目をFAILする以外の妥当な全source成功checkerは作成できない。U1 Step40の正式独立レビュー・完了確認は未完了。
