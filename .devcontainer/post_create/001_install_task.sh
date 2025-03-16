#!/bin/bash
if ! command -v task >/dev/null 2>&1; then
    uv tool install go-task-bin
fi
