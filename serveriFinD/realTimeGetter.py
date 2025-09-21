import requests
import json
import tokenGetter
import time
import pandas as pd

# === 配置 ===
thsUrl = 'https://quantapi.51ifind.com/api/v1/real_time_quotation'
thsHeaders = {
    "Content-Type": "application/json",
    "access_token": tokenGetter.getAccessToken()
}

def get_real_time_quotation(code: str, interval: int = 3, repeat: int = 1):
    """
    获取单只股票的实时行情
    code: 股票代码，例如 "300033.SZ"
    interval: 查询间隔秒数
    repeat: 查询次数，默认为1次，可设置多次轮询
    返回一个列表，每个元素为一次查询结果的字典
    """
    results = []

    thsPara = {
        "codes": code,
        "indicators": "latest"  # 获取最新行情
    }

    for _ in range(repeat):
        resp = requests.post(url=thsUrl, json=thsPara, headers=thsHeaders)
        data = json.loads(resp.content.decode("utf-8"))

        if data.get("errorcode", -1) != 0:
            print("Error:", data.get("errmsg", "unknown"))
            results.append({})
        else:
            # 转成平面表格
            df = pd.json_normalize(data.get('tables', []))
            if 'pricetype' in df.columns:
                df = df.drop(columns=['pricetype'])
            # 有些字段是列表，展开
            df = df.apply(lambda x: x.explode().astype(str).groupby(level=0).agg(", ".join) if x.dtype == 'object' else x)
            results.append(df.to_dict(orient='records')[0] if not df.empty else {})

        time.sleep(interval)

    return results


# === 示例 ===
if __name__ == "__main__":
    code = "300033.SZ"
    real_time_data = get_real_time_quotation(code, interval=3, repeat=1)
    print(json.dumps(real_time_data, indent=2, ensure_ascii=False))