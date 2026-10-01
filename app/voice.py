"""Sounix voice input, modeled on speech-to-console.

Flow: listen -> wake phrase -> transcribe speech -> deliver text -> end phrase.
Text goes to a callback (feed it to Sounix) or is typed into the focused window.
Voice commands like "use deep model" or "go local only" are handled first.

Deps: pip install numpy faster-whisper   (sounddevice only if not using PipeWire)
      plus openai (cloud Whisper) and/or faster-whisper (offline, recommended
      for sensitive security work), and pyautogui only if you use output="type".
"""
from __future__ import annotations

import io
import queue
import re
import shutil
import subprocess
import threading
import wave
from dataclasses import dataclass
from typing import Callable

import numpy as np

RATE = 16000
BLOCK_S = 0.1


@dataclass
class VoiceConfig:
    wake_phrase: str = "hey sounix"
    end_phrase: str = "end sounix"
    silent_threshold: int = 750        # RMS on int16; lower = more sensitive
    min_audio_seconds: float = 0.5     # ignore blips shorter than this
    silence_seconds: float = 0.8       # pause that ends an utterance
    backend: str = "local"             # "local" (faster-whisper) | "openai"
    local_model: str = "small.en"
    openai_model: str = "whisper-1"
    output: str = "callback"           # "callback" | "type"
    capture: str = "auto"              # "auto" (PipeWire if found) | "pipewire" | "sounddevice"
    source: str = ""                   # PipeWire mic name or id; blank = system default


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


# ---- transcription backends -----------------------------------------
class LocalTranscriber:
    def __init__(self, cfg: VoiceConfig):
        from faster_whisper import WhisperModel
        self.model = WhisperModel(cfg.local_model, compute_type="int8")

    def __call__(self, pcm: np.ndarray) -> str:
        audio = pcm.astype(np.float32) / 32768.0
        segs, _ = self.model.transcribe(audio, language="en", vad_filter=True, initial_prompt="Hey Sounix. Sounix is a Linux security assistant.")
        return " ".join(s.text.strip() for s in segs)


class OpenAITranscriber:
    def __init__(self, cfg: VoiceConfig):
        from openai import OpenAI
        self.client, self.model = OpenAI(), cfg.openai_model

    def __call__(self, pcm: np.ndarray) -> str:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        buf.seek(0)
        buf.name = "audio.wav"
        return self.client.audio.transcriptions.create(model=self.model, file=buf).text


# ---- the listener ---------------------------------------------------
class VoiceListener:
    def __init__(self, on_text: Callable[[str], None], cfg: VoiceConfig | None = None,
                 commands: dict[str, Callable[[], None]] | None = None,
                 arg_commands: dict[str, Callable[[str], None]] | None = None):
        self.cfg = cfg or VoiceConfig()
        self.on_text = on_text
        self.commands = {_norm(k): v for k, v in (commands or {}).items()}
        # prefix commands that take the rest of the sentence, e.g. "use model llama 3.1"
        self.arg_commands = {_norm(k): v for k, v in (arg_commands or {}).items()}
        self.transcribe = (LocalTranscriber if self.cfg.backend == "local"
                           else OpenAITranscriber)(self.cfg)
        self.active = False
        self.last_level = 0.0
        self._utterances: queue.Queue = queue.Queue()
        self._stop = threading.Event()

    def start(self) -> None:
        threading.Thread(target=self._worker, daemon=True).start()
        self._capture()  # blocks until stop()

    def stop(self) -> None:
        self._stop.set()

    # capture: read 0.1 s blocks from the mic; energy-based VAD splits them into utterances
    def _blocks(self):
        use_pw = self.cfg.capture == "pipewire" or (
            self.cfg.capture == "auto" and shutil.which("pw-record"))
        return self._pipewire_blocks() if use_pw else self._sounddevice_blocks()

    def _pipewire_blocks(self):
        cmd = ["pw-record", "--raw", "--rate", str(RATE), "--channels", "1", "--format", "s16"]
        if self.cfg.source:
            cmd += ["--target", self.cfg.source]
        proc = subprocess.Popen(cmd + ["-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        size = int(RATE * BLOCK_S) * 2
        try:
            while not self._stop.is_set():
                data = proc.stdout.read(size)
                if len(data) < size:
                    raise RuntimeError("pw-record stopped; test it in a terminal first")
                yield np.frombuffer(data, dtype=np.int16)
        finally:
            proc.terminate()

    def _sounddevice_blocks(self):
        import sounddevice as sd
        with sd.InputStream(samplerate=RATE, channels=1, dtype="int16",
                            blocksize=int(RATE * BLOCK_S)) as stream:
            while not self._stop.is_set():
                block, _ = stream.read(int(RATE * BLOCK_S))
                yield block[:, 0]

    def _capture(self) -> None:
        cfg, chunks, quiet = self.cfg, [], 0.0
        for block in self._blocks():
            rms = float(np.sqrt(np.mean(block.astype(np.float32) ** 2)))
            self.last_level = rms
            if rms >= cfg.silent_threshold:
                chunks.append(block); quiet = 0.0
            elif chunks:
                chunks.append(block); quiet += BLOCK_S
                if quiet >= cfg.silence_seconds:
                    pcm = np.concatenate(chunks)
                    if len(pcm) / RATE >= cfg.min_audio_seconds:
                        self._utterances.put(pcm)
                    chunks, quiet = [], 0.0

    # worker: transcribe in order, then run the wake/end state machine
    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                pcm = self._utterances.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                self._handle(self.transcribe(pcm))
            except Exception as exc:
                print(f"[voice] transcription error: {exc}")

    def _handle(self, text: str) -> None:
        n, wake, end = _norm(text), _norm(self.cfg.wake_phrase), _norm(self.cfg.end_phrase)
        if not self.active:
            if wake in n:
                self.active = True
                print("[voice] active")
                n = n.split(wake, 1)[1].strip()
            else:
                return
        stopping = end in n
        if stopping:
            n = n.split(end, 1)[0].strip()
        if n:
            prefix = next((p for p in self.arg_commands if n.startswith(p + " ")), None)
            if n in self.commands:
                self.commands[n]()
            elif prefix:
                self.arg_commands[prefix](n[len(prefix):].strip())
            else:
                self._deliver(n)
        if stopping:
            self.active = False
            print("[voice] idle")

    def _deliver(self, text: str) -> None:
        if self.cfg.output == "type":
            import pyautogui
            pyautogui.write(text + " ", interval=0.01)
        else:
            self.on_text(text)
