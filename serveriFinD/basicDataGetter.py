import requests
import json
import tokenGetter

# === 配置 ===
thsUrl = 'https://quantapi.51ifind.com/api/v1/basic_data_service'
thsHeaders = {
    "Content-Type": "application/json",
    "access_token": tokenGetter.getAccessToken()
}

def get_basic_data(codes):
    """
    输入：codes 可以是字符串（"300033.SZ,600000.SH"）或列表（["300033.SZ", "600000.SH"]）
    返回：JSON 格式的基础数据列表
    """
    if isinstance(codes, list):
        codes = ",".join(codes)

    thsPara = {
        "codes": codes,
        "indipara": [
            {
                "indicator": "ths_regular_report_actual_dd_stock",
                "indiparams": ["104"]
            },
            {
                "indicator": "ths_total_shares_stock",
                "indiparams": ["20220705"]
            }
        ]
    }

    resp = requests.post(url=thsUrl, json=thsPara, headers=thsHeaders)
    j = json.loads(resp.content.decode("utf-8"))

    if j.get("errorcode", -1) != 0:
        print("Error:", j.get("errmsg", "unknown"))
        return []

    result = []
    for item in j.get("tables", []):
        table = item.get("table", {})
        data = {
            "thscode": item.get("thscode"),
            "ths_regular_report_actual_dd_stock": table.get("ths_regular_report_actual_dd_stock", [None])[0],
            "ths_total_shares_stock": table.get("ths_total_shares_stock", [None])[0]
        }
        result.append(data)

    return result


if __name__ == "__main__":
    # 测试：可以输入单个code，也可以输入列表
    codes_list = ["300033.SZ", "600000.SH"]
    data_json = get_basic_data(codes_list)
    print(json.dumps(data_json, indent=2, ensure_ascii=False))