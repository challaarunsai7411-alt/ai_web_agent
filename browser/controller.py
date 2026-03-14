import asyncio
from playwright.async_api import async_playwright, Page, Browser

class BrowserController:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    async def start(self) -> Page:
        """Launches the browser and opens a new page."""
        self.playwright = await async_playwright().start()
        # Run in visible mode for development
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        return self.page

    async def navigate(self, url: str):
        """Navigates to a specific URL."""
        if not self.page:
            raise Exception("Browser is not started. Call start() first.")
        await self.page.goto(url, wait_until="domcontentloaded")
        # Give dynamic content a brief moment to load
        await self.page.wait_for_timeout(2000)

    async def close(self):
        """Cleans up browser resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()