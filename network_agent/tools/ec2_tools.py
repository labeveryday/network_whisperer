import boto3


def describe_instances(region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances()
    instance_ids = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_ids.append(instance["InstanceId"])
    return {
        "InstanceIds": instance_ids,
        "region": region
    }


# Describe security groups in a region
def describe_security_groups(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_security_groups(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            }
        ]
    )
    
    security_groups = []
    for sg in response['SecurityGroups']:
        inbound_rules = []
        outbound_rules = []
        
        # Format inbound rules
        for rule in sg['IpPermissions']:
            port_range = f"{rule.get('FromPort', 'All')} - {rule.get('ToPort', 'All')}"
            for ip_range in rule.get('IpRanges', []):
                inbound_rules.append({
                    'Protocol': rule.get('IpProtocol', '-1'),
                    'Ports': port_range,
                    'Source': ip_range.get('CidrIp'),
                    'Description': ip_range.get('Description', '')
                })
            
            # Include security group references
            for group in rule.get('UserIdGroupPairs', []):
                inbound_rules.append({
                    'Protocol': rule.get('IpProtocol', '-1'),
                    'Ports': port_range,
                    'Source': f"sg-{group.get('GroupId')}",
                    'Description': group.get('Description', '')
                })
        
        # Format outbound rules
        for rule in sg['IpPermissionsEgress']:
            port_range = f"{rule.get('FromPort', 'All')} - {rule.get('ToPort', 'All')}"
            for ip_range in rule.get('IpRanges', []):
                outbound_rules.append({
                    'Protocol': rule.get('IpProtocol', '-1'),
                    'Ports': port_range,
                    'Destination': ip_range.get('CidrIp'),
                    'Description': ip_range.get('Description', '')
                })
            
            # Include security group references
            for group in rule.get('UserIdGroupPairs', []):
                outbound_rules.append({
                    'Protocol': rule.get('IpProtocol', '-1'),
                    'Ports': port_range,
                    'Destination': f"sg-{group.get('GroupId')}",
                    'Description': group.get('Description', '')
                })
        
        security_groups.append({
            'GroupId': sg['GroupId'],
            'GroupName': sg['GroupName'],
            'Description': sg['Description'],
            'InboundRules': inbound_rules,
            'OutboundRules': outbound_rules
        })
    
    return security_groups



ec2_tools = [
    {
        "toolSpec": {
            "name": "describe_instances",
            "description": "List ec2 instances in all a region",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "description": "AWS region (e.g., us-west-2)"}
                    },
                    "required": []
                }
            } 
        }
    },
    {
        "toolSpec": {
            "name": "describe_security_groups",
            "description": "Describe security groups in a specified AWS region",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {"type": "string", "description": "VPC ID"},
                        "region": {"type": "string", "description": "AWS region (e.g., us-west-2)"},
                    },
                    "required": ["vpc_id"]
                }
            }
        }
    }
]


def handle_ec2_tool(tool_use):
    tool_name = tool_use['name']
    input_data = tool_use['input']
    
    if tool_name == "describe_instances":
        result = describe_instances(region=input_data.get('region', 'us-west-2'))
    elif tool_name == "describe_security_groups":
        result = describe_security_groups(region=input_data.get('region', 'us-west-2'))
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
