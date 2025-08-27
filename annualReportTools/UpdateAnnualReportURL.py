import os
import re
from mapper import annualReportMapper as mapper

# 获取项目根目录（包含 annualReportTools 的目录）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def get_relative_path(abs_path: str) -> str:
    """
    将绝对路径转换为相对于项目根目录的路径
    """
    path = os.path.relpath(abs_path, PROJECT_ROOT)
    # 保持路径前面带上 'annualReportTools/' 前缀
    path = os.path.join("annualReportTools", path)
    print(f"转换路径: {abs_path} -> {path}")
    return path


def update_db_from_txt(year_range=range(2020, 2026)):
    """
    扫描 txt_Format 文件夹，根据文件名更新 annual_report 表中的 pdf_url 和 txt_url
    """
    base_dir = os.path.join(PROJECT_ROOT, "annualFiles")

    for year in year_range:
        txt_dir = os.path.join(base_dir, str(year), "txt_Format")
        pdf_dir = os.path.join(base_dir, str(year), "pdf_Format")

        if not os.path.exists(txt_dir):
            print(f"⚠️ 跳过 {year}，目录不存在: {txt_dir}")
            continue

        for file_name in os.listdir(txt_dir):
            if not file_name.endswith(".txt"):
                continue

            try:
                # 文件名格式: 000001_公司简称_2020.txt
                match = re.match(r"(\d{6})_(.+)_(\d{4})\.txt", file_name)
                if not match:
                    print(f"⚠️ 文件名格式不符合要求，跳过: {file_name}")
                    continue

                company_code, company_name, year_str = match.groups()

                # 相对路径
                txt_abs_path = os.path.join(txt_dir, file_name)
                txt_url = get_relative_path(txt_abs_path)

                pdf_file_name = f"{company_code}_{company_name}_{year_str}.pdf"
                pdf_abs_path = os.path.join(pdf_dir, pdf_file_name)
                pdf_url = get_relative_path(pdf_abs_path) if os.path.exists(pdf_abs_path) else ""

                # 更新数据库
                mapper.updateAnnualReportUrls(
                    company_code=company_code,
                    year=year_str,
                    pdf_url=pdf_url,
                    txt_url=txt_url
                )

                print(f"✅ 已更新: {company_code} {company_name} {year_str}")

            except Exception as e:
                print(f"❌ 处理文件 {file_name} 出错: {e}")

    print("🎯 数据库更新完成")


if __name__ == "__main__":
    update_db_from_txt()