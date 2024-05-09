import base64
import uuid
import socket
import ipaddress
import redis
import argparse
import sys
import json
from google.protobuf.message import Message
from dash_api.types_pb2 import Guid,  IpAddress, IpPrefix
from google.protobuf.json_format import MessageToDict
    
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

def format_guid_dict(node):
    b64 = base64.b64decode(node['value'])
    return str(uuid.UUID(bytes=b64))


def format_port_list(node):
    if 'range' in node[0]:
        r = node[0]['range']
        return f"{r.get('min', 0)}-{r.get('max', 0)}"
    return ','.join([str(x['value']) for x in node])

def format_ip_address_dict(node):
    if 'ipv4' in node:
        return format_ip(node['ipv4'])
    
def format_ip_address(node):
    if node.HasField('ipv4'):
        return format_ip(node.ipv4)

def format_ip_prefix(node):
    ip = format_ip_address_dict(node['ip'])
    mask = format_ip_address_dict(node['mask'])
    network = ipaddress.IPv4Network(f'{ip}/{mask}', strict=False)
    return str(network)


def get_decoded_value(key,pb):
    r = redis.Redis(host='localhost', port=6379)
    v = r.hgetall(key)
    print(v)
    pb.ParseFromString(v[b'pb'])
    json_string = MessageToDict(pb,preserving_proto_field_name=True)
    print(json_string)
    json_string = find_known_types_sec(pb,json_string)
    return json_string

decode_types = (IpAddress, Guid, IpPrefix)
decode_fn = {'IpAddress':format_ip_address_dict,'Guid':format_guid_dict, 'mac_address':format_mac, 'IpPrefix': format_ip_prefix}


def find_known_types_sec(pb2_obj,pb2_dict):


    def find_index(proto_obj,proto_dict = pb2_dict):
          for field_descriptor, value in proto_obj.ListFields():
            field_name = field_descriptor.name
            field_type =  field_descriptor.type
            if field_type == field_descriptor.TYPE_MESSAGE:
                obj = getattr(proto_obj, field_name)
                if isinstance(obj,decode_types):
                    class_name = obj.__name__
                    proto_dict[field_name] = decode_fn[class_name](proto_dict[field_name])
                elif field_descriptor.label == field_descriptor.LABEL_REPEATED:
                    final_list = []
                    requires_change = False
                    for ind,value in enumerate(obj):
                        if isinstance(value,Message) and isinstance(value,decode_types):
                            requires_change = True
                            class_name = value.__name__
                            final_list.append(decode_fn[class_name](proto_dict[field_name][ind]))
                        else:
                            find_index(value,proto_dict[field_name][ind])
                    if requires_change:
                        proto_dict[field_name] = final_list
                else:
                    find_index(obj,proto_dict[field_name])
            elif field_name in decode_fn:
                proto_dict[field_name] = decode_fn[field_name](proto_dict[field_name])
    find_index(pb2_obj)
    return pb2_dict
