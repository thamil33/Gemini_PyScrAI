# Zeus CLI Guide

## Overview

The Zeus CLI is the operator-facing entrypoint for running and inspecting ScrAI simulations from the terminal. It packages the core simulation runtime, data repositories, and phase engine behind a single command (`scrai`) so that you can:

- bootstrap fresh simulations or resume existing ones
- advance or cycle simulation phases (Initialize → Event Generation → Action Collection → Action Resolution → World Update → Snapshot)
- inject player or NPC actions on the fly
- review world state, actor rosters, pending events/actions, and phase logs for debugging ("Zeus mode")

Under the hood, the CLI builds a `RuntimeContext` using either the in-memory JSON store (for local development) or Firestore (for shared backends) and persists simulation state via the configured repositories.

## Prerequisites

- **Python** ≥ 3.11 (3.13 virtualenv supported via `.venv` in repo).
- **pip** ≥ 23 for editable/install extras.
- **Firestore (optional):** Google Cloud project + service-account JSON if you intend to use the Firestore backend.
- **git** (if you are developing against the repository).
- (Recommended) `make` or PowerShell for scripting, though all commands are shown explicitly.

## Installation & Environment Setup

1. **Clone the repository (or pull latest):**
	```bash
	git clone https://github.com/thamil33/Gemini_PyScrAI.git
	cd Gemini_PyScrAI
	```

2. **Create & activate a virtual environment:**
	```bash
	python -m venv .venv
	source .venv/Scripts/activate
	# On macOS/Linux use: source .venv/bin/activate
	```

3. **Install the package (editable) and optional dev tooling:**
	```bash
	pip install -e .[dev]
	```
	This exposes the Zeus CLI as the `scrai` console script.

4. **(Optional) Copy env templates:**
	```bash
	cp .env.example .env
	```
	Update values as needed (see Configuration below).

## Configuration

The CLI merges configuration from `config/settings.toml`, any overrides you supply, and environment variables.

### Defaults

- `config/settings.toml` ships with sensible defaults for the memory backend, the `simple_town` scenario module, and LLM provider placeholders.
- `.env.example` lists the environment variables the runtime understands. Duplicate it to `.env` (auto-loaded via `python-dotenv` when the CLI starts).

### Environment Variable Overrides

Key overrides consumed by the runtime:

| Variable | Purpose | Example |
| --- | --- | --- |
| `SCRAI_BACKEND` | Default backend (`memory` or `firestore`) | `SCRAI_BACKEND=firestore`
| `SCRAI_STATE_PATH` | Path to JSON state file for memory backend | `SCRAI_STATE_PATH=C:/scrai/state.json`
| `SCRAI_FIRESTORE_PROJECT_ID` | Google Cloud project ID | `SCRAI_FIRESTORE_PROJECT_ID=my-project`
| `SCRAI_FIRESTORE_CREDENTIALS` | Path to service-account JSON | `SCRAI_FIRESTORE_CREDENTIALS=C:/keys/service.json`
| `SCRAI_SIMULATION_SCENARIO` | Override default scenario module | `SCRAI_SIMULATION_SCENARIO=custom_module`

Any environment variable prefixed with `SCRAI_` is automatically mapped to CLI options (thanks to `auto_envvar_prefix="SCRAI"`). For example, setting `SCRAI_BACKEND=firestore` removes the need to pass `--backend firestore` on every invocation.

### Firestore Backend Notes

If you switch to Firestore:

- Provide `--project-id` and `--credentials` (or matching env vars) so `FirestoreClient` can authenticate.
- Ensure the service-account has read/write access to the target Firestore project.
- Collections used: `simulations`, `actors`, `events`, and `actions`.

For local development, the memory backend plus a dedicated state file is the fastest path.

## Global Options & Environment Variables

Every command begins with the base invocation:

```bash
scrai [GLOBAL OPTIONS] <group> <command> [ARGS]
```

Global options (also available via env vars):

| Option | Description | Memory Default |
| --- | --- | --- |
| `--backend {memory,firestore}` | Select persistence layer | `memory` |
| `--state-path PATH` | JSON state file for memory backend | `~/.scrai/state.json` |
| `--project-id TEXT` | Firestore project ID | _None_ |
| `--credentials PATH` | Path to Firestore credentials JSON | _None_ |
| `--help` | Show usage | – |
| `--version` | Show CLI version | – |

Example environment-based invocation (no global flags needed):

```bash
export SCRAI_BACKEND=memory
export SCRAI_STATE_PATH="$PWD/state.json"
scrai simulation list
```

## Core Simulation Commands

| Command | Purpose | Example |
| --- | --- | --- |
| `simulation create` | Create a new simulation document with seed config | `scrai simulation create --name "Zeus MVP" --scenario simple_town` |
| `simulation list` | List IDs and metadata for all simulations | `scrai simulation list` |
| `simulation show <id>` | Print detailed snapshot; add `--details` for actors/events/actions | `scrai simulation show sim-1234 --details` |
| `simulation start <id>` | Kick off the initialize phase (for `created` or `paused` sims) | `scrai simulation start sim-1234` |
| `simulation advance <id> [--phase=...]` | Execute the next phase (or force a specific one) | `scrai simulation advance sim-1234` |
| `simulation cycle <id>` | Run a full turn (all phases in order) | `scrai simulation cycle sim-1234` |
| `simulation log <id>` | Dump `phase_log` entries captured during execution | `scrai simulation log sim-1234` |

