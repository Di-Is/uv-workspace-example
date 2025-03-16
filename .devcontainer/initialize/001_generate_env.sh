#!/bin/bash
set -e

usage() {
  echo "Usage: $0 -o <output_path> [-n <compose_project_name>] [-u <devel_user_id>]"
  exit 1
}

# Parse options
while getopts "o:n:u:" opt; do
  case "$opt" in
    o) OUTPUT_PATH="$OPTARG" ;;
    n) ARG_PROJECT_NAME="$OPTARG" ;;
    u) ARG_DEVEL_USER_ID="$OPTARG" ;;
    *) usage ;;
  esac
done

# Ensure output path is provided
if [ -z "$OUTPUT_PATH" ]; then
  echo "Error: Please specify the output path using the -o option."
  usage
fi

# Determine COMPOSE_PROJECT_NAME based on priority
if [ -n "$ARG_PROJECT_NAME" ]; then
  # Highest priority: specified as an argument
  COMPOSE_PROJECT_NAME="$ARG_PROJECT_NAME"
elif [ -n "$COMPOSE_PROJECT_NAME" ]; then
  # Medium priority: defined as an environment variable
  COMPOSE_PROJECT_NAME="$COMPOSE_PROJECT_NAME"
else
  # Lowest priority: use git repository name if available
  if command -v git >/dev/null 2>&1; then
    repo_path=$(basename -s .git $(git config --get remote.origin.url))
    if [ -n "$repo_path" ]; then
      COMPOSE_PROJECT_NAME=$(basename "$repo_path")-`id -un`
    else
      echo "Error: Not inside a git repository. Cannot determine COMPOSE_PROJECT_NAME."
      exit 1
    fi
  else
    echo "Error: git is not available and no COMPOSE_PROJECT_NAME was specified."
    exit 1
  fi
fi

# Determine DEVEL_USER_ID
if [ -n "$ARG_DEVEL_USER_ID" ]; then
  DEVEL_USER_ID="$ARG_DEVEL_USER_ID"
else
  DEVEL_USER_ID=$(id -u)
fi

# Validate DEVEL_USER_ID (must be a positive integer)
if ! [[ "$DEVEL_USER_ID" =~ ^[0-9]+$ ]]; then
  echo "Error: DEVEL_USER_ID must be a positive integer."
  exit 1
fi

# Output the .env file
cat > "$OUTPUT_PATH" <<EOF
COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME
DEVEL_USER_ID=$DEVEL_USER_ID
EOF

echo ".env file has been generated at $OUTPUT_PATH."
