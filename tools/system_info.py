"""
tools/system_info.py - Mocked "system info" tool.

This demonstrates the CrewAI BaseTool interface. The _run() method currently
returns hardcoded mock data. To make it real, replace the body of _run() with
actual system calls (e.g. psutil, subprocess, os).

Pattern for adding more tools:
  1. Copy this file, rename class and `name`/`description`.
  2. Implement _run() with real logic.
  3. Import and add to tools/__init__.py ALL_TOOLS list.
  4. Pass ALL_TOOLS to the Agent's `tools=` argument in agent.py.
"""
import json
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SystemInfoInput(BaseModel):
    """Input schema for SystemInfoTool. No arguments required."""
    query: str = Field(
        default="all",
        description="What system info to retrieve: 'all', 'cpu', 'memory', or 'disk'.",
    )


class SystemInfoTool(BaseTool):
    """
    Returns basic system resource information (mocked).
    Use this when the user asks about system status, resource usage, or
    machine health.
    """

    name: str = "system_info"
    description: str = (
        "Returns current system information such as CPU usage, memory, and disk. "
        "Call this when the user asks about system status or machine resources."
    )
    args_schema: Type[BaseModel] = SystemInfoInput

    def _run(self, query: str = "all") -> str:
        """
        MOCK IMPLEMENTATION - returns static data.
        Replace with real psutil calls when ready:

            import psutil
            return json.dumps({
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
            })
        """
        mock_data = {
            "cpu_percent": 14.2,
            "memory_percent": 61.8,
            "disk_percent": 43.0,
            "note": "[MOCK] This data is not real. Implement _run() with psutil for live data.",
        }

        if query == "cpu":
            return json.dumps({"cpu_percent": mock_data["cpu_percent"]})
        if query == "memory":
            return json.dumps({"memory_percent": mock_data["memory_percent"]})
        if query == "disk":
            return json.dumps({"disk_percent": mock_data["disk_percent"]})

        return json.dumps(mock_data)
