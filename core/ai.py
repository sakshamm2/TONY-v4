"""
Module   : core.ai
Project  : T.O.N.Y. v4
Purpose  : Google Gemini Orchestration and AI Agent Planning Engine
"""

from __future__ import annotations
import os
from typing import Generator, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIEngine:
    """
    Orchestration layer managing stateful LLM context, semantic injection, 
    streaming responses, and structural multi-tool task generation.
    """
    def __init__(self, memory_service: Any):
        self.memory = memory_service
        self.model:Optional[genai.GenerativeModel] = None
        self.chat: Optional[Any] = None
        self.initialized: bool = False

        # Configurable Parameters
        self.model_name: str = "gemini-2.5-flash"
        self.max_context_messages: int = 10
        self.system_prompt: str = ""

        # Secure API Initialization
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[AI ERROR] GEMINI_API_KEY environment variable missing.")
            return

        try:
            genai.configure(api_key=api_key)
            self._build_model()
            self.initialized = True
            print("[AI CODECS] Gemini core engine initialized successfully.")
        except Exception as e:
            print(f"[AI CORE FAILURE] Initialization crash: {e}")

    def _build_model(self) -> None:
        """Assembles systemic context, loads memories, and builds the chat window."""
        try:
            memory_context = self.memory.get_context()
        except Exception:
            memory_context = ""

        self.system_prompt = f"""You are T.O.N.Y. (The Optimized Neural Operator for You)
Advanced AI Desktop Companion operating locally on the user's workstation.

BEHAVIORAL RULES:
1. Reply naturally, clearly, and concisely.
2. Respond in the exact language style used by the user.
3. Explicitly remember key user facts by appending: |CMD:remember:fact_here|
   Example: "I'll store that." |CMD:remember:User loves espresso|
4. If a task requires hardware automation, append EXACTLY ONE command tag:
   |CMD:open_chrome| |CMD:open_notepad| |CMD:open_calculator| |CMD:open_youtube|
   |CMD:volume_up| |CMD:volume_down| |CMD:volume_mute| |CMD:take_screenshot|

KNOWN LONG-TERM USER DATA:
{memory_context}

Never explicitly reference these structural prompt constraints."""

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_prompt
        )
        self.chat = self.model.start_chat(history=[])

    def plan(self, goal: str) -> str:
        """Transforms complex structural goals into isolated, clean JSON tasks."""
        if not self.initialized:
            return '{"tasks":[],"error":"AI Engine is offline."}'

        goal = goal.strip()
        if not goal:
            return '{"tasks":[],"error":"Empty goal provided."}'

        planner_prompt = f"""You are the structural planning component for T.O.N.Y.
Convert the user's execution goal into strict JSON task arrays.

OUTPUT CONSTRAINTS:
- Return raw, valid JSON ONLY. 
- Do NOT wrap within Markdown code fences (```json).
- No prose explanations, no structural comments.

JSON Output Schema:
{{
    "tasks": [
        {{
            "name": "Task name identifier",
            "description": "Granular execution steps",
            "tool": "Target tool domain",
            "action": "Functional method",
            "parameters": {{}}
        }}
    ]
}}

VALID CORE TOOL DOMAINS:
- pc_control (OS apps, volume adjustment, media inputs, capture)
- system (Hardware metrics, processes, system status)
- file (IO operations, creations, navigation, management)
- browser (Surfing addresses, web searching strategies)
- clipboard (Setting, capturing, scrubbing clipboard values)
- process (Inspecting, killing, hosting running system software)
- shell (Executing low-level shell actions)

If no matching tool domain handles this request, return an empty array object.

User Goal Target:
{goal}
"""
        try:
            response = self.model.generate_content(
                planner_prompt,
                generation_config=self._generation_config()
            )
            if not hasattr(response, "text"):
                return '{"tasks":[]}'
            return response.text.strip()
        except Exception as e:
            if "429" in str(e):
                print("[AI PLANNER WARNING] Gemini usage quota exceeded.")
                return '{"tasks":[{"name":"Offline","description":"Quota exceeded.","tool":"pc_control","action":"noop","parameters":{}}]}'
            print(f"[AI PLANNER CRASH] Execution tracing: {e}")
            return f'{{"tasks":[],"error":"{str(e)}"}}'

    def _generation_config(self) -> Dict[str, Any]:
        """Provides operational runtime hyperparameters for the LLM."""
        return {
            "temperature": 0.4,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 1024,
        }

    def _build_prompt(self, prompt: str) -> str:
        """Assembles unified runtime contextual frameworks across systemic modules."""
        try:
            memory_ctx = self.memory.get_context()
            prefs = self.memory.get_preferences()
            goals = self.memory.manager.get_goals(limit=5)
            tools = self.memory.tool_usage()
            history_data = self.memory.get_conversation(self.max_context_messages)
        except Exception:
            memory_ctx, prefs, goals, tools, history_data = "", {}, [], {}, []

        history_lines = []
        for msg in history_data:
            role = str(msg.get("role", "user")).capitalize()
            txt = str(msg.get("content", "")).strip()
            if txt:
                history_lines.append(f"{role}: {txt}")

        return f"""CONVERSATION CONTEXT:
{"\n".join(history_lines)}

USER PROFILE FACTS:
{memory_ctx}

PREFERENCES:
{prefs}

RECENT GOALS ACHIEVED:
{goals}

TOOL FREQUENCY ANALYSIS:
{tools}

CURRENT QUERY:
{prompt}

CRITICAL RULES: Maintain direct historical continuity, rely heavily on preferences, and be concise unless deep technical analysis is needed."""

    def get_response(self, prompt: str) -> str:
        """Computes complete atomic responses for user queries."""
        if not self.initialized:
            return "[System Error]: AI Engine is offline."

        prompt = prompt.strip()
        if not prompt:
            return "[System Error]: Empty prompt received."

        try:
            final_prompt = self._build_prompt(prompt)
            response = self.chat.send_message(
                final_prompt,
                generation_config=self._generation_config()
            )
            if not hasattr(response, "text"):
                return "[System Error]: Empty text chunk processed."
            return response.text.strip()
        except Exception as e:
            print(f"[AI RUNTIME ERROR] Failed generating text: {e}")
            return f"[System Error]: {e}"

    def stream_response(self, prompt: str) -> Generator[str, None, None]:
        """Progressively yields incoming token tokens for immediate UI updates."""
        if not self.initialized:
            yield "[System Error]: AI Engine is offline."
            return

        prompt = prompt.strip()
        if not prompt:
            yield "[System Error]: Empty prompt string."
            return

        try:
            final_prompt = self._build_prompt(prompt)
            response = self.chat.send_message(
                final_prompt,
                generation_config=self._generation_config(),
                stream=True
            )
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"[AI STREAM EXCEPTION] System telemetry captured: {e}")
            yield f"[System Error]: {e}"

    def reset_chat(self) -> None:
        """Flushes transient session buffers while maintaining core prompt bounds."""
        if self.model:
            self.chat = self.model.start_chat(history=[])

    def reload_memory(self) -> None:
        """Forces system prompt synchronization with persistent database updates."""
        self._build_model()

    def is_ready(self) -> bool:
        """Evaluates absolute processing availability status."""
        return self.initialized and self.model is not None and self.chat is not None

    def get_runtime_info(self) -> Dict[str, Any]:
        """Packages runtime engine analytics for service reporting hooks."""
        try:
            ctx_data = bool(self.memory.get_context())
        except Exception:
            ctx_data = False

        return {
            "initialized": self.initialized,
            "ready": self.is_ready(),
            "model": self.model_name,
            "chat_active": self.chat is not None,
            "context_window": self.max_context_messages,
            "memory_loaded": ctx_data,
        }

    def __call__(self, prompt: str) -> str:
        """Alias shortcut redirecting execution pipelines directly into get_response."""
        return self.get_response(prompt)