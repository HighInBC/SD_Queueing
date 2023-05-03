#!/usr/bin/env python3
import json
import sys
import os
import base64
import datetime
from sdq.redis_handler import connect_to_redis, read_from_return_queue, InvalidInputException
from sdq.config_parser import ConfigParser

def get_image_path(label, seed, index, filename):
    counter_key = "_".join(label)
    file_number = counter.get(counter_key, 0)
    counter[counter_key] = file_number + 1
    file_number = str(file_number).zfill(4)
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    path = os.path.join("incoming", date, *label)
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, f"{file_number}_{seed}_{filename}_{index}.png")
    return path


def handle_job(job):
    seed = job["request"]["payload"]["seed"]
    server_id = job.get("server_id", "unknown")
    *label, filename = job["request"]["label"]

    images = job["response"]
    print(f"\nReceived {len(images)} images. From server {server_id}")

    for i, image in enumerate(images):
        image_path = get_image_path(label, seed, i, filename)
        print(f"\tSaving image {i} to {image_path}")

        image_data = base64.b64decode(image)
        with open(os.path.join(os.getcwd(), image_path), "wb") as f:
            f.write(image_data)


def main():
    config = ConfigParser(config_file='config.json')
    global counter
    counter = {}

    try:
        redis_connection = connect_to_redis(config)
    except InvalidInputException as e:
        print(f"Error: {e}")
        sys.exit(1)

    return_queue = config.return_queue or "default_return_queue"

    while True:
        try:
            response = read_from_return_queue(redis_connection, return_queue)
            if response is not None:
                handle_job(response)
            else:
                print("No job received. Exiting.")
                break
        except InvalidInputException as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
