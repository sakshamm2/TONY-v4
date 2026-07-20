"""
Module   : modules.automation
Project  : T.O.N.Y. v4
Purpose  : Deep OS Automation Engine (Mouse, Keyboard, and GUI Navigation)
"""

from __future__ import annotations
import time
from typing import Dict, Any, Tuple, Optional

# Optional dependency for hardware-level peripheral manipulation
try:
    import pyautogui
    
    # Configure PyAutoGUI Safety Failsafes
    pyautogui.FAILSAFE = True  # Moving mouse to a corner aborts the script
    pyautogui.PAUSE = 0.1      # Adds a baseline delay between all operations
except ImportError:
    pyautogui = None
    print("[SYSTEM WARNING] 'pyautogui' not installed. Advanced automation disabled.")


class AutomationEngine:
    """
    Advanced agent module allowing precise programmatic control over the user's 
    desktop environment, simulating actual human hardware inputs.
    """

    # ==========================================================
    # Keyboard Emulation
    # ==========================================================
    @staticmethod
    def type_text(text: str, interval: float = 0.05) -> Dict[str, Any]:
        """
        Simulates natural human typing on the keyboard.
        """
        if not pyautogui:
            return {"success": False, "error": "Automation dependency missing."}

        try:
            # interval adds a slight delay between keypresses to prevent buffer overflow
            pyautogui.write(text, interval=interval)
            return {"success": True, "message": f"Successfully typed {len(text)} characters."}
        except Exception as e:
            return {"success": False, "error": f"Typing failed: {e}"}

    @staticmethod
    def execute_hotkey(*keys: str) -> Dict[str, Any]:
        """
        Executes a sequence of simultaneous keypresses (e.g., 'ctrl', 'c').
        """
        if not pyautogui:
            return {"success": False, "error": "Automation dependency missing."}

        try:
            pyautogui.hotkey(*keys)
            return {"success": True, "message": f"Executed hotkey sequence: {' + '.join(keys)}"}
        except Exception as e:
            return {"success": False, "error": f"Hotkey execution failed: {e}"}

    @staticmethod
    def press_key(key: str, presses: int = 1) -> Dict[str, Any]:
        """
        Presses a single functional key (e.g., 'enter', 'tab', 'esc') multiple times.
        """
        if not pyautogui:
            return {"success": False, "error": "Automation dependency missing."}

        try:
            pyautogui.press(key, presses=presses)
            return {"success": True, "message": f"Pressed '{key}' {presses} time(s)."}
        except Exception as e:
            return {"success": False, "error": f"Key press failed: {e}"}

    # ==========================================================
    # Mouse Cursor Emulation
    # ==========================================================
    @staticmethod
    def move_to(x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """
        Moves the mouse cursor to specific X/Y coordinate axes on the screen.
        """
        if not pyautogui:
            return {"success": False, "error": "Automation dependency missing."}

        try:
            pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
            return {"success": True, "message": f"Cursor moved to ({x}, {y})."}
        except Exception as e:
            return {"success": False, "error": f"Movement failed: {e}"}

    @staticmethod
    def click(x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1) -> Dict[str, Any]:
        """
        Executes a mouse click. If no coordinates are provided, clicks at the current location.
        """
        if not pyautogui:
            return {"success": False, "error": "Automation dependency missing."}

        try:
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, button=button, clicks=clicks)
                msg = f"Clicked '{button}' at ({x}, {y})."
            else:
                pyautogui.click(button=button, clicks=clicks)
                msg = f"Clicked '{button}' at current cursor location."
                
            return {"success": True, "message": msg}
        except Exception as e:
            return {"success": False, "error": f"Click execution failed: {e}"}

    @staticmethod
    def scroll(clicks: int) -> Dict[str, Any]:
        """
        Scrolls the mouse wheel. Positive clicks scroll up, negative scroll down.
        """
        if not pyautogui:
            return {"success": False, "error": "Automation dependency missing."}

        try:
            pyautogui.scroll(clicks)
            direction = "up" if clicks > 0 else "down"
            return {"success": True, "message": f"Scrolled {direction} by {abs(clicks)} units."}
        except Exception as e:
            return {"success": False, "error": f"Scroll failed: {e}"}

    # ==========================================================
    # Computer Vision / Screen Analytics
    # ==========================================================
    @staticmethod
    def locate_and_click(image_path: str, confidence: float = 0.8) -> Dict[str, Any]:
        """
        Uses OpenCV/PyAutoGUI computer vision to find a UI element on the screen 
        matching the provided image file, and clicks it automatically.
        """
        if not pyautogui:
            return {"success": False, "error": "Automation dependency missing."}

        try:
            # Note: The confidence parameter requires python3-opencv to be installed
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            
            if location:
                pyautogui.click(location)
                return {
                    "success": True, 
                    "message": f"Element found and clicked at coordinates {location}.",
                    "coordinates": {"x": location.x, "y": location.y}
                }
            else:
                return {"success": False, "error": "Image reference not found on screen."}
                
        except pyautogui.ImageNotFoundException:
            return {"success": False, "error": "Image reference not found on screen."}
        except Exception as e:
            return {"success": False, "error": f"Computer vision failure: {e}"}