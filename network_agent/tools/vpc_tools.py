import boto3


def list_vpcs(region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_vpcs()
    vpcs = [{'VpcId': vpc['VpcId'], 'CidrBlock': vpc['CidrBlock'], 
             'IsDefault': vpc['IsDefault']} for vpc in response['Vpcs']]
    return {
        'vpcs': vpcs,
        "region": region
    }

def check_internet_gateway(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_internet_gateways(
        Filters=[
            {
                'Name': 'attachment.vpc-id',
                'Values': [vpc_id]
            }
        ]
    )
    internet_gateways = [
        {
            'InternetGatewayId': ig['InternetGatewayId'],
            'AttachedToVpc': vpc_id in [att['VpcId'] for att in ig['Attachments']]
        } for ig in response['InternetGateways']
    ]
    return {
        'vpc_id': vpc_id,
        'internetGateways': internet_gateways
    }

def check_nat_gateway(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_nat_gateways(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            }
        ]
    )
    nat_gateways = [
        {
            'NatGatewayId': natgw['NatGatewayId'],
            'SubnetId': natgw['SubnetId'],
            'State': natgw['State'],
            'PublicIp': natgw['NatGatewayAddresses'][0]['PublicIp'] if natgw['NatGatewayAddresses'] else None
        } for natgw in response['NatGateways']
    ]
    return {
        'vpc_id': vpc_id,
        'NatGateways': nat_gateways
    }

def get_route_tables(vpc_id, region="us-west-2"):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_route_tables(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            }
        ]
    )
    route_tables = []
    for rt in response['RouteTables']:
        routes = []
        for route in rt['Routes']:
            route_data = {
                'DestinationCidrBlock': route.get('DestinationCidrBlock'),
                'GatewayId': route.get('GatewayId'),
                'NatGatewayId': route.get('NatGatewayId'),
                'InstanceId': route.get('InstanceId'),
                'VpcPeeringConnectionId': route.get('VpcPeeringConnectionId'),
                'NetworkInterfaceId': route.get('NetworkInterfaceId')
            }
            routes.append({k: v for k, v in route_data.items() if v is not None})
        
        route_tables.append({
            'RouteTableId': rt['RouteTableId'],
            'IsMain': any(assoc['Main'] for assoc in rt.get('Associations', [])),
            'Routes': routes
        })
    
    return {
        'vpc_id': vpc_id,
        'routeTables': route_tables
    }


vpc_tools = [
    {
        "toolSpec": {
            "name": "list_vpcs",
            "description": "List VPCs in a specified AWS region",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "description": "AWS region (e.g., us-west-2)"}
                    }
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "check_internet_gateway",
            "description": "Check Internet Gateway for a specified VPC",
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
            "name": "check_nat_gateway",
            "description": "Check NAT Gateway for a specified VPC",
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
            "name": "get_route_tables",
            "description": "Get route tables for a specified VPC",
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


def handle_vpc_tool(tool_use):
    tool_name = tool_use['name']
    input_data = tool_use['input']
    
    if tool_name == "list_vpcs":
        result = list_vpcs(region=input_data.get('region', 'us-west-2'))
    elif tool_name == "check_internet_gateway":
        result = check_internet_gateway(input_data['vpc_id'], region=input_data.get('region', 'us-west-2'))
    elif tool_name == "check_nat_gateway":
        result = check_nat_gateway(input_data['vpc_id'], region=input_data.get('region', 'us-west-2'))
    elif tool_name == "get_route_tables":
        result = get_route_tables(input_data['vpc_id'], region=input_data.get('region', 'us-west-2'))
    else:
        result = {"error": f"Unknown VPC tool: {tool_name}"}

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
