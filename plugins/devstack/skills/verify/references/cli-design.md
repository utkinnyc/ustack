# A control CLI agents can use

Agents run these commands hundreds of times. Every property below saves a retry.

| Property | Example |
|---|---|
| **JSON out**, one object per command. Extending a CLI people already use: add `--json` and keep its normal output unchanged | `{"ok": true, "screenshot": "/tmp/x.png"}` |
| **Errors say what to do** | `{"ok": false, "error": "server not running", "fix": "run: control up"}` |
| **Exit codes:** 0 ok, 1 check failed, 2 usage or environment error | |
| **`doctor` first:** checks every tool and service, lists what's missing and how to fix it | |
| **Subcommands** grouped by area, so `--help` stays short at each level | `control ios launch`, `control web click` |
| **Full `--help`** with one example per command | |
| **`--dry-run`** on anything that deletes, resets or sends | `control reset --dry-run` prints what it would wipe |
| **Refuses production:** checks the target host or DB path and stops unless `--allow-prod` | |
| **Idempotent** where possible: `up` when already up says so and exits 0 | |
| **Waits for itself:** commands return when the app has settled, with a timeout | `control web click … ` waits for network idle |
| **State in one git-ignored file** (PIDs, ports, device IDs), so commands compose across calls | `.verify-state.json` |

Composable, small commands beat one big `test-everything`. Tests for the CLI itself go wherever the codebase keeps its tests.
