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
@click.option("--plan", "-p", type=click.Path(exists=True), help="Path to MD audit plan (overrides config)")
@click.option("--no-plan", is_flag=True, help="Skip audit plan even if configured")
@click.option("--mode", "-m", type=click.Choice(["own", "competitor"]), default="own",
              help="Audit mode: own (deep) or competitor (light)")
@click.option("--depth", "-d", type=int, default=None,
              help="Max crawl depth (default: 3 for own, 1 for competitor)")
@click.option("--max-pages", type=int, default=None,
              help="Max pages to crawl (default: 50 for own, 20 for competitor)")
@click.option("--llm", "-l", default=None, help="LLM provider:model (e.g., xai:grok, anthropic:sonnet)")
@click.option("--no-llm", is_flag=True, help="Skip LLM analysis (basic report only)")
@click.option("--output", "-o", type=click.Path(), help="Output report path (overrides config)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--pacing", type=click.Choice(["off", "low", "medium", "high"]),
              default="medium", help="Crawl pacing level")
def audit(url: str, plan: str, no_plan: bool, mode: str, depth: int, max_pages: int,
          llm: str, no_llm: bool, output: str, verbose: bool, pacing: str):
    """Run an audit on URL.

    Examples:
        saa audit https://example.com --mode own --verbose
        saa audit https://competitor.com --mode competitor --llm xai:grok
        saa audit https://mysite.com --no-llm -o report.md
    """
    from datetime import datetime
    from urllib.parse import urlparse

    config = load_config()

    # Override config with CLI options
    config.mode = mode
    config.pacing = pacing
    if llm:
        config.default_llm = llm

    # Resolve plan: CLI > config > none
    if no_plan:
        plan = None
    elif not plan and config.default_plan:
        plan_path = Path(config.default_plan)
        if plan_path.exists():
            plan = str(plan_path)
        elif verbose:
            click.echo(f"Warning: Configured plan not found: {config.default_plan}")

    # Resolve output: CLI > config (auto-generate filename) > stdout
    if not output and config.output_dir:
        output_dir = Path(config.output_dir)
        if output_dir.exists():
            domain = urlparse(url).netloc.replace(":", "_")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            output = str(output_dir / f"{domain}_{timestamp}.md")
        elif verbose:
            click.echo(f"Warning: Output dir not found: {config.output_dir}")

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
        if output:
            click.echo(f"Output: {output}")
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


def _check_chromium_installed() -> bool:
    """Check if Playwright Chromium is installed."""
    import sys
    from pathlib import Path

    # Check common Playwright cache locations
    if sys.platform == "darwin":
        cache_dir = Path.home() / "Library/Caches/ms-playwright"
    else:
        cache_dir = Path.home() / ".cache/ms-playwright"

    if not cache_dir.exists():
        return False

    # Look for chromium directory
    chromium_dirs = list(cache_dir.glob("chromium-*"))
    return len(chromium_dirs) > 0


def _install_chromium() -> bool:
    """Install Playwright Chromium. Returns True on success."""
    import shutil
    import subprocess
    import sys

    # Find playwright executable
    playwright_cmd = shutil.which("playwright")

    # If not in PATH, try the pipx venv location
    if not playwright_cmd:
        pipx_playwright = Path.home() / ".local/pipx/venvs/saa/bin/playwright"
        if pipx_playwright.exists():
            playwright_cmd = str(pipx_playwright)

    if not playwright_cmd:
        return False

    result = subprocess.run([playwright_cmd, "install", "chromium"])
    return result.returncode == 0


def _check_api_keys(keys_file: Path) -> dict:
    """Check which API keys are configured. Returns dict of provider: bool."""
    keys = {"xai": False, "anthropic": False}
    if not keys_file.exists():
        return keys

    content = keys_file.read_text()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        if line.startswith("XAI_API_KEY=") and len(line.split("=", 1)[1]) > 5:
            keys["xai"] = True
        if line.startswith("ANTHROPIC_API_KEY=") and len(line.split("=", 1)[1]) > 5:
            keys["anthropic"] = True
    return keys


def _get_bundled_plan() -> str:
    """Get the bundled default audit plan content."""
    import importlib.resources as pkg_resources
    try:
        # Python 3.11+
        plan_source = pkg_resources.files("saa.data").joinpath("default-audit-plan.md")
        return plan_source.read_text()
    except (TypeError, AttributeError):
        # Fallback for older Python
        with pkg_resources.open_text("saa.data", "default-audit-plan.md") as f:
            return f.read()


