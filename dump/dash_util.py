import base64
import uuid
import socket
import ipaddress
import redis
import argparse
import sys
import json
from google.protobuf.message import Message
import google.protobuf.json_format
from dash_api.types_pb2 import Guid, ValueOrRange, IpAddress, IpVersion
from dash_api.appliance_pb2 import Appliance
from dash_api.vnet_pb2 import Vnet
from dash_api.eni_pb2 import Eni, State
from dash_api.qos_pb2 import Qos
from dash_api.route_pb2 import Route
from dash_api.route_rule_pb2 import RouteRule
from dash_api.vnet_mapping_pb2 import VnetMapping
from dash_api.acl_group_pb2 import AclGroup
from dash_api.acl_out_pb2 import AclOut
from dash_api.acl_in_pb2 import AclIn
from dash_api.acl_rule_pb2 import AclRule, Action
from dash_api.prefix_tag_pb2 import PrefixTag
import dash_api.utils as utils
from google.protobuf.json_format import MessageToDict

def json_walk(node, key, f):
    unode = f(node, key)
    if unode != node:
        return unode
    if type(node) is dict:
        return {k: json_walk(v, k, f) for k, v in node.items()}
    elif type(node) is list:
        return [json_walk(x, key, f) for x in node]
    else:
        return f(node, key)


def make_json_walker(k, f):
        def ff(node, key):
            if key == k:
                return f(node)
            return node
        def walker(j):
            return json_walk(j, None, ff)
        return walker
    
def format_ip(node):
    return str(ipaddress.IPv4Address(socket.ntohl(node)))

def format_mac(node):
    b64 = base64.b64decode(node)
    return ':'.join(b64.hex()[i:i+2] for i in range(0,12,2))

def format_uuid(node):
    b64 = base64.b64decode(node['value'])
    return str(uuid.UUID(bytes=b64))

def format_uuid_from_guid(node):
    return str(uuid.UUID(bytes=node))

def format_port_list(node):
    if 'range' in node[0]:
        r = node[0]['range']
        return f"{r.get('min', 0)}-{r.get('max', 0)}"
    return ','.join([str(x['value']) for x in node])

def format_ip_address(node):
    if node.HasField('ipv4'):
        return format_ip(node.ipv4)

def convert_prefix(node):
    l = []
    for prefix in node:
        ip = prefix['ip']['ipv4']
        mask = prefix['mask']['ipv4']
        network = ipaddress.IPv4Network(f'{ip}/{mask}', strict=False)
        l.append(str(network))
    return l

def remove_ipv4_dict(node):
    return node['ipv4']

beautifiers = [
    make_json_walker('ipv4', format_ip),
    make_json_walker('macAddress', format_mac),
    make_json_walker('guid', format_uuid),
    make_json_walker('dstPort', format_port_list),
    make_json_walker('srcPort', format_port_list),
    make_json_walker('dstAddr', convert_prefix),
    make_json_walker('srcAddr', convert_prefix),
    make_json_walker('prefixList', convert_prefix),
    make_json_walker('sip', remove_ipv4_dict),
    make_json_walker('underlayIp', remove_ipv4_dict),
    ]

def get_decoded_value(key,pb):
    r = redis.Redis(host='localhost', port=6379)
    v = r.hgetall(key)
    pb.ParseFromString(v[b'pb'])
    table_name= "DASH_ACL_GROUP_TABLE"
    retval = utils.PbBinaryToJsonString(table_name.encode("utf-8"), v[b'pb'])
    print(retval)
    json_string = json_format.MessageToJson(message)
    print(json_string)
    
    return return_list(pb)


def return_list(pb):
    parsed_dict = {}
    for field_descriptor, value in pb.ListFields():
        field_name = field_descriptor.name
        field_type =  field_descriptor.type
        field_value = None
        if field_type == field_descriptor.TYPE_MESSAGE:
            obj = getattr(pb, field_name)
            if isinstance(obj,IpAddress):
                field_value = format_ip_address(obj)
            if isinstance(obj,Guid):
                field_value = format_uuid_from_guid(obj.value)
            if field_descriptor.label == field_descriptor.LABEL_REPEATED:
                list1 = []
                for value in obj:
                    list1.append(return_list(value))
                field_value = list1
            if field_value is None:
                field_value = return_list(obj)
        elif field_type == field_descriptor.TYPE_ENUM:
            if field_descriptor.enum_type == IpVersion.DESCRIPTOR:
                field_value = IpVersion.Name(value)
            elif field_descriptor.enum_type == Action.DESCRIPTOR:
                field_value = Action.Name(value)
            elif field_descriptor.enum_type == State.DESCRIPTOR:
                field_value = State.Name(value)
            else:
                field_value = str(value)
        else:
            field_value = str(value)
        parsed_dict[field_name] = field_value
    return parsed_dict
