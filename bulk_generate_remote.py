#!/usr/bin/env python3

import argparse
import itertools
import json
import os
import sdq.redis_handler
from sdq.sd_handler import get_payload_from_png

def parse_args():
    parser = argparse.ArgumentParser(description='A script to generate images using provided target and server information.')
    parser.add_argument('-t', '--target',   type=str, required=True, help='The JSON file containing the information for the task.')
    parser.add_argument('-c', '--config',   type=str, required=True, help='The JSON file defining the redis connection.')
    parser.add_argument('-s', '--size',     type=int, required=True, help='The number of images to generate total.')
    parser.add_argument('-b', '--batch',    type=int, default=2,     help='The number of images to generate per batch(limited by server max).')
    parser.add_argument('-p', '--path',     type=str, required=True, help='The base label to store the files.')
    parser.add_argument('-r', '--priority', type=int, default=0,     help='The priority of the job. Higher priority jobs are processed first.')
    parser.add_argument('-x', '--srx',      type=str,                help='Search and replace for axis X in the format: <original>,<alt1>,<alt2>')
    parser.add_argument('-y', '--sry',      type=str,                help='Search and replace for axis Y in the format: <original>,<alt1>,<alt2>')
    parser.add_argument('-z', '--srz',      type=str,                help='Search and replace for axis Z in the format: <original>,<alt1>,<alt2>')
    return parser.parse_args()

def load_payload(target_file):
    file_ext = os.path.splitext(target_file)[1]

    if file_ext == '.json':
        with open(target_file, 'r') as f:
            payload = json.load(f)
    elif file_ext == '.png':
        payload = get_payload_from_png(target_file)
    else:
        raise ValueError("Unsupported file type. Please provide a .json or .png file.")

    return payload

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
    priority     = args.priority

    srx = args.srx.split(',') if args.srx else None
    sry = args.sry.split(',') if args.sry else None
    srz = args.srz.split(',') if args.srz else None

    with open(config_file, 'r') as f:
        config = json.load(f)

    base_queue_name = config['ingress_queue']
    return_queue = config['return_queue']

    redis_connection = sdq.redis_handler.connect_to_redis(config)

    root_path = 'bulk_images'

    payload = load_payload(target_file)
    print("Payload loaded: {}".format(payload))

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
            sdq.redis_handler.send_job_to_ingress_queue(redis_connection, base_queue_name, payload, return_queue, [root_path,output_path,*change], priority)
            print(".")
    print("Done generating images.")

if __name__ == "__main__":
    main()