**Tips:**

- Use `simulation show --details` frequently during Zeus-mode investigations to capture the state of every repository.
- When forcing phases via `--phase`, pass the raw enum value (e.g., `event_generation`). Invalid values are rejected with a helpful message listing all valid phases.

## Action Management Commands

| Command | Purpose | Example |
| --- | --- | --- |
| `action inject <sim-id>` | Inject a new action. Auto-creates actors if requested. | `scrai action inject sim-1234 --actor-id actor-cli --intent "Inspect facilities" --auto-create-actor` |
| `action list <sim-id>` | List all recorded actions (across statuses). | `scrai action list sim-1234` |

`action inject` accepts several useful flags:

- `--description`: Custom human-readable description (defaults to the intent string).
- `--action-type`: One of the `ActionType` enum values (`movement`, `communication`, `custom`, etc.).
- `--priority`: One of `ActionPriority` (`low`, `normal`, `high`, `urgent`).
- `--metadata key=value`: Repeated flag for embedding arbitrary metadata (stored on the action record). Use `--metadata related_event=event-briefing` for linking.
- `--auto-create-actor`: Create a lightweight `Actor` stub if the supplied `actor_id` does not exist yet.

## Working With Logs & Diagnostics

- **Phase logs:** `simulation log <id>` prints the accumulated `phase_log` history (phase name, timestamp, and any notes returned by handlers). Useful for auditing automated runs.
- **State file inspection (memory backend):** The JSON blob lives at `~/.scrai/state.json` by default. You can open it directly to inspect persisted repositories. Use `--state-path` to redirect to a scratch file for experiments.
- **Verbose output:** Most commands already print the executed phase, next phase, generated IDs, and handler notes. Pipe output to a file for longer debugging sessions (`scrai simulation cycle sim-1234 > cycle.log`).
- **LLM diagnostics:** If the configured LLM provider fails validation, the CLI will surface exceptions when the phase engine attempts to call it. Double-check API keys in `.env`.

## Smoke Screen Test

Run this quick sequence after installing to confirm the CLI, repositories, and phase engine are wired correctly. The flow uses the memory backend with an isolated state file.

```bash
# 1. Pick a scratch directory for the state file
export SCRAI_STATE_PATH="$PWD/zeus-state.json"
export SCRAI_BACKEND=memory

# 2. Create a fresh simulation (auto-id is printed)
scrai simulation create --name "Zeus Smoke Test" --scenario simple_town

# 3. Copy the printed simulation ID for reuse
export SIM_ID=<replace-with-id>

# 4. Start the simulation (runs Initialize phase)
scrai simulation start "$SIM_ID"

# 5. Inject a sample action (auto-create placeholder actor)
scrai action inject "$SIM_ID" --actor-id actor-smoke --intent "Run diagnostics" --auto-create-actor

# 6. Advance one more phase (Action Collection → Action Resolution)
scrai simulation advance "$SIM_ID"

# 7. Show full details to verify repositories updated
scrai simulation show "$SIM_ID" --details

# 8. Print phase log for audit trail (optional)
scrai simulation log "$SIM_ID"

# 9. Clean up the scratch state file when done
rm "$SCRAI_STATE_PATH"
```

Expected outcomes:

- `simulation create` prints `Created simulation sim-XXXXXXXX`.
- `simulation start` includes `Executed Phase: initialize` and `Next Phase: event_generation`.
- `action inject` prints the generated action ID and updates the simulation's pending actions.
- The subsequent `simulation advance` shows the phase progression notes.
- `simulation show --details` lists the injected actor/action.
- `simulation log` displays at least one entry for the initialize phase.

## Troubleshooting & Tips

- **Command not found:** Ensure the virtual environment is activated before running `scrai`; otherwise install globally with `pip install -e .`.
- **State file race conditions:** For collaborative testing on memory backend, use distinct `--state-path` values to avoid overwriting each other’s data.
- **Firestore auth failures:** Verify that the credentials JSON path is accessible, the file contains valid service-account credentials, and `GOOGLE_APPLICATION_CREDENTIALS` (if set) does not conflict.
- **Unknown phase errors:** Check the capitalization of `--phase` values; they must match the enum (`event_generation`, not `EventGeneration`).
- **Resetting repositories:** Deleting the memory state file (`state.json`) completely resets all repositories. On Firestore, delete the relevant documents/collections manually or via scripts.
- **Automating flows:** Because the CLI is Click-based, you can script scenarios via shell scripts or invoke commands programmatically using Click’s testing utilities (`CliRunner`) as demonstrated in `tests/test_cli.py`.
