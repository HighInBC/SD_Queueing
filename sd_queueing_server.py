#!/usr/bin/env python3
import json
import time
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
    config = load_config()
    redis_connection = connect_to_redis(config)

    while True:
        print("Reading from ingress queue...")
        response = read_from_ingress_queue(redis_connection, config["ingress_queue"])
        payload = response["payload"]
        return_queue = response["return_queue"]
        print(json.dumps(response, indent=4))
        if payload is not None:
            base64_images = process_stable_diffusion_request(payload)
            send_response_to_return_queue(redis_connection, return_queue, response, base64_images)
        else:
            print("Waiting for job...")
            time.sleep(1)

if __name__ == "__main__":
    main()
