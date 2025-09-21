import requests
import json
import tokenGetter

# === 配置 ===
thsUrl = "https://quantapi.51ifind.com/api/v1/basic_data_service"
thsHeaders = {
    "Content-Type": "application/json",
    "access_token": tokenGetter.getAccessToken()
}

def get_company_name(code: str) -> str:
    """
    输入单个股票代码，返回公司中文名
    例如: get_company_name("600000.SH") -> "浦发银行"
    """
    thsPara = {
        "codes": code,
        "indipara": [
            {
                "indicator": "ths_corp_cn_name_stock",  # 公司中文名指标
                "indiparams": [""]
            }
        ]
    }

    # 请求
    resp = requests.post(url=thsUrl, json=thsPara, headers=thsHeaders)
    j = json.loads(resp.content.decode("utf-8"))

    # 错误处理
    if j.get("errorcode", -1) != 0:
        print("Error:", j.get("errmsg", "unknown"))
        return None

    # 提取公司名
    tables = j.get("tables", [])
    if tables:
        table = tables[0].get("table", {})
        name_list = table.get("ths_corp_cn_name_stock", [])
        if name_list:
            return name_list[0]

    return None


if __name__ == "__main__":
    # 示例：查询单个股票的公司名
    code = "600000.SH"
    name = get_company_name(code)
    print(name)