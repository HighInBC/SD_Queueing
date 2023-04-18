#!/usr/bin/env python3
import json
import time
from sshtunnel import SSHTunnelForwarder
from redis_handler import connect_to_redis, read_from_ingress_queue, send_response_to_return_queue
from sd_handler import process_stable_diffusion_request

def load_config():
    """
    Load configuration from "config.json" and return the configuration dictionary.
    """
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    return config

def create_ssh_tunnel(config):
    """
    Create an SSH tunnel to the remote server using the provided configuration.
    """
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

def main():
    config = load_config()
    tunnel = create_ssh_tunnel(config)
    config["redis_port"] = tunnel.local_bind_port
    config["redis_host"] = "127.0.0.1"
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
