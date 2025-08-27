import requests
import pdfReader

API_KEY = "sk-179ec153725c446fa367779e72c4f301"

url = "https://api.deepseek.com/chat/completions"

def chat(message,file):
    if file:
        text = pdfReader.extract_text_from_pdf(file)
        message = f"根据以下内容回答我的问题：\n{text[:3000]}\n问题是：{message},返回使用txt文本，不要md格式"

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


    reply = chat(
        f"请帮我分析这份PDF内容：\n{text[:3000]}, 返回使用txt文本，不要md格式",
        file_path
    )
    return reply

def fileSynopsis(file_path):
    text = pdfReader.extract_text_from_pdf(file_path)

    reply = chat(
        f"对这份PDF文件总结成几个要点：\n{text[:3000]}, 返回使用txt文本；每个要点少于50字，用分号分隔。样例如下 要点1: test; 要点2: test1",
        file_path
    )
    return reply

