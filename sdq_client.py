#!/usr/bin/env python3
import argparse
import json
import redis_handler
import base64

def main():
    parser = argparse.ArgumentParser(description='Client script to send and receive jobs via Redis.')
    parser.add_argument('job_file', type=str, help='JSON file containing the job contents.')
    args = parser.parse_args()
    
    with open(args.job_file, 'r') as f:
        job_contents = json.load(f)
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    redis_connection = redis_handler.connect_to_redis(config)
    base_queue_name = config['ingress_queue']
    return_queue = config['return_queue']
    print("Sending job to ingress queue...")
    redis_handler.send_job_to_ingress_queue(redis_connection, base_queue_name, job_contents, return_queue, "test.png")
    print("Waiting for response...")
    job = redis_handler.read_from_return_queue(redis_connection, return_queue)
    request = job['request']
    response = job['response']

    label = request['label']
    for i, image in enumerate(response):
        image = base64.b64decode(image)
        filename = f"{label}_{i}.png"
        with open(filename, 'wb') as f:
            f.write(image)

if __name__ == '__main__':
    main()
