#!/usr/bin/env -S uv run --script
"""Execute tasks from yml config file."""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml",
# ]
# ///
import os
import subprocess
import sys
from logging import INFO, basicConfig, getLogger
from pathlib import Path

import yaml

TASK_KEY = "tasks"

basicConfig(level=INFO, format="%(message)s")
logger = getLogger(__name__)


def load_yaml_files(filepaths: list[str]) -> dict:
    """Load and merge multiple YAML files."""
    merged_data = {}
    for filepath in filepaths:
        with Path(filepath).open() as file:
            data = yaml.safe_load(file) or {}
            merged_data = deep_merge(merged_data, data)
    return merged_data


def deep_merge(a: dict, b: dict) -> dict:
    """Deep merge two dictionaries, appending lists instead of replacing them."""
    if not isinstance(a, dict) or not isinstance(b, dict):
        if isinstance(a, list) and isinstance(b, list):
            return a + b  # リストは結合
        return b  # 他の型はbで上書き

    merged = a.copy()
    for key, value in b.items():
        if key in merged:
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = deep_merge(merged[key], value)
            elif isinstance(merged[key], list) and isinstance(value, list):
                merged[key].extend(value)  # リストを結合
            else:
                merged[key] = value  # それ以外は上書き
        else:
            merged[key] = value

    return merged


def execute_task(task_name: str, cmds: list[str], envs: dict[str, str]) -> None:
    """Execute a task as a subprocess with isolated environment."""
    msg = f"Running step: {task_name}"
    logger.info(msg)

    # 環境変数の準備
    task_env = os.environ.copy()
    task_env.update(envs)
    try:
        for cmd in cmds:
            subprocess.run(cmd, check=True, env=task_env, shell=True)  # noqa: S602
    except subprocess.CalledProcessError as e:
        msg = f"Step '{task_name}' failed (exit code: {e.returncode}). Aborting."
        logger.exception(msg)
        sys.exit(e.returncode)


def main() -> None:
    """Main function."""
    min_narg = 2
    if len(sys.argv) < min_narg:
        logger.info("Usage: python3 run_tasks.py [--debug] <config1.yml> [config2.yml ...>")
        sys.exit(1)

    args = sys.argv[1:]
    if args[0] in ["--debug", "-d"]:
        debug_mode = True
        args.pop(0)
    else:
        debug_mode = False

    yaml_files = args

    # YAMLをマージ
    yaml_data = load_yaml_files(yaml_files)

    if debug_mode:
        logger.info("========== Merged YAML ==========================")
        logger.info(yaml.dump(yaml_data, default_flow_style=False))
        logger.info("=================================================")

    # `tasks` フェーズが存在しない場合はエラー
    tasks = yaml_data.get(TASK_KEY) or []
    if not tasks:
        msg = f"'{TASK_KEY}' not found or empty in YAML."
        logger.info(msg)
        sys.exit(1)

    msg = f"Executing {len(tasks)} tasks."
    logger.info(msg)

    global_envs = {
        env.split("=")[0]: env.split("=", 1)[1]
        for env in (yaml_data.get("global", {}).get("envs", []) or [])
        if isinstance(env, str) and "=" in env
    }

    # execute task
    for task in tasks:
        task_name = task.get("name", "Unnamed Task")
        cmds = task.get("cmds", [])

        if not cmds:
            msg = f"Skipping step '{task_name}' due to missing cmds."
            logger.info(msg)
            continue

        step_envs = {
            env.split("=")[0]: env.split("=", 1)[1]
            for env in (task.get("envs", []) or [])
            if isinstance(env, str) and "=" in env
        }
        all_envs = global_envs.copy()
        all_envs.update(step_envs)
        execute_task(task_name, cmds, all_envs)

    logger.info("All steps completed successfully.")


if __name__ == "__main__":
    main()
