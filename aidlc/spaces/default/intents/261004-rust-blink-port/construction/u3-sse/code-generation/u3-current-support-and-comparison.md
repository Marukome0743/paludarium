# U3 支持命令と比較の現状

## APIと支持範囲

C3 decodeとC5 Cpuの型境界を維持する。AVX SIMD/EVEXと未追加familyはUnsupportedのまま。現在のassigned集合はlegacy129 mnemonicと追加暗号7形式で、全136行の実装file・実測encoding・ケース名・比較fileを `verification/u3-current-sha-reuse/inventory-case-audit.json` に示す。scalar MOVSD/CMPSDはstring形式と区別する。PCLMUL selector00/11と同じlane選択の無視bit変種だけを扱い、cross selectorは未対応。CPUID family広告を部分実装だけで有効にしない。

## 比較根拠

fresh native577変種の正常23,576／fault1,162行は同じ11195 CIで比較した。全assigned mnemonicに少なくとも1変種を対応付けるが、保守的静的候補の全register/prefix/offset形を個別に検証したとは言わない。RFLAGS0xcd5以外の非比較bitとtrap RF、CPUID host identity/featureの仮想契約との差を明示する。CPUID guest出力は独立契約assertで検査する。

Intel16byte SHA非整列#GPは読み込み前に発生し、fault時のRIP/XMM/GPR/MXCSR/flags/メモリを保存する。exact AMD signature a00f11/a10f11/b00f21の6シナリオだけnative差異を区別し独立virtual state invariantsを検査する。Intel c06f2/a06d1はstrict native比較、未知vendor/signature、encoding/input/trap変化はFAIL。詳細は既存native-contract.rsとu3_oracle.rs。

## 残る境界

U3 filter単独80%測定はGAP、9製品file測定81.293%とは別。固定probe/aubeの有限native DBIと命令比較をguest全機能完走に読み替えない。全静的候補の到達可能性・全入力・child Node・後続syscall/JITの保証はしない。旧調査/実行失敗は履歴保持する。
