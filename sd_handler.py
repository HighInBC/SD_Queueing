import requests
import base64
import json
import random

class StableDiffusionRequestException(Exception):
    pass

def process_stable_diffusion_request(payload):
    if not isinstance(payload, dict):
        raise StableDiffusionRequestException("Payload must be a dictionary.")
    if "prompt" not in payload:
        raise StableDiffusionRequestException("Payload must contain the 'prompt' key.")

    payload['seed'] = random.randint(0, 2**32-1)

    try:
        response = requests.post("http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise StableDiffusionRequestException(f"Failed to send request: {e}")

    try:
        images = response.json()['images']
    except KeyError:
        print(response.json())
        raise StableDiffusionRequestException("The 'images' key is missing from the response.")
    except ValueError:
        raise StableDiffusionRequestException("Failed to parse the response JSON.")

    return images
