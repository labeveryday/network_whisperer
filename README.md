# Network Whisperer Agent

A Python-based network analysis agent for AWS infrastructure that provides comprehensive insights into your VPC configurations, ec2 and network resources, and other functions.

## Capabilities

The agent provides the following network analysis tools:

### VPC Tools
- List all VPCs in a specified region
- Check Internet Gateway configurations
- Check NAT Gateway configurations
- Retrieve and analyze Route Tables

### Network Tools
- List and analyze subnets within a VPC
- Describe and analyze Network ACLs

### EC2 Tools
- Describe EC2 instances and their configurations
- Analyze Security Groups

### General Tools
- Get current datetime (with timezone support)
- Calculate CIDR range information

>NOTE: All tools can be found in `./network_agent/tools/`clear

## Prerequisites

- Python 3.x
- AWS credentials configured
- Required Python packages (add requirements.txt to your project)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd network_whisperer
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required dependencies:

```bash
pip install -r requirements.txt
```

4. Configure AWS credentials: Ensure you have AWS credentials configured either through:

AWS CLI configuration

Environment variables:

```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-west-2"
```

## Running the Application

### Using Streamlit

1. Cd to the `./network_agent` directory

```bash
cd network_agent/
```

2. Run the application:
   
```bash
streamlit run main.py
```

This will:

- Start the Streamlit server
- Automatically open your default web browser to the application
- Display the Network Whisperer interface

>If the browser doesn't open automatically, you can access the application at http://localhost:8501

### Usage

1. Import the necessary modules in your main.py:

```python
from network_agent.tool_handler import handle_tool_use

# Example usage
tool_request = {
    "name": "list_vpcs",
    "input": {
        "region": "us-west-2"
    },
    "toolUseId": "unique_id"
}

result = handle_tool_use(tool_request)
```

2. Available Tool Commands:

```python
# VPC Operations
list_vpcs(region="us-west-2")
check_internet_gateway(vpc_id, region="us-west-2")
check_nat_gateway(vpc_id, region="us-west-2")
get_route_tables(vpc_id, region="us-west-2")

# Network Operations
list_subnets(vpc_id, region="us-west-2")
describe_network_acls(vpc_id, region="us-west-2")

# EC2 Operations
describe_ec2_instances(region="us-west-2")
describe_security_groups(region="us-west-2")

# Utility Operations
get_current_datetime(timezone="UTC")
calculate_cidr_range(cidr_block)
```

**Default Configuration**
- Default region: us-west-2
- Default timezone: UTC

**Error Handling**
The tool handler returns error messages in the following format:

```json
{
    "error": "Error message description"
}
```

### Best Practices

1. Always specify the region when making API calls
2. Use environment variables for sensitive information
3. Implement proper error handling in your main application
4. Monitor API usage to stay within AWS service limits

## About me

My passions lie in building cool stuff and impacting people's lives. I'm fortunate to weave all these elements together in my role as a Developer Advocate. On GitHub, I share my ongoing learning journey and the projects I'm building. Don't hesitate to reach out for a friendly hello or to ask any questions!

My hangouts:
- [LinkedIn](https://www.linkedin.com/in/duanlightfoot/)
- [YouTube](https://www.youtube.com/@LabEveryday)