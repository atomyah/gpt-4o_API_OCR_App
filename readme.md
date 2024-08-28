# 環境設定
## 前提
- Pythonがインストールされている
- venvが使える（Pythonが入っていれば使える）

## requirements.txtから作成する場合
1. 仮想環境作成
```
python -m venv ocr_venv
```

2. 仮想環境の有効化
- Windows
```
ocr_venv\Scripts\activate
```

- Mac
```
source ocr_venv/bin/activate
```

3. ライブラリインストール
```
pip install -r requirements.txt
```

## （参考）環境を最初から作成する場合
1. 仮想環境作成
```
python -m venv ocr_venv
```

2. 仮想環境の有効化
- Windows
```
ocr_venv\Scripts\activate
```

- Mac
```
source ocr_venv/bin/activate
```

3. ライブラリインストール
```
pip install streamlit
pip install openai
pip install pdf2image
```

4. requirement.txtの出力（参考なので実施しなくてよい）
```
pip freeze > requirements.txt
```

5. requirements.txtからパッケージをインストール（参考なので実施しなくてよい）
```
pip install -r requirements.txt
```

# アプリ実行
```
streamlit run ocr_app.py
```
