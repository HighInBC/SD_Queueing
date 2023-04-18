#!/usr/bin/env python3
import argparse
import json
import redis_handler
import base64

def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='Client script to send and receive jobs via Redis.')
    parser.add_argument('job_file', type=str, help='JSON file containing the job contents.')
    args = parser.parse_args()
    
    # Load the job contents from the JSON file
    with open(args.job_file, 'r') as f:
        job_contents = json.load(f)
    
    # Load the Redis configuration from the config file
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Connect to Redis using the configuration
    redis_connection = redis_handler.connect_to_redis(config)
    
    # Extract the ingress queue and return queue from the config
    base_queue_name = config['ingress_queue']
    return_queue = config['return_queue']
    
    # Send the job to the ingress queue
    print("Sending job to ingress queue...")
    redis_handler.send_job_to_ingress_queue(redis_connection, base_queue_name, job_contents, return_queue, "test.png")
    print("Job sent to ingress queue.")
    
    # Wait for and read the response from the return queue
    print("Waiting for response...")
    job = redis_handler.read_from_return_queue(redis_connection, return_queue)
    request = job['request']
    response = job['response']

    # response is an array of base64-encoded png images. Save based on the label.
    label = request['label']
    for i, image in enumerate(response):
        # base64 decode the image
        image = base64.b64decode(image)
        filename = f"{label}_{i}.png"
        with open(filename, 'wb') as f:
            f.write(image)


if __name__ == '__main__':
    main()
