"""
Module   : core.voice
Project  : T.O.N.Y. v4
Purpose  : Microsoft Edge-TTS Generation and Core Audio Engine Interface
"""

from __future__ import annotations
import os
import re
import time
import socket
import asyncio
import logging
import tempfile
from pathlib import Path
from queue import Queue
from typing import Dict, Any
from contextlib import suppress

import edge_tts
import pygame
import speech_recognition as sr
import win32com.client

# Suppress Pygame branding printouts on startup initialization
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

class VoiceInterface:
    """
    Audio management implementation managing clear voice capture pipelines, 
    streaming speech synthesis, and reliable local accessibility system rollbacks.
    """
    def __init__(self):
        # Speech Recognition Pipeline Configurations
        self.recognizer = sr.Recognizer()
        
        # Audio Initialization Architecture
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Premium Synthesis Options
        self.voice: str = "en-US-ChristopherNeural"
        self.rate: str = "+0%"
        self.pitch: str = "+0Hz"

        # Safe Offline Processing Core Fallback (SAPI5)
        try:
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        except Exception:
            self.speaker = None
            print("[VOICE WARNING] SAPI5 COM bindings unallocated locally.")

        # Thread Control Real-time Tracking Flags
        self._stop_requested: bool = False
        self._speaking: bool = False

        # Diagnostic Analytics Performance Records
        self._spoken_count: int = 0
        self._listen_count: int = 0
        self._last_runtime: float = 0.0
        self._last_text: str = ""
        self._speech_queue: Queue = Queue()

    @property
    def speaking(self) -> bool:
        return self._speaking

    @property
    def spoken_count(self) -> int:
        return self._spoken_count

    @property
    def listen_count(self) -> int:
        return self._listen_count

    @property
    def runtime(self) -> float:
        return self._last_runtime

    def _clean_text(self, text: str) -> str:
        """Sanitizes text strings to avoid processing raw technical logs."""
        if not text:
            return ""

        if text.startswith("[System Error]") or text.startswith("[Unrecognized Audio]"):
            return "System alert. An error has occurred processing that request."

        text = re.sub(r"[*#`|]", "", text)
        text = re.sub(r"CMD:[^\n]+", "", text)
        return text.replace("\n", " ").strip()

    def _run_async(self, coro) -> Any:
        """Safely executes background coroutines outside native async event loops."""
        try:
            asyncio.get_running_loop()
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        except RuntimeError:
            return asyncio.run(coro)

    def speak(self, text: str) -> None:
        """Translates structural text strings into premium synthesized speech patterns."""
        cleaned = self._clean_text(text)
        if not cleaned:
            return

        self._speaking = True
        self._stop_requested = False
        self._spoken_count += 1
        self._last_text = cleaned
        start_marker = time.perf_counter()

        temp_path = Path(tempfile.gettempdir()) / f"tony_audio_{int(time.time())}.mp3"

        try:
            # Generate Edge-TTS audio file
            self._run_async(self._generate_audio(cleaned, temp_path))
            
            # Execute standard audio stream playback
            pygame.mixer.music.load(str(temp_path))
            pygame.mixer.music.play()
            
            playback_clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                if self._stop_requested:
                    pygame.mixer.music.stop()
                    break
                playback_clock.tick(30)
                
            pygame.mixer.music.unload()
        except Exception as tts_error:
            print(f"[VOICE EXCEPTION] Cloud EdgeTTS failed: {tts_error}. Deploying local COM pipeline.")
            if self.speaker:
                try:
                    self.speaker.Speak(cleaned)
                except Exception as native_err:
                    print(f"[VOICE FAILURE] Native engine failed: {native_err}")
        finally:
            with suppress(Exception):
                if temp_path.exists():
                    temp_path.unlink()
            
            self._last_runtime = time.perf_counter() - start_marker
            self._speaking = False

    async def _generate_audio(self, text: str, output_file: Path) -> None:
        """Direct cloud worker query engine generating target mp3 assets."""
        communicator = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch
        )
        await communicator.save(str(output_file))

    def set_voice(self, voice: str) -> None:
        if voice:
            self.voice = voice

    def set_rate(self, rate: str) -> None:
        self.rate = rate

    def set_pitch(self, pitch: str) -> None:
        self.pitch = pitch

    def stop_speaking(self) -> None:
        """Instantly terminates concurrent operational speaker audio hardware pipelines."""
        self._stop_requested = True
        self._speaking = False
        with suppress(Exception):
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

    def listen_once(self) -> str:
        """Captures hardware microphone audio signals to generate structured text transcriptions."""
        self._listen_count += 1
        try:
            with sr.Microphone() as hardware_mic:
                self.recognizer.adjust_for_ambient_noise(hardware_mic, duration=0.4)
                audio_buffer = self.recognizer.listen(hardware_mic, timeout=5, phrase_time_limit=10)
                return self.recognizer.recognize_google(audio_buffer, language="en-US")
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return "[Unrecognized Audio]"
        except sr.RequestError:
            return "[Network Error]"
        except Exception:
            return "[Voice Error]"

    def get_statistics(self) -> Dict[str, Any]:
        """Packages localized diagnostics performance metrics."""
        return {
            "voice": self.voice,
            "rate": self.rate,
            "pitch": self.pitch,
            "speaking": self._speaking,
            "spoken_count": self._spoken_count,
            "listen_count": self._listen_count,
            "runtime": self._last_runtime,
            "last_text": self._last_text
        }