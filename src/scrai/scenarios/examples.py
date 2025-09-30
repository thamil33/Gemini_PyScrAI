from __future__ import annotations

from datetime import datetime, timezone

from ..models import Action, Actor, Event
from ..models.action import ActionPriority, ActionType
from ..models.actor import ActorType
from ..models.event import EventType
from .base import Scenario, ScenarioContext


class SimpleTownScenario(Scenario):
    """Minimal scenario that seeds a small community."""

    name = "simple_town"

    def seed(self, context: ScenarioContext) -> None:
        mayor = Actor(
            id="actor-mayor",
            name="Mayor Alex",
            type=ActorType.NPC,
            attributes={"traits": {"leadership": "high", "openness": "moderate"}},
            location={"name": "Town Hall"},
            metadata={"role": "mayor"},
        )
        doctor = Actor(
            id="actor-doctor",
            name="Dr. Rivera",
            type=ActorType.NPC,
            attributes={"traits": {"empathy": "high", "innovation": "moderate"}},
            location={"name": "Clinic"},
            metadata={"role": "doctor"},
        )
        caretaker = Actor(
            id="actor-caretaker",
            name="Sam Lee",
            type=ActorType.NPC,
            attributes={"traits": {"patience": "high", "organization": "high"}},
            location={"name": "Community Center"},
            metadata={"role": "operations"},
        )

        morning_briefing = Event(
            id="event-briefing",
            title="Morning Briefing",
            description="Daily meeting to sync on community needs and incidents.",
            type=EventType.SYSTEM,
            scheduled_for=datetime.now(tz=timezone.utc),
            affected_actors=[mayor.id, doctor.id, caretaker.id],
            metadata={"location": "Town Hall"},
        )

        kickoff_action = Action(
            id="action-briefing-start",
            actor_id=mayor.id,
            type=ActionType.COMMUNICATION,
            intent="Open the morning briefing with an overview of priorities",
            description="Kick off the briefing with agenda overview.",
            parameters={"agenda": ["health status", "resource requests", "community updates"]},
            priority=ActionPriority.NORMAL,
            metadata={"related_event": morning_briefing.id},
        )

        context.extend(
            actors=[mayor, doctor, caretaker],
            events=[morning_briefing],
            actions=[kickoff_action],
        )


__all__ = ["SimpleTownScenario"]
