#!/usr/bin/env bash
# Loads the messy fixture into the workspace (see ../_fixtures/load.sh).
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$here/../_fixtures/load.sh" messy "$here"
