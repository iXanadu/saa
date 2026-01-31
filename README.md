# Site Audit Agent (SAA)

CLI tool for automated website audits using stealthy headless Chromium and LLM-powered analysis.

## Prerequisites

- Python 3.11+
- Chromium browser installed
- API keys for LLM providers (xAI and/or Anthropic)

## Installation

```bash
# Install from private repo (requires SSH key linked to GitHub)
pip install git+ssh://git@github.com/iXanadu/saa.git

# Initialize config directory
saa init

# Install Playwright browsers
playwright install chromium
```

## Configuration

Config is loaded in order (later overrides earlier):
1. `/etc/saa/` - System-wide (admin-managed)
2. `~/.saa/` - User override
3. `./.env`, `./.keys` - Project override
4. Environment variables - Highest priority

### Single-user setup

After running `saa init`, edit the config files in `~/.saa/`:

**~/.saa/.keys** (API keys - keep secret):
```
XAI_API_KEY=your-xai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

**~/.saa/.env** (optional settings):
```
SAA_CHROMIUM_PATH=/path/to/chromium
SAA_DEFAULT_LLM=xai:grok
SAA_MAX_PAGES=50
SAA_DEFAULT_DEPTH=3
```

### Multi-user server setup (centrally managed keys)

Admin sets up system-wide config so users don't need their own API keys:

```bash
# Create system config directory
sudo mkdir -p /etc/saa

# Add API keys
sudo nano /etc/saa/.keys
# XAI_API_KEY=your-key
# ANTHROPIC_API_KEY=your-key

# Add settings
sudo nano /etc/saa/.env
# SAA_CHROMIUM_PATH=/usr/bin/chromium
# SAA_DEFAULT_LLM=xai:grok

# Restrict access to keys (optional: create saa-users group)
sudo groupadd saa-users
sudo chown root:saa-users /etc/saa/.keys
sudo chmod 640 /etc/saa/.keys

# Add users who can run saa
sudo usermod -aG saa-users projectA
sudo usermod -aG saa-users projectB
```

Users in the `saa-users` group can now run `saa` without managing keys.

## Usage

```bash
# Basic audit
saa audit https://example.com

# Deep audit of your own site
saa audit https://mysite.com --mode own --verbose

# Light competitor scan
saa audit https://competitor.com --mode competitor

# With custom audit plan
saa audit https://mysite.com --plan ./my-audit-plan.md

# Skip LLM analysis (basic report only)
saa audit https://example.com --no-llm

# Save report to file
saa audit https://example.com -o report.md
```

## Modes

- **own**: Deep audit of your own sites (depth 10, up to 200 pages, exhaustive checks)
- **competitor**: Light learning scan (depth 1, up to 20 pages, focus on insights)

## Options

| Option | Description |
|--------|-------------|
| `--mode`, `-m` | Audit mode: `own` or `competitor` |
| `--depth`, `-d` | Max crawl depth |
| `--max-pages` | Max pages to crawl |
| `--llm`, `-l` | LLM provider:model (e.g., `xai:grok`, `anthropic:sonnet`) |
| `--no-llm` | Skip LLM analysis |
| `--plan`, `-p` | Path to custom audit plan (markdown) |
| `--output`, `-o` | Output file path |
| `--pacing` | Crawl pacing: `off`, `low`, `medium`, `high` |
| `--verbose`, `-v` | Verbose output |

## Updating

```bash
pip install --upgrade git+ssh://git@github.com/iXanadu/saa.git
```
