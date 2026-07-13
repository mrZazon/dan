from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from dan.services.base import Service
from dan.core.config import DEFAULT_DATA_DIR

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = DEFAULT_DATA_DIR / "screenshots"


class BrowserService(Service):
    """Manages a headless Chromium browser via Playwright.

    Provides page navigation, content extraction, interaction, and screenshots.
    A single browser instance persists across tool calls.
    """

    name = "browser"

    def __init__(self) -> None:
        self._playwright: Any = None
        self._browser: Any = None
        self._page: Any = None

    async def initialize(self) -> None:
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._page = await self._browser.new_page(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug("Browser initialized")

    async def shutdown(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.debug("Browser shut down")

    async def health_check(self) -> bool:
        return self._page is not None and not self._page.is_closed()

    @property
    def page(self) -> Any:
        if not self._page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        return self._page

    async def navigate(self, url: str) -> dict[str, Any]:
        """Navigate to a URL. Returns page title and URL."""
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return {
            "title": await self.page.title(),
            "url": self.page.url,
        }

    async def get_content(self, max_chars: int = 8000) -> str:
        """Extract readable text content from the current page."""
        text = await self.page.evaluate("""
            () => {
                const elements = document.querySelectorAll(
                    'article, main, [role="main"], .content, .post, .entry, .article-body, .story-body'
                );
                if (elements.length > 0) {
                    return Array.from(elements).map(e => e.innerText).join('\\n\\n');
                }
                return document.body.innerText || '';
            }
        """)
        text = text.strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "\n... (truncated)"
        return text

    async def get_links(self, max_links: int = 20) -> list[dict[str, str]]:
        """Extract all links from the current page."""
        links = await self.page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.innerText.trim().slice(0, 100),
                href: a.href
            })).filter(l => l.text && l.href.startsWith('http'))
        """)
        return links[:max_links]

    async def click(self, selector: str) -> None:
        """Click an element by CSS selector."""
        await self.page.click(selector, timeout=10000)

    async def type_text(self, selector: str, text: str, press_enter: bool = True) -> None:
        """Type text into an input field."""
        await self.page.fill(selector, text, timeout=10000)
        if press_enter:
            await self.page.press(selector, "Enter")
            await self.page.wait_for_load_state("domcontentloaded", timeout=15000)

    async def screenshot(self, name: str = "page") -> str:
        """Take a screenshot. Returns the file path."""
        path = SCREENSHOT_DIR / f"{name}.png"
        await self.page.screenshot(path=str(path), full_page=False)
        return str(path)

    async def search(self, engine_url: str, query: str) -> dict[str, Any]:
        """Navigate to a search engine and search."""
        await self.navigate(engine_url)

        # Auto-dismiss cookie consent dialogs
        for consent_selector in [
            'button:has-text("Reject all")',
            'button:has-text("Rechazar todo")',
            'button:has-text("Accept all")',
            'button:has-text("Aceptar todo")',
            'button:has-text("I agree")',
            '#L2AGLb',  # Google "Accept all" button
            '[aria-label="Reject all"]',
            '[aria-label="Accept all"]',
        ]:
            try:
                btn = self.page.locator(consent_selector).first
                if await btn.is_visible(timeout=1500):
                    await btn.click()
                    await self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                    break
            except Exception:
                continue

        # Try common search input selectors
        for selector in [
            'input[name="q"]',
            'input[name="search"]',
            'input[type="search"]',
            'input#search',
            'textarea[name="q"]',
            '#searchform input',
        ]:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                await self.page.fill(selector, query)
                await self.page.press(selector, "Enter")
                await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                return {
                    "title": await self.page.title(),
                    "url": self.page.url,
                }
            except Exception:
                continue
        return {"error": "Could not find search input on this page"}
