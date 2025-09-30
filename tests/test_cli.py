from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from scrai.cli.main import cli


def test_cli_simulation_lifecycle(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    runner = CliRunner()

    create_result = runner.invoke(
        cli,
        [
            "--backend",
            "memory",
            "--state-path",
            str(state_path),
            "simulation",
            "create",
            "--name",
            "Test Simulation",
        ],
    )
    assert create_result.exit_code == 0
    assert "Created simulation" in create_result.output
    simulation_id = create_result.output.strip().split()[-1]

    start_result = runner.invoke(
        cli,
        [
            "--backend",
            "memory",
            "--state-path",
            str(state_path),
            "simulation",
            "start",
            simulation_id,
        ],
    )
    assert start_result.exit_code == 0
    assert "Executed Phase" in start_result.output

    action_result = runner.invoke(
        cli,
        [
            "--backend",
            "memory",
            "--state-path",
            str(state_path),
            "action",
            "inject",
            simulation_id,
            "--actor-id",
            "actor-cli",
            "--intent",
            "Inspect facilities",
            "--auto-create-actor",
        ],
    )
    assert action_result.exit_code == 0
    assert "Injected action" in action_result.output

    show_result = runner.invoke(
        cli,
        [
            "--backend",
            "memory",
            "--state-path",
            str(state_path),
            "simulation",
            "show",
            simulation_id,
            "--details",
        ],
    )
    assert show_result.exit_code == 0
    assert "actor-cli" in show_result.output
    assert "Inspect facilities" in show_result.output

    list_result = runner.invoke(
        cli,
        [
            "--backend",
            "memory",
            "--state-path",
            str(state_path),
            "simulation",
            "list",
        ],
    )
    assert list_result.exit_code == 0
    assert simulation_id in list_result.output
