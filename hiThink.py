import json
import pdfReader

import requests
APP_ID = "20f596f28a1c4a398ce94b93b2ddaf29"
APP_KEY = "c7479ab08dd945e38200c5e3b4a21a3f"

GET_TOKEN_URL = "https://aimiai.com/api/token/get"
CHAT_URL = "https://aimiai.com/api/agent_chat"

def getToken():
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "appId": APP_ID,
        "appKey": APP_KEY
    }
    response = requests.post(GET_TOKEN_URL, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result['data']
        # print(result['data'])
    else:
        return "请求失败，错误码：" + response.status_code

def pdfAnalysis(file_path):
    text = pdfReader.extract_text_from_pdf(file_path)
    question = f"请帮我分析这份PDF内容：\n{text[:3000]}, 返回使用txt文本，不要md格式,不要用**等符号"
    mode = "fast"
    reply = chat(question, mode)
    return reply

def fincialAssistant(file_path, question):
    text = pdfReader.extract_text_from_pdf(file_path)
    question = f"根据以下内容回答我的问题：\n{text[:3000]}\n问题是：{question},返回使用txt文本，不要md格式,不要用**等符号"
    mode = "fast"
    reply = chat(question, mode)
    return reply

def chat(question, mode):
    token = "Bearer " + getToken()
    print(token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    data = {
        "question": question,
        "mode": mode
    }

    response = requests.post(CHAT_URL, headers=headers, json=data, stream=True)
    # 设置编码，防止中文乱码
    response.encoding = "utf-8"

    answer = []  # 存储分片

    if response.status_code == 200:
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data:"):
                try:
                    msg = json.loads(line[len("data:"):])
                    section = msg.get("section", {})
                    if "rich_text" in section:
                        answer.append(section["rich_text"])  # 收集分片
                    if section.get("is_last", False):  # 结束标记
                        break
                except Exception as e:
                    print("解析失败:", e)
    else:
        print("请求失败:", response.status_code)

    return "".join(answer)

