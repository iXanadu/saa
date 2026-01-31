# Product Requirements Document (PRD): Site Audit Agent (SAA)

## Overview
### Product Name
Site Audit Agent (SAA)

### Product Description
SAA is a lightweight, Mac/server-runnable CLI tool for automating website audits. It reads an MD-format natural language audit plan (or uses a built-in default), crawls remote sites using stealthy headless Chromium to evade detection and handle dynamic content, extracts data, applies pacing to mimic human behavior, and generates reports via LLM integration (default: Grok). It supports modes for deep dives on own sites (exhaustive checks) and light learning scans on competitors (focus on strengths/innovations). Designed for long-term scalability, with modular architecture, config-driven flexibility, and easy packaging as a pip-installable CLI.

The tool is remote-site focused—no local project folder access needed—making it ideal for verifying PRDs/specs on production/staging servers or gathering intel from competitors.

### Target Users
- Developers/product managers auditing web apps (own or competitors).
- QA/SEO teams for automated checks.
- Strategists seeking competitive insights.

### Key Goals
- Reliable audits bypassing AI tool limitations (e.g., blocks, incomplete renders).
- Flexible LLM switching for analysis/reporting.
- Paced, stealthy crawling for high success rates.
- Scalable from quick scans to deep audits.

### Scope
- **In Scope**: MD plan parsing (via LLM), mode-based filtering (own/competitor), paced crawling with stealth Chromium, data extraction/checks, LLM report generation, CLI ergonomics, config/env support.
- **Out of Scope**: Local file/code audits, real-time monitoring, GUI, advanced ML (e.g., auto-anomaly detection).

## User Stories
As a user, I want to:
1. Run audits via CLI (e.g., `saa audit --plan plan.md --mode own --llm xai:grok-4 --output report.md`).
2. Use a default plan if none provided, filtered by mode (deep for own, learning for competitors).
3. Configure via .env (keys/defaults) and optional yaml (prefs), with hierarchical loading (project > global).
4. Evade detections with pacing/delays, behavioral sim, and stealth.
5. Switch LLMs easily (e.g., --llm anthropic:sonnet).
6. Get mode-tailored reports: Issues/fixes for own, insights/ideas for competitors.

## Functional Requirements
### Core Features
1. **CLI Entry**:
   - Subcommands: `audit` (main), `config` (set/view), `init` (setup ~/.saa).
   - Flags: --plan (MD file), --mode (own/competitor), --llm (provider:model), --output, --verbose, --pacing (off/low/medium/high).

2. **Audit Plan Handling**:
   - Input: MD file or default (hardcoded string, mode-filtered).
   - Parsing: LLM API call to structure into JSON (e.g., {checks: [...], depth: 3}).
   - Default Plan: As detailed in conversation (mode-aware sections for SEO, images, etc.).

3. **Crawling and Extraction**:
   - Headless Chromium via Playwright + stealth.
   - Pacing: Randomized delays (1-5s default), limits (max pages 50), behavioral sim (scroll/mouse).
   - Depth: Mode-based (3 for own, 1 for competitor).
   - Extracts: HTML, links, metas, images, metrics (load times via Playwright).
   - Checks: Dynamic per parsed plan (e.g., image sizes, schema validation).

4. **LLM Integration**:
   - Dispatcher for providers (xai, anthropic; models like grok-4, sonnet).
   - Prompts: Parse plan, then generate mode-specific report from findings.
   - API keys from .env.

5. **Reporting**:
   - Markdown/PDF output with mode-appropriate sections (issues for own, insights for competitor).
   - Evidence: Code snippets, metrics, suggestions.

### Non-Functional Requirements
- **Performance**: <5 mins for small sites; pacing tunable.
- **Security**: No persistent data; keys in .env/keychain.
- **Reliability**: Retries on errors, auto-backoff on blocks; 99% success via stealth/pacing.
- **Compatibility**: macOS 13+, Python 3.10+; portable to Linux servers.
- **Scalability**: Modular for future (e.g., batch mode, Docker).

### Dependencies
- External: LLM APIs (xAI/Anthropic keys).
- Internal: See Specs.

## Assumptions and Risks
- Assumptions: Sites are public/remote; user handles CLI/config.
- Risks: Anti-bot evolution requires stealth updates; LLM costs for large audits.

## Success Metrics
- 99% audit success without blocks (via pacing/stealth).
- Usable reports leading to actionable insights/fixes.
