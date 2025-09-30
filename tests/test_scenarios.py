from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from scrai.models import SimulationState
from scrai.models.simulation_state import SimulationPhase, SimulationStatus
from scrai.scenarios import ScenarioContext
from scrai.scenarios.examples import SimpleTownScenario


def test_simple_town_scenario_seed_populates_context() -> None:
    state = SimulationState(
        id="sim-test",
        name="Scenario Test",
        description="Testing simple town scenario seeding.",
        status=SimulationStatus.CREATED,
        current_phase=SimulationPhase.INITIALIZE,
        phase_number=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    context = ScenarioContext(state=state)
    scenario = SimpleTownScenario()

    scenario.seed(context)

    assert len(context.actors) == 3
    assert {actor.id for actor in context.actors} == {
        "actor-mayor",
        "actor-doctor",
        "actor-caretaker",
    }
    assert len(context.events) == 1
    assert context.events[0].id == "event-briefing"
    assert len(context.actions) == 1
    assert context.actions[0].metadata["related_event"] == "event-briefing"
