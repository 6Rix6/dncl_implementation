# DNCL インタプリタ

共通テスト手順記述標準言語 (DNCL) の Python 実装

## 概要

このプロジェクトは、日本の大学入試センターが定めた共通テスト用の手順記述言語 (DNCL) のインタプリタです。DNCL は、高等学校の「情報関係基礎」試験で使用される日本語ベースのプログラミング言語です。

## 機能

✅ **完全な言語サポート**

- 変数と配列 (1 次元・2 次元)
- 表示文 (`を表示する`)
- 代入文 (`←`)
- 算術演算 (`＋`, `－`, `×`, `/`, `÷`, `％`)
- 比較演算 (`＝`, `≠`, `＞`, `≧`, `＜`, `≦`)
- 論理演算 (`かつ`, `または`, `でない`)
- 条件分岐 (`もし`, `ならば`, `そうでなければ`, `そうでなくもし`)
- ループ
  - 前判定 (`の間、を繰り返す`)
  - 後判定 (`繰り返し、を、になるまで実行する`)
  - 順次繰返し (`を〜から〜まで〜ずつ増やしながら/減らしながら`)
- 関数定義と呼び出し (`関数 〜 を 〜 と定義する`)
- 組み込み関数 (`乱数`, `奇数`, `二乗`, `べき乗`)

## インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd dncl_implementation

# Python 3.7以上が必要です
python --version
```

依存関係は標準ライブラリのみです。

## 使い方

### REPL モード（対話型）

```bash
python main.py
```

対話型シェルが起動します：

```
DNCL インタプリタ (共通テスト手順記述標準言語)
終了するには 'exit' または Ctrl+C を入力してください

>>> x ← 10
>>> 「xの値: 」と x を表示する
xの値: 10
```

### ファイル実行モード

```bash
python main.py examples/fibonacci.dncl
```

詳細な出力が必要な場合：

```bash
python main.py -v examples/fibonacci.dncl
```

## サンプルプログラム

`examples/` ディレクトリに以下のサンプルがあります：

- **`hello.dncl`** - 基本的な変数と表示
- **`arithmetic.dncl`** - 算術演算
- **`conditionals.dncl`** - 条件分岐
- **`loops.dncl`** - 各種ループ
- **`functions.dncl`** - 関数定義と呼び出し
- **`arrays.dncl`** - 配列操作
- **`fibonacci.dncl`** - フィボナッチ数列

### 例: フィボナッチ数列

```dncl
「フィボナッチ数列（最初の10項）」を表示する

a ← 0
b ← 1

a を表示する
b を表示する

i を 2 から 9 まで 1 ずつ増やしながら，
  c ← a ＋ b
  c を表示する
  a ← b
  b ← c
を繰り返す
```

実行結果：

```
フィボナッチ数列（最初の10項）
0
1
1
2
3
5
8
13
21
34
```

## アーキテクチャ

インタプリタは以下のコンポーネントで構成されています：

```
┌─────────────┐
│ DNCL Source │
└──────┬──────┘
       │
       ▼
   ┌────────┐
   │ Lexer  │  トークン化
   └───┬────┘
       │
       ▼
   ┌────────┐
   │ Parser │  AST構築
   └───┬────┘
       │
       ▼
┌──────────────┐
│ Interpreter  │  実行
└──────────────┘
```

### ファイル構成

- **`ast_nodes.py`** - AST（抽象構文木）ノード定義
- **`lexer.py`** - 字句解析器（トークナイザー）
- **`parser.py`** - 構文解析器
- **`interpreter.py`** - インタプリタ（実行エンジン）
- **`repl.py`** - 対話型シェル
- **`main.py`** - メインエントリーポイント

## テスト

すべてのサンプルプログラムを実行してテスト：

```bash
# 各サンプルを実行
python main.py examples/hello.dncl
python main.py examples/arithmetic.dncl
python main.py examples/conditionals.dncl
python main.py examples/loops.dncl
python main.py examples/functions.dncl
python main.py examples/arrays.dncl
python main.py examples/fibonacci.dncl
```

## 言語仕様

このインタプリタは、大学入試センターが公開している[DNCL 仕様書](DNCL-Spec.md)に基づいて実装されています。

### 主な構文

#### 変数の代入

```dncl
x ← 10
Tokuten[0] ← 95
```

#### 表示

```dncl
x を表示する
「結果: 」と x を表示する
```

#### 条件分岐

```dncl
もし x ＞ 10 ならば
  「大きい」を表示する
を実行し、そうでなければ
  「小さい」を表示する
を実行する
```

#### ループ

```dncl
# 前判定
x ＜ 10 の間，
  x を 1 増やす
を繰り返す

# 後判定
繰り返し，
  x を 1 増やす
を，x ≧ 10 になるまで実行する

# 順次繰返し
i を 1 から 10 まで 1 ずつ増やしながら，
  i を表示する
を繰り返す
```

#### 関数

```dncl
関数 和を表示する (n) を
  wa ← 0
  i を 1 から n まで 1 ずつ増やしながら，
    wa ← wa ＋ i
  を繰り返す
  wa を表示する
と定義する

和を表示する (10)
```

## 開発

### デバッグモード

詳細な実行情報を表示：

```bash
python main.py -v examples/fibonacci.dncl
```

トークンと AST の情報が表示されます。

## ライセンス

このプロジェクトは教育目的で作成されています。

## 参考

- [共通テスト手順記述標準言語 (DNCL) の説明](https://www.dnc.ac.jp/albums/abm.php?d=67&f=abm00000819.pdf&n=R4_%E5%85%B1%E9%80%9A%E3%83%86%E3%82%B9%E3%83%88%E6%89%8B%E9%A0%86%E8%A8%98%E8%BF%B0%E6%A8%99%E6%BA%96%E8%A8%80%E8%AA%9E%EF%BC%88DNCL%EF%BC%89%E3%81%AE%E8%AA%AC%E6%98%8E.pdf) - 独立行政法人大学入試センター 2022 年 1 月

## 作者

DNCL Python Implementation
