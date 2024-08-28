import base64
import requests
# from pdf2image import convert_from_path
import pandas as pd
from io import StringIO
import _config

# file Path
image_path = "手書き領収書.png" # jpgでもよい

prompt = """
    入力画像は領収書の画像です。
    この画像から、日付、宛名、合計金額、但し書きを抽出して、以下の条件のもとカンマ区切りcsv形式で出力してください。
    ・出力内容はリストに入れて出力しない 
    ・出力項目は、日付、宛名、合計金額、但し書きの4項目のみとする
    ・他の日本語は出力しない
    ・金額にカンマは入れない
    """

# OpenAI API Key
api_key = _config.KEY

# def pdf_to_images(pdf_path):
#     return convert_from_path(pdf_path, fmt='jpeg')

# Function to encode the image
def encode_image(image_path):
    # Save the image to a temporary path
    # temp_image_path = "temp_image.jpeg"
    # image.save(temp_image_path)
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Convert PDF to jpeg image
# images = pdf_to_images(pdf_path)

# Encode the first image from the PDF
# base64_image = encode_image(images[0])
base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4o",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
content = response.json()['choices'][0]['message']['content']

data = StringIO(content)
df = pd.read_csv(data, header=None)
df.columns = ["日付","宛名","合計金額","但し書き"]

# content_list = []
# content_list.append(content.split(','))
# df = pd.DataFrame(content_list, columns=["日付","宛名","合計金額","但し書き"])

print(df)
