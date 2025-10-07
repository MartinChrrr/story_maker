import requests
import json
import base64
from pathlib import Path
import Keys



def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def api_call():
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Keys.OPEN_ROOTER}",
        "Content-Type": "application/json"
    }

    # Read and encode the image
    image_path = "static/uploaded_images/1.png"
    base64_image = encode_image_to_base64(image_path)
    data_url = f"data:image/jpeg;base64,{base64_image}"

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                }
            ]
        }
    ]

    payload = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=payload).json()
    # print(response.choices[0].message.content)
    return response

with open('temp.json') as f:
  data = json.load(f)
  print(data["choices"][0]["message"]["content"])