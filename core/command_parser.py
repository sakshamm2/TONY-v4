"""
Module   : core.command_parser
Project  : T.O.N.Y. v4
Purpose  : Regex Engine for Extracting Runtime Commands and Memories
"""

from __future__ import annotations
import re
from typing import List, Optional, Tuple

class CommandParser:
    """
    Utility parser responsible for scanning, tokenizing, and stripping 
    inline control markup and memory triggers within unstructured AI text.
    """
    # Pre-compiled regular expressions for runtime performance optimization
    COMMAND_PATTERN = re.compile(r"\|CMD:(.*?)\|")
    MEMORY_PATTERN = re.compile(r"\|CMD:remember:(.*?)\|")

    @staticmethod
    def parse(response: str) -> Tuple[str, List[str]]:
        """
        Parses raw text responses to isolate functional desktop commands 
        and extracts clean, reader-ready string dialogue.
        """
        if not response:
            return "", []

        commands: List[str] = []
        raw_matches = CommandParser.COMMAND_PATTERN.findall(response)

        for cmd in raw_matches:
            cmd_clean = cmd.strip()
            if not cmd_clean or cmd_clean.startswith("remember:"):
                continue
            commands.append(cmd_clean)

        # Strip out markup tags and sanitize excessive newline gaps
        clean_text = CommandParser.COMMAND_PATTERN.sub("", response).strip()
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)

        return clean_text, commands

    @staticmethod
    def extract_memory(response: str) -> Optional[str]:
        """
        Scans response blocks for deliberate long-term memory updates.
        Example target: |CMD:remember:User prefers dark mode|
        """
        if not response:
            return None

        match = CommandParser.MEMORY_PATTERN.search(response)
        if not match:
            return None

        extracted = match.group(1).strip()
        return extracted if extracted else None

    @staticmethod
    def has_commands(response: str) -> bool:
        """Evaluates whether the provided text contains any inline execution commands."""
        return bool(CommandParser.COMMAND_PATTERN.search(response))

    @staticmethod
    def command_count(response: str) -> int:
        """Returns the total volume of control patterns embedded in the text block."""
        return len(CommandParser.COMMAND_PATTERN.findall(response))

    @staticmethod
    def get_commands(response: str) -> List[str]:
        """Convenience method returning isolated automation tasks."""
        _, commands = CommandParser.parse(response)
        return commands

    @staticmethod
    def remove_commands(response: str) -> str:
        """Convenience method returning markup-free structural text."""
        clean_text, _ = CommandParser.parse(response)
        return clean_text

    @staticmethod
    def contains_memory(response: str) -> bool:
        """Evaluates whether the given string triggers a persistent memory block."""
        return CommandParser.extract_memory(response) is not None