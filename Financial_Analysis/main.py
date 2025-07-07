
from threading import Thread, Lock, Semaphore

import pandas as pd
from flask import Flask, request, jsonify
import requests
import json
from iFinDPy import *
from datetime import datetime

app = Flask(__name__)

SESSION_ID = ""
WENCAI_API = "https://aimiai.com/api/agent_chat"
API_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6Ijg5YjU0MDliMjkzODRkZDQ5NDljNmIyOWJmZTRmN2Q4IiwidXNlcklkIjoiNzkxMzI5MDE1IiwiZXhwIjoxNzUzNzcwODUzfQ.Hk7S7s3J9oS7NAAp-0l0ipgUYnwl2hwbwuOgRx2E5r0"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question")
    mode = data.get("mode", "fast")

    if not question:
        return jsonify({"error": "question is required"}), 400

    headers = {
        "Content-Type": "application/json",
        "session-id": SESSION_ID,
        "Authorization" :API_TOKEN
    }

    payload = {
        "question": question,
        "mode": mode
    }

    try:
        response = requests.post(WENCAI_API, json=payload, headers=headers, stream=True, timeout=300)
        response.encoding = 'utf-8'  # 修复乱码问题
        response.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Request to Wencai failed: {str(e)}"}), 500

    # 不拼接，直接收集所有data行
    all_chunks = []
    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.strip().startswith("data:"):
            continue
        try:
            # 取出 data: 后的 JSON
            json_part = json.loads(line.strip()[5:])
            all_chunks.append(json_part)
        except Exception as e:
            all_chunks.append({"error": f"Parse error: {str(e)}", "raw": line.strip()})

    return jsonify({
        "question": question,
        "chunks": all_chunks
    })

# 登录 iFinD
login_result = THS_iFinDLogin("ceshi1575", "59eumU9S")
if login_result != 0:
    print("同花顺登录失败")
else:
    print("同花顺登录成功")

# --- 接口1：沪深300收盘价 ---
@app.route("/dp_basicdata", methods=["GET"])
def dp_basicdata():
    date = request.args.get("date", "2020-11-16")
    dp = THS_DP('block', f'{date};001005290', 'date:Y,thscode:Y,security_name:Y')
    if dp.errorcode != 0:
        return jsonify({"error": dp.errmsg}), 500
    codes = dp.data['THSCODE'].tolist()
    result = THS_BD(codes, 'ths_close_price_stock', f'reportdate={date};reporttype=100')
    if result.errorcode != 0:
        return jsonify({"error": result.errmsg}), 500
    return result.data.to_json(orient="records", force_ascii=False)

# --- 接口2：上证50实时行情 ---
@app.route("/dp_realtime", methods=["GET"])
def dp_realtime():
    today_str = datetime.today().strftime('%Y-%m-%d')
    dp = THS_DP('block', f'{today_str};001005260', 'date:Y,thscode:Y,security_name:Y')
    if dp.errorcode != 0:
        return jsonify({"error": dp.errmsg}), 500
    codes = dp.data['THSCODE'].tolist()
    result = THS_RQ(codes, 'latest')
    if result.errorcode != 0:
        return jsonify({"error": result.errmsg}), 500
    filename = f'realtimedata_{today_str}.csv'
    result.data.to_csv(filename)
    return jsonify({"status": "success", "file": filename})

# --- 接口3：资金流 + 股性评分 ---
@app.route("/iwencai", methods=["GET"])
def iwencai_demo():
    zjlx = THS_WC('主力资金流向', 'stock')
    xny = THS_WC('股性评分', 'stock')
    if zjlx.errorcode != 0 or xny.errorcode != 0:
        return jsonify({"error": "问财获取失败"}), 500
    return jsonify({
        "资金流向": zjlx.data.to_dict(orient="records"),
        "股性评分": xny.data.to_dict(orient="records")
    })

# --- 接口4：公告下载 ---
@app.route("/report_download", methods=["GET"])
def report_download():
    df = THS_ReportQuery('300033.SZ',
                         'beginrDate:2021-08-01;endrDate:2021-08-31;reportType:901',
                         'reportDate:Y,thscode:Y,secName:Y,ctime:Y,reportTitle:Y,pdfURL:Y,seq:Y').data
    downloaded = []
    for i in range(len(df)):
        pdfName = df.iloc[i, 4] + str(df.iloc[i, 6]) + '.pdf'
        pdfURL = df.iloc[i, 5]
        r = requests.get(pdfURL)
        with open(pdfName, 'wb+') as f:
            f.write(r.content)
        downloaded.append(pdfName)
    return jsonify({"status": "downloaded", "files": downloaded})

# --- 接口5：多线程提取全市场
#
#
# 高频数据（简化版） ---
sem = Semaphore(5)
dllock = Lock()

def hf_worker(codestr, lock, indilist):
    sem.acquire()
    result = THS_HF(codestr, ';'.join(indilist), '', '2020-08-11 09:15:00', '2020-08-11 15:30:00', 'format:json')
    if result.errorcode == 0:
        lock.acquire()
        with open('test1.txt', 'a') as f:
            f.write(str(result.data) + '\n')
        lock.release()
    sem.release()

@app.route("/multithread_hf", methods=["GET"])
def multiThread_demo():
    today_str = datetime.today().strftime('%Y-%m-%d')
    data = THS_DP('block', f'{today_str};001005010', 'date:Y,thscode:Y,security_name:Y')
    if data.errorcode != 0:
        return jsonify({"error": data.errmsg}), 500
    stock_list = data.data['THSCODE'].tolist()
    indi_list = ['close', 'high', 'low', 'volume']
    lock = Lock()
    threads = []
    chunk_size = max(1, int(len(stock_list) / 10))
    for i in range(0, len(stock_list), chunk_size):
        now_codes = ','.join(stock_list[i:i + chunk_size])
        t = Thread(target=hf_worker, args=(now_codes, lock, indi_list))
        threads.append(t)
    for t in threads: t.start()
    for t in threads: t.join()
    return jsonify({"status": "高频数据已写入 test1.txt"})

