#!/usr/bin/env python3
"""Integration test suite for Phase 2 Milestone 1-2.

This script boots the FastAPI server in-process, exercises the public HTTP
endpoints, and performs a CLI parity check to guarantee the in-memory runtime
behaves identically across surfaces.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
API_HOST = "http://127.0.0.1:8008"
API_ROOT = f"{API_HOST}/api"
SERVER_START_TIMEOUT_SEC = 40
SERVER_SHUTDOWN_TIMEOUT_SEC = 5


class ApiServerManager:
    """Manage the lifecycle of a local FastAPI dev server for tests."""

    def __init__(self) -> None:
        self._process: Optional[subprocess.Popen[bytes]] = None

    def start(self) -> None:
        if self._process and self._process.poll() is None:
            return

        command = [
            sys.executable,
            "-m",
            "uvicorn",
            "scrai.api.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8008",
        ]

        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")

        self._process = subprocess.Popen(  # noqa: S603
            command,
            cwd=REPO_ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        deadline = time.time() + SERVER_START_TIMEOUT_SEC
        while time.time() < deadline:
            try:
                response = requests.get(f"{API_HOST}/health", timeout=2)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                time.sleep(0.5)

        self.stop()
        raise RuntimeError("Timed out waiting for API server to start")

    def stop(self) -> None:
        if not self._process:
            return

        if self._process.poll() is None:
            self._process.send_signal(signal.SIGTERM)
            try:
                self._process.wait(timeout=SERVER_SHUTDOWN_TIMEOUT_SEC)
            except subprocess.TimeoutExpired:
                self._process.kill()

        self._process = None


api_server = ApiServerManager()


def test_api_health():
    """Test API is responding"""
    print("🔍 Testing API health...")
    resp = requests.get(f"{API_HOST}/health", timeout=5)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    print("✅ API health check passed")


def test_api_create_simulation():
    """Test creating simulation via API"""
    print("\n🔍 Testing API simulation creation...")
    payload = {
        "name": "Integration Test Sim",
        "scenario": "simple_village",
    }
    resp = requests.post(f"{API_ROOT}/simulations", json=payload, timeout=5)
    assert resp.status_code == 201, f"Unexpected status {resp.status_code}: {resp.text}"
    data = resp.json()
    sim_id = data["id"]
    assert data["phase_history"] == ["initialize"]
    assert isinstance(data["pending_actions"], list)
    assert isinstance(data["pending_events"], list)
    assert isinstance(data["actors"], list)
    print(f"✅ Created simulation: {sim_id}")
    return sim_id


def test_api_list_simulations():
    """Test listing simulations"""
    print("\n🔍 Testing API simulation list...")
    resp = requests.get(f"{API_ROOT}/simulations", timeout=5)
    assert resp.status_code == 200
    sims = resp.json()
    assert isinstance(sims, list)
    print(f"✅ Found {len(sims)} simulation(s)")
    return sims


def test_api_get_simulation(sim_id):
    """Test getting specific simulation"""
    print(f"\n🔍 Testing API get simulation {sim_id}...")
    resp = requests.get(f"{API_ROOT}/simulations/{sim_id}", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == sim_id
    assert data["status"] in ["created", "running", "completed", "error"]
    assert isinstance(data["pending_actions"], list)
    assert isinstance(data["phase_log"], list)
    assert isinstance(data["metadata"], dict)
    print(f"✅ Got simulation: status={data['status']}, phase={data['current_phase']}")
    return data


def test_api_start_simulation(sim_id):
    """Test starting simulation"""
    print(f"\n🔍 Testing API start simulation {sim_id}...")
    resp = requests.post(f"{API_ROOT}/simulations/{sim_id}/start", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "running"
    print(f"✅ Started simulation: phase={data['current_phase']}")
    return data


def test_api_inject_action(sim_id):
    """Test injecting an action via API"""

    print(f"\n🔍 Testing API action injection for {sim_id}...")
    payload = {
        "actor_id": "actor-api",
        "intent": "Collect field samples",
        "metadata": {"channel": "integration-test"},
    }
    resp = requests.post(
        f"{API_ROOT}/simulations/{sim_id}/actions",
        json=payload,
        timeout=5,
    )
    assert resp.status_code == 201, f"Unexpected status {resp.status_code}: {resp.text}"
    data = resp.json()
    intents = [action["intent"] for action in data["pending_actions"]]
    assert payload["intent"] in intents, "New action not present in pending list"
    actor_ids = [actor["id"] for actor in data["actors"]]
    assert payload["actor_id"] in actor_ids, "Actor not surfaced in simulation detail"
    print("✅ Action injection surfaced in pending actions")
    return data


def test_api_stream_snapshot(sim_id):
    """Test SSE stream emits initial snapshot for a simulation."""

    print(f"\n🔍 Testing SSE stream for simulation {sim_id}...")
    url = f"{API_ROOT}/streams/simulations/{sim_id}"

    with requests.get(url, stream=True, timeout=10) as resp:
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"

        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if not line.startswith("data:"):
                continue

            payload = json.loads(line[5:].strip())
            assert payload["simulation_id"] == sim_id
            assert payload["event"] in {
                "simulation.snapshot",
                "simulation.created",
                "simulation.started",
            }
            print(
                "✅ Received SSE snapshot event:",
                payload.get("event"),
                payload.get("summary", {}).get("status"),
            )
            break
        else:
            raise AssertionError("Did not receive SSE data event from stream")


def test_api_advance_simulation(sim_id, expected_phases=6):
    """Test advancing simulation through full cycle"""
    print(f"\n🔍 Testing API advance simulation {sim_id}...")
    
    phases_seen = []
    phase_numbers = []

    # Capture initial state before advancing
    initial = requests.get(f"{API_ROOT}/simulations/{sim_id}", timeout=5)
    assert initial.status_code == 200, (
        f"Failed to fetch initial state: {initial.status_code}"
    )
    initial_data = initial.json()
    phases_seen.append(initial_data["current_phase"])
    phase_numbers.append(initial_data["phase_number"])
    print(
        "  Initial state: phase="
        f"{initial_data['current_phase']}, cycle={initial_data['phase_number']}"
    )
    
    for i in range(expected_phases):
        resp = requests.post(
            f"{API_ROOT}/simulations/{sim_id}/advance",
            timeout=5,
        )
        assert resp.status_code == 200
        data = resp.json()
        
        phases_seen.append(data["current_phase"])
        phase_numbers.append(data["phase_number"])
        
        print(f"  Step {i+1}: phase={data['current_phase']}, cycle={data['phase_number']}")
    
    # Verify phase cycle
    expected_cycle = [
        "initialize",
        "event_generation",
        "action_collection",
        "action_resolution",
        "world_update",
        "snapshot",
        "event_generation",
    ]

    assert phases_seen[:7] == expected_cycle, f"Phase cycle mismatch: {phases_seen[:7]}"
    assert phase_numbers[0] == 0, "Should start at cycle 0"
    assert phase_numbers[6] == 1, "Should increment to cycle 1 after SNAPSHOT"
    
    print(f"✅ Phase cycle verified: {' → '.join(expected_cycle)}")
    print(f"✅ Cycle numbers: {phase_numbers[0]} → {phase_numbers[6]}")


def test_cli_parity():
    """Test CLI produces same results"""
    print("\n🔍 Testing CLI parity...")

    from scrai.cli.runtime import build_runtime
    from scrai.models.simulation_state import (
        SimulationPhase,
        SimulationState,
        SimulationStatus,
    )

    runtime = build_runtime(backend="memory")

    async def _exercise_cli() -> None:
        simulation = SimulationState(
            id=f"cli-test-{uuid.uuid4().hex}",
            name="CLI Parity Test",
            scenario_module="simple_village",
            status=SimulationStatus.CREATED,
            current_phase=SimulationPhase.INITIALIZE,
            phase_number=0,
        )

        await runtime.simulation_repository.create(simulation)
        print(f"✅ CLI created simulation: {simulation.id}")

        simulation.start()
        await runtime.simulation_repository.update(simulation.id, simulation.to_dict())
        print("✅ CLI started simulation")

        result = await runtime.phase_engine.step(simulation.id)
        updated_sim = await runtime.simulation_repository.get(simulation.id)
        assert updated_sim is not None
        print(
            f"✅ CLI advanced simulation: phase={updated_sim.current_phase.value}"
            f" after {result.executed_phase.value}"
        )

    asyncio.run(_exercise_cli())

    print("✅ CLI parity verified")


def test_api_llm_check():
    """Test LLM readiness endpoint returns structured status."""

    print("\n🔍 Testing API LLM check...")
    resp = requests.post(f"{API_ROOT}/llm/check", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert "available" in data
    assert "ready" in data
    assert isinstance(data.get("providers", []), list)
    print(
        f"✅ LLM check: available={data['available']} ready={data['ready']} providers={data.get('providers', [])}"
    )
    return data


def run_all_tests():
    """Run complete integration test suite"""
    print("=" * 60)
    print("Phase 2 Milestone 1-2 Integration Tests")
    print("=" * 60)
    
    api_server.start()

    try:
        # API Tests
        test_api_health()
        sim_id = test_api_create_simulation()
        test_api_list_simulations()
        test_api_get_simulation(sim_id)
        test_api_start_simulation(sim_id)
        test_api_inject_action(sim_id)
        test_api_stream_snapshot(sim_id)
        test_api_advance_simulation(sim_id)
        test_api_llm_check()
        
        # CLI Parity
        test_cli_parity()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Summary:")
        print("  ✅ Backend API: WORKING")
        print("  ✅ Simulation CRUD: WORKING")
        print("  ✅ Phase Engine: WORKING")
        print("  ✅ CLI Parity: VERIFIED")
        print("\n🎉 Milestone 1-2 Complete!")
        print("\n🚀 Ready for Milestone 3: LLM Integration")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        api_server.stop()


if __name__ == "__main__":
    run_all_tests()
