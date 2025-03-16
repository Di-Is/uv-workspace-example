#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml",
# ]
# ///
import sys
import os
import subprocess
import yaml

TASK_KEY = "tasks"
DEBUG_MODE = False

def load_yaml_files(filepaths):
    """Load and merge multiple YAML files."""
    merged_data = {}
    for filepath in filepaths:
        with open(filepath, "r") as file:
            data = yaml.safe_load(file) or {}
            merged_data = deep_merge(merged_data, data)
    return merged_data

def deep_merge(a, b):
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


def execute_task(task_name, cmds, envs):
    """Execute a task as a subprocess with isolated environment."""
    print(f"Running step: {task_name}")
    
    # 環境変数の準備
    task_env = os.environ.copy()
    task_env.update(envs)
    try:
        for cmd in cmds:
            subprocess.run(cmd, check=True, env=task_env, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Step '{task_name}' failed (exit code: {e.returncode}). Aborting.")
        sys.exit(e.returncode)

def main():
    global DEBUG_MODE

    if len(sys.argv) < 2:
        print("Usage: python3 run_tasks.py [--debug] <config1.yml> [config2.yml ...>")
        sys.exit(1)

    args = sys.argv[1:]
    if args[0] in ["--debug", "-d"]:
        DEBUG_MODE = True
        args.pop(0)

    yaml_files = args

    # YAMLをマージ
    yaml_data = load_yaml_files(yaml_files)

    if DEBUG_MODE:
        print("--- Merged YAML ---")
        print(yaml.dump(yaml_data, default_flow_style=False))
        print("-------------------")

    # `tasks` フェーズが存在しない場合はエラー
    tasks = yaml_data.get(TASK_KEY) or []
    if not tasks:
        print(f"Phase '{TASK_KEY}' not found or empty in YAML.")
        sys.exit(1)

    print(f"Executing {len(tasks)} steps for phase '{TASK_KEY}'.")

    # グローバル環境変数
    global_envs = {
        env.split("=")[0]: env.split("=", 1)[1]
        for env in (yaml_data.get("global", {}).get("envs", []) or [])
        if isinstance(env, str) and "=" in env
    }

    # 各タスクを実行
    for task in tasks:
        task_name = task.get("name", "Unnamed Task")
        cmds = task.get("cmds", [])

        if not cmds:
            print(f"Skipping step '{task_name}' due to missing cmds.")
            continue

        # ステップ専用環境変数
        step_envs = {
            env.split("=")[0]: env.split("=", 1)[1]
            for env in (task.get("envs", []) or [])
            if isinstance(env, str) and "=" in env
        }

        # グローバル環境変数とマージ（ステップ側が優先）
        all_envs = global_envs.copy()
        all_envs.update(step_envs)
        print(cmds)
        execute_task(task_name, cmds, all_envs)

    print("All steps completed successfully.")

if __name__ == "__main__":
    main()
