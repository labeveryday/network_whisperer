import boto3


def list_subnets(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    subnets = [{'SubnetId': subnet['SubnetId'], 'CidrBlock': subnet['CidrBlock'], 'AvailabilityZone': subnet['AvailabilityZone']} for subnet in response['Subnets']]
    return {
        'vpc_id': vpc_id,
        'subnets': subnets,
        "region": region
    }


def describe_network_acls(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_network_acls(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    nacls = [{'NetworkAclId': nacl['NetworkAclId'], 'IsDefault': nacl['IsDefault']} for nacl in response['NetworkAcls']]
    return {
        'vpc_id': vpc_id,
        'network_acls': nacls,
        "region": region
    }


network_tools = [
    {
        "toolSpec": {
            "name": "list_subnets",
            "description": "List subnets in a specified VPC",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {"type": "string", "description": "VPC ID"},
                        "region": {"type": "string", "description": "AWS region (e.g., us-west-2)"}
                    },
                    "required": ["vpc_id"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "describe_network_acls",
            "description": "Describe Network ACLs for a specified VPC",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {"type": "string", "description": "VPC ID"},
                        "region": {"type": "string", "description": "AWS region (e.g., us-west-2)"}
                    },
                    "required": ["vpc_id"]
                }
            }
        }
    }
]


def handle_network_tool(tool_use):
    tool_name = tool_use['name']
    input_data = tool_use['input']
    
    if tool_name == "list_subnets":
        result = list_subnets(input_data['vpc_id'], region=input_data.get('region', 'us-west-2'))
    elif tool_name == "describe_network_acls":
        result = describe_network_acls(input_data['vpc_id'], region=input_data.get('region', 'us-west-2'))
    else:
        result = {"error": f"Unknown network tool: {tool_name}"}

    return {
        "role": "user",
        "content": [
            {
                "toolResult": {
                    "toolUseId": tool_use['toolUseId'],
                    "content": [{"json": result}],
                    "status": "success"
                }
            }
        ]
    }