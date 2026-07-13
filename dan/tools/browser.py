from __future__ import annotations

import logging
from typing import Any

from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool

logger = logging.getLogger(__name__)

# Module-level singleton — lazily initialized on first use
_browser_service = None


def _get_browser():
    global _browser_service
    if _browser_service is None:
        from dan.services.browser import BrowserService
        _browser_service = BrowserService()
    return _browser_service


async def _ensure_browser():
    svc = _get_browser()
    if not await svc.health_check():
        await svc.initialize()
    return svc


@tool
class BrowserNavigateTool(Tool):
    name = "browser_navigate"
    description = "Opens a URL in the browser and returns the page title"
    aliases = ("open url in browser", "go to website", "browse to")
    intents = {
        "open in browser": 5,
        "browse to": 5,
        "go to website": 5,
        "visit website": 5,
        "open website": 4,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", kwargs.get("message", ""))
        if not url:
            return ToolResult(success=False, message="No URL provided.")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            svc = await _ensure_browser()
            info = await svc.navigate(url)
            return ToolResult(
                success=True,
                message=f"Opened: {info['title']}\nURL: {info['url']}",
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to navigate: {e}")


@tool
class BrowserReadTool(Tool):
    name = "browser_read"
    description = "Reads the text content of the current browser page"
    aliases = ("read page", "read website content", "get page text")
    intents = {
        "read page": 5,
        "read website": 5,
        "get page content": 5,
        "page text": 5,
        "what does the page say": 4,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        try:
            svc = await _ensure_browser()
            text = await svc.get_content()
            if not text.strip():
                return ToolResult(success=True, message="Page returned empty content.")
            title = await svc.page.title()
            return ToolResult(
                success=True,
                message=f"Content from {title}:\n\n{text}",
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to read page: {e}")


@tool
class BrowserClickTool(Tool):
    name = "browser_click"
    description = "Clicks an element on the current browser page by CSS selector"
    aliases = ("click element", "press button", "click button")
    intents = {
        "click": 5,
        "press button": 5,
        "click button": 5,
        "click link": 4,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        selector = kwargs.get("selector", "")
        if not selector:
            return ToolResult(success=False, message="No CSS selector provided.")
        try:
            svc = await _ensure_browser()
            await svc.click(selector)
            return ToolResult(success=True, message=f"Clicked: {selector}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to click: {e}")


@tool
class BrowserTypeTool(Tool):
    name = "browser_type"
    description = "Types text into a form field and optionally submits it"
    aliases = ("type in field", "fill form", "enter text")
    intents = {
        "type in": 5,
        "fill form": 5,
        "enter text": 5,
        "type into": 5,
        "fill field": 5,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        selector = kwargs.get("selector", 'input[type="search"], input[name="q"], input[type="text"]')
        text = kwargs.get("text", kwargs.get("message", ""))
        press_enter = kwargs.get("press_enter", True)

        if not text:
            return ToolResult(success=False, message="No text to type provided.")

        try:
            svc = await _ensure_browser()
            await svc.type_text(selector, text, press_enter=press_enter)
            return ToolResult(success=True, message=f"Typed: {text}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to type: {e}")


@tool
class BrowserScreenshotTool(Tool):
    name = "browser_screenshot"
    description = "Takes a screenshot of the current browser page"
    aliases = ("screenshot", "capture page", "take screenshot")
    intents = {
        "screenshot": 5,
        "capture page": 5,
        "take screenshot": 5,
        "what does it look like": 3,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        name = kwargs.get("name", "page")
        try:
            svc = await _ensure_browser()
            path = await svc.screenshot(name)
            return ToolResult(success=True, message=f"Screenshot saved: {path}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to screenshot: {e}")


@tool
class BrowserSearchTool(Tool):
    name = "browser_search"
    description = "Searches the web using a real browser (renders JavaScript)"
    aliases = ("search with browser", "real search", "google it")
    intents = {
        "search with browser": 5,
        "real search": 5,
        "google it": 5,
        "browser search": 5,
    }

    def __init__(self) -> None:
        self._engine_url = "https://duckduckgo.com"

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query", kwargs.get("message", ""))
        engine = kwargs.get("engine", self._engine_url)

        if not query:
            return ToolResult(success=False, message="No search query provided.")

        try:
            svc = await _ensure_browser()
            info = await svc.search(engine, query)
            if "error" in info:
                return ToolResult(success=False, message=info["error"])

            # Read the results page
            text = await svc.get_content()
            return ToolResult(
                success=True,
                message=f"Search results for: {query}\nURL: {info['url']}\n\n{text}",
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Search failed: {e}")


@tool
class BrowserCloseTool(Tool):
    name = "browser_close"
    description = "Closes the browser"
    aliases = ("close browser", "quit browser", "shut browser")
    intents = {
        "close browser": 5,
        "quit browser": 5,
        "shut browser": 5,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        global _browser_service
        if _browser_service:
            await _browser_service.shutdown()
            _browser_service = None
            return ToolResult(success=True, message="Browser closed.")
        return ToolResult(success=True, message="No browser was open.")
