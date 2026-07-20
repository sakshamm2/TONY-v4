"""
Module   : modules.pc_control
Project  : T.O.N.Y. v4
Purpose  : Desktop Automation Controller for Native OS Integrations
"""

from __future__ import annotations
import os
import subprocess
import webbrowser
from datetime import datetime

# Optional dependency for media and hardware control pipelines
try:
    import pyautogui
except ImportError:
    pyautogui = None
    print("[SYSTEM WARNING] pyautogui not installed. Hardware/Media controls disabled.")

class PCController:
    """
    Direct interface bridging high-level agent intentions with low-level Windows OS processes.
    """
    @staticmethod
    def execute_command(cmd_string: str) -> str:
        """Parses and fires localized desktop operations based on recognized commands."""
        cmd = cmd_string.lower().strip()

        try:
            # ==========================================================
            # Web Browsing Intercepts
            # ==========================================================
            if "open_chrome" in cmd or "open_browser" in cmd:
                webbrowser.open("https://www.google.com")
                return "Opening web browser."

            elif "open_youtube" in cmd:
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube."

            # ==========================================================
            # Application Spawning
            # ==========================================================
            elif "open_notepad" in cmd:
                subprocess.Popen("notepad.exe")
                return "Opening Notepad."
            
            elif "open_calculator" in cmd:
                subprocess.Popen("calc.exe")
                return "Opening Calculator."
            
            elif "open_paint" in cmd:
                subprocess.Popen("mspaint.exe")
                return "Opening Paint."
            
            elif "open_explorer" in cmd:
                subprocess.Popen("explorer.exe")
                return "Opening File Explorer."
            
            elif "open_clock" in cmd:
                subprocess.Popen(["explorer.exe", "shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"])
                return "Opening Clock."
            
            elif "open_settings" in cmd:
                subprocess.Popen(["cmd", "/c", "start", "ms-settings:"], shell=True)
                return "Opening Settings."
            
            elif "open_cmd" in cmd:
                subprocess.Popen("cmd.exe")
                return "Opening Command Prompt."
            
            elif "open_powershell" in cmd:
                subprocess.Popen("powershell.exe")
                return "Opening PowerShell."
            
            elif "open_task_manager" in cmd:
                subprocess.Popen("taskmgr.exe")
                return "Opening Task Manager."
            
            elif "open_control_panel" in cmd:
                subprocess.Popen("control.exe")
                return "Opening Control Panel."
            
            elif "open_snipping_tool" in cmd:
                subprocess.Popen("snippingtool.exe")
                return "Opening Snipping Tool."

            # ==========================================================
            # System State Control
            # ==========================================================
            elif "lock_pc" in cmd:
                subprocess.Popen("rundll32.exe user32.dll,LockWorkStation")
                return "Locking PC."
            
            elif "shutdown_pc" in cmd:
                subprocess.Popen("shutdown /s /t 0", shell=True)
                return "Shutting down the system."
            
            elif "restart_pc" in cmd:
                subprocess.Popen("shutdown /r /t 0", shell=True)
                return "Restarting the system."

            # ==========================================================
            # Hardware & Media Controls (Requires pyautogui)
            # ==========================================================
            elif pyautogui:
                if "volume_up" in cmd:
                    pyautogui.press("volumeup", presses=5)
                    return "Increasing system volume."
                
                elif "volume_down" in cmd:
                    pyautogui.press("volumedown", presses=5)
                    return "Decreasing system volume."
                
                elif "volume_mute" in cmd:
                    pyautogui.press("volumemute")
                    return "Muting system volume."
                
                elif "media_play_pause" in cmd:
                    pyautogui.press("playpause")
                    return "Toggling media playback."
                
                elif "media_next" in cmd:
                    pyautogui.press("nexttrack")
                    return "Skipping to next track."
                
                elif "media_previous" in cmd:
                    pyautogui.press("prevtrack")
                    return "Returning to previous track."

                # Capture Pipeline
                elif "take_screenshot" in cmd:
                    os.makedirs("screenshots", exist_ok=True)
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filepath = os.path.join("screenshots", f"screenshot_{timestamp}.png")
                    
                    pyautogui.screenshot(filepath)
                    
                    # Note: os.startfile is Windows exclusive, aligning with the .exe commands above.
                    if os.name == 'nt':
                        os.startfile(filepath)
                        
                    return f"Screenshot successfully saved to {filepath}"

            # Fallback Failure State
            return f"Command '{cmd_string}' is not supported or lacks module dependencies."

        except Exception as e:
            return f"Failed to execute '{cmd_string}'. Internal Error: {e}"