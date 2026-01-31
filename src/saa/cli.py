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
@click.option("--system", is_flag=True, help="Initialize system-wide config at /etc/saa/ (requires sudo)")
def init(system: bool):
    """Initialize SAA configuration directory.

    Creates config files with templates:

    \b
    .env   - Settings (chromium path, default LLM, crawl limits)
    .keys  - API keys for LLM providers (xAI, Anthropic)

    \b
    Config loading priority (later overrides earlier):
      1. /etc/saa/    - System-wide (admin-managed, for multi-user servers)
      2. ~/.saa/      - User config (single-user or user overrides)
      3. ./.env       - Project-specific overrides

    \b
    Examples:
      saa init           # Create ~/.saa/ for current user
      sudo saa init --system  # Create /etc/saa/ for all users
    """
    import os
    from pathlib import Path

    if system:
        saa_dir = Path("/etc/saa")
        if os.geteuid() != 0:
            click.echo("Error: --system requires root. Use: sudo saa init --system", err=True)
            raise SystemExit(1)
    else:
        saa_dir = Path.home() / ".saa"

    saa_dir.mkdir(exist_ok=True)
    click.echo(f"Initializing SAA config at {saa_dir}")
    click.echo("")

    env_file = saa_dir / ".env"
    if not env_file.exists():
        env_file.write_text(
            "# SAA Configuration\n"
            "# Uncomment and edit the settings you want to change.\n"
            "#\n"
            "# Path to Chromium browser (auto-detected if not set)\n"
            "# SAA_CHROMIUM_PATH=/usr/bin/chromium\n"
            "#\n"
            "# Default LLM provider:model (xai:grok, anthropic:sonnet, anthropic:opus)\n"
            "# SAA_DEFAULT_LLM=xai:grok\n"
            "#\n"
            "# Crawl limits\n"
            "# SAA_MAX_PAGES=50\n"
            "# SAA_DEFAULT_DEPTH=3\n"
        )
        click.echo(f"  Created: {env_file}")
        click.echo(f"           Settings like chromium path, default LLM, crawl limits")
    else:
        click.echo(f"  Exists:  {env_file}")

    keys_file = saa_dir / ".keys"
    if not keys_file.exists():
        keys_file.write_text(
            "# API Keys for LLM providers\n"
            "# At least one key is required for LLM-powered analysis.\n"
            "# Get keys from:\n"
            "#   xAI:       https://console.x.ai/\n"
            "#   Anthropic: https://console.anthropic.com/\n"
            "#\n"
            "# Uncomment and add your key(s):\n"
            "# XAI_API_KEY=xai-your-key-here\n"
            "# ANTHROPIC_API_KEY=sk-ant-your-key-here\n"
        )
        if system:
            os.chmod(keys_file, 0o640)  # root:group readable
            click.echo(f"  Created: {keys_file} (permissions: 640)")
        else:
            os.chmod(keys_file, 0o600)  # owner only
            click.echo(f"  Created: {keys_file} (permissions: 600)")
        click.echo(f"           API keys for xAI (Grok) and/or Anthropic (Claude)")
    else:
        click.echo(f"  Exists:  {keys_file}")

    click.echo("")
    click.echo("Next steps:")
    click.echo(f"  1. Edit {keys_file} and add your API key(s)")
    click.echo(f"  2. (Optional) Edit {env_file} to customize settings")
    click.echo(f"  3. Run: saa audit https://example.com")
    if system:
        click.echo("")
        click.echo("For multi-user access, set group permissions:")
        click.echo(f"  sudo groupadd saa-users")
        click.echo(f"  sudo chgrp saa-users {keys_file}")
        click.echo(f"  sudo usermod -aG saa-users USERNAME")


@main.command()
def check():
    """Check if a newer version is available on GitHub.

    Compares your installed version against the latest commit on GitHub.
    Uses SSH to access the private repository.
    """
    import shutil
    import subprocess
    from datetime import datetime

    click.echo(f"Installed version: {__version__}")

    # Get install timestamp from package location
    import saa
    pkg_path = Path(saa.__file__).parent
    mtime = pkg_path.stat().st_mtime
    install_time = datetime.fromtimestamp(mtime)
    click.echo(f"Installed at: {install_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Check remote via git
    if not shutil.which("git"):
        click.echo("\nCannot check remote: git not found")
        return

    click.echo("\nChecking GitHub...")
    try:
        result = subprocess.run(
            ["git", "ls-remote", "git@github.com:iXanadu/saa.git", "HEAD"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            remote_commit = result.stdout.strip().split()[0][:7]
            click.echo(f"Latest commit: {remote_commit}")
            click.echo("\nIf you've pushed changes after your install time, run:")
            click.echo("  saa update")
        else:
            click.echo("Could not reach GitHub (check SSH key)")
    except subprocess.TimeoutExpired:
        click.echo("Timeout connecting to GitHub")
    except Exception as e:
        click.echo(f"Error checking remote: {e}")


@main.command()
def update():
    """Update saa to the latest version from GitHub.

    Runs 'pipx reinstall saa' to pull the latest code.
    Requires pipx to be installed.
    """
    import shutil
    import subprocess

    if not shutil.which("pipx"):
        click.echo("Error: pipx not found.", err=True)
        click.echo("\nInstall pipx first:")
        click.echo("  brew install pipx")
        click.echo("\nOr update manually with pip:")
        click.echo("  pip install --upgrade git+ssh://git@github.com/iXanadu/saa.git")
        raise SystemExit(1)

    click.echo("Updating saa via pipx reinstall...")
    click.echo("(This pulls the latest code from GitHub)\n")

    result = subprocess.run(["pipx", "reinstall", "saa"])

    if result.returncode == 0:
        click.echo("\nUpdate complete! Run 'saa check' to verify.")
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
