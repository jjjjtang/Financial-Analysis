import requests
import re
import openpyxl
import time
import os

AUTHOR = " - 唐哲"
def get_report(page_num,date):
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Content-Length": "195",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.cninfo.com.cn",
        "Origin": "http://www.cninfo.com.cn",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&checkedCategory=category_ndbg_szsh",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {
        "pageNum": page_num,
        "pageSize": 30,
        "column": "szse",
        "tabName": "fulltext",
        "plate": plate,
        "searchkey": "",
        "secid": "",
        "category": "category_ndbg_szsh",
        "trade": trade,
        "seDate": date,
        "sortName": "code",
        "sortType": "asc",
        "isHLtitle": "false"
    }
    response = requests.post(url, data=data, headers=headers)
    return response

# 发送HTTP请求并获取响应
def download_report(date):
    global counter
    all_results = []
    page_num = 1
    response_test = get_report(page_num, date)

    try:
        data_test = response_test.json()
        total_pages = data_test["totalpages"]

        # 检查total_pages是否为0
        if total_pages == 0:
            return all_results  # 提前返回空结果

    except (ValueError, KeyError) as e:
        print(f"获取总页数失败: {e}")
        return all_results  # 提前返回空结果

    max_retries = 3  # 最大重试次数

    while page_num <= total_pages+1:  # 多处理一页
        retry_count = 0  # 当前重试次数
        while retry_count <= max_retries:
            try:
                # 请求报告数据
                response = get_report(page_num, date)
                response.raise_for_status()
                data = response.json()

                # 解析并处理数据
                if data["announcements"] is None:
                    break
                else:
                    all_results.extend(data["announcements"])

                # 计算进度时，检查total_pages是否为0
                if total_pages > 0:
                    per = (counter / total_pages)
                    if per < 1:
                        print(f"\r当前年份下载进度 {per * 100:.2f} %", end='')
                    else:
                        print(f"\r下载完成，正在保存……", end='')
                else:
                    print("无法计算下载进度，总页数为0。")

                # 跳出重试循环
                break

            except requests.exceptions.RequestException as e:
                print(f"出现网络请求错误！: {e}")
                print(f"5秒后重试...")
                time.sleep(5)
                retry_count += 1

            except (ValueError, KeyError) as e:
                print(f"解析响应数据失败: {e}")
                print(f"5秒后重试...")
                time.sleep(5)
                retry_count += 1

            # 如果达到最大重试次数，跳过此页
            if retry_count > max_retries:
                print(f"{max_retries}次重试后均失败. 跳过第{page_num}页.")
                break

        page_num += 1
        counter += 1  # 更新处理进度

    return all_results


def main(year):
    global sum
    date_count = f"{year}-01-01~{year}-12-31"
    response = get_report(1, date_count)
    data = response.json()
    sum = data["totalpages"]

    year = year + 1
    all_results = []
    time_segments = [
        f"{year}-01-01~{year}-04-01",
        f"{year}-04-02~{year}-04-15",
        f"{year}-04-16~{year}-04-22",
        f"{year}-04-23~{year}-04-26",
        f"{year}-04-27~{year}-04-28",
        f"{year}-04-29~{year}-04-30",
        f"{year}-05-01~{year}-07-31",
        f"{year}-08-01~{year}-10-31",
        f"{year}-11-01~{year}-11-30",
        f"{year}-12-01~{year}-12-31"
    ]

    # 最多获取 20 条
    MAX_RESULTS = 20

    for i in time_segments:
        results = download_report(i)
        all_results.extend(results)
        if len(all_results) >= MAX_RESULTS:  # 达到上限就停
            all_results = all_results[:MAX_RESULTS]
            break

    # 创建Excel文件并添加表头
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "公司年报 - 【人工智能学院】"
    worksheet.append(["公司代码", "公司简称", "标题", "年份", "年报链接"])

    # 解析搜索结果并添加到Excel表格中
    for item in all_results[:MAX_RESULTS]:  # 确保不会超过20条
        company_code = item["secCode"]
        company_name = item["secName"]
        title = item["announcementTitle"].strip()
        title = re.sub(r"<.*?>", "", title)
        title = title.replace("：", "")
        title = f"《{title}》"

        adjunct_url = item["adjunctUrl"]
        year_match = re.search(r"(\d{4})年", title)
        if year_match:
            year_str = year_match.group(1)
        else:
            year_str = setYear
        time = f"{year_str}"
        announcement_url = f"http://static.cninfo.com.cn/{adjunct_url}"

        exclude_flag = any(keyword in title for keyword in exclude_keywords)

        if not exclude_flag:
            worksheet.append([company_code, company_name, title, time, announcement_url])

    # 确保 annualReport 文件夹存在
    save_dir = "./annualReport"
    os.makedirs(save_dir, exist_ok=True)

    # 保存 Excel 文件
    save_path = os.path.join(save_dir, f"年报链接_{setYear}{AUTHOR}.xlsx")
    workbook.save(save_path)
    print(f"文件已保存：{save_path}")


if __name__ == '__main__':
    # 排除列表可以加入'更正后','修订版'来规避数据重复或公司发布之前年份的年报修订版等问题，
    exclude_keywords = ['英文','已取消','摘要']
    # 控制行业，若为空则不控制，仅可从参考内容中选取，中间用英文分号隔开
    # 参考内容："农、林、牧、渔业;电力、热力、燃气及水生产和供应业;建筑业;采矿业;制造业;批发和零售业;交通运输、仓储和邮政业;住宿和餐饮业;信息传输、软件和信息技术服务业;金融业;房地产业;租赁和商务服务业;科学研究和技术服务业;水利、环境和公共设施管理业;居民服务、修理和其他服务业;教育;卫生和社会工作;文化、体育和娱乐业;综合"
    trade = ""
    # 板块控制：深市sz 沪市sh 深主板szmb 沪主板shmb 创业板szcy 科创板shkcp 北交所bj 请按照格式填写
    plate = "sz;sh"
    global counter
    global sum
    counter = 1  # 计数器
    setYear = 2020 #设置下载年份
    Flag = 1  #是否开启批量下载模式
    if Flag:
        for setYear in range(2025,2026):
            counter = 1  # 计数器
            main(setYear)
            print(f"----{setYear}年下载完成")
    else:
        main(setYear)
        print(f"----{setYear}年下载完成")


