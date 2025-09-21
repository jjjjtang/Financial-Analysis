import requests
import json
import tokenGetter

# === 配置 ===
thsUrl = "https://quantapi.51ifind.com/api/v1/basic_data_service"
thsHeaders = {
    "Content-Type": "application/json",
    "access_token": tokenGetter.getAccessToken()
}

# 只查询你确定会返回值的基础指标，避免空值过多
def get_company_profile(code: str) -> dict:
    """
    输入单个股票代码，返回完整公司画像信息，只保留非null字段
    """
    indicators = [
        "ths_corp_cn_name_stock",        # 公司中文名
        "ths_stock_short_name_stock",    # 股票简称
        "ths_office_address_stock",      # 办公地址
        "ths_legal_representative_stock" # 法人代表
    ]

    thsPara = {
        "codes": code,
        "indipara": [{"indicator": ind, "indiparams": [""]} for ind in indicators]
    }

    # 请求
    resp = requests.post(url=thsUrl, json=thsPara, headers=thsHeaders)
    j = resp.json()

    # 错误处理
    if j.get("errorcode", -1) != 0:
        print("Error:", j.get("errmsg", "unknown"))
        return {}

    # 提取信息，只保留非空字段
    info = {"code": code}
    tables = j.get("tables", [])
    if tables:
        table = tables[0].get("table", {})
        for ind in indicators:
            val = table.get(ind, [None])[0]
            if val is not None and val != "":
                info[ind] = val

    return info


if __name__ == "__main__":
    code = "600000.SH"
    profile = get_company_profile(code)
    print(json.dumps(profile, indent=2, ensure_ascii=False))