# Project Context Memory

**Last Updated:** 2026-01-31
**Version:** 0.3.5
**Status:** Feature-Complete - Ready for Server Deployment

---

## Current Focus

CLI polish complete. Self-update system, plan management, and quiet mode implemented. Ready for production server deployment and multi-user testing.

---

## Completed Features

- [x] CLI tool with Click (audit, config, init, check, update, plan)
- [x] Stealth Chromium crawling via Playwright
- [x] BFS multi-page crawling with depth/page limits
- [x] Check registry (meta_tags, open_graph, images, https, performance, schema)
- [x] LLM integration (xAI Grok, Anthropic Claude)
- [x] Custom audit plan support (markdown)
- [x] Report generation with LLM enhancement
- [x] Private GitHub distribution (`iXanadu/saa`)
- [x] pipx installation
- [x] System-wide config (`/etc/saa/`) for multi-user servers
- [x] `saa init --system` admin command
- [x] Self-update system (`saa check`, `saa update`)
- [x] Bundled default audit plan
- [x] Plan versioning with archive/rollback
- [x] Quiet mode with updating status line (`-q`)
- [x] Comprehensive help with examples

---

## Key Technical Details

| Item | Value |
|------|-------|
| Python | 3.13+ (also tested with 3.14) |
| CLI Framework | Click |
| Browser | Playwright + playwright-stealth |
| LLM Providers | xAI (grok-3), Anthropic (claude-sonnet-4) |
| Package Build | hatchling (pyproject.toml) |
| Distribution | Private GitHub + SSH |

---

## CLI Quick Reference

```bash
# Setup
saa init                          # User config (~/.saa/)
sudo saa init --system            # System config (/etc/saa/)

# Check & Update
saa check                         # Check for updates
saa update                        # Update via pipx

# Audit
saa audit https://example.com     # Basic audit
saa audit URL -o report.md        # Save to file
saa audit URL -q                  # Quiet mode
saa audit URL -v                  # Verbose
saa audit URL -m competitor       # Light competitor scan

# Plan Management
saa plan                          # Show current plan
saa plan --list                   # List archived versions
saa plan --rollback               # Restore previous
saa init --update-plan            # Update to latest bundled plan
```

---

## Config Hierarchy

```
1. /etc/saa/.keys, /etc/saa/.env   (system-wide, admin)
2. ~/.saa/.keys, ~/.saa/.env       (user)
3. ./.env, ./.keys                 (project)
4. Environment variables           (highest priority)
```

---

## Installation Commands

**Single user (pipx):**
```bash
pipx install git+ssh://git@github.com/iXanadu/saa.git
saa init
```

**Multi-user server:**
```bash
sudo pip install git+ssh://git@github.com/iXanadu/saa.git
sudo playwright install chromium
sudo playwright install-deps   # Linux only
sudo saa init --system
# Add API keys to /etc/saa/.keys
# Setup group: saa-users
```

---

## Next Session Priorities

1. **Deploy to production server** - Test full workflow
2. **Test multi-user access** - Group permissions, shared keys
3. **Refine audit plan** - Improve report quality based on results
4. **Run actual audits** - Real-world testing

---

## Known Issues

- `pipx upgrade saa` doesn't work for git packages - use `saa update` instead
- Two `saa` commands on dev machine (pyenv shim vs pipx) - use full path if needed
- Playwright Chromium is separate from package - must install after pip

---

## Version History

| Version | Changes |
|---------|---------|
| 0.3.5 | Quiet mode (-q) with updating status line |
| 0.3.4 | Expanded help examples |
| 0.3.3 | Quick Start in main help |
| 0.3.2 | Check alerts on missing config/plan |
| 0.3.1 | Plan management (archive, rollback) |
| 0.3.0 | Bundled audit plan, config options |
| 0.2.1 | Improved version comparison in check |
| 0.2.0 | Smart init (Chromium check, API key validation) |
| 0.1.2 | macOS + Linux group commands |
| 0.1.1 | saa check and saa update commands |
| 0.1.0 | Initial release |

---

## User Preferences

- **Editor:** Always suggest `vi` (not nano) - muscle memory

---

## Notes

- Report v2 tested on dev.trustworthyagents.com - shows specific URLs
- LLM timeout: 180s for large crawls
- Default "own" mode: depth=10, max_pages=200
- Archived plans stored in `{config}/plans/` with timestamps
