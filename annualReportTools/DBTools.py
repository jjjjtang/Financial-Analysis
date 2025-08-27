import os
import pandas as pd
import entity
from mapper import annualReportMapper as mapper

def import_excel_to_db(excel_path: str):
    try:
        df = pd.read_excel(excel_path)

        for _, row in df.iterrows():
            # 构造 Annual_Report 对象
            report = entity.Annual_Report(
                id=None,  # 数据库自增，这里设 None
                company_code=str(row["公司代码"]).strip(),
                company_name=str(row["公司简称"]).strip(),
                title=str(row["标题"]).strip(),
                year=str(row["年份"]).strip(),
                link=str(row["年报链接"]).strip(),
                pdf_url="",  # 默认空，后续下载时更新
                txt_url=""   # 默认空，后续转换时更新
            )

            mapper.insertAnnualReport(report)

    except Exception as e:
        print(f"❌ 导入 {excel_path} 出错: {e}")


def main():
    folder = "./annualReport"
    if not os.path.exists(folder):
        print(f"❌ 文件夹 {folder} 不存在")
        return

    files = [f for f in os.listdir(folder) if f.endswith(".xlsx")]

    if not files:
        print("⚠️ annualReport 文件夹下没有找到任何 Excel 文件")
        return

    for file in files:
        excel_path = os.path.join(folder, file)
        print(f"📂 正在导入: {excel_path}")
        import_excel_to_db(excel_path)

    print("✅ 所有 Excel 已导入数据库")


if __name__ == "__main__":
    main()