import streamlit as st
import pandas as pd
from pdf2image import convert_from_bytes
import os
import base64
import requests
from io import StringIO
import _config

# 「PDF読み取りアプリケーション」の文字を小さくするCSS
st.markdown("""
    <style>
    .small-title {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)




prompt = """
    入力画像は請求書の画像です。この画像から、日付、相手の株式会社名、件名、請求番号、品名、数量、単価、個別金額（税抜）、請求書合計金額（税込）の9項目を以下の条件のもとカンマ区切りcsv形式で出力してください。
    ・品名が複数ある場合は複数行で出力し、1つの品に対応する金額を個別金額（税抜）とする
    ・請求書合計金額（税込）には、請求書全体の合計金額を入力する。同じ請求書に複数の品がある場合は、1つの合計金額の値を複数行に渡って入力する
    ・品名が1つであれば1行で出力する
    ・数量に単位はつけない
    ・出力内容はリストに入れて出力しない 
    ・他の日本語は出力しない
    ・金額もしくは数値には、1000の桁を表すカンマは入れない
    ・```は入れない
    ・株式会社名に御中などの敬称はつけない
    ・請求先会社に「株式会社」がつく場合は必ずつける
    """


def ocr_pdf_to_csv(uploaded_files, output_folder, output_name):
    concat_df = pd.DataFrame([]) # concat_dfは複数のファイルから抽出されたデータを1つのデータフレームに統合するためのもの
    for uploaded_file in uploaded_files:
        # PDFをバイトデータから画像に変換
        image = pdf_to_images(uploaded_file.read())
        base64_image = encode_image(image[0])

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
        content = response.json()['choices'][0]['message']['content'] # response.json()は、APIからのレスポンスをJSON形式に変換、
                                                                      # response.json()['choices']は、JSONレスポンスからchoicesというキーを持つ部分を抽出、
                                                                      # response.json()['choices'][0]は、そのリストの最初の要素を取得、
                                                                      # response.json()['choices'][0]['message']は、最初の要素からmessageというキーを持つ部分を抽出、
                                                                      # response.json()['choices'][0]['message']['content']は、message部分からcontentというキーを持つ部分を抽出し、
                                                                      # これが実際に生成されたテキスト（つまり、抽出された請求書データ）
        
        data = StringIO(content) # StringIOは、Pythonのioモジュールに含まれているクラスで、文字列をメモリ上のファイルのように扱うことができる．
                                 # pandas.read_csv関数がファイルオブジェクトを受け取るように設計されているため、StringIOオブジェクト（中身はカンマ区切りのCSVそのものと同じだけど）に変換してる．
        df = pd.read_csv(data, header=None) # data（StringIOオブジェクト）内のCSV形式の文字列データを読み込み、データフレームに変換．
        df['ファイル名'] = uploaded_file.name # データフレームdfに新しい列「ファイル名」を追加し、その列にアップロードされたファイルの名前を格納．

        concat_df = pd.concat([concat_df, df]) # 複数のdfを行方向（デフォルト）に結合している．

    columns = ["日付","請求先会社","件名","請求番号","品名","数量","単価","個別金額（税抜）","合計金額（税込）","ファイル名"] # ヘッダー（列名）をつける．
    concat_df.columns = columns # ヘッダー（列名）をつける．
    concat_df = concat_df.reset_index(drop=True) # データフレームconcat_dfのインデックスをリセット(drop=Trueで古いインデックスは削除される).
    print(concat_df)
    output_file = os.path.join(output_folder, output_name)
    concat_df.to_csv(output_file, index=False, encoding='utf-8-sig') # windowsの場合encoding='utf-8-sig'ないとCSVが文字化け
    return output_file, concat_df

def pdf_to_images(pdf_bytes):
    return convert_from_bytes(pdf_bytes)

# Function to encode the image
def encode_image(image):
    # Save the image to a temporary path
    temp_image_path = "temp_image.jpeg"
    image.save(temp_image_path)
    
    with open(temp_image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# OpenAI API Key
api_key = _config.KEY

# APP
st.markdown('<p class="small-title">PDF読み取りアプリケーション</p>', unsafe_allow_html=True)

uploaded_files = st.file_uploader("PDFファイルをアップロードしてください", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.write(f"{len(uploaded_files)} file(s) uploaded.")

    output_folder = os.getcwd() 
    output_filename = st.text_input("エキスポートするCSVファイルに名前を付けて下さい", value="ocr_results.csv", placeholder="ocr_results.csv")
    
    if st.button('実行'):
        # ↓ concat_dfはocr_pdf_to_csvの結果が入る．output_fileは７３行目concat_df.to_csv(output_file, index=False)でconcat_dfをcsvに出力したそのファイル名
        output_file, concat_df = ocr_pdf_to_csv(uploaded_files, output_folder, output_filename)
        st.success(f"読み取り成功!")
        st.dataframe(concat_df)
        with open(output_file, 'rb') as f:
            st.download_button('CSVをダウンロード', f, file_name=output_filename)
