# Project Architecture & Development Philosophy Bible

**A Comprehensive Guide to Building Production-Ready Software Applications**

*This document captures a generalized philosophy, patterns, and practices for software development, inspired by production experiences across various projects. It is designed as a blank slate for any team or individual to start new projects with strong, consistent direction—framework-agnostic but leaning toward Python ecosystems for simplicity and extensibility. It emphasizes maintainability, security, and scalability from day one, without prescribing a specific framework like Django.*

**Version:** 1.0  
**Last Updated:** January 2026  

---

## Table of Contents

**Part I: Philosophy & Architecture**  
1. [Core Philosophy](#core-philosophy)  
2. [Why Modularity and Extensibility By Default](#why-modularity-and-extensibility-by-default)  
3. [Project Structure & Organization](#project-structure--organization)  

**Part II: Implementation Patterns**  
4. [Data Layer](#the-data-layer)  
5. [Service Layer](#the-service-layer)  
6. [Interface Patterns](#interface-patterns)  

**Part III: Configuration & Infrastructure**  
7. [Environment Configuration](#environment-configuration)  
8. [Storage Philosophy](#storage-philosophy)  
9. [Session Continuity & AI-Assisted Development](#session-continuity--ai-assisted-development)  
10. [Deployment Workflow](#deployment-workflow)  

**Part IV: Quality & Security**  
11. [Testing Patterns](#testing-patterns)  
12. [Security Practices](#security-practices)  

**Part V: Advanced Patterns**  
13. [Common Patterns Reference](#common-patterns-reference)  
14. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)  
15. [Task Management Patterns](#task-management-patterns)  
16. [Service Registry Pattern](#service-registry-pattern)  
17. [Configuration Patterns](#configuration-patterns)  
18. [Role-Based Access Flags](#role-based-access-flags)  
19. [Background Task Pattern](#background-task-pattern)  

**Appendix**  
20. [Quick Reference Card](#quick-reference-card)  
21. [Checklist for New Projects](#appendix-checklist-for-new-projects)  

---

## Core Philosophy

### Build for Production from Day One

Every decision assumes the application will eventually run in production, serve real users or tasks, and need to scale. This means:

- **No local-only shortcuts** - Use production-like storage (e.g., PostgreSQL or SQLite with backups) even in development.
- **Secure by default** - Network isolation (e.g., Tailscale), secrets management, and encryption ready from the start.
- **Proper credential separation** - Secrets never in code or version control; use environment files.
- **Modular architecture** - Design for extensibility, assuming features like multi-instance support will be added later.

### Progressive Enhancement, Not Premature Optimization

Build the simplest thing that works correctly, then enhance:

1. **MVP first** - Get core functionality working (e.g., basic task handling).
2. **Polish second** - Add refinements, better interfaces, edge cases.
3. **Optimize third** - Performance tuning only when measured (e.g., profiling CPU usage).

### Interfaces are Thin, Logic is Deep

User interfaces (e.g., CLI, API, messaging) should be simple handlers. All business logic lives in services or core methods:

```
Input → Interface (thin) → Service Layer (business logic) → Data Layer (storage access) → Storage
```

This separation enables:
- Testable logic without interface overhead.
- Reusable components across interfaces, tasks, and APIs.
- Clear boundaries for debugging and maintenance.

---

## Why Modularity and Extensibility By Default

### The Problem with Monolithic Afterthoughts

Adding modularity or extensibility to an existing rigid application is painful. You must:

1. Refactor core components to support plugins or extensions.
2. Modify every interaction to include extension points.
3. Update every task to check boundaries.
4. Audit for data leakage or conflicts.
5. Migrate existing logic to modular structure.

### Our Solution: Plugin-Capable Design from Day One

Every project incorporates a skills or plugin registry, allowing:

- Loose coupling between core and features.
- Easy addition of new capabilities (e.g., a server monitoring skill).
- Consistent patterns for invocation and response.

Even for single-purpose MVPs, use this pattern. When expanding (e.g., adding admin tasks), you're ready.

### The Core Registry

A central registry holds extensible components (e.g., skills, services):

```python
# Example in Python
registry = {}
def register_skill(name, skill_class):
    registry[name] = skill_class
```

Key decisions:
- **Name-based lookup** - Simple string keys for invocation.
- **Metadata** - Each entry includes description and params for self-documentation.
- **Isolation** - Plugins run in sandboxes where possible.

---

## Project Structure & Organization

### Standard Directory Layout

```
projectname/
├── projectname/           # Core package
│   ├── __init__.py
│   ├── core.py            # Main engine, loops, orchestrator
│   ├── config.py          # Environment and secrets loader
│   ├── memory.py          # Persistent storage layer
│   ├── skills/            # Extensible plugins (named by function)
│   │   ├── __init__.py
│   │   └── [skill].py     # e.g., monitor.py
│   ├── interfaces/        # Communication handlers (named by type)
│   │   ├── __init__.py
│   │   └── [interface].py # e.g., telegram.py, webui.py
│   └── utils.py           # Shared helpers (logging, alerts)
├── scripts/               # Operational tools
│   └── setup.sh           # Installation and deployment scripts
├── tests/                 # Unit and integration tests
│   └── test_[module].py
├── docs/                  # Documentation
│   └── PROJECT_BIBLE.md   # This document
├── .env                   # Non-sensitive config (in git as .example)
├── .keys                  # Sensitive secrets (NEVER in git)
├── requirements.txt       # Dependencies
├── Dockerfile             # Optional containerization
└── README.md              # Quick start and overview
```

### Naming Philosophy

**Name modules by function or domain, not technology:**

- `skills/monitor.py` not `psutil_wrapper.py`
- `interfaces/telegram.py` not `messaging_handler.py`

**Core modules every project needs:**

1. **core.py** - Main runtime and orchestration
2. **config.py** - Configuration management

**Domain modules are project-specific** - they represent capabilities (e.g., monitoring for MVP).

### When to Create a New Module

Create a new module when:

1. The functionality represents a distinct domain or skill.
2. The code has its own identity (not just supporting another module).
3. The module could be extracted as a reusable component.
4. It will have its own tests or configurations.

Don't create a new module just for a single function. Group related utilities in `utils.py`.

---

## The Data Layer

### Base Storage Hierarchy

Use abstract bases for data access in `memory.py`:

```python
class BaseStorage:
    """Base with timestamp and audit fields."""
    # Implement created_at, updated_at as properties or fields

class PersistentStorage(BaseStorage):
    """For data that needs isolation or scoping."""
    # Add scoping (e.g., session_id or user_id FK if needed)

class TrackedStorage(PersistentStorage):
    """Adds audit trail of changes."""
    # Add modified_by, version fields
```

### Choosing the Right Storage

| Type | Use When |
|------|----------|
| `BaseStorage` | Transient or system-level data (e.g., cache) |
| `PersistentStorage` | Core data needing durability (e.g., session history) |
| `TrackedStorage` | When audit trails are required (e.g., alerts log) |

### Data Field Guidelines

**Always include:**
- Timestamps for creation/update.
- Help text or docs for non-obvious fields.
- Validation strategies (e.g., constraints or schemas).
- Error handling for access (e.g., retries on failure).

**Status field pattern:**
```python
STATUS_CHOICES = [
    ('active', 'Active'),
    ('warning', 'Warning'),
    ('error', 'Error'),
]
status = 'active'  # With validation
```

**File handling pattern:**
- Use secure paths (e.g., relative to project root).
- Avoid user-controlled filenames.

---

## The Service Layer

### Why Services Over Monolithic Logic

Keep core logic focused; services handle domain-specific operations:

**Problems with monolithic logic:**
- Code becomes tangled and hard to test.
- Difficult to reuse across interfaces.
- Circular dependencies.

**Services solve this:**
- Plain classes for business operations.
- Testable with mocks.
- Clear boundaries.
- Reusable for your Django provisioning or future skills.

### Service Layer Architecture

```
projectname/
└── services/
    ├── __init__.py          # Re-export public interfaces
    ├── base_service.py      # Abstract base (if needed)
    ├── monitor_service.py   # MVP proactive checks
    └── [future_service].py  # e.g., admin_provision.py
```

### Service Design Principles

#### 1. Single Responsibility

Each service does one thing well:

```python
# Good - focused
class MonitorService:
    def check_metrics(self) -> dict:
        pass

# Bad - too broad
class SystemService:
    def check_metrics(self): pass
    def send_alert(self): pass
    def log_event(self): pass
```

#### 2. Dataclasses for Results

Use dataclasses for outputs:

```python
from dataclasses import dataclass

@dataclass
class MetricResult:
    success: bool
    data: dict = None
    error: str = ""
```

#### 3. Pure vs Integrated Services

**Pure**: No dependencies on storage/external:

```python
class PureMonitorService:
    def get_raw_metrics(self) -> dict:
        import psutil
        return {'cpu': psutil.cpu_percent()}
```

**Integrated**: Combine with storage:

```python
class MonitorService:
    def __init__(self, memory_store):
        self.memory = memory_store

    def check_and_alert(self) -> MetricResult:
        raw = PureMonitorService().get_raw_metrics()
        # Compare to thresholds, save to memory, alert if needed
        pass
```

#### 4. Factory Pattern for Extensibility

For interchangeable implementations:

```python
def get_service(name: str) -> BaseService:
    if name == 'monitor':
        return MonitorService()
    raise ValueError(f"Unknown service: {name}")
```

### Service Method Guidelines

**Clear signatures:**
```python
async def check_metrics(self, interval: int = 600) -> MetricResult:
    pass
```

**Explicit error handling:**
```python
def execute(self):
    try:
        # logic
        return MetricResult(success=True, data=...)
    except Exception as e:
        logger.error(f"Failed: {e}")
        return MetricResult(success=False, error=str(e))
```

---

## Interface Patterns

### The Thin Interface Philosophy

Interfaces (e.g., Telegram, Web UI) should:
1. Parse input
2. Call services
3. Return output

Interfaces should NOT:
- Contain business logic
- Have complex conditionals
- Access storage directly

```python
# Good - thin
async def handle_query(request):
    text = request.text
    result = await agent.process_message(text)
    return result
```

### Scoped Interfaces

Every interface accessing data MUST scope to user/session:

- Use whitelists (e.g., chat ID for Telegram)
- Validate inputs strictly

### Custom Decorators

For common behaviors (e.g., logging):

```python
def logged(func):
    async def wrapped(*args):
        logger.info("Starting")
        result = await func(*args)
        logger.info("Done")
        return result
    return wrapped
```

### Context Providers

Make session/user available globally if needed (e.g., via async contextvars).

---

## Environment Configuration

### The Two-File System

Separate config from secrets:

| File | Contents | In Git? |
|------|----------|---------|
| `.env` | Non-sensitive (hosts, paths, intervals) | Yes (as .example) |
| `.keys` | Secrets (tokens, keys) | NEVER |

### .env Structure

```bash
# Environment
ENV=local

# Debug
DEBUG=true

# Interfaces
TELEGRAM_CHAT_ID=your-id

# Monitoring
CHECK_INTERVAL_SECONDS=300
ALERT_THRESHOLD_DISK=80
```

### .keys Structure

```bash
TELEGRAM_TOKEN=your-token
```

### Config.py Pattern

Single loader with environment branching:

```python
import os
from dotenv import load_dotenv

load_dotenv('.env')
load_dotenv('.keys')

ENV = os.getenv('ENV', 'local')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

if ENV == 'prod':
    # Prod-specific (e.g., stricter thresholds)
    pass
```

### Three-Tier Architecture

```
Local (laptop) → Dev server → Prod server
```

Use consistent storage across tiers for confidence.

---

## Storage Philosophy

### Persistent Storage Only - No Exceptions

Use durable storage from day one (e.g., SQLite for MVP, PostgreSQL for scale):

**Why?**
1. Behavioral consistency across environments.
2. Early detection of scale issues.
3. Confidence in migrations/persistence.

### Storage Naming Convention

`project_{env}.db` (e.g., `agent_beast_dev.db`)

### Access Per Application

Use dedicated credentials/connections.

### Best Practices

1. Explicit migrations/upgrades.
2. Review operations before applying.
3. Test in dev first.
4. Use transactions for atomicity.

---

## Session Continuity & AI-Assisted Development

### The Problem

AI tools like Claude Code lack memory between sessions. Without structure, each starts from scratch.

### The Solution: State Tracking Files

Three files for continuity:

#### 1. CODEBASE_STATE.md - Technical State

Current codebase snapshot:

```markdown
# Agent Beast - Codebase State

**Last Updated:** 2026-01-26

## Current State Summary
- Phase: MVP Development
- Progress: 20%
- Status: Active

## Recent Work Completed
1. Core engine - Jan 26

## Next Planned Work
1. Telegram integration
2. Web UI

## Architecture Notes
- Using async for proactivity
```

#### 2. CONTEXT_MEMORY.md - Working Context

Decisions and focus:

```markdown
# Agent Beast - Context Memory

**Last Updated:** 2026-01-26

## Active Focus Area
Building MVP core and interfaces.

## Recent Decisions
- Long-polling for Telegram
- Skills registry for extensibility

## Patterns Being Used
- Thin interfaces, deep services
- Persistent SQLite

## Known Issues
- [ ] Add LLM fallback
```

#### 3. DEV_HANDOFF.md - Deployment Notes

Post-git-pull steps:

```markdown
# Dev Handoff Notes

**Last Updated:** 2026-01-26

## Current Handoff
After pulling:
- pip install -r requirements.txt
- systemctl restart agent-beast.service

## New Environment Variables
- TELEGRAM_TOKEN (add to .keys)
```

### Session Progress Files

Daily summaries in `sessions/` for reference.

---

## Deployment Workflow

### Why Manual Over Automated

Manual ensures oversight for your part-time style.

### The Workflow

1. **Local Dev** (Mac/laptop)
   - AI collaboration
   - Test locally
   - Commit/push

2. **Code Push**
   - Git workflow

3. **Manual Server Deployment**
   - SSH to Linode (via Tailscale)
   - `git pull`
   - Follow DEV_HANDOFF.md
   - Restart service

### Standard Steps

```bash
cd /var/www/agent_beast
git pull origin main
cat DEV_HANDOFF.md  # Check extras
pip install -r requirements.txt
systemctl restart agent-beast.service
```

### Server Architecture

Agent as daemon → Supervised by systemd → No nginx in MVP (Web UI direct via FastAPI).

---

## Testing Patterns

### Test Structure

```
tests/
├── test_core.py
├── test_memory.py
└── test_skills.py
```

### Basic Tests

```python
class CoreTest:
    def test_process_message(self):
        result = agent.process_message("cpu load?")
        assert 'CPU' in result
```

### Service Tests

Use mocks:

```python
from unittest.mock import patch

class MonitorTest:
    @patch('psutil.cpu_percent')
    def test_high_cpu_alert(self, mock_cpu):
        mock_cpu.return_value = 95
        result = monitor.execute({})
        assert 'alert' in result.lower()
```

---

## Security Practices

### Never Commit Secrets

Files NEVER in git:
- `.keys`
- Credentials files

### .gitignore Essentials

```gitignore
.keys
*.db
logs/
__pycache__/
venv/
```

### Security Defaults

- No public ports
- Input validation
- Read-only operations
- Encrypted secrets

---

## Common Patterns Reference

### Operation Result Dataclass

```python
@dataclass
class OperationResult:
    success: bool
    data: Any = None
    error: str = ""
```

### Status Choices

Use enums or dicts for states.

### Soft Delete

Flag-based deletion for data.

### Caching

Simple dict or external for hot data.

---

## Anti-Patterns to Avoid

1. Business Logic in Interfaces
2. Missing Scoping/Validation
3. Hardcoded Config
4. Not Using Transactions/Retries
5. Circular Dependencies

---

## Task Management Patterns

Use threads/schedulers for proactivity.

---

## Service Registry Pattern

Dict-based registration for services/skills.

---

## Configuration Patterns

Separate non-sensitive/sensitive; environment branching.

---

## Role-Based Access Flags

Boolean flags for capabilities (if multi-user added later).

---

## Background Task Pattern

Threads for simple; queues for complex.

---

## Quick Reference Card

### Initialization

```bash
mkdir agent_beast && cd agent_beast
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./scripts/setup.sh
```

### Daily Commands

```bash
systemctl start agent-beast
tail -f logs/agent.log
```

### Hierarchy

Core (engine) → Services/Skills (logic) → Interfaces (thin)

### File Structure Recap

Core package with skills/interfaces.

### Environment Variables

.env for config; .keys for secrets.

---

## Conclusion

This bible provides a blank slate with strong direction for projects—emphasizing modularity, security, and extensibility. Follow these patterns for applications that are production-ready from day one and evolve without pain.

---

## Appendix: Checklist for New Projects

- [ ] Create folder and copy template structure
- [ ] Set up venv
- [ ] Configure .env / .keys
- [ ] Generate secrets (e.g., tokens)
- [ ] Install dependencies
- [ ] Set up storage (SQLite)
- [ ] Configure daemon (systemd)
- [ ] Add core philosophy docs
- [ ] Test core loop
- [ ] Deploy and verify persistence

---
