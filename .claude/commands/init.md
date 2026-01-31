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

## 4. Create Database (if needed)

Ask user if they want you to create the PostgreSQL databases. If yes, run these commands:

```bash
# Create dedicated user for this app
createuser -h postgres.o6.org -U db_admin projectname

# Set password (uses shared DB_PASSWORD from .keys)
psql -h postgres.o6.org -U db_admin -d postgres -c "ALTER USER projectname WITH PASSWORD 'R%qMuGnizHl^V0iD';"

# Grant db_admin ability to set ownership to new user
psql -h postgres.o6.org -U db_admin -d postgres -c "GRANT projectname TO db_admin;"

# Create dev and prod databases owned by app user
createdb -h postgres.o6.org -U db_admin -O projectname projectname_dev
createdb -h postgres.o6.org -U db_admin -O projectname projectname_prod
```
(Uses db_admin credentials from ~/.pgpass)

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
