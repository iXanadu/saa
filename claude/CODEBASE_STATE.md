# Project Codebase State

**Last Updated:** 2026-01-31
**Version:** 0.5.1
**Status:** Published to PyPI - Production Ready

---

## Project Overview

Site Audit Agent (SAA) - CLI tool for automated website audits using stealthy headless Chromium and LLM-powered analysis.

**Public URLs:**
- PyPI: https://pypi.org/project/site-audit-agent/
- GitHub: https://github.com/iXanadu/saa

---

## Architecture

```
src/saa/
├── __init__.py      # Package version (0.5.1)
├── cli.py           # Click CLI (audit, config, init, check, update, plan)
├── config.py        # Hierarchical config loading (/etc/saa → ~/.saa → .env)
├── models.py        # Pydantic models (PageData, Finding, etc.)
├── crawler.py       # Playwright stealth crawler with BFS + progress callback
├── checks.py        # Check registry (meta_tags, images, schema, etc.)
├── llm.py           # LLM dispatcher (xAI Grok, Anthropic Claude)
├── plan.py          # Audit plan loading
├── report.py        # Markdown report generation with LLM enhancement
└── data/
    └── default-audit-plan.md  # Bundled audit plan template
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `saa audit URL` | Run audit on URL |
| `saa init` | Setup config, check dependencies |
| `saa init --system` | Setup system-wide config (/etc/saa/) |
| `saa check` | Check for updates (code and plan) |
| `saa update` | Update via pipx |
| `saa plan` | Show current plan location |
| `saa plan --view` | Output plan content |
| `saa plan --edit` | Open plan in editor |
| `saa plan --update` | Update to latest bundled plan |
| `saa plan --list` | List archived plans |
| `saa plan --rollback` | Restore previous plan |
| `saa config --list` | Show current config |

---

## Key Audit Flags

| Flag | Description |
|------|-------------|
| `-o, --output` | Output file path |
| `-q, --quiet` | Quiet mode (single updating status line) |
| `-v, --verbose` | Verbose output |
| `-m, --mode` | own (deep) or competitor (light) |
| `-p, --plan` | Custom audit plan |
| `-l, --llm` | LLM provider (xai:grok, anthropic:sonnet) |
| `--no-llm` | Skip LLM analysis |
| `--pacing` | Crawl speed (off, low, medium, high) |

---

## Recent Work (2026-01-31 - Public Release)

### Public Release
- GPL-3.0 license added
- Public GitHub repo at iXanadu/saa
- Published to PyPI as `site-audit-agent`

### Permission Model
- System settings in /etc/saa/.env (shared, no keys)
- User keys in ~/.saa/.keys (private per user)
- Config loading skips unreadable files gracefully

### Smart Init
- Detects system config, only creates user keys
- System init prompts for user keys creation
- Uses SUDO_USER for real user home
- Chowns files to real user under sudo
- Checks /opt/playwright for all users

### Plan Commands
- `--view` to output content
- `--edit` to open in editor
- `--update` to get latest bundled
- `--bundled` to show default

### Compatibility
- Checks pipx venv paths before PATH (fixes pyenv issues)

---

## Installation

**From PyPI (recommended):**
```bash
pipx install site-audit-agent
saa init
vi ~/.saa/.keys
```

**Multi-user server:**
```bash
sudo apt install pipx
sudo PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install site-audit-agent
sudo saa init --system
```

**From GitHub:**
```bash
pipx install git+https://github.com/iXanadu/saa.git
```

---

## Config Locations

| Location | Purpose | Precedence |
|----------|---------|------------|
| `/etc/saa/.env` | System-wide settings | 1 (lowest) |
| `~/.saa/.env` | User settings | 2 |
| `~/.saa/.keys` | User API keys | 2 |
| `./.env`, `./.keys` | Project override | 3 |
| Environment vars | Runtime override | 4 (highest) |

---

## Config Files

```
/etc/saa/           # System (admin creates)
├── .env            # Shared settings
└── audit-plan.md   # Default plan

~/.saa/             # User (saa init creates)
├── .keys           # API keys (private!)
└── (optional .env) # User overrides
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SAA_DEFAULT_LLM` | Default LLM (xai:grok, anthropic:sonnet) |
| `SAA_DEFAULT_PLAN` | Path to audit plan |
| `SAA_OUTPUT_DIR` | Auto-save reports here |
| `SAA_MAX_PAGES` | Max pages to crawl |
| `SAA_DEFAULT_DEPTH` | Max crawl depth |
| `XAI_API_KEY` | xAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `PLAYWRIGHT_BROWSERS_PATH` | Browser location (/opt/playwright for system) |

---

## Testing Status

- [x] Manual testing on websites
- [x] pipx install from PyPI tested
- [x] pipx install from GitHub tested
- [x] Multi-user server deployment tested
- [x] macOS install with pyenv tested
- [x] localhost URL audits work
- [ ] Automated tests (pytest)

---

## Next Planned Work

1. Use in real projects
2. Refine audit plan based on results
3. Consider additional checks (accessibility, broken links)
4. Automated tests

---

## Reference

- **PyPI:** https://pypi.org/project/site-audit-agent/
- **GitHub:** https://github.com/iXanadu/saa
- **Specs:** `claude/specs/`
- **Bundled Plan:** `src/saa/data/default-audit-plan.md`
- **Session Progress:** `claude/session_progress/`
