# ScrAI Development Setup Guide

## Prerequisites

### Required Software
- **Python 3.11+** (3.13.3 recommended)
- **Git** for version control
- **VS Code** (recommended IDE)
- **Google Cloud SDK** (for Firestore)

### Required Accounts
- **Google Cloud Platform** account with billing enabled
- **OpenAI** or **OpenRouter** API account
- **GitHub** account for version control

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/thamil33/Gemini_PyScrAI.git
cd Gemini_PyScrAI
```

### 2. Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"
```

### 3. Google Cloud Setup

#### Install Google Cloud SDK
```bash
# Follow instructions at: https://cloud.google.com/sdk/docs/install
gcloud init
gcloud auth login
gcloud auth application-default login
```

#### Create Firestore Database
```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Create Firestore database
gcloud firestore databases create --location=us-central
```

#### Service Account (Optional)
```bash
# Create service account
gcloud iam service-accounts create scrai-dev \
    --display-name="ScrAI Development"

# Grant Firestore permissions
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:scrai-dev@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Create key file
gcloud iam service-accounts keys create config/firestore-key.json \
    --iam-account="scrai-dev@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com"
```

### 4. Environment Variables

Create `.env` file in project root:

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=config/firestore-key.json

# LLM API Configuration
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key

# Development Settings
DEBUG=True
LOG_LEVEL=DEBUG

# Simulation Defaults
DEFAULT_MAX_PHASES=100
AUTO_APPROVE_EVENTS=False
AUTO_APPROVE_ACTIONS=False
```

### 5. Development Tools Setup

#### Pre-commit Hooks
```bash
pre-commit install
```

#### VS Code Extensions
Recommended extensions:
- Python
- Pylance
- Black Formatter
- Flake8
- GitLens
- Firestore Rules

#### VS Code Settings
Add to `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Project Structure

```
Gemini_PyScrAI/
├── src/scrai/           # Main package
│   ├── models/          # Data models
│   ├── data/            # Repository layer
│   ├── llm/             # LLM integration
│   ├── engine/          # Phase engine
│   ├── scenarios/       # Scenario modules
│   └── cli/             # Command line interface
├── tests/               # Test suite
├── config/              # Configuration files
├── docs/                # Documentation
│   ├── dev/             # Developer docs
│   └── user/            # User guides
├── pyproject.toml       # Package configuration
├── .env                 # Environment variables
└── README.md            # Project overview
```

## Development Workflow

### 1. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scrai

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_actor_creation
```

### 2. Code Formatting

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### 3. Database Operations

#### Local Firestore Emulator
```bash
# Install emulator
gcloud components install cloud-firestore-emulator

# Start emulator
gcloud beta emulators firestore start --host-port=localhost:8080

# Set environment for emulator
export FIRESTORE_EMULATOR_HOST=localhost:8080
```

#### Database Management
```bash
# View Firestore data
gcloud firestore export gs://your-bucket/backup

# Import test data
gcloud firestore import gs://your-bucket/test-data

# Clear database (development only!)
# Use Firestore console or custom script
```

### 4. Running the CLI

```bash
# Install in development mode
pip install -e .

# Run CLI commands
scrai --help
# Create a simulation using the default memory backend
scrai --backend memory simulation create --name "Test Sim"
# Start/advance a simulation
scrai --backend memory simulation start sim-id
scrai --backend memory simulation advance sim-id
# Inject an action from the CLI
scrai --backend memory action inject sim-id --actor-id test-agent --intent "Inspect facilities" --auto-create-actor
```

## Testing Strategy

### Unit Tests
- **Models**: Test data validation and methods
- **Repositories**: Test CRUD operations with mocked Firestore
- **LLM Clients**: Test API integration with mocked responses
- **Phase Engine**: Test state transitions and logic

### Integration Tests
- **Data Layer**: Test with Firestore emulator
- **Full Scenarios**: End-to-end simulation runs
- **API Integration**: Test with real LLM APIs (rate-limited)

### Test Data
- Sample actors, events, actions in `tests/data/`
- Test scenarios in `tests/scenarios/`
- Mock LLM responses in `tests/mocks/`

## Debugging

### Logging Configuration
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Module-specific logging
logger = logging.getLogger('scrai.data')
logger.setLevel(logging.DEBUG)
```

### Common Debug Commands
```bash
# Check Firestore connection
python -c "from scrai.data import FirestoreClient; import asyncio; asyncio.run(FirestoreClient().initialize())"

# Test LLM API
python -c "from scrai.llm import OpenAIClient; import asyncio; asyncio.run(OpenAIClient().generate_text('Hello'))"

# Validate environment
python -c "import os; print(os.getenv('GOOGLE_CLOUD_PROJECT'))"
```

### Performance Profiling
```bash
# Profile code execution
python -m cProfile -o profile.stats your_script.py

# Analyze results
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

## Deployment

### Local Development
- Use Firestore emulator
- Mock LLM APIs for faster testing
- Local configuration files

### Development Environment
- Real Firestore database
- Development LLM API keys
- Separate project/database

### Production Environment
- Production Firestore database
- Production LLM API keys
- Monitoring and logging enabled
- Backup and disaster recovery

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure package is installed in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Firestore Connection Issues
```bash
# Check authentication
gcloud auth list
gcloud auth application-default print-access-token

# Verify project
gcloud config get-value project

# Test permissions
gcloud firestore collections list
```

#### LLM API Issues
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check rate limits
# Monitor API usage in respective dashboards
```

#### Environment Issues
```bash
# Verify virtual environment
which python
pip list

# Check environment variables
env | grep -E "(GOOGLE|OPENAI|OPENROUTER)"
```

### Getting Help

1. **Check logs**: Review application logs for error details
2. **Review docs**: Check API documentation and guides
3. **Search issues**: Look for similar problems in issue tracker
4. **Ask team**: Reach out on development chat/forum
5. **Create issue**: Document new problems for team

## Contributing

### Code Style
- Follow PEP 8 standards
- Use Black for formatting
- Add type hints to all functions
- Write docstrings for public APIs
- Keep functions focused and testable

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "Add your feature"

# Push and create pull request
git push origin feature/your-feature
```

### Pull Request Process
1. Write descriptive commit messages
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass
5. Request review from team members