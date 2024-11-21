# tools/general_tools.py
from datetime import datetime
import pytz
from typing import Dict, Any


def get_current_datetime(timezone_str: str = "UTC") -> Dict[str, str]:
    """
    Get the current date and time in the specified timezone.

    This function returns the current date and time for a given timezone.
    If no timezone is specified, it defaults to UTC.

    Args:
    timezone_str (str): The timezone to use (e.g., "America/New_York", "Europe/London").

    Returns:
    Dict[str, str]: A dictionary containing the formatted datetime and the timezone used.
                    If an error occurs, it returns a dictionary with an error message.

    Raises:
    pytz.exceptions.UnknownTimeZoneError: If an invalid timezone is provided.
    """
    try:
        tz = pytz.timezone(timezone_str)
        current_time = datetime.now(tz)
        return {
            "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "timezone": timezone_str
        }
    except pytz.exceptions.UnknownTimeZoneError:
        return {"error": f"Unknown timezone: {timezone_str}"}


def calculate_cidr_range(cidr: str) -> Dict[str, Any]:
    """
    Calculate the range of IP addresses for a given CIDR notation.

    This function takes a CIDR notation and returns details about the IP range,
    including the network address, broadcast address, number of addresses, and netmask.

    Args:
    cidr (str): The CIDR notation (e.g., "192.168.1.0/24").

    Returns:
    Dict[str, Any]: A dictionary containing CIDR range details or an error message
                    if the CIDR notation is invalid.

    Raises:
    ValueError: If the CIDR notation is invalid.
    """
    try:
        from ipaddress import ip_network
        network = ip_network(cidr)
        return {
            "network_address": str(network.network_address),
            "broadcast_address": str(network.broadcast_address),
            "num_addresses": network.num_addresses,
            "netmask": str(network.netmask)
        }
    except ValueError as e:
        return {"error": f"Invalid CIDR notation: {str(e)}"}


general_tools = [
    {
        "toolSpec": {
            "name": "get_current_datetime",
            "description": "Get the current date and time in a specified timezone",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "utc": {"type": "string", "description": "The timezone to use (e.g., UTC)"}
                    },
                    "required": []
                }
            } 
        }
    },
    {
        "toolSpec": {
            "name": "calculate_cidr_range",
            "description": "Calculate the range of IP addresses for a given CIDR notation",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "cidr": {"type": "string", "description": "The CIDR notation (e.g., 192.168.1.0/24)"}
                    },
                    "required": ["cidr"]
                }
            } 
        }
    }
]


def handle_general_tool(tool_use: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle general tool use requests.

    Args:
    tool_use (Dict[str, Any]): A dictionary containing the tool use request details.

    Returns:
    Dict[str, Any]: The result of the tool operation or an error message.
    """
    tool_name = tool_use['name']
    input_data = tool_use['input']

    try:
        if tool_name == "get_current_datetime":
            result = get_current_datetime(input_data.get('timezone', 'UTC'))
        elif tool_name == "calculate_cidr_range":
            result = calculate_cidr_range(input_data['cidr'])
        else:
            return {"error": f"Unknown general tool: {tool_name}"}

        return {
            "toolResult": {
                "toolUseId": tool_use['toolUseId'],
                "content": [{"json": result}],
                "status": "success"
            }
        }
    except Exception as e:
        return {
            "toolResult": {
                "toolUseId": tool_use['toolUseId'],
                "content": [{"json": {"error": str(e)}}],
                "status": "error"
            }
        }