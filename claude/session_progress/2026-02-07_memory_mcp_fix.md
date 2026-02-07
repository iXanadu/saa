# Session Progress: 2026-02-07 - Memory MCP Connection Fix

## Session Overview

Short diagnostic session to test and fix the claude-memory MCP server connection. The MCP server was failing to connect because it defaulted to `localhost:8920` while the backend API runs on `macmini:8920`.

## Objectives Achieved

### 1. Diagnosed Memory MCP Connection Failure
- `memory_status` returned "All connection attempts failed"
- User confirmed backend is healthy: `curl http://macmini:8920/health` returns `{"status":"ok","checks":{"postgres":true,"ollama":true}}`
- Traced the issue through the MCP config chain

### 2. Root Cause Identified
- MCP server config in `~/.claude.json` had `"env": {}` (no environment variables)
- Server code at `/opt/srv/claude-memory-mcp/src/claude_memory_mcp/config.py` defaults `memory_api_url` to `http://localhost:8920`
- Backend API actually runs on `macmini:8920` (Mac Mini server)

### 3. Fix Applied
- Added `MEMORY_API_URL` environment variable to MCP server config in `~/.claude.json`
- Value: `http://macmini:8920`
- Requires Claude Code restart to take effect (MCP subprocess reads env at spawn time)

## Files Modified

| File | Changes |
|------|---------|
| `~/.claude.json` | Added `"MEMORY_API_URL": "http://macmini:8920"` to `mcpServers.claude-memory.env` |

## Technical Details

### MCP Server Architecture
```
Claude Code (stdio) → claude_memory_mcp.server (Python subprocess)
                       → httpx client → http://macmini:8920 (REST API)
                                          → PostgreSQL (storage)
                                          → Ollama (embeddings)
```

### Config Chain
- `~/.claude.json` defines MCP server with `type: stdio`
- Python command: `/Users/robertpickles/.pyenv/versions/cc-memory-3.12/bin/python -m claude_memory_mcp.server`
- Server uses pydantic-settings with `env_prefix=""` — so `MEMORY_API_URL` env var maps to `memory_api_url` field
- Code lives at `/opt/srv/claude-memory-mcp/`

## Pending / Next Session

1. **Verify fix works** — restart Claude Code and test `memory_status`
2. **Store initial project memories** — session progress, project conventions
3. **Continue with SAA roadmap** — real-world audits, audit plan refinement, automated tests

## Notes

- Memory MCP server installed in pyenv virtualenv `cc-memory-3.12`
- Backend runs on Mac Mini (`macmini`) with PostgreSQL + Ollama
- The fix was a one-line env var addition, no code changes needed
