#!/usr/bin/env bash
# Builds the eval workspace (the current directory) from a fixture.
#   load.sh <fixture> <case dir> [--new-user]
#   <fixture>    clean | messy  (a folder next to this script)
#   --new-user   remove AgentReferences/, as on a first run
# Then, from the case dir, if present:
#   overlay/             copied on top (adds or replaces files)
#   state-append.jsonl   appended to AgentReferences/state.jsonl
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fixture="$here/$1"; case_dir="$2"; shift 2
cp -R "$fixture/." .
if [[ "${1:-}" == "--new-user" ]]; then rm -rf AgentReferences; fi
if [[ -d "$case_dir/overlay" ]]; then cp -R "$case_dir/overlay/." .; fi
if [[ -f "$case_dir/state-append.jsonl" ]]; then cat "$case_dir/state-append.jsonl" >> AgentReferences/state.jsonl; fi
