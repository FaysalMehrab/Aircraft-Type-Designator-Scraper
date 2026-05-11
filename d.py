import asyncio
from playwright.async_api import async_playwright

DEBUGGING_PORT = "http://localhost:9222"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(DEBUGGING_PORT)
        page = browser.contexts[0].pages[0]

        # Check if table exists directly on page
        direct = await page.query_selector("#atd-table")
        print(f"Table directly on page: {direct}")

        # Check for iframes
        frames = page.frames
        print(f"\nTotal frames found: {len(frames)}")
        for i, frame in enumerate(frames):
            print(f"  Frame {i} | URL: {frame.url}")
            table = await frame.query_selector("#atd-table")
            if table:
                print(f"  >>> TABLE FOUND in Frame {i}")

        await browser.close()

asyncio.run(main())