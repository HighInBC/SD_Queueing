import requests
import base64
import json
import random

def process_stable_diffusion_request(request):
    """
    Process the Stable Diffusion API request and return an array of base64-encoded images.
    """
    sd_request = request.get("request")
    sd_request['seed'] = random.randint(0, 2**32-1)
    response = requests.post("127.0.0.1:7860", json=sd_request)
    images = response.json()['images']

    png_images = []
    for image in images:
        img_bytes = base64.b64decode(image)
        png_images.append(img_bytes)

    return png_images
