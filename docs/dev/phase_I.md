# Development Plan for ScrAI - Phase 1: Core Backend & Data Layer
Based on the blueprint and your current setup, here's a comprehensive plan to build the minimal viable engine for ScrAI. You've already completed the initial setup (GitHub repo, version control, Python 3.13.3 virtual environment), so we can jump into the core development work.

## Current Project Status
✅ **Completed:**

- GitHub repository setup and version control
- Python 3.13.3 virtual environment (.venv)
- Basic project structure with `docs/` folder

## Phase 1 Development Plan
The plan focuses on building a solid foundation with the core backend systems before moving to the web UI. This follows the blueprint's recommendation to get an MVP operational first.

### Key Architecture Decisions

- **Data Persistence**: Firestore (as recommended in the blueprint for flexibility and scalability)
- **LLM Integration**: Start with OpenAI/OpenRouter for simplicity
- **Development Approach**: Test-driven development with comprehensive error handling

### Next Steps Summary

1. **Project Structure** - Set up proper Python package structure with `src/`, `tests/`, `config/`
2. **Dependencies** - Install essential packages for Firestore, LLM APIs, and development tools
3. **Core Models** - Implement the fundamental data structures (`Actor`, `Event`, `Action`, `SimulationState`)
4. **Data Layer** - Build Firestore integration with CRUD operations
5. **LLM Bridge** - Create abstract interface with concrete OpenAI provider
6. **Phase Engine** - Implement the core simulation logic and state management
7. **Scenario System** - Build basic scenario module framework
8. **Zeus Mode CLI** - Create debugging and manual control interface
9. **Configuration** - Set up environment-specific settings and credentials
10. **Testing** - Write comprehensive tests for all components

This plan will give you a fully functional backend that can run simulations, manage state, integrate with LLMs, and provide debugging capabilities. Once this foundation is solid, Phase 2 will add the web API and frontend interface.