def _get_saa_dir(system: bool) -> Path:
    """Get the SAA config directory path."""
    if system:
        return Path("/etc/saa")
    return Path.home() / ".saa"


def _archive_plan(saa_dir: Path, plan_file: Path) -> Path | None:
    """Archive existing plan to plans/ directory. Returns archive path."""
    from datetime import datetime

    if not plan_file.exists():
        return None

    plans_dir = saa_dir / "plans"
    plans_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = plans_dir / f"audit-plan_{timestamp}.md"
    archive_path.write_text(plan_file.read_text())
    return archive_path


def _plan_needs_update(saa_dir: Path) -> bool:
    """Check if installed plan differs from bundled plan."""
    plan_file = saa_dir / "audit-plan.md"
    if not plan_file.exists():
        return True

    try:
        bundled = _get_bundled_plan()
        installed = plan_file.read_text()
        return bundled.strip() != installed.strip()
    except Exception:
        return False


@main.command()
@click.option("--system", is_flag=True, help="Initialize system-wide config at /etc/saa/ (requires sudo)")
@click.option("--update-plan", is_flag=True, help="Update audit plan to latest version (archives old)")
def init(system: bool, update_plan: bool):
    """Initialize SAA and check dependencies.

    Checks Playwright/Chromium, creates config files, validates setup.

    \b
    Config loading priority (later overrides earlier):
      1. /etc/saa/    - System-wide (admin-managed, for multi-user servers)
      2. ~/.saa/      - User config (single-user or user overrides)
      3. ./.env       - Project-specific overrides

    \b
    Examples:
      saa init                    # Create ~/.saa/ for current user
      sudo saa init --system      # Create /etc/saa/ for all users
      saa init --update-plan      # Update audit plan, archive old version
    """
    import os

    # Handle --update-plan separately (quick path)
    if update_plan:
        saa_dir = _get_saa_dir(system)
        if system and os.geteuid() != 0:
            click.echo("Error: --system requires root.", err=True)
            raise SystemExit(1)

        plan_file = saa_dir / "audit-plan.md"
        if not saa_dir.exists():
            click.echo(f"Error: Config directory not found: {saa_dir}", err=True)
            click.echo("Run 'saa init' first.")
            raise SystemExit(1)

        try:
            # Archive existing plan
            if plan_file.exists():
                archive_path = _archive_plan(saa_dir, plan_file)
                click.echo(f"Archived: {archive_path}")

            # Install new plan
            plan_content = _get_bundled_plan()
            plan_file.write_text(plan_content)
            click.echo(f"Updated:  {plan_file}")
            click.echo("\nTo rollback: saa plan --rollback")
        except Exception as e:
            click.echo(f"Error updating plan: {e}", err=True)
            raise SystemExit(1)
        return

    click.echo("SAA Setup\n")

    # 1. Check Chromium
    click.echo("Checking dependencies...")
    chromium_ok = _check_chromium_installed()
    if chromium_ok:
        click.echo("  [ok] Playwright Chromium installed")
    else:
        click.echo("  [!!] Playwright Chromium not found")
        if click.confirm("       Install Chromium now?", default=True):
            click.echo("       Installing Chromium (this may take a minute)...")
            if _install_chromium():
                click.echo("       [ok] Chromium installed")
                chromium_ok = True
            else:
                click.echo("       [!!] Installation failed. Try manually:")
                click.echo("            playwright install chromium")
        else:
            click.echo("       Skipped. Install later with: playwright install chromium")

    click.echo("")

    # 2. Setup config directory
    if system:
        saa_dir = Path("/etc/saa")
        if os.geteuid() != 0:
            click.echo("Error: --system requires root. Use: sudo saa init --system", err=True)
            raise SystemExit(1)
    else:
        saa_dir = Path.home() / ".saa"

    click.echo(f"Config directory: {saa_dir}")
    saa_dir.mkdir(exist_ok=True)

    # Copy default audit plan from package
    plan_file = saa_dir / "audit-plan.md"
    if not plan_file.exists():
        try:
            plan_content = _get_bundled_plan()
            plan_file.write_text(plan_content)
            click.echo(f"  [ok] Created {plan_file}")
        except Exception as e:
            click.echo(f"  [!!] Could not copy default audit plan: {e}")
    else:
        # Check if update available
        if _plan_needs_update(saa_dir):
            click.echo(f"  [ok] Exists  {plan_file}")
            click.echo(f"       [!!] Newer plan available: saa init --update-plan")
        else:
            click.echo(f"  [ok] Exists  {plan_file}")

    env_file = saa_dir / ".env"
    if not env_file.exists():
        env_file.write_text(
            "# SAA Configuration\n"
            "# Uncomment and edit the settings you want to change.\n"
            "#\n"
            "# Chromium: Playwright auto-detects, only set to override\n"
            "# SAA_CHROMIUM_PATH=/path/to/chromium\n"
            "#\n"
            "# Default LLM provider:model (xai:grok, anthropic:sonnet, anthropic:opus)\n"
            "# SAA_DEFAULT_LLM=xai:grok\n"
            "#\n"
            "# Crawl limits\n"
            "# SAA_MAX_PAGES=50\n"
            "# SAA_DEFAULT_DEPTH=3\n"
            "#\n"
            f"# Default audit plan (created above)\n"
            f"SAA_DEFAULT_PLAN={plan_file}\n"
            "#\n"
            "# Output directory for reports (auto-generates filename)\n"
            "# If not set, prints to stdout\n"
            "# SAA_OUTPUT_DIR=/var/saa/reports\n"
        )
        click.echo(f"  [ok] Created {env_file}")
    else:
        click.echo(f"  [ok] Exists  {env_file}")

    keys_file = saa_dir / ".keys"
    keys_created = False
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
            os.chmod(keys_file, 0o640)
        else:
            os.chmod(keys_file, 0o600)
        click.echo(f"  [ok] Created {keys_file}")
        keys_created = True
    else:
        click.echo(f"  [ok] Exists  {keys_file}")

    # 3. Check API keys
    click.echo("")
    click.echo("API keys:")
    api_keys = _check_api_keys(keys_file)
    any_key = False
    if api_keys["xai"]:
        click.echo("  [ok] xAI (Grok) configured")
        any_key = True
    if api_keys["anthropic"]:
        click.echo("  [ok] Anthropic (Claude) configured")
        any_key = True
    if not any_key:
        click.echo("  [!!] No API keys configured")
        click.echo(f"       Edit {keys_file} to add your key(s)")

    # 4. Summary
    click.echo("")
    click.echo("=" * 40)
    all_ok = chromium_ok and any_key
    if all_ok:
        click.echo("Ready! Run: saa audit https://example.com")
    else:
        click.echo("Setup incomplete:")
        if not chromium_ok:
            click.echo("  - Install Chromium: playwright install chromium")
        if not any_key:
            click.echo(f"  - Add API key(s) to {keys_file}")

    # 5. Multi-user instructions for --system
    if system:
        click.echo("")
        click.echo("For multi-user access, set group permissions:")
        click.echo("")
        click.echo("  Linux (Ubuntu/Debian):")
        click.echo("    sudo groupadd saa-users")
        click.echo("    sudo usermod -aG saa-users USERNAME")
        click.echo(f"    sudo chgrp saa-users {keys_file}")
        click.echo("")
        click.echo("  macOS:")
        click.echo("    sudo dseditgroup -o create saa-users")
        click.echo("    sudo dseditgroup -o edit -a USERNAME -t user saa-users")
        click.echo(f"    sudo chgrp saa-users {keys_file}")


