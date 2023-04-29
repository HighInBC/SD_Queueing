import requests
import re
import random
import time
from PIL import Image
from PIL.PngImagePlugin import PngImageFile, PngInfo

class StableDiffusionRequestException(Exception):
    pass

class StableDiffusionApiClient:
    def __init__(self, requests_lib=None):
        self._requests = requests_lib or requests

    def process_stable_diffusion_request(self, payload):
        if not isinstance(payload, dict):
            raise StableDiffusionRequestException("Payload must be a dictionary.")
        if "prompt" not in payload:
            raise StableDiffusionRequestException("Payload must contain the 'prompt' key.")

        payload['seed'] = random.randint(0, 2**32-1)

        try:
            response = self._requests.post("http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
            response.raise_for_status()
        except self._requests.exceptions.RequestException as e:
            raise StableDiffusionRequestException(f"Failed to send request: {e}")

        try:
            images = response.json()['images']
        except KeyError:
            print(response.json())
            raise StableDiffusionRequestException("The 'images' key is missing from the response.")
        except ValueError:
            raise StableDiffusionRequestException("Failed to parse the response JSON.")

        return images

    def block_until_api_ready(self, interval=5):
        while True:
            try:
                response = self._requests.get("http://127.0.0.1:7860/sdapi/v1/sd-models")
                if response.status_code == 200:
                    return response
            except:
                pass
            print("Waiting for the API to become ready...")
            time.sleep(interval)

def process_stable_diffusion_request(payload):
    api_client = StableDiffusionApiClient()

    try:
        images = api_client.process_stable_diffusion_request(payload)
    except StableDiffusionRequestException as e:
        raise e

    return images

def decode_payload_string(input_string):
    if not isinstance(input_string, str):
        raise ValueError("Expected input_string to be a string, but got a different type.")

    prompt_match = re.match(r'^(.*?)(?=Negative prompt:)', input_string, re.S)
    prompt = prompt_match.group(1).strip() if prompt_match else ''

    neg_prompt_match = re.search(r'Negative prompt: (.*?)(?=Steps:)', input_string, re.S)
    negative_prompt = neg_prompt_match.group(1).strip() if neg_prompt_match else ''
    
    steps = int(re.search(r'Steps: (\d+)', input_string).group(1))
    sampler_index = re.search(r'Sampler: (.*?)(?=,|$)', input_string).group(1).strip()
    cfg_scale = float(re.search(r'CFG scale: (\d+(\.\d+)?)(?=,|$)', input_string).group(1))
    seed = int(re.search(r'Seed: (\d+)(?=,|$)', input_string).group(1))
    width, height = map(int, re.search(r'Size: (\d+)x(\d+)(?=,|$)', input_string).groups())
    sd_model_checkpoint = re.search(r'Model: (.*?)(?=,|$)', input_string).group(1).strip()
    
    result_dict = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "sampler_index": sampler_index,
        "seed": seed,
        "width": width,
        "height": height,
        "cfg_scale": cfg_scale,
        "restore_faces": True,
        "batch_size": 2,
        "sd_model_checkpoint": sd_model_checkpoint,
        "do_not_save_samples": True,
        "do_not_save_grid": True
    }
    
    return result_dict

def get_payload_from_png(png_path):
    with Image.open(png_path) as img:
        if not isinstance(img, PngImageFile):
            raise ValueError("The file is not a valid PNG image.")
        png_info = img.info
        metadata = {key: png_info[key] for key in png_info}
        return decode_payload_string(metadata['parameters'])

def block_until_api_ready(interval=5):
    api_client = StableDiffusionApiClient()
    try:
        response = api_client.block_until_api_ready(interval)
    except Exception as e:
        raise e
    return response
