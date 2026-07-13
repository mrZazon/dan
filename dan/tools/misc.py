from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class RandomPasswordTool(Tool):
    name = "random_password"
    description = "Generates a random password"
    aliases = ("password", "generate password")
    intents = {"generate password": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        length = kwargs.get("length", "16")
        result = await self._service.execute(f'python3 -c "import secrets, string; print(\'\'.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range({length})))"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class RandomNumberTool(Tool):
    name = "random_number"
    description = "Generates a random number"
    aliases = ("random", "random number")
    intents = {"random number": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        min_val = kwargs.get("min", "1")
        max_val = kwargs.get("max", "100")
        result = await self._service.execute(f'python3 -c "import random; print(random.randint({min_val}, {max_val}))"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class RandomChoiceTool(Tool):
    name = "random_choice"
    description = "Picks a random item from a comma-separated list"
    aliases = ("choice", "random choice")
    intents = {"random choice": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        items = kwargs.get("items", "")
        result = await self._service.execute(f'python3 -c "import random; items=\'{items}\'.split(\',\'); print(random.choice(items))"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class DiceRollTool(Tool):
    name = "dice_roll"
    description = "Rolls dice (e.g. 2d6)"
    aliases = ("dice", "roll dice")
    intents = {"roll dice": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        dice = kwargs.get("dice", "1d6")
        result = await self._service.execute(f'python3 -c "import random; n,s=\'{dice}\'.split(\'d\'); print(sum(random.randint(1,int(s)) for _ in range(int(n))))"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class CoinFlipTool(Tool):
    name = "coin_flip"
    description = "Flips a coin"
    aliases = ("flip", "flip coin")
    intents = {"flip coin": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('python3 -c "import random; print(random.choice([\'Heads\', \'Tails\']))"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class TimerTool(Tool):
    name = "timer"
    description = "Sets a timer for a number of seconds"
    aliases = ("set timer", "timer")
    intents = {"set timer": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        seconds = kwargs.get("seconds", "60")
        result = await self._service.execute(f'echo "Timer set for {seconds} seconds" && sleep {seconds} && echo "Time\'s up!" && notify-send "Timer" "Time\'s up!" 2>/dev/null')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class StopwatchTool(Tool):
    name = "stopwatch"
    description = "Starts a stopwatch"
    aliases = ("stopwatch", "start stopwatch")
    intents = {"start stopwatch": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute('echo "Stopwatch started. Press Ctrl+C to stop." && date +%s > /tmp/dan_sw_start && read')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class ColorCodeTool(Tool):
    name = "color_code"
    description = "Shows a color code"
    aliases = ("color code", "ansi color")
    intents = {"color code": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        name = kwargs.get("name", "red")
        result = await self._service.execute(f'python3 -c "colors={{\'red\':\'\\033[91m\',\'green\':\'\\033[92m\',\'yellow\':\'\\033[93m\',\'blue\':\'\\033[94m\',\'purple\':\'\\033[95m\',\'cyan\':\'\\033[96m\',\'white\':\'\\033[97m\',\'reset\':\'\\033[0m\'}}; print(f\'{{colors.get(\"{name}\",\"\")}}{name}{{colors[\"reset\"]}}\')"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class QRCodeTool(Tool):
    name = "qr_code"
    description = "Generates a QR code"
    aliases = ("qr", "qr code")
    intents = {"qr code": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f'python3 -c "import qrcode; qr=qrcode.make(\'{text}\'); qr.save(\'/tmp/qr.png\'); print(\'QR saved to /tmp/qr.png\')" 2>/dev/null || echo "qrcode not installed"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class MorseEncodeTool(Tool):
    name = "morse_encode"
    description = "Encodes text to Morse code"
    aliases = ("morse", "morse code")
    intents = {"morse code": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        result = await self._service.execute(f"python3 -c \"morse={{'a':'.-','b':'-...','c':'-.-.','d':'-..','e':'.','f':'..-.','g':'--.','h':'....','i':'..','j':'.---','k':'-.-','l':'.-..','m':'--','n':'-.','o':'---','p':'.--.','q':'--.-','r':'.-.','s':'...','t':'-','u':'..-','v':'...-','w':'.--','x':'-..-','y':'-.--','z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',' ':'/'}}; print(' '.join(morse.get(c,c) for c in '{text}'.lower()))\"")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class AsciiArtTool(Tool):
    name = "ascii_art"
    description = "Shows ASCII art text"
    aliases = ("figlet", "ascii art")
    intents = {"ascii art": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "DAN")
        result = await self._service.execute(f'echo "{text}" | figlet 2>/dev/null || echo "{text}"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class ColorPrintTool(Tool):
    name = "color_print"
    description = "Prints colored text"
    aliases = ("colored", "color print")
    intents = {"color print": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        color = kwargs.get("color", "white")
        result = await self._service.execute(f'python3 -c "colors={{\'red\':\'\\033[91m\',\'green\':\'\\033[92m\',\'yellow\':\'\\033[93m\',\'blue\':\'\\033[94m\',\'purple\':\'\\033[95m\',\'cyan\':\'\\033[96m\',\'white\':\'\\033[97m\'}}; print(f\'{{colors.get(\"{color}\",\"\")}}{text}\\033[0m\')"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class ProgressBarTool(Tool):
    name = "progress_bar"
    description = "Shows a progress bar"
    aliases = ("progress", "progress bar")
    intents = {"progress bar": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        percent = kwargs.get("percent", "50")
        result = await self._service.execute(f'python3 -c "p=int({percent}); filled=\'█\'*int(p/2); empty=\'░\'*(50-int(p/2)); print(f\'[{{filled}}{{empty}}] {{p}}%\')"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class TablePrintTool(Tool):
    name = "table_print"
    description = "Prints a formatted table"
    aliases = ("table", "print table")
    intents = {"print table": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        data = kwargs.get("data", "")
        result = await self._service.execute(f'python3 -c "rows=\'{data}\'.split(\'|\'); widths=[max(len(cell) for cell in row.split(\',\')) for row in rows]; [print(\'  \'.join(cell.strip().ljust(w) for cell,w in zip(row.split(\',\'),widths))) for row in rows]"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class SpinnerTool(Tool):
    name = "spinner"
    description = "Shows a spinner animation"
    aliases = ("loading", "spinner")
    intents = {"spinner": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "Loading")
        result = await self._service.execute(f"python3 -c \"import itertools,sys,time; [print(f'\\r{text} {{c}}',end='',flush=True) or time.sleep(0.1) for c in itertools.cycle('|/-\\\\\\\\') for _ in range(30)]\" && echo")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})
