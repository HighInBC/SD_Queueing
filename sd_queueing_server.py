#!/usr/bin/env python3

import json
from redis_handler import connect_to_redis, read_from_ingress_queue, send_response_to_return_queue
from sd_handler import process_stable_diffusion_request

def load_config():
    """
    Load configuration from "config.json" and return the configuration dictionary.
    """
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    return config

def main():
    # Load configuration
    config = load_config()

    # Connect to Redis
    redis_connection = connect_to_redis(config)

    while True:
        # Read from the ingress queue
        request, return_queue = read_from_ingress_queue(redis_connection, config["ingress_queue"])

        # Process the Stable Diffusion request
        base64_images = process_stable_diffusion_request(request)

        # Send the response to the return queue
        send_response_to_return_queue(redis_connection, return_queue, request, base64_images)
        break

if __name__ == "__main__":
    main()
