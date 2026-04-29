import requests
import base64
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_page(image_path, page_number):
    base64_image = encode_image(image_path)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(BASE_DIR, "prompt.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen/qwen2.5-vl-72b-instruct",  # 🔥 vision-capable
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }
    )

    result = response.json()

    return result["choices"][0]["message"]["content"]