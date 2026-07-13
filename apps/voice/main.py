"""D.A.N. Voice CLI — talk to D.A.N. with your voice.

Usage:
    dan voice [--stt-model MODEL]
"""
from __future__ import annotations

import argparse
import asyncio
import os
import queue
import sys
import threading
import time

import numpy as np

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.status import Status

from dan.core.config import DANConfig
from dan.core.tool_registry import ToolRegistry
from dan.core.router import Router
from dan.memory.session import SessionMemory
from dan.providers.ollama import OllamaProvider
from dan.skills.registry import SkillRegistry
from dan.voice import TTS, STT

console = Console()

# Shared state
_stop_event = threading.Event()


def _keyboard_listener() -> None:
    """Listen for space to stop recording."""
    import tty
    import termios

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while not _stop_event.is_set():
            if os.read(fd, 1) == b" ":
                _stop_event.set()
                break
    except (OSError, IOError):
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _listen_with_transcription(
    stt: STT,
    silence_threshold: float = 0.01,
    silence_duration: float = 1.5,
    max_duration: float = 30.0,
    sample_rate: int = 16000,
) -> str:
    """Listen with real-time transcription and space to stop."""
    import sounddevice as sd

    _stop_event.clear()
    stt.transcribe(np.zeros(16000, dtype=np.float32))

    audio_chunks: list[np.ndarray] = []
    silent_chunks = 0
    chunks_per_second = 10
    silence_limit = int(silence_duration * chunks_per_second)
    max_chunks = int(max_duration * chunks_per_second)
    block_size = int(sample_rate / chunks_per_second)

    # Start keyboard listener
    kb_thread = threading.Thread(target=_keyboard_listener, daemon=True)
    kb_thread.start()

    q: queue.Queue = queue.Queue()

    def callback(indata, frames, time_info, status):
        q.put(indata.copy())

    sys.stdout.write("\033[1;31m🎤 Listening... (SPACE to stop)\033[0m\n")
    sys.stdout.flush()

    last_transcribe_time = time.time()
    partial_text = ""

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        blocksize=block_size,
        callback=callback,
    ):
        for _ in range(max_chunks):
            if _stop_event.is_set():
                break

            try:
                chunk = q.get(timeout=0.2)
            except queue.Empty:
                continue

            level = np.abs(chunk).mean()
            if level < silence_threshold:
                silent_chunks += 1
                if silent_chunks >= silence_limit:
                    break
            else:
                silent_chunks = 0

            audio_chunks.append(chunk)

            # Live waveform
            bars = int(level * 100)
            bar = "█" * min(bars, 30)
            sys.stdout.write(f"\r\033[1;33m   {bar}\033[0m")
            sys.stdout.flush()

            # Partial transcription every 2s
            now = time.time()
            if now - last_transcribe_time >= 2.0 and len(audio_chunks) >= 20:
                last_transcribe_time = now
                audio_so_far = np.concatenate(audio_chunks).flatten()
                try:
                    new_text = stt.transcribe(audio_so_far, beam_size=3)
                    if new_text and new_text != partial_text:
                        partial_text = new_text
                        sys.stdout.write(f"\r\033[1;36m   📝 {partial_text}\033[0m\n")
                        sys.stdout.flush()
                except Exception:
                    pass

    # Clear line
    sys.stdout.write("\r\033[2K")
    sys.stdout.flush()

    if not audio_chunks:
        return ""

    # Final transcription
    audio = np.concatenate(audio_chunks).flatten()
    sys.stdout.write("\033[1;33m   ⏳ Transcribing...\033[0m\n")
    sys.stdout.flush()

    text = stt.transcribe(audio)
    return text


async def cmd_voice(args: argparse.Namespace, config: DANConfig) -> None:
    """Start voice interaction mode."""
    with Status("[bold green]Initializing voice...", console=console, spinner="dots") as status:
        status.update("[bold green]Loading TTS...")
        tts = TTS()
        status.update("[bold green]Loading STT...")
        stt = STT(model_size=args.stt_model)
        status.update("[bold green]Loading interpret model...")
        interpret = OllamaProvider()
        await interpret.load_model(config.interpret.model)
        status.update("[bold green]Loading reason model...")
        reason = OllamaProvider()
        await reason.load_model(config.reason.model)
        status.update("[bold green]Loading persona model...")
        persona = OllamaProvider()
        await persona.load_model(config.persona.model)

    registry = ToolRegistry()
    registry.discover()
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

    header = Text()
    header.append("D.A.N.", style="bold green")
    header.append(" Voice Mode", style="bold")
    console.print(Panel(header, border_style="green", padding=(0, 1)))
    console.print("  [info]SPACE to stop recording, Ctrl+C to quit[/info]")
    console.print()

    while True:
        try:
            text = _listen_with_transcription(stt)

            if not text:
                console.print("[dim]   (no speech detected)[/dim]")
                continue

            if text.lower() in ("exit", "quit", "goodbye", "bye"):
                tts.speak("Goodbye!")
                console.print("[info]Goodbye![/info]")
                break

            console.print(f"[bold cyan]you>[/bold cyan] {text}")
            session.add_user(text)

            with Status("[bold yellow]Thinking...", console=console, spinner="dots"):
                steps_log = await router.route_agentic(text, max_steps=5)

            if steps_log:
                for step in steps_log:
                    if step["type"] == "tool":
                        console.print(f"  [dim]→ {step['name']}[/dim]")

                last = steps_log[-1]
                if last["type"] == "response":
                    response = last["text"]
                elif last["type"] == "done":
                    response = last.get("summary", "Done.")
                else:
                    response = "Done."

                console.print(f"[bold green]dan>[/bold green] {response}")
                session.add_assistant(response)
                tts.speak(response)
            else:
                console.print("[info]No response generated.[/info]")

        except KeyboardInterrupt:
            console.print("\n[info]Goodbye![/info]")
            break
        except Exception as e:
            console.print(f"[error]Error:[/error] {e}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dan voice",
        description="D.A.N. Voice — talk to your AI assistant",
    )
    parser.add_argument(
        "--stt-model",
        default="tiny",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size (default: tiny)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = DANConfig.from_file()
    asyncio.run(cmd_voice(args, config))


if __name__ == "__main__":
    main()
