import argparse
import subprocess
import sys
from pathlib import Path
from typing import NoReturn


def execute_test(python_version: str, package: str) -> NoReturn:
    """pytestを呼び出しテストを実行する.

    Args:
        python_version: pythonバージョン
        package: テスト対象のパッケージ名
    """
    repo_dir = Path(__file__).parent.parent
    package_dir = repo_dir / "libs" / package

    if python_version == "all":
        with Path(repo_dir / ".python-versions").open("r") as f:
            py_versions = f.read().splitlines()
    else:
        py_versions = [python_version]

    for py_version in py_versions:
        # コマンドを構築
        cmd = ["uv", "run", "--no-dev", "--group", "test", "--python", py_version, "pytest"]
        # コマンドを実行し、標準出力とエラー出力を画面に表示する
        result = subprocess.run(cmd, cwd=package_dir, check=False)  # noqa: S603
        if result.returncode != 0:
            # コマンドのリターンコードで終了
            sys.exit(result.returncode)
    sys.exit(0)


def main() -> NoReturn:
    """メイン関数."""
    # 引数のパーサーを作成
    parser = argparse.ArgumentParser(
        description="CLIツール: 指定された python_version と package を使用して uv run コマンドを実行します。"
    )
    parser.add_argument("python_version", type=str, help="使用するPythonのバージョン")
    parser.add_argument("package", type=str, help="実行するパッケージ名")
    args = parser.parse_args()
    execute_test(args.python_version, args.package)


if __name__ == "__main__":
    main()
