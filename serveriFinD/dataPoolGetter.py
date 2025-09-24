import requests
import json
import tokenGetter
import pandas as pd

# === 配置 ===
thsUrl = "https://quantapi.51ifind.com/api/v1/basic_data_service"
thsHeaders = {
    "Content-Type": "application/json",
    "access_token": tokenGetter.getAccessToken()
}

def get_financial_indicators(code, indicators=None):
    """
    获取公司财务指标（净利润、EPS、ROE等）
    返回前端可直接使用的 ECharts 数据
    """
    if indicators is None:
        indicators = [
            "ths_net_profit_stock",       # 净利润
            "ths_roe_stock",              # 净资产收益率
            "ths_eps_stock",              # 每股收益
            "ths_operating_income_stock"  # 营业收入
        ]

    thsPara = {
        "codes": code,
        "indipara": [{"indicator": ind, "indiparams": [""]} for ind in indicators]
    }

    resp = requests.post(url=thsUrl, json=thsPara, headers=thsHeaders)
    data = json.loads(resp.content.decode("utf-8"))

    # 错误处理
    if data.get("errorcode", -1) != 0:
        print("❌ Error:", data.get("errmsg", "unknown"))
        return {}

    # 解析结果
    tables = data.get("tables", [])
    if not tables:
        print("❌ No data")
        return {}

    table = tables[0].get("table", {})
    result = {ind: table.get(ind, [None])[0] for ind in indicators}

    # === ECharts 格式 ===
    echarts_data = {
        "legend": indicators,
        "series": [{"name": k, "value": v} for k, v in result.items() if v is not None]
    }

    return {
        "raw": data,
        "table": result,
        "echarts": echarts_data
    }


# === 示例调用 ===
if __name__ == "__main__":
    code = "600000.SH"  # 浦发银行
    result = get_financial_indicators(code)
    print("==== 表格 ====")
    print(json.dumps(result["table"], indent=2, ensure_ascii=False))
    print("\n==== ECharts 数据 ====")
    print(json.dumps(result["echarts"], indent=2, ensure_ascii=False))