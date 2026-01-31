import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    stealth = Stealth()  # Default config; can customize later (e.g., Stealth(navigator_webdriver=True))
    async with async_playwright() as p:
        # Replace with your exact path
        browser = await p.chromium.launch(headless=True, executable_path='/Applications/Chromium.app/Contents/MacOS/Chromium')
        context = await browser.new_context()
        await stealth.apply_stealth_async(context)  # Apply stealth to the context
        page = await context.new_page()
        await page.goto('https://example.com')
        print(await page.title())
        await browser.close()

asyncio.run(main())
