import requests
import json
import pandas as pd
import tokenGetter  # 你本地的 token 获取模块

# === 配置 ===
thsUrl = 'https://quantapi.51ifind.com/api/v1/cmd_history_quotation'
thsHeaders = {
    "Content-Type": "application/json",
    "access_token": tokenGetter.getAccessToken()
}


def get_history_quotes(codes, startdate, enddate, indicators="open,high,low,close"):
    """
    获取历史行情数据（支持多只股票）
    :param codes: 股票代码字符串，例如 "000001.SZ,600000.SH"
    :param startdate: 开始日期 (YYYY-MM-DD)
    :param enddate: 结束日期 (YYYY-MM-DD)
    :param indicators: 行情指标，默认 open,high,low,close
    :return: dict {stock_code: DataFrame}
    """
    thsPara = {
        "codes": codes,
        "indicators": indicators,
        "startdate": startdate,
        "enddate": enddate,
        "functionpara": {"Fill": "Blank"}
    }

    resp = requests.post(url=thsUrl, json=thsPara, headers=thsHeaders)
    data = json.loads(resp.content.decode("utf-8"))

    # 错误处理
    if data.get("errorcode", -1) != 0:
        print("❌ Error:", data.get("errmsg", "unknown"))
        return {}

    results = {}
    for stock in data.get("tables", []):
        code = stock["thscode"]
        time_list = stock["time"]
        price_table = stock["table"]

        df = pd.DataFrame(price_table, index=time_list)
        df.index.name = "date"
        results[code] = df

    return results


def to_echarts_format(parsed_data):
    """
    转换为前端 ECharts candlestick 需要的格式
    :param parsed_data: {code: DataFrame}
    :return: dict {code: {"dates": [...], "values": [[open, close, low, high], ...]}}
    """
    echarts_data = {}
    for code, df in parsed_data.items():
        echarts_data[code] = {
            "dates": df.index.tolist(),
            "values": df.apply(lambda row: [row["open"], row["close"], row["low"], row["high"]], axis=1).tolist()
        }
    return echarts_data


# === 测试示例 ===
if __name__ == "__main__":
    codes = "000001.SZ,600000.SH"
    startdate = "2024-07-05"
    enddate = "2025-07-05"

    # 1. 获取历史行情
    parsed = get_history_quotes(codes, startdate, enddate)
    print(parsed)

    # 2. 打印表格示例
    for code, df in parsed.items():
        print(f"\n📈 {code} 历史行情 (前5行)")
        print(df.head())

    # 3. 转换为 ECharts JSON 格式
    echarts_data = to_echarts_format(parsed)
    print("\n==== ECharts 格式 (前2条数据) ====")
    print(json.dumps({c: d for c, d in echarts_data.items()}, indent=2, ensure_ascii=False)[:800])