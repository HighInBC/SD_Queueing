#!/usr/bin/env python3
import json
import sys
import os
import base64
import sdq.redis_handler


def load_config(config_file="config.json"):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


def get_image_path(label, seed, index, filename):
    counter_key = "_".join(label)
    file_number = counter.get(counter_key, 0)
    counter[counter_key] = file_number + 1
    file_number = str(file_number).zfill(4)
    saveas = f"{file_number}_{seed}_{filename}_{index}.png"
    return os.path.join("incoming", *label, saveas)


def handle_job(job):
    seed = job["request"]["payload"]["seed"]
    server_id = job.get("server_id", "unknown")
    *label, filename = job["request"]["label"]
    path = os.path.join(os.getcwd(), "incoming", *label)
    os.makedirs(path, exist_ok=True)

    images = job["response"]
    print(f"\nReceived {len(images)} images. From server {server_id}")
    print(f"Saving images to {path}...")

    for i, image in enumerate(images):
        image_path = get_image_path(label, seed, i, filename)
        print(f"Saving image {i} to {image_path}")

        image_data = base64.b64decode(image)
        with open(os.path.join(os.getcwd(), image_path), "wb") as f:
            f.write(image_data)


def main():
    config = load_config()
    global counter
    counter = {}

    try:
        redis_connection = sdq.redis_handler.connect_to_redis(config)
    except sdq.redis_handler.InvalidInputException as e:
        print(f"Error: {e}")
        sys.exit(1)

    return_queue = config.get("return_queue", "default_return_queue")

    while True:
        try:
            response = sdq.redis_handler.read_from_return_queue(redis_connection, return_queue)
            if response is not None:
                handle_job(response)
            else:
                print("No job received. Exiting.")
                break
        except sdq.redis_handler.InvalidInputException as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
