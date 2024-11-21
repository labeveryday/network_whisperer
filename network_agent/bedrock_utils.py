# bedrock_utils.py
import boto3
import json
import logging
from botocore.exceptions import BotoCoreError, ClientError
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M'
)
logger = logging.getLogger(__name__)


# Define available models
AVAILABLE_MODELS = {
    "claude_3_sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "claude_3_haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    "claude_2": "anthropic.claude-v2:1",
    # Add more models as needed
}

# Default model
DEFAULT_MODEL = "claude_3_haiku"


SYSTEM_MESSAGE = """
You are an AWS Network Assistant, designed to help with AWS networking tasks and queries. \
Your role is to provide accurate information and assist with AWS networking operations using the tools provided. Follow these guidelines strictly:

1. Tool Usage:
   - Always use the provided tools to fetch real data. Never invent or assume information.
   - If a tool requires information that hasn't been provided (e.g., region or VPC ID), ask the user for this information before using the tool.
   - Explain which tool you're using and why before you use it.

2. Responses:
   - Be honest and transparent. If you don't have enough information or if the tools don't provide the necessary data, say so clearly.
   - Never make up examples or hypothetical data. Stick to facts from tool outputs or general AWS knowledge.
   - If you're unsure about something, express your uncertainty and suggest using a tool to verify.

3. AWS Resources:
   - Remember that AWS resource IDs (like VPC IDs, subnet IDs, etc.) are specific and should never be invented.
   - If asked about specific resources without context, always ask for clarification or suggest using a tool to list the resources first.

4. Clarity and Education:
   - Explain AWS concepts clearly when relevant to the user's query.
   - If a user's request is unclear or could be interpreted in multiple ways, ask for clarification.

5. Tool Limitations:
   - Be aware of the limitations of your tools. If a user asks for something beyond your tools' capabilities, explain this limitation clearly.

6. Privacy and Security:
   - Do not ask for or store AWS credentials or sensitive information.
   - Remind users not to share sensitive information if they attempt to do so.

Remember, your primary goal is to assist with AWS networking tasks accurately and safely. \
Always prioritize providing correct information over guessing or making assumptions.
"""


def initialize_bedrock_client(region_name: str = "us-west-2") -> boto3.client:
    """
    Initialize and return a Bedrock runtime client.

    This function creates a boto3 client for the Bedrock runtime service.
    It's used to interact with the Bedrock API for model invocations.

    Args:
    region_name (str): The AWS region to connect to. Defaults to "us-east-1".

    Returns:
    boto3.client: A configured Bedrock runtime client.

    Raises:
    BotoCoreError: If there's an issue creating the Bedrock client.
    """
    try:
        client = boto3.client("bedrock-runtime", region_name=region_name)
        logger.info(f"Bedrock client initialized for region: {region_name}")
        return client
    except BotoCoreError as e:
        logger.error(f"Failed to initialize Bedrock client: {str(e)}")
        raise


def create_converse_request(messages: List[Dict[str, Any]], tools: List[Dict[str, Any]],
    max_tokens: int = 500, temperature: float = 0.7, top_p: float = 1, model_key: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Create a request object for the Bedrock converse API.
    """
    try:
        model_id = AVAILABLE_MODELS.get(model_key)
        if not model_id:
            raise ValueError(f"Invalid model key: {model_key}. Available models are: {', '.join(AVAILABLE_MODELS.keys())}")

        request = {
            "modelId": model_id,
            "messages": messages,
            "system": [{"text": SYSTEM_MESSAGE}],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p
            },
            "toolConfig": {
                "tools": tools,
                "toolChoice": {"auto":{}}
            }
        }
        logger.debug(f"Created converse request for model: {model_id}")
        return request
    except Exception as e:
        logger.error(f"Error creating converse request: {str(e)}")
        raise




def converse_with_claude(bedrock_client: boto3.client, request: Dict[str, Any], model_key: str = DEFAULT_MODEL) -> Optional[Dict[str, Any]]:
    """
    Send a request to Claude via the Bedrock converse API.

    This function sends the prepared request to the Bedrock API and handles the response.

    Args:
    bedrock_client (boto3.client): The Bedrock runtime client.
    request (Dict[str, Any]): The prepared request payload.
    model_key (str): Key for the model to use. Defaults to DEFAULT_MODEL.

    Returns:
    Optional[Dict[str, Any]]: The model's response message, or None if an error occurred.

    Raises:
    ClientError: If there's an API-specific error from Bedrock.
    ValueError: If an invalid model key is provided.
    Exception: For any other unexpected errors.
    """
    try:
        model_id = AVAILABLE_MODELS.get(model_key)
        if not model_id:
            raise ValueError(f"Invalid model key: {model_key}. Available models are: {', '.join(AVAILABLE_MODELS.keys())}")

        request["modelId"] = model_id  # Ensure the correct model ID is used
        response = bedrock_client.converse(**request)
        logger.info(f"Successfully received response from Bedrock using model: {DEFAULT_MODEL}")
        return response['output']['message']
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Bedrock API error: {error_code} - {error_message}")
        if error_code == "ValidationException":
            logger.warning("Check if the conversation alternates correctly between user and assistant roles")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in converse_with_claude: {str(e)}")
        raise