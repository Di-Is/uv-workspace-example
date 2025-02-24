# uvのworkspace機能を活用した複数のPythonパッケージの管理について

## はじめに

本記事では、Pythonのパッケージ管理ツール `uv`が提供するworkspace機能を活用し、1つのリポジトリ内で複数のPythonパッケージを効率的に管理する方法を紹介します。

## workspacesとは？

workspace機能は、大規模なコードベースを複数のパッケージに分割して管理するための仕組みです。
私は初めて出会いましたが、`cargo`や`npm`など他言語のパッケージ管理ツールにも類似の機能が存在するそうです。

uvのworkspace には以下の特徴があります。

- **単一のロックファイルで全パッケージの依存関係を管理**  
  → 1つのuv.lockで全体を管理できるため、全パッケージで依存関係の整合性が保たれます。  
- **全パッケージが同一の仮想環境にインストール**  
  → 開発時やテスト時に、統一された環境下で各パッケージが連携して動作することが保証されます。

これらの特徴から、以下のケースではworkspaceでの管理が適すると思われます。

- **依存関係に矛盾がなく、全パッケージが同時にインストール可能な場合**  
  例: すべてのライブラリが同一バージョンの共通依存に基づいている場合。  
- **同一の用途・目的で連携するパッケージ群を管理する場合**  
  例: コア機能とその拡張ライブラリを 1 つのリポジトリ内で管理したいとき。

一方で、異なるユーザー向けのコードや全く異なる用途のライブラリを1つのリポジトリで管理する場合、依存関係の衝突が発生したり、不用意に依存関係が更新される可能性があるため、workspaceは適しません。

なお、この様なケースでもuvを使って効率良くパッケージを管理できる方法があります。
下記の記事で詳細に説明されているので、そちらを御覧ください。
pre-commitやタスクランナー、IDE等のパッケージ構成を超えて実際の開発フローを見据えた部分まで考えられていてとても参考になります。

https://zenn.dev/mottyzzz/articles/20250113193501

また、uvの公式docsでもworkspaceの向き不向きについて説明されています。

https://docs.astral.sh/uv/concepts/projects/workspaces/#when-not-to-use-workspaces

## workspace を利用したパッケージ管理の実践例

ここでは、コア機能を提供するライブラリ `precise_logger` と、その拡張ライブラリ `precise_logger_json` の 2 つのパッケージを 1 つのリポジトリで管理する例を紹介します。  
- **precise_logger**: 小数点以下まで含むタイムスタンプを出力できる `logging.Formatter` の拡張クラスを提供。  
- **precise_logger_json**: JSON 形式の構造化ログを出力できる `logging.Formatter` の拡張クラスであり、内部で `precise_logger` を依存関係として利用し、同等の機能を提供。

~~地味にPythonのログのタイムスタンプに小数含めるの面倒なんですよね。~~

### 前提条件

本記事の検証環境は以下の通りです。

- OS: Ubuntu 24.04 (Docker コンテナ)
- CPU: x86_64
- uv version: v0.6.2

### リポジトリ構成

最初に示した2つのパッケージは以下のようなディレクトリ構成で配置します。

```tree
|-- libs
|   |-- precise_logger
|   |   |-- pyproject.toml
|   |   `-- src
|   |       `-- precise_logger
|   |           `-- __init__.py
|   `-- precise_logger_json
|       |-- pyproject.toml
|       `-- src
|           `-- precise_logger_json
|               `-- __init__.py
`-- pyproject.toml
```

リポジトリトップの pyproject.toml では、workspace の構成パッケージが libs 直下にあることを明示します。
このトップレベルの階層はworkspace rootとも呼ばれます。
なお、workspace を利用する場合、workspace rootの [project] テーブルは必須ではありません。

```toml:pyproject.toml(リポジトリトップ)
[tool.uv.workspace]
members = ["libs/*"]
```

precise-loggerのpyproject.tomlはシンプルです。

