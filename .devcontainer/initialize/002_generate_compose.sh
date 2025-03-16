#!/bin/bash

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker command not found. Please install docker."
    exit 1
fi

# 使用方法の表示
usage() {
    echo "Usage: $0 -o output.yml [-d] file_or_directory1 file_or_directory2 ..."
    echo "  -o, --output   Specify the output file"
    echo "  -d, --debug    Print the generated compose.yml to stdout before writing to file"
    exit 1
}

# 引数の解析
OUTPUT=""
DEBUG=false
INPUT_PATHS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
    -o | --output)
        OUTPUT="$2"
        shift 2
        ;;
    -d | --debug)
        DEBUG=true
        shift
        ;;
    -*)
        echo "Unknown option: $1"
        usage
        ;;
    *)
        INPUT_PATHS+=("$1")
        shift
        ;;
    esac
done

# 必須パラメータのチェック
if [[ -z "$OUTPUT" || ${#INPUT_PATHS[@]} -eq 0 ]]; then
    usage
fi

# ファイルとディレクトリの引数を展開して対象ファイルリストを作成
COMPOSE_FILES=()
for path in "${INPUT_PATHS[@]}"; do
    if [[ -d "$path" ]]; then
        # ディレクトリの場合、再帰的に .yml, .yaml を検索
        while IFS= read -r -d $'\0' file; do
            COMPOSE_FILES+=("$file")
        done < <(find "$path" -type f \( -iname "*.yml" -o -iname "*.yaml" \) -print0)
    elif [[ -f "$path" ]]; then
        COMPOSE_FILES+=("$path")
    else
        echo "Warning: '$path' は有効なファイルまたはディレクトリではありません。スキップします。"
    fi
done

if [[ ${#COMPOSE_FILES[@]} -eq 0 ]]; then
    echo "処理対象となる .yml または .yaml ファイルが見つかりませんでした。"
    exit 1
fi

# docker compose に渡す -f オプションのリストを作成
COMPOSE_ARGS=()
for file in "${COMPOSE_FILES[@]}"; do
    COMPOSE_ARGS+=("-f" "$file")
done

# docker compose config を実行し、結果を取得
MERGED_COMPOSE=$(docker compose "${COMPOSE_ARGS[@]}" config --no-normalize --no-interpolate --no-path-resolution)

# コマンドが成功したか確認
if [[ $? -ne 0 ]]; then
    echo "Failed to create merged compose file."
    exit 1
fi

# デバッグモードなら、出力前に生成したcompose.ymlを表示
if [[ "$DEBUG" == true ]]; then
    echo "========== Merged Compose File Preview =========="
    echo "$MERGED_COMPOSE"
    echo "==============================================="
fi

# 既存のファイルがある場合の処理
if [[ -f "$OUTPUT" ]]; then
    TMP_FILE=$(mktemp)
    echo "$MERGED_COMPOSE" >"$TMP_FILE"

    # 差分があるか確認
    if diff -q "$TMP_FILE" "$OUTPUT" >/dev/null; then
        echo "No changes detected. Skipping write."
        rm -f "$TMP_FILE"
        exit 0
    else
        echo "Changes detected in '$OUTPUT'. Showing differences:"
        diff -u "$OUTPUT" "$TMP_FILE" | tail -n +3
        echo "-----------------------------------------------"

        # 差分がある場合のみ上書き確認
        read -p "Overwrite '$OUTPUT' with new changes? (y/n): " choice
        case "$choice" in
        y | Y)
            echo "Overwriting $OUTPUT..."
            mv "$TMP_FILE" "$OUTPUT"
            ;;
        n | N)
            echo "Operation cancelled."
            rm -f "$TMP_FILE"
            exit 1
            ;;
        *)
            echo "Invalid choice. Operation cancelled."
            rm -f "$TMP_FILE"
            exit 1
            ;;
        esac
    fi
else
    # 直接ファイルに保存
    echo "$MERGED_COMPOSE" >"$OUTPUT"
fi

echo "Merged compose file created: $OUTPUT"
