import base64
import requests
from pdf2image import convert_from_path
import pandas as pd
from io import StringIO
import _config

# PDF Path
pdf_path = "請求書2.pdf"

prompt = """
    入力画像は請求書の画像です。この画像から、日付、相手の株式会社名、件名、品名、数量、請求金額を抽出して、以下の条件のもとカンマ区切りcsv形式で出力してください。
    ・出力内容はリストに入れて出力しない 
    ・他の日本語は出力しない
    ・金額にカンマは入れない
    """
# read_csv関数はCSV形式のデータを1行あたり1つのフィールドしか持たないと期待しているのに、実際には複数のフィールドが含まれているためエラーが発生しています。
# ここで、プロンプトの「・出力内容はリストに入れて出力しない」という部分が重要になります。この指示があると、出力内容がリスト形式ではなくCSV形式で直接出力されるように指示されています。
# しかし、これを削除すると、出力がリスト形式になり、それがCSV形式に変換されないため、pandasのread_csv関数が正しく解析できなくなります。


# OpenAI API Key
api_key = _config.KEY

def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path, fmt='jpeg')

# Function to encode the image
def encode_image(image):
    # Save the image to a temporary path
    temp_image_path = "temp_image.jpeg"
    image.save(temp_image_path)
    
    with open(temp_image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Convert PDF to jpeg image
images = pdf_to_images(pdf_path)

# Encode the first image from the PDF
base64_image = encode_image(images[0])

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
df.columns = ["日付","請求先会社","件名","品名","数量","請求金額"]

# content_list = []
# content_list.append(content.split(','))
# # print(content_list)
# # print(type(content_list))
# df = pd.DataFrame(content_list, columns=["日付","請求先会社","件名","品名","数量","請求金額"])

print(df)
