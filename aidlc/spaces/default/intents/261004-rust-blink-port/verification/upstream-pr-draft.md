# upstream への draft PR の案（まだ出していない）

- 出し先：`aletheia-works/paludarium` の `main`
- head：`Marukome0743/paludarium:codex/build-and-test`（e3c29d1d8c2dae3c705d54de2c6fb0a2451e46d9。upstream の main db981106 から 99 commit 進んでいる。遅れは 0）
- 形：draft。手元の記録の commit（a7aecb72）は入れない（push していない）。
- コマンド（出すと決めたとき）：`gh pr create --repo aletheia-works/paludarium --base main --head Marukome0743:codex/build-and-test --draft --title '<タイトル>' --body-file <本文のファイル>`

---

## タイトル

Rust port of the blink x86-64 user-mode emulator: stages 1–5 (incl. wasm JIT) and 0.1.0 release tooling

## 本文

jart/blink の x86-64 Linux ユーザーモードエミュレータを Rust で作り直したものです。段階 1〜5（wasm の JIT まで）と、0.1.0 を公開するための道具を入れています。AI-DLC の 15 の作業単位（U1〜U15）で作りました。まだ draft です。下の「残っていること」が片付いたら ready にします。

### 入っているもの

- **エミュレータの crate（11）**：`paludarium-types`・`-decoder`・`-mmu`・`-host`・`-vfs`・`-loader`・`-cpu`・`-jit`・`-kernel`・`-runtime`・`paludarium`。版はそろえて 0.1.0 です。
  - 整数・SSE の命令。
  - メモリとシグナル、スレッドと futex、イベントとソケット。
  - 仮想ファイルシステム（ディレクトリの外へ出られない）、プロセスの起動、端末の入出力。
  - 実装していない syscall は `ENOSYS` を返します。
- **ホスト**：ネイティブの Linux・macOS・Windows と、wasm（Node.js の Worker、Chromium・Firefox・本物の Safari）。
- **JIT**：wasm 向けの JIT（整数 SSE の変換を含む）。JIT あり・なしは同じ差分テストで比べています。
- **npm**：`@paludarium/wasm`（起動用 JS と production wasm）。
- **公開の道具**：`scripts/release/`、`.github/workflows/release-check.yml`・`release.yml`・`u15-acceptance.yml`、`docs/release.md`。公開は tag から行い、保護された `release` environment での人の承認を通ります。初回だけ対象と期限を絞ったトークンを使い、2 回目からは Trusted Publishing です。
- **CI**：`ci.yml`（PR のゲート）、macOS・Windows・全体の品質、ファジング（13 対象×600 秒、ASan/LSan）、各作業単位のソースの照合。

### 確かめたこと（fork の e3c29d1d）

| 確認 | 結果 |
|---|---|
| PR のゲート `ci.yml`（23 job：lint、3OS の単体テスト、依存の検査、x86-64 Linux の差分テスト、wasm 4 環境、カバレッジ 80%） | 成功（fork の run 39114018191） |
| 公開物の確認 `release-check.yml` | 成功（39114018143） |
| 全品質 `u14-quality.yml`（34 job） | 成功（39114108809） |
| macOS の品質 `u12-quality.yml`（29 job） | 成功（39114110570、Safari の 1 job だけ再実行） |
| Windows の品質 `u13-quality.yml`（29 job） | 成功（39114112207） |
| ファジング `u14-fuzz.yml`（13 対象×600 秒） | 成功（39114114216） |
| ソースの照合 `u1-u14-source-bound.yml` | 成功（39114116352） |
| 行カバレッジ（workspace / 1 段階目の 11 crate / 端末 / wasm launcher / CPU・デコーダ） | 93.85% / 93.85% / 86.82% / 86.88% / 82.71% |
| JIT の速さ（FR8.3） | JIT ありが約 12.9% 速い。片側の正確検定で p = 1/1024 |

run の番号は fork（`Marukome0743/paludarium`）のものです。取り込むと head が変わるので、upstream の head で CI と受け入れの証拠を作り直します。

### 残っていること（ready にする前）

- **Safari の揺れ（NFR7）**：safaridriver 側の時間切れで、Safari の job が 1 回だけ落ちました。session の作成を 1 回だけやり直す直しを入れます。
- **CI の整理**：作業中に使った診断の workflow 21 個を消し、古い作業ブランチの起動条件を外します。夜間の workflow は、ファジングと全品質を呼ぶ形に作り直します。
- **残している軽微な指摘の直し**。
- これらは 1 回にまとめて、このブランチに足します。

### 取り込みと公開（upstream の管理者にお願いすること）

`docs/release.md` の「Owner hand-off」のとおりです。

1. この PR の取り込み（squash を想定）。
2. upstream に `release` environment を作り、必須レビュアーを置き、管理者の迂回を禁止する。
3. 11 crate と `@paludarium/wasm` の名前の所有と、初回の公開の方法（対象と期限を絞ったトークン）を決める。
4. Trusted Publisher を登録する（upstream、`release.yml`、`release`）。
5. main の head で品質の run を回し、`u15-acceptance.yml` を手動で起動する。
6. `v0.1.0` の tag を送り、environment で承認する。

PR のたびに必須にするチェックは、`ci.yml` の 23 job と `release-check.yml` を想定しています。

🤖 Generated with [Claude Code](https://claude.com/claude-code)
