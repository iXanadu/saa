# Site Audit Agent (SAA)

CLI tool for automated website audits using stealthy headless Chromium and LLM-powered analysis.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Run an audit
saa audit https://example.com

# With options
saa audit https://example.com --mode own --verbose --pacing medium

# Initialize config
saa init

# View config
saa config --list
```

## Modes

- **own**: Deep audit of your own sites (exhaustive checks, depth 3)
- **competitor**: Light learning scan (focus on insights, depth 1)
