#!/usr/bin/env python3
import json
import time
import sys
from sshtunnel import SSHTunnelForwarder
from sdq.redis_handler import connect_to_redis, read_from_ingress_queue, send_response_to_return_queue
from sdq.sd_handler import process_stable_diffusion_request

def load_config(config_file):
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    return config

def main():
    config_file = "config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    config = load_config(config_file)
    redis_connection = connect_to_redis(config)

    while True:
        print("Reading from ingress queue...")
        response = read_from_ingress_queue(redis_connection, config["ingress_queue"])
        payload = response["payload"]
        return_queue = response["return_queue"]
        print(json.dumps(response, indent=4))
        if payload is not None:
            base64_images = process_stable_diffusion_request(payload)
            send_response_to_return_queue(redis_connection, return_queue, response, base64_images, config["server_id"])
        else:
            print("Waiting for job...")
            time.sleep(1)

if __name__ == "__main__":
    main()
