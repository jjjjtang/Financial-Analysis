import requests
import pdfReader

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

def pdfAnalysis(file_path):
    text = pdfReader.extract_text_from_pdf(file_path)

    reply = chat(f"请帮我分析这份PDF内容：\n{text[:3000]}")
    return reply

