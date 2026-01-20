#!/usr/bin/env bash
set -euo pipefail

# Remove macOS metadata files that violate runtime contracts
find OUTPUTS -maxdepth 1 -type f -name ".DS_Store" -delete 2>/dev/null || true
