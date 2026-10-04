# U2 対象取得と命令フォームの棚卸し

検証済み：取得した native binaries と source/lock を固定して静的走査と bounded native body trace を保存した。全入力経路の runtime inventory と probe/aube の emulator 全体合格は未検証（U10）。静的 disassembly は埋込データ・死んだ経路・feature dispatch を含むので、その530 mnemonicを実行要求とみなさない。

## 固定対象と取得経緯

| 対象 | 固定 source identity | Binary SHA256 |
|---|---|---|
| probe | sibling formicarium revision d0bc647364c7cf48cd4cfd96af8ad863194636fe と観測したdirty source hash | 15e90407b6cc2dc8389048805475fb9c7b11d3e10f89c1da0d52dad7b1c99292 |
| aube v2.6.1 | https://github.com/aubepkg/aube.git commit bd94e42f54d3b5e3dd102716b7197f316cb5f4ed; annotated tag6c2e056ffcea46905bc4370118c2c6d676c8dbe7 | 11a363b499dcb356845d7b13d5f1cd2e644fb6d5764bfe1eaf5769e5b8880f4b |

probe Cargo.lock SHA256 7c225a7f5366474efde2725c3a96dbd1cc6b2b9954a35a28013e77e81d77bed5、manifest9edf236ba348a319efeb9a3afc90464b74fbe17f8c35acbe482e9254db6371a7。その他の source hash は code-generation/evidence.md に記録する。Session#1645 SHA2565eefa02f680d4a3e30249aad55f07675cced08c794e6a44d7e60197026dbeb2f。Sibling build script SHA256a96363e42c0038c3457fcdbb33385339aa8791a26c8f5f4c5dbe0317bc160f7d。

ドキュメント根拠：sibling script は release/locked、x86_64-unknown-linux-musl、空の AUBE_PRIMER_PATH で構築する。原artifactにはbuild receiptがなく、dirty sourceとの対応と歴史上のcontainerを確定できないため **provenance GAP** として保持する。観測した両ファイルは ELF64 x86-64 DYN。source取得にはjjを使用した。取得直後のcloneはmainだったため、releaseの読み出しは明示revisionを用い、隔離再構築時にはcache内のtreeをbd94...に復元して対応を確認する。

## 取得と trace の観測

`tests/guests/u2/inventory.py` は objdump の prefix と register 幅を正規化する。原artifactのJSONは probe162052命令行/172 mnemonic/865フォーム、aube5405600行/530 mnemonic/4658フォーム。静的な出現数であり、意味論の検証率ではない。以前の正規化前aube集計はこの値で置き換える。

`tests/guests/u2/trace.py` は実際のRIP bytes/operandsを記録する。最大20000命令・内部20秒、外側process timeout30秒を維持する。`.runtime.json` のentry sampleはloader初期化であり、本体到達の証拠には採用しない。採用した本体sampleは次のとおり。

| 操作 | 観測した本体の開始点 | 件数・停止理由 | Native 完了 |
|---|---|---|---|
| probe no arguments | 最初のstdout write: PASS tokio-timer | 20000 / budget | exit0,8 PASS checks |
| aube --version | 最初のstdout write | 9312 / budget | exit0,2.6.1 linux-x64 |
| aube install | 最初のfixture package.json open | 4551 / budget | exit0 |
| aube install --frozen-lockfile | 最初のfixture package.json open after removing fixture node_modules | 6040 / budget | exit0 |
| aube list | 最初のstdout write | 7447 / budget | exit0 |

#1645のlocal dependencyはsibling fixtureから取得し、networkを使わず実行する。JSONには開始RIP、捕捉filename/stdout、assembly/bytesと `complete_runtime_inventory:false` を保存する。budget停止は未出現経路の到達不能を証明しない。native操作の完了はtrace終了後に別途実行した。

不採用の観測：probe --version は無効なcheckでexit2。install/frozenのstdout起点試行はstdout writeへ到達せず、native stdoutは0 bytesだった。いずれも本体取得には数えない。最初のDocker inventory CLIの停止では、照合した当該PID17744だけを停止した。

## 整数候補と分類

`classify.py` は正規化した静的行と `.eh_frame` のFDE範囲を照合する。FDE内の出現は補助証拠であり、到達性の証明ではない。追加10整数候補を実装してnative比較した。ENTER/XLATとword stack形式もnativeケースを先行し、実装・比較した。

| 候補 | 静的行・FDE内の行 | Native testcase とフォーム |
|---|---|---|
| ADCX / ADOX | 3944/3944;3695/3695 | u2_bmi_forms,32/64,独立CF/OF carry chain |
| ANDN / BZHI | 50/50;43/43 | u2_bmi_forms,32/64,zero/幅境界/大きいindexとcount下位8bit |
| MOVBE | 12/12 | u2_bmi_forms,16/32/64,memory load/store |
| MULX / PEXT | 4665/4665;1/1 | u2_bmi_forms,32/64,暗黙RDXとhigh/low destinations、mask extraction |
| RORX / SHLX / SHRX | 320/320;285/237;234/210 | u2_bmi_forms,32/64,immediate/register count mask |
| ENTER / ENTERW | 416/0;8/0 | u2_frame_forms,64/16,nesting0/1/2/31;3件のsignal-context fault |
| XLAT | 320/0 | u2_frame_forms,AL0..255,RBX,address32,FS and GS+address32 |
| LEAVEW / POPFW / POPF / PUSHF | 4/0;4/0;302/0;302/0 | u2_frame_forms,word frameとPUSHFW/POPFW。64-bit形式は既存integer guest |

