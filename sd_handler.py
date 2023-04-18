import requests
import base64
import json
import random

def process_stable_diffusion_request(payload):
    """
    Process the Stable Diffusion API request and return an array of base64-encoded images.
    """
    payload['seed'] = random.randint(0, 2**32-1)
    response = requests.post("http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
    images = response.json()['images']

    return images