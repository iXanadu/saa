# Project Codebase State

**Last Updated:** Not yet initialized
**Status:** New Project - Awaiting Setup

---

## Project Overview

This is a new  project created from the claude_prod_template.

---

## Setup Status


**Note**: This project uses **pyenv** for Python environment management, NOT venv.

---

## Next Steps

1. Read the PRD/specs in `claude/specs/` to understand project requirements
3. Configure environment files
4. Create core apps based on PRD
5. Update this file with actual project state

## IMPORTANT INSTRUCTIONS
**Note**: Implement the MVP exactly per AGENT_BEAST_SPEC.md. Start with core.py, memory.py, and the skills registry. Use async where appropriate. Follow the security defaults.

**Telegram implementation rules**:
- Use python-telegram-bot (async version 21.x).
- Load the bot token from environment variable TELEGRAM_TOKEN (will be in .keys).
- Use long-polling mode (application.run_polling()). Do NOT implement webhook.
- Whitelist only one chat ID (load from TELEGRAM_CHAT_ID env var). - Ignore all other messages.
- Handle both free-text messages and simple commands (/start, /status, /help).
- For proactive alerts: use await bot.send_message(chat_id, text) when thresholds are exceeded.
- Format messages nicely (use Markdown: bold, code, emojis for alerts 🔥 or ✅).
- Log every incoming message and outgoing response via structlog.
- Keep it simple — no inline keyboards, no complex menus in MVP.
---

## Reference

- **PRD/Specs:** `claude/specs/`
- **Example configs:** `claude/examples/basic_project/`
- **Code patterns:** `claude/examples/basic_project/code_patterns/`
