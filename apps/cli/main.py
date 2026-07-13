"""D.A.N. CLI - Command Line Interface for D.A.N.

Usage:
    dan [--config CONFIG] [--verbose] COMMAND [ARGS...]

Commands:
    run         Run a single command
    interact    Start interactive mode
    tools       List available tools
    skills      List learned skills
    plugins     List loaded plugins
    config      Show current configuration
    version     Show version information
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.status import Status
from rich.theme import Theme

from dan.core.config import DANConfig
from dan.core.tool_registry import ToolRegistry
from dan.core.router import Router, Layer
from dan.core.safety import check_command_safety, get_tool_danger_level, DANGEROUS, CAUTION
from dan.memory.session import SessionMemory
from dan.plugins.registry import PluginRegistry
from dan.providers.ollama import OllamaProvider
from dan.providers.base import ProviderMessage
from dan.skills.registry import SkillRegistry

__version__ = "0.1.0"

DAN_THEME = Theme({
    "user": "bold cyan",
    "dan": "bold green",
    "info": "dim white",
    "tool": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "warning": "bold yellow",
})

console = Console(theme=DAN_THEME)
logger = logging.getLogger("dan")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="[dim]%(name)s[/dim] %(message)s",
        datefmt="%H:%M:%S",
    )
    if verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
    else:
        for name in ("httpx", "httpcore", "urllib3"):
            logging.getLogger(name).setLevel(logging.CRITICAL)


def cmd_run(args: argparse.Namespace, config: DANConfig) -> None:
    """Execute a single command."""
    registry = ToolRegistry()
    registry.discover()
    from dan.core.dispatcher import Dispatcher
    dispatcher = Dispatcher(registry=registry, threshold=config.core.threshold)
    result = dispatcher.dispatch(args.message)
    if result.match is None:
        console.print(f"[error]No match.[/error] {result.message}")
    else:
        tool = result.match.tool
        console.print(f"[tool]{tool.name}[/tool] (score: {result.confidence:.2f})")


def _confirm(prompt: str) -> bool:
    try:
        answer = input(f"[dan] {prompt} [y/N] ").strip().lower()
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def _extract_command_from_args(tool_name: str, args: dict) -> str | None:
    if tool_name == "command":
        return args.get("command", args.get("message", ""))
    if tool_name == "sudo":
        return f"sudo {args.get('command', '')}"
    if tool_name == "delete_file":
        return f"rm {args.get('path', '')}"
    if tool_name == "kill_process":
        return f"kill {args.get('pid', '')}"
    if tool_name == "kill_by_name":
        return f"pkill {args.get('name', '')}"
    return None


async def cmd_interact(args: argparse.Namespace, config: DANConfig) -> None:
    """Start interactive mode."""
    registry = ToolRegistry()
    registry.discover()

    # Show loading status during model initialization
    with Status("[bold green]Connecting to Ollama...", console=console, spinner="dots") as status:
        interpret = OllamaProvider()
        reason = OllamaProvider()
        persona = OllamaProvider()
        status.update("[bold green]Loading interpret model...")
        await interpret.load_model(config.interpret.model)
        status.update("[bold green]Loading reason model...")
        await reason.load_model(config.reason.model)
        status.update("[bold green]Loading persona model...")
        await persona.load_model(config.persona.model)

    skill_registry = SkillRegistry()
    session = SessionMemory()
    router = Router(
        registry=registry,
        skill_registry=skill_registry,
        interpret_provider=interpret,
        reason_provider=reason,
        persona_provider=persona,
        threshold=config.core.threshold,
        session=session,
    )

    # Header
    header = Text()
    header.append("D.A.N.", style="bold green")
    header.append(f" v{__version__}", style="dim")
    console.print(Panel(header, border_style="green", padding=(0, 1)))
    console.print(f"  [info]interpret[/info] {config.interpret.model}  "
                  f"[info]reason[/info] {config.reason.model}  "
                  f"[info]persona[/info] {config.persona.model}  "
                  f"[info]tools[/info] {len(registry)}")
    console.print()

    while True:
        try:
            message = input("\033[1;36myou>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[info]Goodbye![/info]")
            break

        if not message:
            continue
        if message.lower() in ("exit", "quit"):
            console.print("[info]Goodbye![/info]")
            break

        session.add_user(message)

        # Detect if this needs the agentic loop (multi-step questions)
        _AGENTIC_KEYWORDS = {
            "what should i", "plan my", "organize", "daily", "today",
            "what do i have", "what's on", "what am i doing", "my schedule",
            "what's my routine", "what do i usually", "good morning",
            "briefing", "start my day", "what's today",
        }
        use_agentic = any(kw in message.lower() for kw in _AGENTIC_KEYWORDS)

        try:
            if use_agentic:
                # Agentic loop — plan → execute → read → repeat
                with Status("[bold yellow]Thinking...", console=console, spinner="dots") as status:
                    steps_log = await router.route_agentic(message, max_steps=5)

                if steps_log:
                    # Show tool steps
                    for step in steps_log:
                        if step["type"] == "tool":
                            console.print(f"  [dim]→ {step['name']}[/dim]")
                    # Show final response
                    last = steps_log[-1]
                    if last["type"] == "response":
                        sys.stdout.write("\033[1;32mdan>\033[0m ")
                        sys.stdout.flush()
                        sys.stdout.write(last["text"])
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                        session.add_assistant(last["text"])

            else:
                # Single-shot routing
                with Status("[bold yellow]Thinking...", console=console, spinner="dots") as status:
                    route = await router.route(message)

                if route.tool_name:
                    steps = route.steps if route.steps else [{"tool": route.tool_name, "args": route.args}]

                    for i, step in enumerate(steps):
                        tool_name = step["tool"]
                        tool_args = step["args"]

                        # Safety check
                        danger = get_tool_danger_level(tool_name)
                        if danger in (DANGEROUS, CAUTION):
                            cmd_str = _extract_command_from_args(tool_name, tool_args)
                            desc = f"{danger.upper()}: {tool_name}"
                            if cmd_str:
                                desc += f" → {cmd_str}"
                            if not _confirm(f"[warning]{desc}. Execute?[/warning]"):
                                console.print("[info]Cancelled.[/info]")
                                break

                        if tool_name == "command":
                            cmd_str = tool_args.get("command", "")
                            verdict = check_command_safety(cmd_str)
                            if not verdict.safe:
                                if not _confirm(f"[error]DESTRUCTIVE:[/error] {verdict.reason} ({cmd_str}). Execute?"):
                                    console.print("[info]Cancelled.[/info]")
                                    break

                        with Status(f"[bold yellow]Running {tool_name}...", console=console, spinner="dots"):
                            tool_class = registry.get(tool_name)
                            tool_instance = tool_class()
                            tool_result = await tool_instance.execute(**tool_args)

                        console.print(f"\033[1;32mdan>\033[0m {tool_result.message}")
                        session.add_assistant(tool_result.message)

                elif route.skill_name:
                    console.print(f"[info]skill: {route.skill_name}[/info]")

                elif route.needs_stream:
                    # L3 persona handles conversation — stream from persona model
                    sys.stdout.write("\033[1;32mdan>\033[0m ")
                    sys.stdout.flush()
                    prompt = f"[CONVERSATION]\nUser: \"{message}\"\n[END]"
                    msgs = [ProviderMessage(role="user", content=prompt)]
                    response_parts: list[str] = []
                    try:
                        async for chunk in persona.stream(
                            msgs,
                            temperature=0.5,
                            max_tokens=256,
                        ):
                            sys.stdout.write(chunk)
                            sys.stdout.flush()
                            response_parts.append(chunk)
                    except Exception as stream_err:
                        logger.exception("Stream failed")
                        console.print(f"\n[error]Stream error:[/error] {stream_err}")
                    print()
                    full_response = "".join(response_parts)
                    if full_response.strip():
                        session.add_assistant(full_response.strip())

                elif route.raw_response:
                    console.print(f"\033[1;32mdan>\033[0m {route.raw_response}")
                    session.add_assistant(route.raw_response)

                else:
                    console.print("[info]No tool found for that request.[/info]")

        except Exception as e:
            logger.exception("Error processing message")
            console.print(f"[error]Error:[/error] {e}")


def cmd_tools(args: argparse.Namespace, config: DANConfig) -> None:
    """List available tools."""
    registry = ToolRegistry()
    registry.discover()
    tools = registry.tools()
    if not tools:
        console.print("[info]No tools registered.[/info]")
        return
    console.print(f"[tool]Tools[/tool] ({len(tools)})")
    for tool in tools:
        console.print(f"  [yellow]●[/yellow] [tool]{tool.name}[/tool]: {tool.description}")


def cmd_skills(args: argparse.Namespace, config: DANConfig) -> None:
    """List learned skills."""
    skill_registry = SkillRegistry()
    skills = skill_registry.list_skills()
    if not skills:
        console.print("[info]No skills learned yet.[/info]")
        return
    console.print(f"[tool]Skills[/tool] ({len(skills)})")
    for skill in skills:
        console.print(f"  [yellow]●[/yellow] [tool]{skill.name}[/tool]: {skill.description}")
        console.print(f"    [info]intent[/info] {skill.intent}  [info]tool[/info] {skill.tool_name}  "
                      f"[info]rate[/info] {skill.success_rate:.0%}")


def cmd_plugins(args: argparse.Namespace, config: DANConfig) -> None:
    """List loaded plugins."""
    plugin_registry = PluginRegistry()
    plugins = plugin_registry.list_plugins()
    if not plugins:
        console.print("[info]No plugins loaded.[/info]")
        return
    console.print(f"[tool]Plugins[/tool] ({len(plugins)})")
    for plugin in plugins:
        console.print(f"  [yellow]●[/yellow] [tool]{plugin.name}[/tool] v{plugin.version}: {plugin.description}")


def cmd_config(args: argparse.Namespace, config: DANConfig) -> None:
    """Show current configuration."""
    console.print("[tool]Core[/tool]")
    console.print(f"  [info]threshold[/info] {config.core.threshold}  [info]log[/info] {config.core.log_level}")
    console.print("[tool]Interpret[/tool]")
    console.print(f"  [info]provider[/info] {config.interpret.name}  [info]model[/info] {config.interpret.model}  [info]device[/info] {config.interpret.device}")
    console.print("[tool]Reason[/tool]")
    console.print(f"  [info]provider[/info] {config.reason.name}  [info]model[/info] {config.reason.model}  [info]device[/info] {config.reason.device}")
    console.print("[tool]Memory[/tool]")
    console.print(f"  [info]short_term[/info] {config.memory.short_term_limit}  [info]long_term[/info] {config.memory.long_term_path}")
    console.print("[tool]Skills[/tool]")
    console.print(f"  [info]store[/info] {config.skills.store_path}  [info]min_exec[/info] {config.skills.min_executions}  [info]min_conf[/info] {config.skills.min_confidence}")


def cmd_version(args: argparse.Namespace, config: DANConfig) -> None:
    console.print(f"[green]D.A.N.[/green] v{__version__}")
    console.print("[info]Distributed Assistant Neural-network[/info]")
    console.print("[info]An open-source Agentic Execution Framework[/info]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dan",
        description="D.A.N. - Distributed Assistant Neural-network",
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        default=None,
        help="Path to configuration file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    run_parser = subparsers.add_parser("run", help="Run a single command")
    run_parser.add_argument("message", help="Message to process")

    subparsers.add_parser("interact", help="Start interactive mode")
    subparsers.add_parser("tools", help="List available tools")
    subparsers.add_parser("skills", help="List learned skills")
    subparsers.add_parser("plugins", help="List loaded plugins")
    subparsers.add_parser("config", help="Show current configuration")
    subparsers.add_parser("version", help="Show version information")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)
    config = DANConfig.from_file(args.config)

    commands = {
        "run": cmd_run,
        "interact": cmd_interact,
        "tools": cmd_tools,
        "skills": cmd_skills,
        "plugins": cmd_plugins,
        "config": cmd_config,
        "version": cmd_version,
    }

    if not args.command:
        console.print("[info]No command specified. Use 'dan --help' for usage.[/info]")
        sys.exit(1)

    cmd_func = commands.get(args.command)
    if not cmd_func:
        console.print(f"[error]Unknown command:[/error] {args.command}")
        sys.exit(1)

    if asyncio.iscoroutinefunction(cmd_func):
        asyncio.run(cmd_func(args, config))
    else:
        cmd_func(args, config)


if __name__ == "__main__":
    main()
