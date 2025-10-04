from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ...models import Action, Actor, Event
from ...models.action import ActionPriority, ActionType
from ...models.actor import ActorType
from ...models.event import EventType
from ..base import Scenario, ScenarioContext


class SimpleTownScenario(Scenario):
    """A vibrant small town scenario showcasing diverse actors, locations, events, and interactions."""

    name = "simple_town"

    def seed(self, context: ScenarioContext) -> None:
        now = datetime.now(tz=timezone.utc)
        
        # === ACTORS ===
        # Town leadership
        mayor = Actor(
            id="actor-mayor",
            name="Mayor Alex Chen",
            type=ActorType.NPC,
            attributes={
                "traits": {
                    "leadership": "high",
                    "openness": "moderate",
                    "diplomacy": "high"
                },
                "skills": ["public_speaking", "policy_making", "conflict_resolution"]
            },
            location={"name": "Town Hall", "lat": 40.7128, "lng": -74.0060},
            metadata={"role": "mayor", "experience_years": 8},
        )
        
        # Healthcare
        doctor = Actor(
            id="actor-doctor",
            name="Dr. Sofia Rivera",
            type=ActorType.NPC,
            attributes={
                "traits": {
                    "empathy": "high",
                    "innovation": "moderate",
                    "analytical": "high"
                },
                "skills": ["diagnosis", "emergency_medicine", "patient_care"]
            },
            location={"name": "Community Clinic", "lat": 40.7135, "lng": -74.0050},
            metadata={"role": "doctor", "specialization": "general_practice"},
        )
        
        # Community services
        caretaker = Actor(
            id="actor-caretaker",
            name="Sam Lee",
            type=ActorType.NPC,
            attributes={
                "traits": {
                    "patience": "high",
                    "organization": "high",
                    "creativity": "moderate"
                },
                "skills": ["event_planning", "resource_management", "community_outreach"]
            },
            location={"name": "Community Center", "lat": 40.7140, "lng": -74.0070},
            metadata={"role": "operations_manager"},
        )
        
        # Education
        teacher = Actor(
            id="actor-teacher",
            name="Ms. Jordan Park",
            type=ActorType.NPC,
            attributes={
                "traits": {
                    "patience": "high",
                    "creativity": "high",
                    "enthusiasm": "high"
                },
                "skills": ["teaching", "mentoring", "curriculum_design"]
            },
            location={"name": "Town School", "lat": 40.7125, "lng": -74.0080},
            metadata={"role": "teacher", "subject": "science"},
        )
        
        # Local business
        shopkeeper = Actor(
            id="actor-shopkeeper",
            name="Marcus Thompson",
            type=ActorType.NPC,
            attributes={
                "traits": {
                    "entrepreneurship": "high",
                    "friendliness": "high",
                    "pragmatism": "moderate"
                },
                "skills": ["sales", "inventory_management", "customer_service"]
            },
            location={"name": "General Store", "lat": 40.7130, "lng": -74.0065},
            metadata={"role": "shopkeeper", "business": "general_goods"},
        )
        
        # Emergency services
        firefighter = Actor(
            id="actor-firefighter",
            name="Captain Jamie Rodriguez",
            type=ActorType.NPC,
            attributes={
                "traits": {
                    "courage": "high",
                    "teamwork": "high",
                    "quick_thinking": "high"
                },
                "skills": ["emergency_response", "leadership", "rescue_operations"]
            },
            location={"name": "Fire Station", "lat": 40.7138, "lng": -74.0055},
            metadata={"role": "fire_captain", "years_service": 12},
        )
        
        # Community resident (player character type)
        resident = Actor(
            id="actor-resident",
            name="Taylor Morgan",
            type=ActorType.PLAYER,
            attributes={
                "traits": {
                    "curiosity": "high",
                    "helpfulness": "moderate",
                    "adaptability": "high"
                },
                "skills": ["problem_solving", "communication"]
            },
            location={"name": "Main Street", "lat": 40.7132, "lng": -74.0062},
            metadata={"role": "resident", "new_to_town": True},
        )
        
        # === EVENTS ===
        # Daily governance
        morning_briefing = Event(
            id="event-briefing",
            title="Morning Town Briefing",
            description="Daily coordination meeting for town leadership to sync on priorities, incidents, and resource allocation.",
            type=EventType.SYSTEM,
            scheduled_for=now,
            affected_actors=[mayor.id, doctor.id, caretaker.id, firefighter.id],
            metadata={
                "location": "Town Hall",
                "recurring": "daily",
                "duration_minutes": 30
            },
        )
        
        # Community engagement
        farmers_market = Event(
            id="event-market",
            title="Weekly Farmers Market",
            description="Community market featuring local produce, crafts, and social gathering.",
            type=EventType.SOCIAL,
            scheduled_for=now + timedelta(hours=4),
            affected_actors=[shopkeeper.id, caretaker.id, resident.id],
            metadata={
                "location": "Town Square",
                "recurring": "weekly",
                "duration_hours": 3
            },
        )
        
        # Educational activity
        science_fair = Event(
            id="event-science-fair",
            title="School Science Fair",
            description="Annual science fair where students showcase their projects to the community.",
            type=EventType.SOCIAL,
            scheduled_for=now + timedelta(days=2),
            affected_actors=[teacher.id, mayor.id, resident.id],
            metadata={
                "location": "Town School",
                "participants_expected": 45,
                "judges_needed": 3
            },
        )
        
        # Emergency scenario
        power_outage = Event(
            id="event-outage",
            title="Partial Power Outage",
            description="Storm damage has caused power loss in the eastern district. Emergency services coordinating response.",
            type=EventType.ENVIRONMENTAL,
            scheduled_for=now + timedelta(hours=1),
            affected_actors=[firefighter.id, mayor.id, shopkeeper.id],
            metadata={
                "location": "Eastern District",
                "severity": "moderate",
                "estimated_duration_hours": 3
            },
        )
        
        # === ACTIONS ===
        # Briefing actions
        briefing_start = Action(
            id="action-briefing-start",
            actor_id=mayor.id,
            type=ActionType.COMMUNICATION,
            intent="Open the morning briefing with an overview of town priorities and agenda",
            description="Mayor welcomes attendees and outlines the discussion topics for today's coordination meeting.",
            parameters={
                "agenda": [
                    "health_status_report",
                    "resource_requests",
                    "community_events",
                    "emergency_preparedness"
                ],
                "attendees": [doctor.id, caretaker.id, firefighter.id]
            },
            priority=ActionPriority.NORMAL,
            metadata={"related_event": morning_briefing.id, "phase": "opening"},
        )
        
        health_report = Action(
            id="action-health-report",
            actor_id=doctor.id,
            type=ActionType.COMMUNICATION,
            intent="Provide health status update to town leadership",
            description="Dr. Rivera shares current health trends, vaccination rates, and clinic capacity.",
            parameters={
                "topics": ["seasonal_flu_cases", "vaccination_progress", "clinic_utilization"],
                "recommendations": ["increase_outreach", "prepare_winter_supplies"]
            },
            priority=ActionPriority.NORMAL,
            metadata={"related_event": morning_briefing.id, "phase": "reports"},
        )
        
        # Market preparation
        market_setup = Action(
            id="action-market-setup",
            actor_id=caretaker.id,
            type=ActionType.SOCIAL,
            intent="Coordinate setup logistics for the weekly farmers market",
            description="Sam organizes vendor assignments, ensures permits are in order, and arranges volunteer support.",
            parameters={
                "vendors": 12,
                "volunteers_needed": 4,
                "equipment": ["tables", "canopies", "signage"]
            },
            priority=ActionPriority.HIGH,
            metadata={"related_event": farmers_market.id, "deadline": "4_hours"},
        )
        
        # Educational engagement
        science_fair_judging = Action(
            id="action-science-judging",
            actor_id=teacher.id,
            type=ActionType.SOCIAL,
            intent="Recruit judges and finalize science fair logistics",
            description="Ms. Park contacts community leaders to serve as judges and prepares evaluation criteria.",
            parameters={
                "judges_needed": 3,
                "criteria": ["creativity", "scientific_method", "presentation"],
                "categories": ["biology", "physics", "engineering"]
            },
            priority=ActionPriority.NORMAL,
            metadata={"related_event": science_fair.id},
        )
        
        # Emergency preparation
        emergency_drill = Action(
            id="action-emergency-drill",
            actor_id=firefighter.id,
            type=ActionType.CUSTOM,
            intent="Review emergency protocols and prepare response equipment",
            description="Captain Rodriguez conducts equipment checks and reviews storm response procedures with the team.",
            parameters={
                "equipment_check": ["generators", "rescue_gear", "communication_devices"],
                "protocols": ["power_outage", "storm_response", "evacuation_routes"]
            },
            priority=ActionPriority.HIGH,
            metadata={"proactive": True, "related_event": power_outage.id},
        )
        
        # Community interaction
        welcome_resident = Action(
            id="action-welcome-resident",
            actor_id=shopkeeper.id,
            type=ActionType.COMMUNICATION,
            intent="Welcome the new resident and offer local insights",
            description="Marcus greets Taylor at the store and shares information about upcoming community events.",
            parameters={
                "topics": ["farmers_market", "science_fair", "local_services"],
                "offer": "community_guidebook"
            },
            priority=ActionPriority.LOW,
            metadata={"relationship_building": True},
        )
        
        explore_town = Action(
            id="action-explore-town",
            actor_id=resident.id,
            type=ActionType.MOVEMENT,
            intent="Explore the town and meet community members",
            description="Taylor walks through town to familiarize themselves with local landmarks and introduce themselves to neighbors.",
            parameters={
                "locations": ["Town Hall", "Community Center", "General Store", "Town School"],
                "goals": ["meet_neighbors", "learn_layout", "find_opportunities"]
            },
            priority=ActionPriority.NORMAL,
            metadata={"first_day": True},
        )

        context.extend(
            actors=[mayor, doctor, caretaker, teacher, shopkeeper, firefighter, resident],
            events=[morning_briefing, farmers_market, science_fair, power_outage],
            actions=[
                briefing_start,
                health_report,
                market_setup,
                science_fair_judging,
                emergency_drill,
                welcome_resident,
                explore_town,
            ],
        )


__all__ = ["SimpleTownScenario"]
