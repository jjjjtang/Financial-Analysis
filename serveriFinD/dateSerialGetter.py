import requests
import json
import tokenGetter

# === 配置 ===
thsUrl = 'https://quantapi.51ifind.com/api/v1/date_sequence'
thsHeaders = {
    "Content-Type": "application/json",
    "access_token": tokenGetter.getAccessToken()
}

def get_date_sequence_flat(codes, startdate, enddate):
    """
    获取多只股票的日期序列指标，并返回前端友好格式
    每条记录为：
    {
        "thscode": 股票代码,
        "date": 日期,
        "ths_open_price_stock": 开盘价,
        "ths_high_price_stock": 最高价,
        "ths_close_price_stock": 收盘价,
        "ths_total_shares_stock": 总股本,
        "ths_free_float_shares_stock": 流通股本,
        "ths_turnover_ratio_stock": 换手率(%),
    }
    """
    # === 所有常用日期序列指标 ===
    indicators = [
        "ths_open_price_stock",          # 开盘价
        "ths_high_price_stock",          # 最高价
        "ths_close_price_stock",         # 收盘价
        "ths_total_shares_stock",        # 总股本
        "ths_free_float_shares_stock",   # 流通股本
        "ths_turnover_ratio_stock",      # 换手率(%)
    ]

    # 构造请求参数
    indipara = [{"indicator": ind, "indiparams": ["", "100", ""]} for ind in indicators]

    thsPara = {
        "codes": codes,
        "startdate": startdate,
        "enddate": enddate,
        "functionpara": {"Fill": "Blank"},
        "indipara": indipara
    }

    # 请求数据
    resp = requests.post(url=thsUrl, json=thsPara, headers=thsHeaders)
    data = json.loads(resp.content.decode("utf-8"))

    # 错误处理
    if data.get("errorcode", -1) != 0:
        print("Error:", data.get("errmsg", "unknown"))
        return []

    # === 解析成前端友好格式 ===
    result = []
    for stock in data.get("tables", []):
        thscode = stock.get("thscode")
        dates = stock.get("time", [])
        table = stock.get("table", {})
        n = len(dates)
        for i in range(n):
            record = {"thscode": thscode, "date": dates[i]}
            for ind in indicators:
                values = table.get(ind, [])
                record[ind] = values[i] if i < len(values) else None
            result.append(record)

    return result


# === 使用示例 ===
if __name__ == "__main__":
    codes = "000001.SZ,600000.SH"
    startdate = "20220605"
    enddate = "20220705"

    flat_data = get_date_sequence_flat(codes, startdate, enddate)
    print(json.dumps(flat_data, indent=2, ensure_ascii=False))