@main.command()
def check():
    """Check if a newer version is available on GitHub.

    Fetches the latest version from GitHub and compares with installed.
    Uses SSH to access the private repository.
    """
    import shutil
    import subprocess
    import tempfile

    click.echo(f"Installed: {__version__}")

    # Check remote via git
    if not shutil.which("git"):
        click.echo("Cannot check remote: git not found")
        return

    click.echo("Checking GitHub...")
    try:
        # Shallow clone to temp dir to get remote version
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["git", "clone", "--depth=1", "--quiet",
                 "git@github.com:iXanadu/saa.git", tmpdir],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                click.echo("Could not reach GitHub (check SSH key)")
                return

            # Read version from cloned repo
            init_file = Path(tmpdir) / "src" / "saa" / "__init__.py"
            if not init_file.exists():
                click.echo("Could not find version in repo")
                return

            remote_version = None
            for line in init_file.read_text().splitlines():
                if line.startswith("__version__"):
                    remote_version = line.split("=")[1].strip().strip('"\'')
                    break

            if not remote_version:
                click.echo("Could not parse remote version")
                return

            click.echo(f"Latest:    {remote_version}")

            # Compare versions
            if remote_version == __version__:
                click.echo("\n[ok] Code is up to date!")
            else:
                click.echo(f"\n[!!] Update available: {__version__} -> {remote_version}")
                click.echo("     Run: saa update")

            # Check config and plan status
            user_dir = Path.home() / ".saa"
            system_dir = Path("/etc/saa")

            # Find which config location is in use (if any)
            active_dir = None
            if system_dir.exists():
                active_dir = system_dir
            elif user_dir.exists():
                active_dir = user_dir

            if not active_dir:
                click.echo("\n[!!] No config found")
                click.echo("     Run: saa init (user) or sudo saa init --system")
            else:
                plan_file = active_dir / "audit-plan.md"
                if not plan_file.exists():
                    click.echo(f"\n[!!] No audit plan in {active_dir}")
                    if active_dir == system_dir:
                        click.echo("     Run: sudo saa init --system --update-plan")
                    else:
                        click.echo("     Run: saa init --update-plan")
                else:
                    # Check if plan needs update
                    remote_plan = Path(tmpdir) / "src" / "saa" / "data" / "default-audit-plan.md"
                    if remote_plan.exists():
                        if remote_plan.read_text().strip() != plan_file.read_text().strip():
                            click.echo(f"\n[!!] New audit plan available for {active_dir}")
                            if active_dir == system_dir:
                                click.echo("     Run: sudo saa init --system --update-plan")
                            else:
                                click.echo("     Run: saa init --update-plan")
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


