"""
Module   : tools.memory_tool
Project  : T.O.N.Y. v4
Purpose  : Allows the AI to permanently save user facts to memory.json
"""

import json
import os
from typing import Dict, Any

class MemoryTool:
    """A tool for saving long-term user facts and preferences."""
    
    name = "memory_tool"
    description = "Use this to save important facts about the user (e.g., their name, likes, dislikes) to long-term memory."
    
    def __init__(self, memory_path: str = "memory.json"):
        self.memory_path = memory_path

    def execute(self, fact: str) -> Dict[str, Any]:
        """Saves a string fact to the user_facts array in memory.json."""
        if not fact:
            return {"success": False, "error": "No fact provided to save."}
            
        try:
            # Load existing memory
            if os.path.exists(self.memory_path):
                with open(self.memory_path, "r") as f:
                    data = json.load(f)
            else:
                data = {"user_facts": []}
                
            # Ensure the array exists
            if "user_facts" not in data:
                data["user_facts"] = []
                
            # Append the new fact
            if fact not in data["user_facts"]:
                data["user_facts"].append(fact)
            
            # Save it back to the file
            with open(self.memory_path, "w") as f:
                json.dump(data, f, indent=4)
                
            return {
                "success": True, 
                "message": f"Successfully committed to long-term memory: '{fact}'"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to save memory: {str(e)}"}