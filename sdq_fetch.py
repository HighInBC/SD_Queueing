#!/usr/bin/env python3
import json
import sys
import os
import base64
from sshtunnel import SSHTunnelForwarder
import redis_handler

def load_config(config_file="config.json"):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config

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

def handle_job(job):
    print("Received job:")
    seed = job["request"]["payload"]["seed"]
    server_id = job.get("server_id", "unknown")
    path = os.path.join(os.getcwd(), *job["request"]["label"])
    print(f"Saving images to {path}...")
    if not os.path.exists(path):
        os.makedirs(path)
    images = job["response"]
    print(f"Received {len(images)} images. From server {server_id}")
    for i, image in enumerate(images):
        print(f"Saving image {i}...")
        filename = f"sd_{seed}_{i}.png"
        image = base64.b64decode(image)
        with open(os.path.join(path, filename), "wb") as f:
            f.write(image)

def main():
    config = load_config()
    tunnel = create_ssh_tunnel(config)

    config["redis_port"] = tunnel.local_bind_port
    config["redis_host"] = "127.0.0.1"
    try:
        redis_connection = redis_handler.connect_to_redis(config)
    except redis_handler.InvalidInputException as e:
        print(f"Error: {e}")
        sys.exit(1)

    return_queue = config.get("return_queue", "default_return_queue")

    while True:
        try:
            response = redis_handler.read_from_return_queue(redis_connection, return_queue)
            if response is not None:
                print("Received job:")
                handle_job(response)
            else:
                print("No job received. Exiting.")
                break
        except redis_handler.InvalidInputException as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()