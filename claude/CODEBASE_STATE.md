# Project Codebase State

**Last Updated:** 2026-01-31
**Version:** 0.3.5
**Status:** Feature-Complete CLI - Ready for Server Deployment

---

## Project Overview

Site Audit Agent (SAA) - CLI tool for automated website audits using stealthy headless Chromium and LLM-powered analysis.

---

## Architecture

```
src/saa/
├── __init__.py      # Package version (0.3.5)
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
| `saa init --update-plan` | Update audit plan (archives old) |
| `saa check` | Check for updates (code and plan) |
| `saa update` | Update via pipx |
| `saa plan` | Manage audit plans (list, rollback) |
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

## Recent Work (2026-01-31 Session 2)

### Self-Update System
- `saa check` - Compares installed vs GitHub version
- `saa update` - Runs pipx reinstall
- Detects missing config/plan and advises

### Plan Management
- Default audit plan bundled with package
- `saa init` copies plan to config directory
- `saa init --update-plan` - Updates plan, archives old to `plans/`
- `saa plan --list` - List archived plans
- `saa plan --rollback` - Restore previous plan

### UX Improvements
- `--quiet/-q` mode with updating status line
- Comprehensive help examples
- macOS + Linux group commands in init help

---

## Installation

```bash
# Single user (pipx)
pipx install git+ssh://git@github.com/iXanadu/saa.git
saa init

# Multi-user server
sudo pip install git+ssh://git@github.com/iXanadu/saa.git
sudo playwright install chromium
sudo playwright install-deps   # Linux only
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

## Config Files

```
{config_dir}/
├── .env              # Settings (LLM, crawl limits)
├── .keys             # API keys (XAI_API_KEY, ANTHROPIC_API_KEY)
├── audit-plan.md     # Default audit plan
└── plans/            # Archived plan versions
    └── audit-plan_{timestamp}.md
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

---

## Testing Status

- [x] Manual testing on dev.trustworthyagents.com
- [x] pipx install tested
- [x] Self-update system tested
- [x] Plan management tested
- [ ] Multi-user server deployment (next)
- [ ] Automated tests (pytest)

---

## Next Planned Work

1. Deploy and test on production server
2. Test multi-user access with group permissions
3. Refine audit plan based on report quality
4. Consider additional checks (broken links, accessibility)

---

## Reference

- **Specs:** `claude/specs/`
- **Bundled Plan:** `src/saa/data/default-audit-plan.md`
- **Session Progress:** `claude/session_progress/`
