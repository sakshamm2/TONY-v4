"""
Module   : core.workers
Project  : T.O.N.Y. v4
Purpose  : Thread-Safe Async Operation Pipelines for Speech and Core LLMs
"""

from __future__ import annotations
import time
from typing import Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot

from core.ai import AIEngine
from core.voice import VoiceInterface

# ==========================================================
# Background Engine: AI processing Thread Worker
# ==========================================================
class AIWorker(QObject):
    """
    Handles streaming text synthesis operations outside main UI event threads.
    """
    started = Signal()
    stream_chunk = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, ai: AIEngine):
        super().__init__()
        self.ai = ai
        
        # Thread Controller Flags
        self._busy: bool = False
        self._processing: bool = False
        self._cancel_requested: bool = False

        # Analytic Parameters
        self._started_at: float = 0.0
        self._finished_at: float = 0.0
        self._last_runtime: float = 0.0
        self._request_count: int = 0
        self._cancel_count: int = 0
        
        self._last_prompt: str = ""
        self._last_response: str = ""

    def is_busy(self) -> bool:
        return self._busy

    @property
    def runtime(self) -> float:
        return self._last_runtime

    @property
    def request_count(self) -> int:
        return self._request_count

    @property
    def cancel_count(self) -> int:
        return self._cancel_count

    @property
    def last_prompt(self) -> str:
        return self._last_prompt

    @property
    def last_response(self) -> str:
        return self._last_response

    def cancel(self) -> None:
        if self._busy:
            self._cancel_requested = True
            self._cancel_count += 1

    @Slot(str)
    def process(self, prompt: str) -> None:
        """Assembles prompt payload context and begins streaming response tokens."""
        if self._busy:
            return

        clean_prompt = prompt.strip()
        if not clean_prompt:
            return

        self._busy = True
        self._processing = True
        self._cancel_requested = False
        self._started_at = time.perf_counter()
        self._request_count += 1
        self._last_prompt = clean_prompt

        self.started.emit()
        full_response = ""

        try:
            for chunk in self.ai.stream_response(clean_prompt):
                if self._cancel_requested:
                    break
                if not chunk:
                    continue

                full_response += chunk
                self.stream_chunk.emit(chunk)

            if not self._cancel_requested:
                self._last_response = full_response
                self.finished.emit(full_response)

        except Exception as ai_err:
            self.error.emit(str(ai_err))
        finally:
            self._finished_at = time.perf_counter()
            self._last_runtime = self._finished_at - self._started_at
            self._busy = False
            self._processing = False
            self._cancel_requested = False

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "busy": self._busy,
            "processing": self._processing,
            "runtime": self._last_runtime,
            "requests": self._request_count,
            "cancellations": self._cancel_count,
            "last_prompt": self._last_prompt,
            "last_response": self._last_response
        }

    def shutdown(self) -> None:
        self.cancel()
        self._busy = False
        self._processing = False


# ==========================================================
# Background Engine: Voice Core Thread Worker
# ==========================================================
class VoiceWorker(QObject):
    """
    Manages resource-intensive microphone listeners and audio generation loops.
    """
    started = Signal()
    finished = Signal()
    error = Signal(str)

    listening_started = Signal()
    listening_finished = Signal()
    voice_detected = Signal(str)

    def __init__(self, voice: VoiceInterface):
        super().__init__()
        self.voice = voice

        # Thread Tracking Parameters
        self._busy: bool = False
        self._speaking: bool = False
        self._listening: bool = False

        self._started_at: float = 0.0
        self._finished_at: float = 0.0
        self._last_runtime: float = 0.0
        self._spoken_count: int = 0
        self._listen_count: int = 0
        self._last_text: str = ""

    def is_busy(self) -> bool:
        return self._busy

    @property
    def runtime(self) -> float:
        return self._last_runtime

    @property
    def speaking(self) -> bool:
        return self._speaking

    @property
    def listening(self) -> bool:
        return self._listening

    @property
    def spoken_count(self) -> int:
        return self._spoken_count

    @property
    def listen_count(self) -> int:
        return self._listen_count

    @Slot(str)
    def speak(self, text: str) -> None:
        """Invokes the localized speech renderer engine inside the worker thread scope."""
        if self._busy:
            return

        clean_text = text.strip()
        if not clean_text:
            return

        self._busy = True
        self._speaking = True
        self._started_at = time.perf_counter()
        self._spoken_count += 1
        self._last_text = clean_text

        self.started.emit()

        try:
            self.voice.speak(clean_text)
            self.finished.emit()
        except Exception as audio_err:
            self.error.emit(str(audio_err))
        finally:
            self._finished_at = time.perf_counter()
            self._last_runtime = self._finished_at - self._started_at
            self._speaking = False
            self._busy = False

    @Slot()
    def listen_once(self) -> None:
        """Initializes a short microphone listener sequence to record voice commands."""
        if self._busy:
            return

        self._busy = True
        self._listening = True
        self._started_at = time.perf_counter()
        self._listen_count += 1

        self.listening_started.emit()

        try:
            captured_text = self.voice.listen_once()
            if captured_text:
                clean_result = captured_text.strip()
                if clean_result:
                    self._last_text = clean_result
                    self.voice_detected.emit(clean_result)
        except Exception as listen_err:
            self.error.emit(str(listen_err))
        finally:
            self._finished_at = time.perf_counter()
            self._last_runtime = self._finished_at - self._started_at
            self.listening_finished.emit()
            self._listening = False
            self._busy = False

    @Slot()
    def stop_speaking(self) -> None:
        """Interrupts and stops ongoing speaker output streams."""
        try:
            self.voice.stop_speaking()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._speaking = False
            self._busy = False

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "busy": self._busy,
            "speaking": self._speaking,
            "listening": self._listening,
            "runtime": self._last_runtime,
            "spoken_count": self._spoken_count,
            "listen_count": self._listen_count,
            "last_text": self._last_text
        }

    def shutdown(self) -> None:
        try:
            self.stop_speaking()
        finally:
            self._busy = False
            self._speaking = False
            self._listening = False