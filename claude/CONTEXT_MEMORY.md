# Project Context Memory

**Last Updated:** 2026-01-31
**Version:** 0.5.1
**Status:** Published to PyPI - Production Ready

---

## Current Focus

First public release complete. Package published to PyPI as `site-audit-agent`. Ready for real-world use.

---

## Completed Features

- [x] CLI tool with Click (audit, config, init, check, update, plan)
- [x] Stealth Chromium crawling via Playwright
- [x] BFS multi-page crawling with depth/page limits
- [x] Check registry (meta_tags, open_graph, images, https, performance, schema)
- [x] LLM integration (xAI Grok, Anthropic Claude)
- [x] Custom audit plan support (markdown)
- [x] Report generation with LLM enhancement
- [x] Public GitHub repo (iXanadu/saa)
- [x] PyPI distribution (site-audit-agent)
- [x] pipx installation
- [x] System-wide config (`/etc/saa/`) for multi-user servers
- [x] User keys model (each user manages own API keys)
- [x] `saa init --system` with user keys prompt
- [x] Self-update system (`saa check`, `saa update`)
- [x] Bundled default audit plan
- [x] Plan versioning with archive/rollback
- [x] Plan view/edit commands
- [x] Quiet mode with updating status line (`-q`)
- [x] GPL-3.0 license

---

## Key Technical Details

| Item | Value |
|------|-------|
| Python | 3.10+ |
| CLI Framework | Click |
| Browser | Playwright + playwright-stealth |
| LLM Providers | xAI (grok), Anthropic (claude-sonnet) |
| Package Build | hatchling (pyproject.toml) |
| Distribution | PyPI + Public GitHub |
| Package Name | site-audit-agent |
| CLI Command | saa |

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

**From GitHub (latest dev):**
```bash
pipx install git+https://github.com/iXanadu/saa.git
```

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
saa audit http://localhost:8000   # Local dev server

# Plan Management
saa plan                          # Show current plan location
saa plan --view                   # Output plan content
saa plan --edit                   # Open in editor
saa plan --update                 # Update to latest bundled
saa plan --list                   # List archived versions
saa plan --rollback               # Restore previous
```

---

## Config Hierarchy

```
1. /etc/saa/.env                  (system-wide settings, admin)
2. ~/.saa/.env, ~/.saa/.keys      (user settings and keys)
3. ./.env, ./.keys                (project override)
4. Environment variables          (highest priority)
```

**Note:** API keys should be in ~/.saa/.keys (user-private) not /etc/saa/

---

## Public URLs

- **PyPI:** https://pypi.org/project/site-audit-agent/
- **GitHub:** https://github.com/iXanadu/saa

---

## Next Session Priorities

1. **Use in real project** - Actual site audits
2. **Refine audit plan** - Improve based on results
3. **Consider additional checks** - Accessibility, broken links
4. **Automated tests** - pytest

---

## Known Issues

- `saa update` tries upgrade then reinstall (handles both PyPI and GitHub installs)
- Playwright Chromium is separate download (~300MB)
- pyenv can intercept commands - code checks pipx paths first

---

## Version History

| Version | Changes |
|---------|---------|
| 0.5.1 | Fix pyenv/playwright path issue |
| 0.5.0 | PyPI release (site-audit-agent) |
| 0.4.8 | Chown user keys under sudo |
| 0.4.7 | SUDO_USER for real user home |
| 0.4.6 | Prompt for user keys in system init |
| 0.4.5 | Smart init (detect system config) |
| 0.4.4 | Check /opt/playwright for all users |
| 0.4.1 | Permission model (system settings, user keys) |
| 0.4.0 | Public release, GPL license |
| 0.3.5 | Quiet mode (-q) |

---

## User Preferences

- **Editor:** Always suggest `vi` (not nano) - muscle memory

---

## Notes

- First open source contribution!
- Package name `saa` was taken on PyPI, using `site-audit-agent`
- CLI command remains `saa`
- Works with localhost URLs for local dev testing
