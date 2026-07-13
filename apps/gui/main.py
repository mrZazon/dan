"""D.A.N. GUI — KDE Plasma 6 desktop assistant.

Usage:
    dan-gui [--stt-model MODEL]
"""
from __future__ import annotations

import argparse
import asyncio
import sys

from dan.core.config import DANConfig
from dan.core.tool_registry import ToolRegistry
from dan.core.router import Router
from dan.memory.session import SessionMemory
from dan.providers.ollama import OllamaProvider
from dan.skills.registry import SkillRegistry
from dan.voice import TTS, STT
from dan.gui import launch_gui


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dan-gui",
        description="D.A.N. GUI — KDE Plasma 6 desktop assistant",
    )
    parser.add_argument(
        "--stt-model",
        default="tiny",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size (default: tiny)",
    )
    args = parser.parse_args()

    config = DANConfig.from_file()

    # Setup components
    registry = ToolRegistry()
    registry.discover()

    tts = TTS()
    stt = STT(model_size=args.stt_model)

    interpret = OllamaProvider()
    reason = OllamaProvider()
    persona = OllamaProvider()

    async def init():
        await interpret.load_model(config.interpret.model)
        await reason.load_model(config.reason.model)
        await persona.load_model(config.persona.model)

    asyncio.run(init())

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

    launch_gui(router=router, tts=tts, stt=stt)


if __name__ == "__main__":
    main()
