from .vpc_tools import vpc_tools, handle_vpc_tool
from .network_tools import network_tools, handle_network_tool
from .ec2_tools import ec2_tools, handle_ec2_tool
from .general_tools import general_tools, handle_general_tool


def get_all_tools():
    return vpc_tools + network_tools + ec2_tools + general_tools


def handle_tool(tool_use):
    tool_name = tool_use['name']
    if tool_name in [tool['toolSpec']['name'] for tool in vpc_tools]:
        return handle_vpc_tool(tool_use)
    elif tool_name in [tool['toolSpec']['name'] for tool in network_tools]:
        return handle_network_tool(tool_use)
    elif tool_name in [tool['toolSpec']['name'] for tool in ec2_tools]:
        return handle_ec2_tool(tool_use)
    elif tool_name in [tool['toolSpec']['name'] for tool in general_tools]:
        return handle_general_tool(tool_use)
    else:
        return {"error": f"Unknown tool: {tool_name}"}
