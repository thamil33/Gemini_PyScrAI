"""LLM prompt templates and utilities for phase handlers."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ..models import Action, Actor, Event, SimulationState


def build_simulation_context(
    simulation: SimulationState,
    actors: List[Actor],
    events: List[Event],
    actions: List[Action],
) -> str:
    """Build a comprehensive context summary for LLM prompts."""
    
    context_parts = [
        f"# Simulation: {simulation.name}",
        f"Scenario: {simulation.scenario_module}",
        f"Current Cycle: {simulation.phase_number}",
        f"Status: {simulation.status.value}",
        "",
        "## Active Actors",
    ]
    
    for actor in actors:
        location_str = actor.location.get("name", "Unknown") if actor.location else "Unknown"
        traits = actor.attributes.get("traits", {})
        skills = actor.attributes.get("skills", [])
        
        context_parts.append(f"- **{actor.name}** (ID: {actor.id})")
        context_parts.append(f"  - Type: {actor.type.value}")
        context_parts.append(f"  - Location: {location_str}")
        if traits:
            context_parts.append(f"  - Traits: {', '.join(f'{k}: {v}' for k, v in traits.items())}")
        if skills:
            context_parts.append(f"  - Skills: {', '.join(skills)}")
        if actor.metadata.get("role"):
            context_parts.append(f"  - Role: {actor.metadata['role']}")
        context_parts.append("")
    
    if events:
        context_parts.append("## Recent Events")
        for event in events:
            context_parts.append(f"- **{event.title}** ({event.type.value})")
            context_parts.append(f"  - {event.description}")
            context_parts.append(f"  - Status: {event.status.value}")
            context_parts.append("")
    
    if actions:
        context_parts.append("## Pending Actions")
        for action in actions:
            actor = next((a for a in actors if a.id == action.actor_id), None)
            actor_name = actor.name if actor else action.actor_id
            context_parts.append(f"- **{actor_name}**: {action.intent}")
            context_parts.append(f"  - Type: {action.type.value}, Priority: {action.priority.value}")
            context_parts.append(f"  - Status: {action.status.value}")
            context_parts.append("")
    
    return "\n".join(context_parts)


EVENT_GENERATION_PROMPT = """You are a creative simulation engine analyzing the current state of a community simulation.

{context}

Your task is to generate new events that naturally emerge from the current simulation state. Consider:
- What would realistically happen next given the actors' locations, roles, and relationships?
- How might pending actions lead to new situations or complications?
- What environmental, social, or system events would add interesting dynamics?
- What opportunities for actor interaction or development exist?

Generate 1-3 NEW events that feel natural and compelling. Each event should:
- Have a clear cause (either emergent from the situation or triggered by an action/actor)
- Affect specific actors
- Include concrete details about what happens
- Fit the scenario's tone and setting

Respond with ONLY a valid JSON array of events in this exact format:
[
  {{
    "title": "Brief event title",
    "description": "Detailed description of what happens",
    "type": "social|environmental|economic|political|system",
    "affected_actors": ["actor-id-1", "actor-id-2"],
    "location": {{"name": "Location Name"}},
    "scope": "local|regional|global",
    "source": "Description of what caused this event",
    "trigger_action_id": "action-id or null",
    "parameters": {{}},
    "metadata": {{}}
  }}
]

Generate events now:"""


ACTION_RESOLUTION_PROMPT = """You are a simulation engine resolving actions taken by actors in a community.

{context}

Your task is to determine the outcome of each pending action. For each action:
- Consider the actor's skills, traits, and current situation
- Evaluate what would realistically happen
- Determine success/failure and consequences
- Identify any side effects or emergent events

For each action, provide:
1. The outcome (success, partial success, failure)
2. A narrative description of what happened
3. Any effects on the actor (attribute changes, location changes, etc.)
4. Any new events that should be generated as a result

Respond with ONLY a valid JSON array in this exact format:
[
  {{
    "action_id": "action-id",
    "status": "completed|failed",
    "outcome_description": "What happened when the actor attempted this",
    "actor_effects": {{
      "attribute_changes": {{"attribute_name": "new_value"}},
      "location_change": {{"name": "New Location"}} or null,
      "metadata_updates": {{}}
    }},
    "generated_events": [
      {{
        "title": "Event title",
        "description": "What happens as a result",
        "type": "social|environmental|economic|political",
        "affected_actors": ["actor-id"],
        "source": "Result of action: action-id",
        "trigger_action_id": "action-id"
      }}
    ]
  }}
]

Resolve actions now:"""


WORLD_UPDATE_PROMPT = """You are a simulation engine applying event effects to the world state.

{context}

Your task is to determine how recent events affect actors and the environment. For each event:
- Identify which actors are affected and how
- Determine attribute changes (reputation, relationships, resources, etc.)
- Update locations if actors moved
- Record any lasting changes to the world state

Respond with ONLY a valid JSON object in this exact format:
{{
  "actor_updates": [
    {{
      "actor_id": "actor-id",
      "attribute_changes": {{"relationship_with_X": "+10", "stress": "high"}},
      "location_change": {{"name": "New Location"}} or null,
      "metadata_updates": {{"recent_events": ["event-id"]}}
    }}
  ],
  "world_state_changes": {{
    "environment": {{}},
    "global_events": [],
    "notes": ["Description of world changes"]
  }}
}}

Apply event effects now:"""


def parse_llm_json_response(content: str, expected_type: str = "array") -> Any:
    """Parse LLM JSON response with error handling."""
    
    # Try to extract JSON from markdown code blocks if present
    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        if end > start:
            content = content[start:end].strip()
    elif "```" in content:
        start = content.find("```") + 3
        end = content.find("```", start)
        if end > start:
            content = content[start:end].strip()
    
    # Clean up common issues
    content = content.strip()
    
    try:
        parsed = json.loads(content)
        
        # Validate expected type
        if expected_type == "array" and not isinstance(parsed, list):
            return []
        elif expected_type == "object" and not isinstance(parsed, dict):
            return {}
        
        return parsed
    except json.JSONDecodeError as e:
        # Log the error and return empty structure
        print(f"Failed to parse LLM JSON response: {e}")
        print(f"Content: {content[:500]}")
        return [] if expected_type == "array" else {}


def safe_get_str(data: Dict[str, Any], key: str, default: str = "") -> str:
    """Safely get string value from dict."""
    value = data.get(key, default)
    return str(value) if value is not None else default


def safe_get_list(data: Dict[str, Any], key: str) -> List[Any]:
    """Safely get list value from dict."""
    value = data.get(key, [])
    return value if isinstance(value, list) else []


def safe_get_dict(data: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Safely get dict value from dict."""
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}
