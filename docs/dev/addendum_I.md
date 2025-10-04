We propose the addition of a flexible LLM configuration feature to the ScrAI development plan. This feature will enable the assignment of multiple LLM client instances—such as distinct OpenRouter clients for different LLM models or local LMStudio instances—to various components of the simulation. 

Key capabilities include:
- A global LLM client configuration applicable by default across the simulation.
- Optional per-actor LLM client assignments, allowing specific actors to interact with distinct models.
- The ability to assign different LLM clients to separate simulation subsystems, such as Actions, Events, or other scenario processes.

Benefits of this feature:
1. Load distribution across multiple LLM models, reducing latency and API bottlenecks.
2. Experimentation with different LLM configurations to optimize performance, narrative generation, and decision-making.
3. Fine-grained control over which models are used for specific actors or simulation components, supporting research flexibility and modular testing.