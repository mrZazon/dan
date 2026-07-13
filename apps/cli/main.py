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
import logging
import sys
from pathlib import Path

from dan.core.config import DANConfig
from dan.core.tool_registry import ToolRegistry
from dan.core.router import Router, Layer
from dan.core.safety import check_command_safety, get_tool_danger_level, DANGEROUS, CAUTION
from dan.memory.session import SessionMemory
from dan.plugins.registry import PluginRegistry
from dan.providers.ollama import OllamaProvider
from dan.skills.registry import SkillRegistry

__version__ = "0.1.0"

logger = logging.getLogger("dan")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_run(args: argparse.Namespace, config: DANConfig) -> None:
    """Execute a single command."""
    registry = ToolRegistry()
    registry.discover()
    from dan.core.dispatcher import Dispatcher
    dispatcher = Dispatcher(registry=registry, threshold=config.core.threshold)
    result = dispatcher.dispatch(args.message)
    if result.match is None:
        print(f"No match. {result.message}")
    else:
        tool = result.match.tool
        print(f"Tool: {tool.name}")
        print(f"Score: {result.confidence}")


def _confirm(prompt: str) -> bool:
    try:
        answer = input(f"dan> {prompt} [y/N] ").strip().lower()
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

    interpret = OllamaProvider()
    reason = OllamaProvider()
    await interpret.load_model(config.interpret.model)
    await reason.load_model(config.reason.model)

    skill_registry = SkillRegistry()
    session = SessionMemory()
    router = Router(
        registry=registry,
        skill_registry=skill_registry,
        interpret_provider=interpret,
        reason_provider=reason,
        threshold=config.core.threshold,
        session=session,
    )

    print(f"D.A.N. v{__version__} - Interactive Mode")
    print(f"Interpret model: {config.interpret.model}")
    print(f"Reason model: {config.reason.model}")
    print(f"Tools loaded: {len(registry)}")
    print("Type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            message = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not message:
            continue
        if message.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        session.add_user(message)

        try:
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
                            desc += f" -> {cmd_str}"
                        if not _confirm(f"{desc}. Execute?"):
                            print("dan> Cancelled.")
                            break

                    # Extra shell-level safety for command tool
                    if tool_name == "command":
                        cmd_str = tool_args.get("command", "")
                        verdict = check_command_safety(cmd_str)
                        if not verdict.safe:
                            if not _confirm(f"DESTRUCTIVE: {verdict.reason} ({cmd_str}). Execute?"):
                                print("dan> Cancelled.")
                                break

                    tool_class = registry.get(tool_name)
                    tool_instance = tool_class()
                    tool_result = await tool_instance.execute(**tool_args)
                    print(f"dan> {tool_result.message}")
                    session.add_assistant(tool_result.message)

            elif route.skill_name:
                print(f"dan> (skill: {route.skill_name})")

            elif route.raw_response:
                print(f"dan> {route.raw_response}")
                session.add_assistant(route.raw_response)

            elif route.confidence == 0.0 and route.tool_name is None:
                from dan.providers.base import ProviderMessage
                sys.stdout.write("dan> ")
                sys.stdout.flush()
                response_parts: list[str] = []
                async for chunk in reason.stream(
                    [ProviderMessage(role="user", content=message)],
                    temperature=0.7,
                    max_tokens=256,
                ):
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                    response_parts.append(chunk)
                print()
                full_response = "".join(response_parts)
                if full_response.strip():
                    session.add_assistant(full_response.strip())
                continue
            else:
                print("dan> No tool found for that request.")

        except Exception as e:
            logger.exception("Error processing message")
            print(f"dan> Error: {e}")


def cmd_tools(args: argparse.Namespace, config: DANConfig) -> None:
    """List available tools."""
    registry = ToolRegistry()
    registry.discover()
    tools = registry.tools()
    if not tools:
        print("No tools registered.")
        return
    print(f"Available tools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")


def cmd_skills(args: argparse.Namespace, config: DANConfig) -> None:
    """List learned skills."""
    skill_registry = SkillRegistry()
    skills = skill_registry.list_skills()
    if not skills:
        print("No skills learned yet.")
        return
    print(f"Learned skills ({len(skills)}):")
    for skill in skills:
        print(f"  - {skill.name}: {skill.description}")
        print(f"    Intent: {skill.intent}")
        print(f"    Tool: {skill.tool_name}")
        print(f"    Success rate: {skill.success_rate:.1%}")


def cmd_plugins(args: argparse.Namespace, config: DANConfig) -> None:
    """List loaded plugins."""
    plugin_registry = PluginRegistry()
    plugins = plugin_registry.list_plugins()
    if not plugins:
        print("No plugins loaded.")
        return
    print(f"Loaded plugins ({len(plugins)}):")
    for plugin in plugins:
        print(f"  - {plugin.name} v{plugin.version}: {plugin.description}")


def cmd_config(args: argparse.Namespace, config: DANConfig) -> None:
    """Show current configuration."""
    print("Core:")
    print(f"  Threshold: {config.core.threshold}")
    print(f"  Log level: {config.core.log_level}")
    print("Interpret provider:")
    print(f"  Name: {config.interpret.name}")
    print(f"  Model: {config.interpret.model}")
    print(f"  Device: {config.interpret.device}")
    print("Reason provider:")
    print(f"  Name: {config.reason.name}")
    print(f"  Model: {config.reason.model}")
    print(f"  Device: {config.reason.device}")
    print("Memory:")
    print(f"  Short-term limit: {config.memory.short_term_limit}")
    print(f"  Long-term path: {config.memory.long_term_path}")
    print("Skills:")
    print(f"  Store path: {config.skills.store_path}")
    print(f"  Min executions: {config.skills.min_executions}")
    print(f"  Min confidence: {config.skills.min_confidence}")


def cmd_version(args: argparse.Namespace, config: DANConfig) -> None:
    print(f"D.A.N. v{__version__}")
    print("Distributed Assistant Neural-network")
    print("An open-source Agentic Execution Framework")


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
        print("No command specified. Use 'dan --help' for usage.")
        sys.exit(1)

    cmd_func = commands.get(args.command)
    if not cmd_func:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

    import asyncio
    if asyncio.iscoroutinefunction(cmd_func):
        asyncio.run(cmd_func(args, config))
    else:
        cmd_func(args, config)


if __name__ == "__main__":
    main()
