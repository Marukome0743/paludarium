# aidlc/ の記録と新しい入口を commit する案

2026-10-18。読み取りだけで調べて書いた。commit も push もしていない。

## 今の状態

- 作業コピーの親は e3c29d1d（fork `codex/build-and-test` の head）。
- `aidlc/` の下の、まだ commit していないファイル：
  - jj が追っているもの（新しいファイル）：172,555（約 3.0 GB）。変更されたファイル：33。
  - jj が大きさの上限（1 MiB）で取り込みを断ったもの：2,957。
- 172,555 ファイルの内訳：

| 分け方 | ファイル | 大きさ |
|---|---|---|
| ビルドとキャッシュのフォルダ（`target/`・`cargo-home/`・`profiles-and-objects/`・`node_modules/`・`__pycache__/` などの下） | 61,979 | 約 1.2 GB |
| 各 Unit の `verification/` の下の証拠（CI の原本、展開した artifact、coverage など） | 約 110,100 | 約 1.85 GB |
| 記録の本体（計画・手順書・code-summary・traceability・質問・state・audit・memory など、`verification/` の外） | 475 | 約 4 MB |

- `aidlc/` の外の未 commit の変更は、手元のもの（`.aidlc-version`・`mise.toml`・`__pycache__` の `.pyc`・`target/` の下）だけで、製品のファイルではない。この commit には入れない。

## 気をつけること

1. **新しい入口との関係**：
   - 正式な確認コマンド（`entry-c.py`）は、e3c29d1d から head までに変わったファイルの一覧を、binding・保存した compare・手元の git の 3 つで照らし合わせる。この一覧には `aidlc/` の下のファイルも入る。
   - GitHub の compare の応答は、変わったファイルを 300 件までしか返さない。そのため、何万もの記録のファイルを製品のブランチに足して push すると、その head では入口が通らない。
   - commit を手元に置くだけ（push しない）なら、入口は binding の head（e3c29d1d）と今の作業コピーの製品のファイルを比べるので、影響しない。commit の後に入口を 1 回実行して確かめる。
2. **大きさ**：証拠を全部入れると約 1.85 GB になり、GitHub のリポジトリとしては大きい。1 MiB を超えるファイルは jj が断るので、入れるには個別に上限を上げる必要がある。正式な確認コマンドが読むファイルのうち 1 MiB を超えるのは、FR8.3 の ZIP（`ci-e3c29d1d/u14-quality-39114108809/artifact-zip/u11-node-12131882922.zip`、1,332,216 bytes）の 1 つだけ。
3. **署名**：jj の commit は手元では署名せず、push のときに署名する（`git.sign-on-push`）。

## 案

### 何を入れるか

- **A. 記録の本体と、正式な確認コマンドが読むものだけ（推奨）**
  - 記録の本体：`verification/` の外の 475 ファイル。
  - 正式な確認コマンドが読むもの：U15 の `verification/entry-e3c29d1d/`（18 ファイル）、`verification/version-allowance/`（118 ファイル。v1〜v4 と、起点の記録の v4 の結果を含む）、`verification/ci-e3c29d1d/`（40 ファイル。FR8.3 の ZIP は上限を上げて入れる）。
  - 合わせて 650 ファイル、約 20 MB。
  - ほかの証拠（約 1.85 GB）は手元に残す。記録の中の参照先は手元にしかないことを、README か code-summary に一行書く。
- **B. ビルドとキャッシュ以外は全部**：約 110,600 ファイル、約 1.85 GB。証拠もリポジトリに残るが、大きい。1 MiB を超える 2,957 ファイルは別に扱いを決める必要がある。
- **C. まだ入れない**：公開が終わるまで手元に置く。

### どこに入れるか

- **1. 製品のブランチの上に、手元の commit として置く（推奨）**
  - e3c29d1d の上に、`aidlc/` だけの commit を 1 つ作る（path を限った `jj commit`）。push はしない。
  - 次の製品の変更（NFR7 の直し、workflow の変更、Minor）とまとめて push する。
  - その前に、入口の新しい版で「変わったファイル」の照合を `aidlc/` の外に限る（`aidlc/` の中は手元の git だけで数える）。これは入口のコードの変更なので、独立レビューと採用が要る。次の製品の変更のときに、binding の更新と一緒に行う。
- **2. 記録だけの別のブランチ**（例 `codex/aidlc-records`）を作って push する。製品のブランチと入口には影響しないが、upstream に入れるときに 2 つのブランチを合わせる手間が増える。

## 手順（A と 1 を選んだとき）

1. 入れるファイルの一覧を作って見せる（650 前後）。
2. `jj commit -m '<message>' <paths…>` で `aidlc/` の中の決めたファイルだけを 1 つの commit にする。ZIP だけは `--config snapshot.max-new-file-size=...` を付けて取り込む。
3. commit の後、作業コピーで正式な確認コマンドを 1 回実行し、exit 0 を確かめる。
4. bookmark は動かさない（`codex/build-and-test` は e3c29d1d のまま）。push しない。
