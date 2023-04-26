#!/usr/bin/env python3
import argparse
import json
from sd_handler import get_payload_from_png

def main():
    parser = argparse.ArgumentParser(description="Get JSON payload from a PNG image.")
    parser.add_argument( "image_path", help="Path to the PNG image file.")

    args = parser.parse_args()

    try:
        payload = get_payload_from_png(args.image_path)
        print(json.dumps(payload, indent=4))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
