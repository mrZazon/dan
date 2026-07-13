from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class OpenAppTool(Tool):
    name = "open_app"
    description = "Opens an application by name"
    aliases = ("launch app", "start app", "run app")
    intents = {"open application": 5, "open app": 5, "launch app": 4, "start application": 4, "run app": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        name = kwargs.get("name", "").strip()
        if not name:
            msg = kwargs.get("message", "")
            import re
            m = re.search(r"(?:open|launch|start|run)\s+(.+)", msg, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
        if not name:
            return ToolResult(success=False, message="No application name provided")
        result = await self._service.execute(f"{name} &")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class CloseAppTool(Tool):
    name = "close_app"
    description = "Closes an application by name"
    aliases = ("stop app", "quit app")
    intents = {"close application": 5, "close app": 5, "stop app": 4, "quit application": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        name = kwargs.get("name", "").strip()
        if not name:
            msg = kwargs.get("message", "")
            import re
            m = re.search(r"(?:close|stop|quit|kill)\s+(.+)", msg, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
        if not name:
            return ToolResult(success=False, message="No application name provided")
        result = await self._service.execute(f"pkill {name}")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ListRunningAppsTool(Tool):
    name = "running_apps"
    description = "Lists currently running GUI applications"
    aliases = ("open apps", "active windows", "gui apps")
    intents = {"list running apps": 5, "running apps": 5, "open apps": 4, "active windows": 4, "gui apps": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute(
            "wmctrl -l 2>/dev/null || xdotool search --name \"\" 2>/dev/null | head -20 || echo \"No window manager tools available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ScreenshotTool(Tool):
    name = "screenshot"
    description = "Takes a screenshot"
    aliases = ("capture screen", "screen capture")
    intents = {"screenshot": 5, "take screenshot": 5, "capture screen": 4, "screen capture": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", "/tmp/screenshot.png")
        result = await self._service.execute(
            f"scrot {path} 2>/dev/null || import -window root {path} 2>/dev/null || echo \"No screenshot tool available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ClipboardCopyTool(Tool):
    name = "clipboard_copy"
    description = "Copies text to the clipboard"
    aliases = ("copy text", "clipboard set")
    intents = {"copy to clipboard": 5, "clipboard copy": 5, "copy text": 4, "clipboard set": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(
            f"echo -n \"{text}\" | xclip -selection clipboard 2>/dev/null || echo \"{text}\" | xsel --clipboard 2>/dev/null || echo \"No clipboard tool available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ClipboardPasteTool(Tool):
    name = "clipboard_paste"
    description = "Pastes text from the clipboard"
    aliases = ("paste text", "clipboard get")
    intents = {"paste from clipboard": 5, "clipboard paste": 5, "paste text": 4, "clipboard get": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute(
            "xclip -selection clipboard -o 2>/dev/null || xsel --clipboard 2>/dev/null || echo \"No clipboard tool available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class VolumeGetTool(Tool):
    name = "volume_get"
    description = "Gets the current volume level"
    aliases = ("current volume", "volume level")
    intents = {"get volume": 5, "volume level": 4, "current volume": 4, "show volume": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute(
            "pactl get-sink-volume @DEFAULT_SINK@ 2>/dev/null || amixer get Master 2>/dev/null || echo \"No audio tool available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class VolumeSetTool(Tool):
    name = "volume_set"
    description = "Sets the volume to a specific level"
    aliases = ("set volume", "adjust volume")
    intents = {"set volume": 5, "change volume": 4, "adjust volume": 4, "volume set": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        level = kwargs.get("level", "50")
        result = await self._service.execute(
            f"pactl set-sink-volume @DEFAULT_SINK@ {level}% 2>/dev/null || amixer set Master {level}% 2>/dev/null || echo \"No audio tool available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class MuteToggleTool(Tool):
    name = "mute_toggle"
    description = "Toggles mute on/off"
    aliases = ("mute", "unmute", "toggle mute")
    intents = {"mute": 5, "unmute": 5, "toggle mute": 5, "mute toggle": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute(
            "pactl set-sink-mute @DEFAULT_SINK@ toggle 2>/dev/null || amixer set Master toggle 2>/dev/null || echo \"No audio tool available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class BrightnessGetTool(Tool):
    name = "brightness_get"
    description = "Gets the current screen brightness"
    aliases = ("current brightness", "brightness level")
    intents = {"get brightness": 5, "brightness level": 4, "current brightness": 4, "show brightness": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute(
            "cat /sys/class/backlight/*/brightness 2>/dev/null || echo \"No brightness control available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class BrightnessSetTool(Tool):
    name = "brightness_set"
    description = "Sets the screen brightness"
    aliases = ("set brightness", "adjust brightness")
    intents = {"set brightness": 5, "change brightness": 4, "adjust brightness": 4, "brightness set": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        level = kwargs.get("level", "50")
        result = await self._service.execute(
            f"echo {level} | sudo tee /sys/class/backlight/*/brightness 2>/dev/null || echo \"No brightness control available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class NotifyTool(Tool):
    name = "notify"
    description = "Sends a desktop notification"
    aliases = ("notification", "alert", "notify-send")
    intents = {"send notification": 5, "notify": 5, "send alert": 4, "desktop notification": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        title = kwargs.get("title", "DAN")
        message = kwargs.get("message", "")
        result = await self._service.execute(
            f"notify-send \"{title}\" \"{message}\" 2>/dev/null || echo \"No notification tool available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class LockScreenTool(Tool):
    name = "lock_screen"
    description = "Locks the screen"
    aliases = ("lock", "screen lock")
    intents = {"lock screen": 5, "screen lock": 4, "lock the screen": 4}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute(
            "qdbus org.kde.screensaver /ScreenSaver Lock 2>/dev/null || xset dpms force off 2>/dev/null || echo \"No lock screen tool available\""
        )
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class ListWindowsTool(Tool):
    name = "list_windows"
    description = "Lists all open windows"
    aliases = ("open windows", "window list")
    intents = {"list windows": 5, "open windows": 4, "window list": 4, "show windows": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("wmctrl -l 2>/dev/null || echo \"wmctrl not available\"")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )


@tool
class FocusWindowTool(Tool):
    name = "focus_window"
    description = "Focuses a window by title"
    aliases = ("switch window", "activate window")
    intents = {"focus window": 5, "switch window": 4, "activate window": 4, "bring window to front": 3}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        title = kwargs.get("title", "")
        result = await self._service.execute(f"wmctrl -a \"{title}\" 2>/dev/null || echo \"wmctrl not available\"")
        return ToolResult(
            success=result.success,
            message=result.stdout or result.stderr,
            data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
        )
