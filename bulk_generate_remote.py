#!/usr/bin/env python3

import argparse
import base64
import itertools
import json
import os
import random
import requests
import redis_handler
from datetime import datetime
from sshtunnel import SSHTunnelForwarder

def parse_args():
    parser = argparse.ArgumentParser(description='A script to generate images using provided target and server information.')
    parser.add_argument('-t', '--target', type=str,            required=True, help='The JSON file containing the information for the task.')
    parser.add_argument('-c', '--config', type=str,            required=True, help='The JSON file defining the redis connection.')
    parser.add_argument('-s', '--size',  type=int,             required=True, help='The number of images to generate total.')
    parser.add_argument('-b', '--batch',  type=int,            default=2,     help='The number of images to generate per batch(limited by server max).')
    parser.add_argument('-p', '--path',   type=str,            required=True, help='The base label to store the files.')
    parser.add_argument('-x', '--srx',    type=str,                           help='Search and replace for axis X in the format: <original>,<alt1>,<alt2>')
    parser.add_argument('-y', '--sry',    type=str,                           help='Search and replace for axis Y in the format: <original>,<alt1>,<alt2>')
    parser.add_argument('-z', '--srz',    type=str,                           help='Search and replace for axis Z in the format: <original>,<alt1>,<alt2>')
    return parser.parse_args()

def create_ssh_tunnel(config):
    tunnel_config = config["ssh_tunnel"]
    print("Creating SSH tunnel to {}@{}:{}".format(tunnel_config["username"], tunnel_config["host"], tunnel_config["port"]))
    tunnel = SSHTunnelForwarder(
        (tunnel_config["host"], tunnel_config["port"]),
        ssh_username=tunnel_config["username"],
        ssh_pkey=tunnel_config["key_file"],
        remote_bind_address=(tunnel_config["remote_bind_address"], tunnel_config["remote_bind_port"])
    )
    tunnel.start()
    print("SSH tunnel started.")
    return tunnel

def combine_arrays(*args):
    if not args:
        return []
    args = [list(arg) for arg in args if isinstance(arg, (list, tuple)) and arg]
    combinations = list(itertools.product(*args))
    result = [list(combination) for combination in combinations]
    return result or []

def main():
    args = parse_args()

    target_file  = args.target
    image_count  = args.size
    output_path  = args.path
    batch_size   = args.batch
    config_file  = args.config

    srx = args.srx.split(',') if args.srx else None
    sry = args.sry.split(',') if args.sry else None
    srz = args.srz.split(',') if args.srz else None

    with open(config_file, 'r') as f:
        config = json.load(f)

    base_queue_name = config['ingress_queue']
    return_queue = config['return_queue']

    tunnel = create_ssh_tunnel(config)

    config["redis_port"] = tunnel.local_bind_port
    config["redis_host"] = "127.0.0.1"

    redis_connection = redis_handler.connect_to_redis(config)

    root_path = 'bulk_images'
    target_path = os.path.join(root_path, output_path)
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    with open(target_file, 'r') as f:
        payload = json.load(f)

    changes         = combine_arrays(srx, sry, srz)
    originals       = changes[0]
    original_prompt = payload['prompt']
    loops_needed = image_count / len(changes) // batch_size
    print("Loops needed: {}".format(loops_needed))
    for i in range(int(loops_needed)):
        print("Loop: {}".format(i))
        for change in changes:
            prompt = original_prompt
            for i in range(len(change)): 
                if originals[i] not in prompt:
                    print("Error: Original not found in prompt: "+originals[i])
                    exit()
                prompt = prompt.replace(originals[i], change[i], 1)

            payload['prompt'] = prompt
            payload['batch_size'] = batch_size
            redis_handler.send_job_to_ingress_queue(redis_connection, base_queue_name, payload, return_queue, [root_path,output_path,*change])
            print(".")
        print("Done sending jobs for loop: {}".format(i))
    print("Done generating images.")

if __name__ == "__main__":
    main()