# Manual Installation Instructions

These steps assume macOS (your setup) with Homebrew. Your existing ungoogled-chromium Mac app won't conflict— we'll use its binary path directly, avoiding new installs. If issues (e.g., version mismatch), fallback to Playwright's standard Chromium.

1. **Prerequisites**:
   - Install Homebrew if missing: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
   - Install Python 3.12: `brew install python@3.12`.
   - Locate your ungoogled-chromium binary: Usually `/Applications/Chromium.app/Contents/MacOS/Chromium` (or search Spotlight for "Chromium" > Show Package Contents).

2. **Virtual Environment**:
   - `mkdir ~/saa && cd ~/saa`.
   - `python3.12 -m venv env && source env/bin/activate`.
   - `pip install click playwright playwright-stealth beautifulsoup4 lxml requests python-dotenv pydantic pyyaml`.

3. **Playwright Setup**:
   - Skip browser download: We'll use your existing binary.
   - Test: Create test.py with:
     ```python
     import asyncio
     from playwright.async_api import async_playwright
     from playwright_stealth import stealth_async

     async def main():
         async with async_playwright() as p:
             browser = await p.chromium.launch(headless=True, executable_path='/Applications/Chromium.app/Contents/MacOS/Chromium')  # Your path
             page = await browser.new_page()
             await stealth_async(page)
             await page.goto('https://example.com')
             print(await page.title())
             await browser.close()

     asyncio.run(main())