この整数候補表に未実装の命令群は残っていない。FDE外の行を証拠なしにdata扱いしていない。固定aws-lc-sys0.44.0 archiveのchecksumはCargo.lockと一致し、151552-byte p256 tableはbinary offset0x1b32000と一致した。ただしENTER0x174692e/XLAT0x1746a61を含む範囲ではなく、両候補を除外する根拠には使えない。

ドキュメント根拠：SIMD/vector/x87、guest thread/syscall統合は別unit（U3/U5/U4/U10）。静的出現だけではU2の範囲を拡張しない。CPU feature query/timer/RNG、privileged/port命令と未対応encodingは明示Unsupported/SIGILLを維持する。対象program全体のfeature dispatch互換性は未検証。検証済み：focused decoder testでVPXOR VEXはUnsupportedのままであり、整数BMI VEX whitelistはAVX SIMDを許可しない。

**限界：** bounded sampleは全runtime経路を網羅しない。原native binaryの歴史上のbuild条件は未確定。probe/aubeのemulator全体成功も未検証。必須フォームの取得・分類・nativeケース対応とは別にこれらの限界を保持する。隔離再構築のreceiptと新対象の照合が完了するまでは、Step2取得gateを完了扱いしない。


## 隔離再構築後に固定した対象
検証済み：`inventory/rebuild/build-receipt.json` は immutable builder、compiler、source snapshot、lock、build args、exit とbinary hashを記録する。probeは原binaryと完全一致、aubeの新hashはff54cffe389cc2cc589d2a737c3499e1b7be4589e9a2fe3bf37c6e7c205cca4a。aube原binaryの歴史上の由来はこの結果から推測で確定しない。source前後のsorted hash一覧はcmp失敗停止付きcommandで一致、jj treeと固定release revisionのdiffは0 files changed。sibling sourceへ書き込んでいない。
新aube静的JSONのSHA256はfd030342c2b2d8bd9acd79c7b77ce0bed87df3fa796620691715206d31b36dcf。旧JSONとも一致し、全4658form文字列・出現数の差分0を `aube.form-comparison.json` に保存した。binary全bytes同一の主張には使わない。
分類の分母はaube4658form：U2整数3136、system/environment190、U3 SIMD/x871332。probe865form：U2整数696、system/environment3、U3 SIMD/x87166。`{aube,probe}.form-classification.json` は全行のform/sample、category、実在するnative case群を保持し、aubeは幅・prefixも記録する。未分類0。categoryは契約範囲の分類であり、静的に現れた全bytesをそのまま実行した割合ではない。system/environmentの全encoding動作は未検証。sample欠如をdata/到達不能の根拠には使わない。
新probe noargsはnative8 PASS/exit0。新aube --version/install/frozen/listはnetworkなし、#1645のappとoutside/linkedを含む専用fixtureで各exit0。採用body sampleはversion5718、install7670、frozen7693、list6774命令、全てbudget停止。version/listはstdout、install/frozenはfixture openを起点にする。各JSONのRIP/bytes/filename/stdoutを保存し、complete_runtime_inventory=falseを維持する。probe本体sampleは同一binary hashにより既存の具体物へ対応させる。
追加prefixもnative比較済み：MULXのaddr32/二重addr32、ENTERのrepz/repnz・REX.R/RX/WR/WRXと66+REX.X/XB、XLATのdata16/REX/RB/XB/WXB・GS64/GS32、PUSHF/POPFのaddr32/segment/repnz/REX、および66+REX.WB POPF。caseはu2_bmi_forms/u2_frame_forms、decoder幅のexact case。MULXは暗黙RDX、ENTER/LEAVE/PUSHF/POPFはRSP/RBPとoperand幅、XLATはAL/RBXとsegment/address幅、ADXはCF/OFを対応表で扱う。stack/flags/stringのその他暗黙operandはRSI/RDI/RCXとDF、DIV系はRAX/RDX。これらはfamily/dimension対応であり、任意のregister alias/flags入力や全program経路を網羅する主張ではない。
必須target取得・分類・case対応のgateは上記新対象で回収した。全任意経路の未検証、原artifactの歴史上の由来不明、U10全program統合は別の限界として保持する。
FS/GS atomicの非ゼロsegment baseは u2_segment_atomic_forms の全LOCK/scalar/pair経路とaddr32/4GiB超target、mapped decoyで補完した。修正前後の観測と最終source検証は docs/u2/repairs/。静的分類分母・取得binary hash・bounded body sampleは変更していない。
