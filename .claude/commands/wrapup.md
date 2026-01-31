Create a session progress document for today's work:

1. **Create a new file** in `claude/session_progress/` with format: `YYYY-MM-DD_brief_description.md`
   - Include session overview and objectives
   - List major accomplishments with technical details
   - List files modified/created with specific changes
   - Document bugs fixed and how they were resolved
   - Note any architectural decisions made
   - List pending tasks or issues for next session

2. **Update `claude/CODEBASE_STATE.md`**:
   - Update "Last Updated" date at the top
   - Update "Recent Major Work Completed" section with today's work
   - Update "Next Planned Work" section based on what remains
   - Update "Testing Status" if any testing was done

3. **Update `claude/CONTEXT_MEMORY.md`**:
   - Update current status with today's accomplishments
   - Mark any completed features
   - Update next session priorities
   - Update known issues section

4. **Commit code change**:
   - git add .
   - git commit -m "Commit Notes"
   - git push

5. **Summary**: Provide a brief recap of what should be remembered for the next session
