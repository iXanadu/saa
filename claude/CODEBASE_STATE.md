# Project Codebase State

**Last Updated:** 2026-01-31
**Status:** MVP Complete - Distributed via Private GitHub

---

## Project Overview

Site Audit Agent (SAA) - CLI tool for automated website audits using stealthy headless Chromium and LLM-powered analysis.

---

## Architecture

```
src/saa/
├── __init__.py      # Package version (0.1.0)
├── cli.py           # Click CLI (audit, config, init commands)
├── config.py        # Hierarchical config loading (/etc/saa → ~/.saa → .env)
├── models.py        # Pydantic models (PageData, Finding, etc.)
├── crawler.py       # Playwright stealth crawler with BFS
├── checks.py        # Check registry (meta_tags, images, schema, etc.)
├── llm.py           # LLM dispatcher (xAI Grok, Anthropic Claude)
├── plan.py          # Audit plan loading
└── report.py        # Markdown report generation with LLM enhancement
```

---

## Recent Major Work Completed

### 2026-01-31: Distribution & Multi-User Setup
- Private GitHub repo: `git@github.com:iXanadu/saa.git`
- System-wide config support (`/etc/saa/`)
- `saa init --system` for admin setup
- pipx installation working
- Improved help documentation

### 2026-01-30: Report Quality & LLM Integration
- Full page/finding data sent to LLM (not truncated)
- Specific URL references in reports (not vague "multiple pages")
- Custom audit plan support (`--plan` flag)
- 180s LLM timeout for large reports

---

## Installation

```bash
# pipx (recommended for CLI tools)
pipx install git+ssh://git@github.com/iXanadu/saa.git
~/.local/pipx/venvs/saa/bin/playwright install chromium

# Multi-user server
sudo pip install git+ssh://git@github.com/iXanadu/saa.git
sudo saa init --system
```

---

## Config Locations

| Location | Purpose | Precedence |
|----------|---------|------------|
| `/etc/saa/` | System-wide (admin) | 1 (lowest) |
| `~/.saa/` | User config | 2 |
| `./.env` | Project override | 3 |
| Environment vars | Runtime override | 4 (highest) |

---

## Testing Status

- [x] Manual testing on dev.trustworthyagents.com (33 pages)
- [x] pipx install tested
- [ ] Multi-user server deployment
- [ ] Automated tests (pytest)

---

## Next Planned Work

1. Test on production server with multiple users
2. Tweak `Default-Test-Plan.md` for report format preferences
3. Add version bumping workflow
4. Consider additional checks (broken links, accessibility)

---

## Reference

- **Specs:** `claude/specs/`
- **Audit Plan:** `claude/specs/Default-Test-Plan.md`
- **Session Progress:** `claude/session_progress/`
