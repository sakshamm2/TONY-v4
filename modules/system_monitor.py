"""
Module   : modules.system_monitor
Project  : T.O.N.Y. v4
Purpose  : Hardware Diagnostics and Live Telemetry Polling Engine
"""

from __future__ import annotations
import psutil # type: ignore
from typing import Dict, Any

class SystemMonitor:
    """
    Utility class for safely extracting realtime hardware usage metrics 
    for UI Dashboards and LLM context bridging.
    """
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Fetches live system statistics including CPU, RAM, and Battery state.
        Failsafes are included for desktop constraints without battery sensors.
        """
        stats: Dict[str, Any] = {}
        
        try:
            # Polling Core Architecture Loads
            stats["cpu"] = psutil.cpu_percent(interval=None)
            stats["ram"] = psutil.virtual_memory().percent
            
            # Polling Power Supply Metrics (Gracefully handles desktop PCs)
            battery = psutil.sensors_battery()
            if battery:
                stats["battery"] = battery.percent
                stats["power_plugged"] = battery.power_plugged
            else:
                stats["battery"] = 100.0
                stats["power_plugged"] = True
                
        except Exception as e:
            print(f"[MONITOR WARNING] Failed to acquire hardware telemetry: {e}")
            stats["cpu"] = 0.0
            stats["ram"] = 0.0
            stats["battery"] = 0.0
            stats["power_plugged"] = True

        return stats