Read the following files to get up to speed with the project:

1. Read the `.env` file to determine the environment:
   - `ENVIRONMENT=local` = Local development machine
   - `ENVIRONMENT=development` = Dev server
   - `ENVIRONMENT=production` = Production server

2. Read `claude/CODEBASE_STATE.md` - current technical state, recent work, and next planned tasks
3. Read `claude/CONTEXT_MEMORY.md` - working context and ongoing priorities
4. Read `claude/DEV_HANDOFF.md` if it exists - check for pending server-side actions
5. Read any files in `claude/specs/` if they exist (PRD, requirements, etc.)
6. List all files in `claude/session_progress/` and read the most recent 2-3 files

After reading these files:
- State which environment we appear to be in (based on .env) and ASK for confirmation
- Summarize the current development status
- Identify pending tasks from "Next Planned Work"
- Note any blockers or technical debt
- **If on dev/prod server**: Check DEV_HANDOFF.md for any actions needed from local Claude
- Ask what we're working on today

---

## Deployment Workflow Reminder

**Claude does NOT automate server deployment.** The workflow is:
1. Claude and user work locally (MacBook/dev machine)
2. Code is committed and pushed to repository
3. User manually SSHs to server, runs `git pull`, restarts service
4. Claude leaves handoff notes in `claude/DEV_HANDOFF.md` when server-side actions are needed

### Handoff Notes (DEV_HANDOFF.md)

**Local Claude → Dev/Prod**: When pushing changes that require actions beyond `git pull`:
- New pip packages to install
- Migrations to run
- collectstatic needed
- New environment variables

**Dev Claude → Local**: When finishing work on the server, note:
- Any server-specific issues discovered
- Configuration changes made
- Things to test locally next

**Never create deployment automation scripts.** Just document what's needed.
