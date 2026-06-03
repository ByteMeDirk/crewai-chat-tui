# tools/__init__.py
# Export all tools here so agent.py can import from a single place.
# To add a new tool: create tools/my_tool.py, add it to this list.

from tools.system_info import SystemInfoTool

ALL_TOOLS = [SystemInfoTool()]
