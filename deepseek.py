# deepseek.py

import requests


# 填写你的 API Key
API_KEY = "sk-179ec153725c446fa367779e72c4f301"

url = "https://api.deepseek.com/chat/completions"

def chat(message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "model": "deepseek-reasoner",  # 指定使用 R1 模型（deepseek-reasoner）或者 V3 模型（deepseek-chat）
        "messages": [
            {"role": "system", "content": "你是一个专业的助手"},
            {"role": "user", "content": message }
        ],
        "stream": False  # 关闭流式传输
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
       # print(result['choices'][0]['message']['content'])
    else:
        return "请求失败，错误码：" + response.status_code

def pdfRead():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    fileURL = "C:\\Users\lenovo\OneDrive\Documents\WeChat Files\wxid_5xne60p1m21312\FileStorage\File\\2025-07\TASK.pdf"

    files = {'file': open(fileURL, 'rb')}
    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        result = response.json()
        print(result['text'])
        return result['text']
    else:
        raise Exception(f"Error extracting text from PDF: {response.text}")

