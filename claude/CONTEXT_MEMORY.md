# Project Context Memory

**Last Updated:** 2026-01-31
**Status:** MVP Complete - Ready for Server Deployment

---

## Current Focus

Distribution and multi-user server support completed. Ready to deploy to production servers.

---

## Completed Features

- [x] CLI tool with Click (`saa audit`, `saa config`, `saa init`)
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

---

## Key Technical Details

| Item | Value |
|------|-------|
| Python | 3.13 (pyenv: saa-3.13) |
| CLI Framework | Click |
| Browser | Playwright + playwright-stealth |
| LLM Providers | xAI (grok-3), Anthropic (claude-sonnet-4) |
| Package Build | hatchling (pyproject.toml) |
| Distribution | Private GitHub + SSH |

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

**Development:**
```bash
cd /Users/robertpickles/pyprojects/saa
pip install -e .
```

**Production (pipx):**
```bash
pipx install git+ssh://git@github.com/iXanadu/saa.git
```

**Multi-user server:**
```bash
sudo pip install git+ssh://git@github.com/iXanadu/saa.git
sudo saa init --system
```

---

## Next Session Priorities

1. **Deploy to server** - Test with actual multi-user setup
2. **Tweak audit plan** - User wants to refine `Default-Test-Plan.md` for better report format
3. **Version management** - Consider bumping to 0.2.0 for distribution release

---

## Known Issues

- `pipx upgrade saa` doesn't work for git packages when version unchanged - use `pipx reinstall saa`
- Two `saa` commands on dev machine (pyenv shim vs pipx) - use full path if needed

---

## Notes

- Report v2 tested on dev.trustworthyagents.com - now shows specific URLs, not vague references
- LLM timeout increased to 180s for large crawls
- Default "own" mode: depth=10, max_pages=200
