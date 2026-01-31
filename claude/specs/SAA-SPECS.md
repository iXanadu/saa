# Technical Specifications (Specs): Site Audit Agent

## Architecture
- **Language**: Python 3.10+.
- **CLI Framework**: Click or Typer for subcommands/flags.
- **Browser**: Playwright with playwright-stealth; custom executable (your ungoogled-chromium app binary to avoid conflicts).
- **Parsing/Extraction**: BeautifulSoup4 + lxml.
- **LLM Dispatcher**: Custom class routing to provider APIs (requests-based).
- **Config**: dotenv for .env (keys/defaults); optional yaml for structured prefs.
- **Flow**:
  1. Parse CLI args/env.
  2. Load/parse plan (LLM if natural lang).
  3. Launch paced stealth browser.
  4. Crawl queue (BFS, mode-depth).
  5. Run checks, aggregate findings.
  6. LLM report gen.
  7. Output file.

## Tools List
| Tool/Library | Purpose | Version |
|--------------|---------|---------|
| Python | Runtime | 3.10+ |
| Click/Typer | CLI | Latest |
| Playwright | Browser automation | Latest |
| playwright-stealth | Anti-detection | Latest |
| BeautifulSoup4 | HTML parsing | 4.12+ |
| lxml | BS4 parser | Latest |
| requests | LLM APIs | 2.31+ |
| python-dotenv | .env loading | Latest |
| pydantic | Data validation | 2.5+ |
| pyyaml | Optional yaml config | Latest |
| ungoogled-chromium | Browser binary (your app) | Existing |

Optional: pdfkit for PDF outputs; zendriver for advanced stealth.

## Code Structure Outline
- `saa/__init__.py`: Package init.
- `saa/cli.py`: CLI entry (subcommands).
- `saa/config.py`: Load .env/yaml hierarchically (cwd > ~/.saa).
- `saa/plan.py`: Default MD string; LLM parse to structured.
- `saa/crawler.py`: Paced Playwright logic, extraction.
- `saa/checks.py`: Dynamic check functions (e.g., image_optimize).
- `saa/llm.py`: Dispatcher (xai/anthropic clients).
- `saa/report.py`: Generate/output.
- `setup.py`: For pip install.

## Packaging
- Pip-installable: `python setup.py install` or Poetry for deps.
- Entry: scripts = ['saa = saa.cli:main'] for PATH addition.
