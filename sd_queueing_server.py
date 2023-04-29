#!/usr/bin/env python3
import json
import time
import signal
import argparse
from sdq.redis_handler import connect_to_redis, read_from_ingress_queue, send_response_to_return_queue
from sdq.sd_handler import block_until_api_ready, process_stable_diffusion_request

interrupted = False
working = False

def signal_handler(signum, frame):
    global interrupted
    global working
    if working == False:
        print("working: "+str(working))
        print("No job in progress. Exiting.")
        exit(0)
    if interrupted:
        print("Force quit signal received. Exiting.")
        exit(0)
    interrupted = True
    print("Stop signal received. Ending after current job. Press Ctrl+C again to force quit.")

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def load_config(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--priority", type=int, default=0, help="The minimum priority to work on, anything below this will be ignored (default 0)")
    parser.add_argument("-d", "--delay", type=int, default=0, help="Wait this long in between processing requests (default 0)")
    parser.add_argument("-c", "--config", type=str, default="config.json", help="The config file (default config.json)")
    return parser.parse_args()

def main(priority, delay, config_file):
    global interrupted
    global working
    config = load_config(config_file)
    redis_connection = connect_to_redis(config)
    block_until_api_ready()

    while True:
        print("Reading from ingress queue...")
        response = read_from_ingress_queue(redis_connection, config["ingress_queue"], priority)
        payload = response["payload"]
        return_queue = response["return_queue"]
        print(json.dumps(response, indent=4))
        if payload is not None:
            working = True
            base64_images = process_stable_diffusion_request(payload)
            send_response_to_return_queue(redis_connection, return_queue, response, base64_images, config["server_id"])
            working = False
            if interrupted:
                print("Interrupted. Exiting.")
                exit(0)
            if delay > 0:
                print(f"Waiting {delay} seconds...")
                time.sleep(delay)
        else:
            print("Waiting for job...")
            time.sleep(1)

if __name__ == "__main__":
    args = parse_args()
    main(args.priority, args.delay, args.config)
