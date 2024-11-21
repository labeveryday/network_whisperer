# chat_engine.py
import json
import logging
from typing import List, Dict, Any
from tool_handler import handle_tool_use
from bedrock_utils import converse_with_claude, create_converse_request

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M'
)
logger = logging.getLogger(__name__)

def chat(user_input: str, messages: List[Dict[str, Any]], bedrock_client: Any, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Main chat function to interact with Claude, handling tool use and maintaining conversation flow.

    Args:
    user_input (str): The user's input text.
    messages (List[Dict[str, Any]]): The conversation history.
    bedrock_client (Any): The Bedrock client for making API calls.
    tools (List[Dict[str, Any]]): List of available tools for Claude to use.

    Returns:
    List[Dict[str, Any]]: Updated conversation history including Claude's responses and tool uses.

    This function manages the conversation flow, ensuring proper alternation between user and assistant roles,
    and handles any tool use requests from Claude.
    """
    try:
        # Add user input to messages
        #messages.append({"role": "user", "content": [{"text": user_input}]})
        
        while True:
            # Get Claude's response
            request = create_converse_request(messages, tools)
            response = converse_with_claude(bedrock_client, request)

            # Example Use Claude 3 Sonnet
            # request = create_converse_request(messages, tools, model_key="claude_3_sonnet")
            # response = converse_with_claude(bedrock_client, request, model_key="claude_3_sonnet")

            
            if not response or 'content' not in response:
                logger.error("Unexpected response format from Claude.")
                raise ValueError("Invalid response from Claude")
            
            # Process Claude's response
            assistant_message = {"role": "assistant", "content": []}
            for content in response['content']:
                if 'text' in content:
                    logger.info(f"Claude: {content['text']}")
                    assistant_message['content'].append({"text": content['text']})
                elif 'toolUse' in content:
                    tool_use = content['toolUse']
                    logger.info(f"Claude is using the {tool_use['name']} tool.")
                    assistant_message['content'].append({"toolUse": tool_use})
            
            # Add Claude's response to messages
            messages.append(assistant_message)
            
            # Check if Claude used a tool
            if any('toolUse' in item for item in assistant_message['content']):
                # Handle all tool uses
                user_message = {"role": "user", "content": []}
                for item in assistant_message['content']:
                    if 'toolUse' in item:
                        try:
                            tool_result = handle_tool_use(item['toolUse'])
                            user_message['content'].append(tool_result['content'][0])
                        except Exception as e:
                            logger.error(f"Error in tool use: {str(e)}")
                            user_message['content'].append({"toolResult": {"status": "error", "message": str(e)}})
                
                # Add tool results as a user message
                messages.append(user_message)
            else:
                # If no tool was used, we're done
                break
        
        return messages
    except Exception as e:
        logger.error(f"An error occurred in the chat function: {str(e)}")
        raise

def print_conversation(messages: List[Dict[str, Any]]) -> None:
    """
    Print the entire conversation history in a readable format.

    Args:
    messages (List[Dict[str, Any]]): The conversation history to print.

    This function iterates through the conversation history and prints each message,
    including text content, tool uses, and tool results, in a formatted manner.
    """
    print("\n=== Conversation History ===")
    for message in messages:
        role = message['role']
        content = message['content']
        
        print(f"\n{role.capitalize()}:")
        for item in content:
            if 'text' in item:
                print(f"  {item['text']}")
            elif 'toolUse' in item:
                tool_use = item['toolUse']
                print(item)
                print(f"  [Tool Use] {tool_use['name']}")
                print(f"    Input: {json.dumps(tool_use['input'], indent=2)}")
            elif 'toolResult' in item:
                tool_result = item['toolResult']
                print(f"  [Tool Result] Status: {tool_result.get('status', 'N/A')}")
                if 'toolUseId' in tool_result:
                    print(f"    ID: {tool_result['toolUseId']}")
                if 'content' in tool_result:
                    print(f"    Output: {json.dumps(tool_result['content'][0]['json'], indent=2)}")
                if 'message' in tool_result:
                    print(f"    Message: {tool_result['message']}")
        print("-" * 50)