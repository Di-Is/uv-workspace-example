#!/bin/bash

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker command not found. Please install docker."
    exit 1
fi

# Display usage
usage() {
    echo "Usage: $0 -o output.yml [-d] file_or_directory1 file_or_directory2 ..."
    echo "  -o, --output   Specify the output file"
    echo "  -d, --debug    Print the generated compose.yml to stdout before writing to file"
    exit 1
}

# Parse arguments
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

# Check required parameters
if [[ -z "$OUTPUT" || ${#INPUT_PATHS[@]} -eq 0 ]]; then
    usage
fi

# Expand file and directory arguments to create list of target files
COMPOSE_FILES=()
for path in "${INPUT_PATHS[@]}"; do
    if [[ -d "$path" ]]; then
        # If directory, recursively search for .yml and .yaml files
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

# Create list of -f options for docker compose
COMPOSE_ARGS=()
for file in "${COMPOSE_FILES[@]}"; do
    COMPOSE_ARGS+=("-f" "$file")
done

# Execute docker compose config and capture the result
MERGED_COMPOSE=$(docker compose "${COMPOSE_ARGS[@]}" config --no-normalize --no-interpolate --no-path-resolution)

# Check if the command succeeded
if [[ $? -ne 0 ]]; then
    echo "Failed to create merged compose file."
    exit 1
fi

# If debug mode, display the generated compose.yml before writing
if [[ "$DEBUG" == true ]]; then
    echo "========== Merged Compose File Preview =========="
    echo "$MERGED_COMPOSE"
    echo "==============================================="
fi

# Handling for existing output file
if [[ -f "$OUTPUT" ]]; then
    TMP_FILE=$(mktemp)
    echo "$MERGED_COMPOSE" >"$TMP_FILE"

    # Check if there are differences
    if diff -q "$TMP_FILE" "$OUTPUT" >/dev/null; then
        echo "No changes detected. Skipping write."
        rm -f "$TMP_FILE"
        exit 0
    else
        echo "Changes detected in '$OUTPUT'. Showing differences:"
        diff -u "$OUTPUT" "$TMP_FILE" | tail -n +3
        echo "-----------------------------------------------"

        # Prompt for overwrite confirmation only if differences exist
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
    # Save directly to file
    echo "$MERGED_COMPOSE" >"$OUTPUT"
fi

echo "Merged compose file created: $OUTPUT"
