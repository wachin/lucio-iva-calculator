#!/usr/bin/env bash
set -euo pipefail

this_script="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
workspace_root="$(dirname "$(dirname "$this_script")")"
dist_dir="$workspace_root/build/dist"
tmp_dir="$workspace_root/build/tmp"

echo "Workspace root is ${workspace_root}"
mkdir -p "$dist_dir" "$tmp_dir"

if command -v lrelease >/dev/null 2>&1; then
    echo "Compiling translations..."
    for ts_file in "$workspace_root"/translations/*.ts; do
        lrelease "$ts_file" -qm "${ts_file%.ts}.qm"
    done
else
    echo "lrelease not found; using existing .qm files."
fi

pyinstaller -w -F -y \
  --name LucioIVACalculator \
  --hidden-import=PyQt6.QtCore \
  --hidden-import=PyQt6.QtGui \
  --hidden-import=PyQt6.QtWidgets \
  --hidden-import=PyQt6.QtSvg \
  --add-data "$workspace_root/assets:assets" \
  --add-data "$workspace_root/translations:translations" \
  --add-data "$workspace_root/docs:docs" \
  --distpath "$dist_dir" \
  --specpath "$tmp_dir" \
  --workpath "$tmp_dir" \
  "$workspace_root/main.py"
