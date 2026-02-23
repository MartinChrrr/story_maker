import os
import requests
import json
import base64


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_description(image_path):
    base64_image = encode_image_to_base64(image_path)
    data_url = f"data:image/jpeg;base64,{base64_image}"
    api_key = os.environ.get("OPEN_ROOTER")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "I want you to return me a json with 'title' 'text' and 'one_line'. "
                                    "In text i want you to tell me a short story for a child between 4 and 7 years old based on this image. "
                                    "In title I want you to choose a small title. "
                                    "And in one_line a short summary in less than 40 characters.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                    ],
                }
            ],
        },
    )
    r = response.json()
    try:
        return r["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return r