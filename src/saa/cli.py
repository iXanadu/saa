"""CLI entry point for Site Audit Agent."""

import asyncio
from pathlib import Path

import click

from saa import __version__
from saa.config import load_config
from saa.crawler import Crawler
from saa.checks import run_checks, DEFAULT_CHECKS_OWN, DEFAULT_CHECKS_COMPETITOR
from saa.report import generate_report
from saa.llm import get_llm_client
from saa.plan import load_plan


@click.group()
@click.version_option(version=__version__, prog_name="saa")
def main():
    """Site Audit Agent - Automated website audits with LLM analysis."""
    pass


@main.command()
@click.argument("url")
@click.option("--plan", "-p", type=click.Path(exists=True), help="Path to MD audit plan")
@click.option("--mode", "-m", type=click.Choice(["own", "competitor"]), default="own",
              help="Audit mode: own (deep) or competitor (light)")
@click.option("--depth", "-d", type=int, default=None,
              help="Max crawl depth (default: 3 for own, 1 for competitor)")
@click.option("--max-pages", type=int, default=None,
              help="Max pages to crawl (default: 50 for own, 20 for competitor)")
@click.option("--llm", "-l", default=None, help="LLM provider:model (e.g., xai:grok, anthropic:sonnet)")
@click.option("--no-llm", is_flag=True, help="Skip LLM analysis (basic report only)")
@click.option("--output", "-o", type=click.Path(), help="Output report path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--pacing", type=click.Choice(["off", "low", "medium", "high"]),
              default="medium", help="Crawl pacing level")
def audit(url: str, plan: str, mode: str, depth: int, max_pages: int,
          llm: str, no_llm: bool, output: str, verbose: bool, pacing: str):
    """Run an audit on URL.

    Examples:
        saa audit https://example.com --mode own --verbose
        saa audit https://competitor.com --mode competitor --llm xai:grok
        saa audit https://mysite.com --no-llm -o report.md
    """
    config = load_config()

    # Override config with CLI options
    config.mode = mode
    config.pacing = pacing
    if llm:
        config.default_llm = llm

    # Set depth and max_pages based on mode if not specified
    # For "own" mode: full crawl (high limits to capture entire site)
    # For "competitor" mode: light scan (limited to avoid detection/overload)
    if depth is None:
        depth = 10 if mode == "own" else 1
    if max_pages is None:
        max_pages = 200 if mode == "own" else 20

    if verbose:
        click.echo(f"Starting audit of {url}")
        click.echo(f"Mode: {mode}, Depth: {depth}, Max pages: {max_pages}, Pacing: {pacing}")
        if plan:
            click.echo(f"Using audit plan: {plan}")
        if not no_llm:
            click.echo(f"LLM: {config.default_llm}")

    # Run the async audit
    try:
        asyncio.run(_run_audit(url, config, plan, output, verbose, mode, depth, max_pages, no_llm))
    except KeyboardInterrupt:
        click.echo("\nAudit cancelled.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


async def _run_audit(url: str, config, plan_path: str, output_path: str,
                     verbose: bool, mode: str, depth: int, max_pages: int, no_llm: bool):
    """Execute the audit asynchronously."""
    click.echo(f"Auditing: {url}")

    # Load audit plan if provided
    plan_content = None
    if plan_path:
        plan_content = load_plan(plan_path)
        if verbose:
            click.echo(f"Loaded audit plan ({len(plan_content)} chars)")

    # Crawl pages
    async with Crawler(config, verbose=verbose) as crawler:
        pages = await crawler.crawl(url, max_depth=depth, max_pages=max_pages)

    # Check if we got any successful pages
    successful_pages = [p for p in pages if not p.error]
    if not successful_pages:
        click.echo("Failed to fetch any pages.", err=True)
        raise SystemExit(1)

    # Run checks based on mode
    checks_to_run = DEFAULT_CHECKS_OWN if mode == "own" else DEFAULT_CHECKS_COMPETITOR
    findings = run_checks(successful_pages, checks_to_run)

    # Get LLM client if enabled
    llm_client = None
    if not no_llm:
        try:
            llm_client = get_llm_client(config.default_llm, config)
            if verbose:
                click.echo(f"Using LLM: {config.default_llm}")
        except ValueError as e:
            if verbose:
                click.echo(f"LLM not available: {e}")
                click.echo("Generating basic report without LLM analysis.")

    # Generate report
    output_text = generate_report(
        start_url=url,
        pages=pages,
        findings=findings,
        mode=mode,
        llm_client=llm_client,
        verbose=verbose,
        plan_content=plan_content,
    )

    if output_path:
        Path(output_path).write_text(output_text)
        click.echo(f"\nReport saved to: {output_path}")
    else:
        click.echo(output_text)


@main.command()
@click.option("--set", "set_key", nargs=2, metavar="KEY VALUE", help="Set config key value")
@click.option("--get", "get_key", metavar="KEY", help="Get config value")
@click.option("--list", "list_all", is_flag=True, help="List all config")
def config(set_key, get_key, list_all):
    """View or set configuration."""
    cfg = load_config()

    if list_all:
        click.echo("Current configuration:")
        click.echo(f"  chromium_path: {cfg.chromium_path}")
        click.echo(f"  default_llm: {cfg.default_llm}")
        click.echo(f"  max_pages: {cfg.max_pages}")
        click.echo(f"  default_depth: {cfg.default_depth}")
        click.echo(f"  pacing: {cfg.pacing}")
    elif get_key:
        value = getattr(cfg, get_key, None)
        if value is not None:
            click.echo(f"{get_key}: {value}")
        else:
            click.echo(f"Unknown config key: {get_key}")
    elif set_key:
        click.echo("Config setting not yet implemented - edit .env directly")
    else:
        click.echo("Use --list to see all config, --get KEY to get a value")


@main.command()
def init():
    """Initialize ~/.saa directory with defaults."""
    import os
    from pathlib import Path

    saa_dir = Path.home() / ".saa"
    saa_dir.mkdir(exist_ok=True)

    env_file = saa_dir / ".env"
    if not env_file.exists():
        env_file.write_text(
            "# SAA Configuration\n"
            "# SAA_CHROMIUM_PATH=/Applications/Chromium.app/Contents/MacOS/Chromium\n"
            "# SAA_DEFAULT_LLM=xai:grok-4\n"
            "# SAA_MAX_PAGES=50\n"
            "# SAA_DEFAULT_DEPTH=3\n"
        )
        click.echo(f"Created {env_file}")

    keys_file = saa_dir / ".keys"
    if not keys_file.exists():
        keys_file.write_text(
            "# API Keys (keep secret!)\n"
            "# XAI_API_KEY=your-key-here\n"
            "# ANTHROPIC_API_KEY=your-key-here\n"
        )
        os.chmod(keys_file, 0o600)  # Restrict permissions
        click.echo(f"Created {keys_file} (permissions: 600)")

    click.echo(f"SAA initialized at {saa_dir}")


if __name__ == "__main__":
    main()
