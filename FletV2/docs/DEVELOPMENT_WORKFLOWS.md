# FletV2 Development Workflows

Essential workflows for developing, testing, and deploying the FletV2 project.

## 🚀 Quick Development Workflow

### Daily Development

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# 2. Develop and test
cd FletV2
python main.py  # Quick test
python -m pytest tests/unit/  # Run tests

# 3. Commit changes
git add .
git commit -m "feat: Add new feature"

# 4. Push and create PR
git push origin feature/my-feature
```

### Commit Message Convention
```bash
feat(dashboard): Add new metric display
fix(clients): Resolve connection timeout
docs(api): Update ServerBridge docs
test(views): Add dashboard integration tests
refactor(theme): Simplify gradient system
```

## 🧪 Testing Workflow

### Test Structure
```
tests/
├── unit/          # Unit tests for individual components
├── integration/   # Integration tests for workflows
└── performance/   # Performance and load tests
```

### Running Tests
```bash
# All tests
pytest tests/

# Specific test type
pytest tests/unit/
pytest tests/integration/

# With coverage
pytest tests/ --cov=FletV2 --cov-report=html

# Performance tests only
pytest tests/performance/ --benchmark-only
```

### Writing Tests
```python
# tests/unit/test_dashboard.py
import pytest
from unittest.mock import Mock
from FletV2.views.dashboard import create_dashboard_view

class TestDashboardView:
    def test_view_creation(self):
        """Test that view returns correct types."""
        page = Mock()
        view, dispose, setup = create_dashboard_view(Mock(), page, Mock())

        assert callable(dispose)
        assert callable(setup)
```

## 🚢 Deployment Workflow

### Build Process
```bash
# Complete build
python scripts/build_fletv2.py

# Quick build for development
flet build windows --project-name "CyberBackup GUI"
```

### Release Process
```bash
# Version bump and release
python scripts/version_manager.py patch  # or minor/major
git push --tags
```

### Deployment Commands
```bash
# Development deployment
python scripts/deploy_dev.py --verbose

# Production deployment
python scripts/deploy_prod.py --version 1.2.3 --validate

# Database backup before deployment
python scripts/backup_database.py
```

## 🔧 Development Environment

### Setup
```bash
# Clone and setup
git clone <repo>
cd Client_Server_Encrypted_Backup_Framework/FletV2

# Virtual environment
python -m venv ../../flet_venv
../../flet_venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### Debug Configuration
```bash
# Development environment
export FLET_DEBUG=1
export FLET_DASHBOARD_DEBUG=1
export PYTHONIOENCODING=utf-8

# Run application
python main.py
```

### Environment Variables
```bash
# Core settings
FLET_DEBUG=1                    # Enable debug mode
FLET_DASHBOARD_DEBUG=1         # Dashboard debug info
CYBERBACKUP_SERVER_PORT=1256   # Server port
CYBERBACKUP_API_PORT=9090      # API port
DATABASE_PATH=./defensive.db   # Database location
LOG_LEVEL=DEBUG                # Logging level
```

## 📊 Code Quality

### Pre-commit Checks
```bash
# Format code
black FletV2/
isort FletV2/

# Lint code
flake8 FletV2/

# Type checking
mypy FletV2/
```

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - run: pip install -r FletV2/requirements.txt
    - run: pytest tests/unit/ --cov=FletV2
```

## 🛠️ Common Tasks

### Adding New View
```python
# views/my_feature.py
def create_my_feature_view(server_bridge, page, state_manager):
    content = ft.Column([
        ft.Text("My Feature", size=24, weight=ft.FontWeight.BOLD),
        # Add UI components
    ])

    async def setup():
        # Load data
        pass

    def dispose():
        # Cleanup
        pass

    return content, dispose, setup
```

### ServerBridge Integration
```python
# utils/server_bridge.py
def get_my_feature_data(self) -> dict:
    """Get feature data."""
    if not self.real_server:
        return {'success': False, 'error': 'Server not connected'}

    try:
        data = self.real_server.get_my_feature_data()
        return {'success': True, 'data': data}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### Theme Integration
```python
from FletV2.theme import create_modern_card, themed_button

# Create themed components
card = create_modern_card(content)
button = themed_button("Click me", on_click=handler)
```

## 🔍 Troubleshooting

### Common Issues

**Import Errors**
```python
# ✅ Correct imports
from FletV2.utils.server_bridge import ServerBridge
from FletV2.theme import create_modern_card

# ❌ Wrong imports
from utils.server_bridge import ServerBridge
from theme import create_modern_card
```

**Async Operations**
```python
# ✅ Non-blocking operations
async def on_click(e):
    data = await run_sync_in_executor(blocking_function)
    update_ui(data)

# ❌ Blocking UI thread
def on_click(e):
    data = server_bridge.get_data()  # Blocks UI!
    update_ui(data)
```

**Memory Management**
```python
# ✅ Proper cleanup
def dispose():
    nonlocal disposed, update_task
    disposed = True

    if update_task and not update_task.done():
        update_task.cancel()
```

### Debug Commands
```bash
# Check system requirements
python scripts/diagnostics.py

# Check database health
python scripts/check_db.py

# Monitor logs
tail -f logs/fletv2.log

# Test server connection
python -c "import socket; print('OK' if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('localhost', 1256)) != 0 else 'IN_USE')"
```

## 📋 Maintenance

### Regular Tasks

**Daily**
- Check system health: `python scripts/diagnostics.py`
- Review error logs: `tail -f logs/errors.log`
- Monitor disk space

**Weekly**
- Create backup: `python scripts/backup_database.py`
- Update dependencies: `pip list --outdated`
- Clean temporary files

**Monthly**
- Full system backup
- Performance optimization
- Security updates

### Database Operations
```bash
# Backup database
python scripts/backup_database.py

# Restore from backup
python scripts/recovery.py

# Check database integrity
sqlite3 defensive.db "PRAGMA integrity_check;"
```

## 🎯 Performance Guidelines

### UI Performance
- Keep view setup functions under 2 seconds
- Use async operations for network calls
- Implement proper cleanup in dispose functions
- Monitor memory usage with large datasets

### Testing Performance
- Unit tests should run under 30 seconds
- Integration tests should complete within 5 minutes
- Performance tests must include benchmarks
- Use test fixtures to avoid duplication

---

This concise guide covers the essential workflows for FletV2 development. For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md). For getting started, see [GETTING_STARTED.md](GETTING_STARTED.md).