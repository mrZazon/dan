from __future__ import annotations

import logging
import queue
import threading
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODEL_DIR = _PROJECT_ROOT / "models" / "piper"


def _get_sd():
    """Lazy import of sounddevice."""
    import sounddevice as sd
    return sd


class TTS:
    """Piper TTS — natural female voice output."""

    def __init__(
        self,
        model_path: Path | str | None = None,
        speaker: str = "amy",
    ) -> None:
        self._model_path = model_path or DEFAULT_MODEL_DIR / "en_US-amy-medium.onnx"
        self._speaker = speaker
        self._synthesizer = None

    def _ensure_loaded(self) -> None:
        if self._synthesizer is not None:
            return
        from piper import PiperVoice
        logger.info("Loading Piper TTS: %s", self._model_path)
        self._synthesizer = PiperVoice.load(str(self._model_path))

    def speak(self, text: str) -> None:
        """Speak text through speakers."""
        sd = _get_sd()
        self._ensure_loaded()
        chunks = list(self._synthesizer.synthesize(text))
        if not chunks:
            return
        audio_int16 = b"".join(c.audio_bytes for c in chunks)
        audio = np.frombuffer(audio_int16, dtype=np.int16).astype(np.float32) / 32768.0
        sd.play(audio, samplerate=chunks[0].sample_rate)
        sd.wait()

    def speak_async(self, text: str) -> threading.Thread:
        """Speak text in a background thread."""
        t = threading.Thread(target=self.speak, args=(text,), daemon=True)
        t.start()
        return t

    def save_wav(self, text: str, path: str | Path) -> None:
        """Save speech to a WAV file."""
        import wave
        self._ensure_loaded()
        chunks = list(self._synthesizer.synthesize(text))
        if not chunks:
            return
        audio_int16 = b"".join(c.audio_bytes for c in chunks)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(chunks[0].sample_rate)
            wf.writeframes(audio_int16)


class STT:
    """Whisper STT — speech recognition from microphone."""

    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
    ) -> None:
        self._model_size = model_size
        self._device = device
        self._model = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        from faster_whisper import WhisperModel
        logger.info("Loading Whisper model: %s", self._model_size)
        self._model = WhisperModel(
            self._model_size,
            device=self._device,
            compute_type="int8",
        )

    def transcribe(
        self,
        audio: np.ndarray,
        beam_size: int = 5,
        language: str = "en",
    ) -> str:
        """Transcribe audio array to text."""
        self._ensure_loaded()
        audio = np.asarray(audio, dtype=np.float32).flatten()
        segments, _ = self._model.transcribe(
            audio,
            beam_size=beam_size,
            language=language,
        )
        text = " ".join(seg.text.strip() for seg in segments)
        logger.info("Transcribed: %r", text)
        return text.strip()

    def listen(
        self,
        duration: float = 5.0,
        sample_rate: int = 16000,
    ) -> str:
        """Record audio from microphone and transcribe."""
        sd = _get_sd()
        self._ensure_loaded()

        logger.info("Recording for %.1fs...", duration)
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        audio = audio.flatten()
        return self.transcribe(audio)

    def listen_stream(
        self,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,
        max_duration: float = 30.0,
        sample_rate: int = 16000,
    ) -> str:
        """Listen continuously until user stops speaking."""
        sd = _get_sd()
        self._ensure_loaded()

        audio_chunks: list[np.ndarray] = []
        silent_chunks = 0
        chunks_per_second = 10
        silence_limit = int(silence_duration * chunks_per_second)
        max_chunks = int(max_duration * chunks_per_second)
        block_size = int(sample_rate / chunks_per_second)

        logger.info("Listening... (speak now)")

        q: queue.Queue = queue.Queue()

        def callback(indata, frames, time_info, status):
            q.put(indata.copy())

        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            blocksize=block_size,
            callback=callback,
        ):
            for _ in range(max_chunks):
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

        if not audio_chunks:
            return ""

        audio = np.concatenate(audio_chunks).flatten()
        return self.transcribe(audio)
