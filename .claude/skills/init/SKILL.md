---
name: init
description: Initialize a new project — env/keys/gitignore from proj-base, read specs, create databases, seed requirements.txt, update state files, and push to GitHub.
---

This is a NEW PROJECT initialization. Follow these steps:

## 1. Gather Project Information

Ask the user for:
- **Project name** (lowercase, no spaces, e.g., `myapp`)
- **Domain** (e.g., `myapp.trustworthyagents.com`)

## 2. Set Up Environment Files

```bash
# Setup base environment files
cp ~/.config/proj-base/.env .env
cp ~/.config/proj-base/.keys .keys
cp ~/.config/proj-base/.gitignore .gitignore

chmod 600 .keys
```

Then use the Edit tool to replace in `.env`:
- `PROJECTNAME` → actual project name (4 places)

## 3. Read Project Specs

Read any files in `claude/specs/` (especially `prd.md`) to understand what this project should do.

## Database — MANUAL, NOT done by `/init`

`/init` never creates or touches databases — a deliberate manual step; never hardcode a credential here, source it from `.keys`.

## 5. Requirements.txt

If it does not exist create it.
If you have read the specifications and know the requrements, Then use the Edit tool to add them to the requirements file, otherwise add a todo to update the requirements file after every session.   

```bash
touch requirements.txt
```

## 6. Update Project State

Update `claude/CODEBASE_STATE.md`:
- Mark completed setup steps
- Add project name and domain
- Update "Last Updated" date

Update `claude/CONTEXT_MEMORY.md`:
- Add project name, domain, database info
- Note any PRD/specs that were read

## 7. GitHub
If a git repo has not been initianted, initiate one. Ask the user if they have GitHub "ssh access", if so push to GitHub

## 8. Summary

When complete, summarize:
- What was set up
- What the PRD says the project should do
- Suggested next steps based on the PRD
- Ask what the user wants to work on first
