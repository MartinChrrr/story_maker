import requests
import json
import Keys as k
import base64

path = "./static/assets/story.png"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_description(image_path):
    base64_image = encode_image_to_base64(image_path)
    data_url = f"data:image/jpeg;base64,{base64_image}"
    aut = "Bearer " + k.OPEN_ROOTER
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": aut,
            "Content-Type": "application/json",
        },
        data= json.dumps({
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",
            "messages": [
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": "Tell me a short story for a child between 4 and 7 years old based on this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": data_url
                }
          }
        ]
      }
    ],
    })
    )
    r = response.json()
    return r["choices"][0]["message"]["content"]


print(get_image_description(path))