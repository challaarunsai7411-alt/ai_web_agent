from playwright.async_api import Page
from typing import Dict, Any

class AccessibilityParser:
    @staticmethod
    async def extract_tree(page: Page) -> Dict[str, Any]:
        """
        Extracts the full accessibility tree from the current page.
        Playwright's accessibility snapshot translates the DOM into 
        the accessibility layer exposed to screen readers.
        """
        try:
            # Capture the accessibility snapshot
            snapshot = await page.accessibility.snapshot()
            return snapshot if snapshot else {}
        except Exception as e:
            print(f"Error extracting accessibility tree: {e}")
            return {}