@main.command()
@click.option("--system", is_flag=True, help="Use system config at /etc/saa/")
@click.option("--list", "list_plans", is_flag=True, help="List archived plans")
@click.option("--rollback", is_flag=True, help="Rollback to previous plan version")
@click.option("--show", is_flag=True, help="Show current plan path")
def plan(system: bool, list_plans: bool, rollback: bool, show: bool):
    """Manage audit plans.

    \b
    Examples:
      saa plan --show              # Show current plan location
      saa plan --list              # List archived plan versions
      saa plan --rollback          # Restore previous plan version
    """
    import os

    saa_dir = _get_saa_dir(system)
    if system and os.geteuid() != 0:
        click.echo("Error: --system requires root.", err=True)
        raise SystemExit(1)

    plan_file = saa_dir / "audit-plan.md"
    plans_dir = saa_dir / "plans"

    if show or (not list_plans and not rollback):
        # Default: show current plan info
        if plan_file.exists():
            click.echo(f"Current plan: {plan_file}")
            if _plan_needs_update(saa_dir):
                click.echo("[!!] Newer version available: saa init --update-plan")
        else:
            click.echo("No plan configured. Run: saa init")
        return

    if list_plans:
        if not plans_dir.exists() or not list(plans_dir.glob("*.md")):
            click.echo("No archived plans found.")
            return

        click.echo(f"Archived plans in {plans_dir}:\n")
        archives = sorted(plans_dir.glob("*.md"), reverse=True)
        for i, archive in enumerate(archives):
            click.echo(f"  {i+1}. {archive.name}")
        click.echo(f"\nTo rollback: saa plan --rollback")
        return

    if rollback:
        if not plans_dir.exists():
            click.echo("No archived plans to rollback to.")
            raise SystemExit(1)

        archives = sorted(plans_dir.glob("*.md"), reverse=True)
        if not archives:
            click.echo("No archived plans to rollback to.")
            raise SystemExit(1)

        # Get most recent archive
        latest_archive = archives[0]
        click.echo(f"Rolling back to: {latest_archive.name}")

        # Archive current plan first (so we can undo the rollback)
        if plan_file.exists():
            archive_path = _archive_plan(saa_dir, plan_file)
            click.echo(f"Archived current: {archive_path.name}")

        # Restore from archive
        plan_file.write_text(latest_archive.read_text())
        click.echo(f"Restored: {plan_file}")

        # Remove the archive we just restored from
        latest_archive.unlink()
        click.echo("Done. Run 'saa plan --list' to see remaining archives.")


if __name__ == "__main__":
    main()