# ------------------- 云端 access_token 获取函数 -------------------
REFRESH_TOKEN = "eyJzaWduX3RpbWUiOiIyMDI1LTA2LTMwIDIwOjQxOjAxIn0=.eyJ1aWQiOiI3OTE0NDU3NDkiLCJ1c2VyIjp7ImFjY291bnQiOiJjZXNoaTE1NzUiLCJhdXRoVXNlckluZm8iOnsiYXBpRm9ybWFsIjoiMSJ9LCJjb2RlQ1NJIjpbXSwiY29kZVp6QXV0aCI6W10sImhhc0FJUHJlZGljdCI6ZmFsc2UsImhhc0FJVGFsayI6ZmFsc2UsImhhc0NJQ0MiOmZhbHNlLCJoYXNDU0kiOmZhbHNlLCJoYXNFdmVudERyaXZlIjpmYWxzZSwiaGFzRlRTRSI6ZmFsc2UsImhhc0Zhc3QiOmZhbHNlLCJoYXNGdW5kVmFsdWF0aW9uIjpmYWxzZSwiaGFzSEsiOnRydWUsImhhc0xNRSI6ZmFsc2UsImhhc0xldmVsMiI6ZmFsc2UsImhhc1JlYWxDTUUiOmZhbHNlLCJoYXNUcmFuc2ZlciI6ZmFsc2UsImhhc1VTIjpmYWxzZSwiaGFzVVNBSW5kZXgiOmZhbHNlLCJoYXNVU0RFQlQiOmZhbHNlLCJtYXJrZXRBdXRoIjp7IkRDRSI6ZmFsc2V9LCJtYXhPbkxpbmUiOjEsIm5vRGlzayI6ZmFsc2UsInByb2R1Y3RUeXBlIjoiU1VQRVJDT01NQU5EUFJPRFVDVCIsInJlZnJlc2hUb2tlbkV4cGlyZWRUaW1lIjoiMjAyNS0wNy0zMCAwOTo0NTozMiIsInNlc3NzaW9uIjoiOGNiYmFjYTMxNWU3MjIwN2EzOTcyYzU2ZmNkNDA4NjMiLCJzaWRJbmZvIjp7fSwidHJhbnNBdXRoIjpmYWxzZSwidWlkIjoiNzkxNDQ1NzQ5IiwidXNlclR5cGUiOiJPRkZJQ0lBTCIsIndpZmluZExpbWl0TWFwIjp7fX19.1CA63D6210EA52B2FC6B81442D5DFD19D4AA0285B5F0ABB3F200CD264F2D39D1"
TOKEN_URL = "https://quantapi.51ifind.com/api/v1/get_access_token"

def get_access_token():
    headers = {
        "Content-Type": "application/json",
        "refresh_token": REFRESH_TOKEN
    }
    try:
        res = requests.post(TOKEN_URL, headers=headers)
        res.raise_for_status()
        token = res.json().get("data", {}).get("access_token")
        if not token:
            raise ValueError("获取 access_token 失败")
        return token
    except Exception as e:
        print(f"[Token错误] {e}")
        return None

# ------------------- 云端基础财务数据接口 -------------------
@app.route("/basic_financials_online", methods=["POST"])
def basic_financials_online():
    data = request.get_json()
    codes = data.get("codes", [])
    date = data.get("date", "")  # 格式如：2023-12-31

    if not codes or not date:
        return jsonify({"error": "请输入 codes 和 date（格式如：2023-12-31）"}), 400

    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "access_token 获取失败，请检查 refresh_token"})

    try:
        payload = {
            "codes": ",".join(codes),
            "indipara": [
                {
                    "indicator": "ths_sq_net_asset_yield_roe_index",  # ROE
                    "indiparams": [date, "100"]
                },
                {
                    "indicator": "ths_eps_basic_index",  # EPS
                    "indiparams": [date, "100"]
                },
                {
                    "indicator": "ths_total_asset_turnover_index",  # 总资产周转率
                    "indiparams": [date, "100"]
                },
                {
                    "indicator": "ths_net_profit_margin_index",  # 净利润率
                    "indiparams": [date, "100"]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "access_token": access_token
        }

        url = "https://quantapi.51ifind.com/api/v1/basic_data_service"
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        result = res.json()

        if "tables" not in result:
            return jsonify({"error": "返回结果无 tables 字段", "raw": result}), 500

        df = pd.json_normalize(result["tables"])
        return df.to_json(orient="records", force_ascii=False)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#------------------查询有效财报日期----------------------
@app.route("/available_dates", methods=["GET"])
def get_available_dates():
    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "access_token 获取失败"})

    url = "https://quantapi.51ifind.com/api/v1/get_trade_dates"
    payload = {
        "marketcode": "212001",  # 上交所
        "functionpara": {
            "dateType": "2",      # 财报类型
            "period": "Q",        # 季度
            "offset": "-20",
            "output": "sequencedate"
        },
        "startdate": "2022-01-01"
    }

    headers = {
        "Content-Type": "application/json",
        "access_token": access_token
    }

    res = requests.post(url, headers=headers, json=payload)
    return jsonify(res.json())

# --- 启动 ---
if __name__ == '__main__':
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 500)
    app.run(host='0.0.0.0', port=5001, debug=True)