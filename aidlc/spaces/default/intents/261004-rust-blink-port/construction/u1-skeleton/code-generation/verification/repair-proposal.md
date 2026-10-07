# 実機LinuxとDocker VMMの比較・修正案

## Sources

- ユーザーの承認：forkのGitHub Actionsで検証し、手元のDockerでも調査する。
- CI run: https://github.com/Marukome0743/paludarium/actions/runs/37669465134
- 署名検証済みcommit: `aa7cf96343813fe60ddf841b9aae108183e2052d`。
- `native-bookworm-37669465134.log`、`native-ubuntu-37669465134.log`、`docker-vmm-u2-alu.log`、`docker-vmm-u2-faults.log`、`docker-vmm-workspace-lib.log`。

## 検証済みの結果

| 対象 | Docker VMM amd64（QEMU） | 実機x86-64 Bookworm | 実機x86-64 Ubuntu |
|---|---|---|---|
| U1差分 | 16件通過 | 16件通過 | 15件通過、hello_c失敗 |
| U2 REP比較fault | 4件不一致 | 同じ4件不一致 | 同じ4件不一致 |
| U2 ENTER allocation fault | 不一致 | 通過 | 通過 |
| U2 ALU | 全体実行は30秒watchdog失敗、単独実行通過 | 通過 | 通過 |

全体チェックは未合格。BookwormのU2は34件通過・4件失敗。実機では後続U4・U7のゲスト生成も失敗した。

DockerのENTER故障RIPは `0x401717 - 61 = 0x4016da`。逆アセンブルの `0x4016da` はENTER後の `_exit` 呼出し。これは実機側のENTER命令自身のfaultと異なる。

Ubuntuのhello_cは `66 48 0f 6e c0`（MOVQ）の未対応で停止し、直後に `66 0f 6c c0`（PUNPCKLQDQ）がある。

U4 `tests/guests/u4/build.sh` は現ファイルの `bash -n` がexit2、CRLFをLFにした一時コピーはexit0。U7にもCRLFだけの行が4行ある。元ファイルはこの調査では変更していない。

REPフラグは実機でも差があるため、QEMUだけの問題として処理できない。現在のflags復元処理とnative observerの初期状態、CPU vendor、割込み／再開時の状態を追加で確認し、設計・仕様と照合して修正対象を確定する。比較maskを拡張して通過させない。

## 次の修正計画案

1. 現在のcode-generationを正式に再開し、以下の追加範囲を計画・テスト手順に反映して新しいPlan Approvalを得る。
2. U1：legacy XMMのMOVQ/PUNPCKLQDQに必要なnative差分ケースを先に追加。MOVQの上位64bitゼロ化、非対称値、自己aliasを含める。decoder/CPUに最小限の対応を加え、内部単体テストを追加する。MMX/AVXは広げない。
3. U2：REP4件のnative observerとCPUモデルを照合。仕様を裏付けてから実装またはobserverを修正する。30秒watchdogは保持する。
4. 検証スクリプト：U4/U7の混在改行をLFへ統一し、native Linuxでゲスト生成が成功することを確認する。
5. 修正ごとの回帰を先に実行し、最後にfork CIの全体テスト・lint・80%以上のカバレッジを確認。Docker VMMで可能な単体／差分を確認し、ENTERの環境差を別途記録する。
6. source manifest・証跡を現在の内容へ更新し、独立レビューと正式なチェックポイント検証を行う。検証コマンドを変更する場合は専用の承認を得る。

Docker VMMとvoicevoxは維持する。合格・承認・工程完了は記録していない。