```toml: pyproject.toml(precise-logger)
[project]
name = "precise-logger"
version = "0.1.0"
requires-python = "~=3.9"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

precise_logger_jsonは、依存関係として python-json-logger と precise_logger を利用します。
なお、precise_logger は PyPi からではなく workspace 内のパッケージとして参照するため、[tool.uv.sources] テーブルでその旨を明示します。

```toml: pyproject.toml(precise-logger-json)
[project]
name = "precise-logger-json"
version = "0.1.0"
requires-python = "~=3.9"
dependencies = ["python-json-logger~=3.0", "precise-logger>=0.1.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv.sources]
precise-logger = { workspace = true }
```

これらのpyproject.tomlと各パッケージの`__init__.py`が準備できれば、最低限の構成は完成です。
`uv tree`で依存関係のツリーを見てみると、2つのパッケージが期待通りに依存解決できていることがわかります。

```bash
$ uv tree
precise-logger-json v0.1.0
├── precise-logger v0.1.0
└── python-json-logger v3.2.1
    └── typing-extensions v4.12.2
```

### uvコマンドと環境の相互作用

workspace利用時のuvコマンドは、実行するディレクトリによって挙動が変わります。
以下の表は、コマンド実行時のディレクトリとuvの各サブコマンドの動作の違いを示しています。

|uvのサブコマンド|各パッケージの階層以下での実行|左記以外(例:リポジトリトップ)での実行|
|--|--|--|
|sync|各パッケージ単体の依存関係のみをインストール|workspace全体の依存関係をインストール|
|add|対象パッケージのpyproject.tomlに依存関係が追加される|エラーとなる※1|
|remove|各パッケージのpyproject.tomlから依存関係が削除される|エラーとなる※1|
|build|各パッケージが個別にビルドされる|workspace rootには[build-system]テーブルが存在しないため、ダミーのパッケージがビルドされる※2|
|run|各パッケージの依存関係が導入された環境でスクリプトを実行する|全依存関係が導入された環境でスクリプトを実行する|

※1: リポジトリトップのpyproject.tomlには[project]テーブルが存在しないためエラーとなる。
※2: unknownという名称のパッケージがビルドされるが、ユースケース的にはエラーになるのがベター?今後のアップデートで変更される可能性あり。

基本的に、各パッケージのディレクトリ内ではそのパッケージ単体、リポジトリトップなど上位階層ではworkspace 全体に対してコマンドが作用する、と理解すれば問題なさそう。
また、実行時のディレクトリに関係なく`--package {パッケージ名}`を指定すれば特定のパッケージに対して、また `sync`、`build`、`run`の3種のコマンドは`--all-packages`オプションを使用することで、workspace全体に作用させることも可能です。

### dependency groupの扱い

PEP 735で導入されたdependency groupは、開発時に使用する追加の依存関係（例: リンターのruff、テストフレームワークのpytest等）をグループとして管理できる仕組みです。
これは、各パッケージの依存関係を定義する[project.dependencies]とは別に管理され、グループ同士のマージも可能です。

uvでは、`uv sync`実行時にdevグループが通常の依存関係とともに環境へインストールされます。
たとえば、以下のように宣言しておけば、`uv run ruff check`によりruffのリンター機能を呼び出せます。

```toml
[dependency-groups]
lint = ["ruff"]
dev = [
    { include-group = "lint" },
]
```

dependency groupの宣言はリポジトリトップまたは各パッケージのpyproject.tomlのいずれか、または両方で可能です。

- リポジトリトップで宣言した場合
    - workspace以下どこでも利用可能となる
- 各パッケージで宣言した場合
    - そのパッケージ以下の階層で利用可能となる
    - workspace rootのdependency groupとの和が適用される※1

※1: 通常の依存解決も行われるため、各パッケージ、root workspaceで矛盾する依存関係が定義されるとエラーが発生します。

動作的には全パッケージ共通の開発ツールはリポジトリトップに、個別で使うものは各パッケージに定義しても良さそうに見えます。
ただ、[開発者](https://github.com/astral-sh/uv/issues/9863#issuecomment-2541762530)は各パッケージで使用する全てのdependency groupは各パッケージで宣言して欲しいと話していたので、その様にするのが無難かもしれません。

## まとめ

今回、uvのworkspace機能を利用して複数の Python パッケージを 1 つのリポジトリで管理する方法を具体的な例とともに紹介しました。
便利な機能が多数提供されますが、プロジェクトごとに向き不向きが出る面もあります。
個人的には導入前に十分な検証と見定めが必要だと思います。

今回作成したコード例は下記リポジトリにまとめているので、ぜひ試してみてください。

https://github.com/Di-Is/uv-workspace-example

## 参考

- [zenn - uvを活用したPythonのマルチプロジェクトのモノレポ構成](https://zenn.dev/mottyzzz/articles/20250113193501)
- [github uv repository - Discussion: uv workspaces in a monorepo - thoughts on change-only testing](https://github.com/astral-sh/uv/issues/6356)
- [uv docs - concepts - projects - workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources)
- [PEP 735 - Dependency Groups in pyproject.toml](https://peps.python.org/pep-0735/)
- [github uv-workspace-example repository](https://github.com/Di-Is/uv-workspace-example)
