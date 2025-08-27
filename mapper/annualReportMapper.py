import entity
import dbConnector

def selectAllAnnualReport():
    connection = None
    try:
        connection = dbConnector.run()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM annual_report"
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
    except Exception as e:
        print("❌ 查询失败:", e)
        return []
    finally:
        if connection:
            try:
                connection.close()
            except Exception as close_error:
                print("⚠️ 关闭连接失败:", close_error)

def selectAnnualReportByCompanyCodeAndYearOrId(company_code: str = None, year: str = None, id: int = None):
    """
    根据公司代码 + 年份 或 ID 查询年报
    """
    if (company_code and year) is None and id is None:
        raise ValueError("必须提供 公司代码 和 年份 或 ID 之一")

    connection = None
    try:
        connection = dbConnector.run()
        with connection.cursor() as cursor:
            if id is not None:
                sql = "SELECT * FROM annual_report WHERE id = %s"
                cursor.execute(sql, (id,))
            else:
                sql = "SELECT * FROM annual_report WHERE company_code = %s AND `year` = %s"
                cursor.execute(sql, (company_code, year))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print("❌ 查询失败:", e)
        return None
    finally:
        if connection:
            try:
                connection.close()
            except Exception as close_error:
                print("⚠️ 关闭连接失败:", close_error)

def insertAnnualReport(annualReport: entity.Annual_Report):
    connection = None
    try:
        connection = dbConnector.run()
        with connection.cursor() as cursor:
            sql = ("INSERT INTO annual_report "
                   "(company_code, company_name, title, `year`, link, pdf_url, txt_url) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s)")
            cursor.execute(sql,
                           (annualReport.company_code,
                            annualReport.company_name,
                            annualReport.title,
                            annualReport.year,
                            annualReport.link,
                            annualReport.pdf_url,
                            annualReport.txt_url))
        connection.commit()
        print("✅ 插入成功")
        return "success"
    except Exception as e:
        print("❌ 插入失败:", e)
        if connection:
            try:
                connection.rollback()
            except Exception as rollback_error:
                print("⚠️ 回滚失败:", rollback_error)
    finally:
        if connection:
            try:
                connection.close()
            except Exception as close_error:
                print("⚠️ 关闭连接失败:", close_error)



def updateAnnualReportUrls(company_code: str, year: str, pdf_url: str, txt_url: str):
    """
    根据公司代码 + 年份 更新 pdf_url 和 txt_url
    """
    connection = None
    try:
        connection = dbConnector.run()
        with connection.cursor() as cursor:
            sql = (
                "UPDATE annual_report "
                "SET pdf_url = %s, txt_url = %s "
                "WHERE company_code = %s AND `year` = %s"
            )
            cursor.execute(sql, (pdf_url, txt_url, company_code, year))
        connection.commit()
        print(f"✅ 更新成功: {company_code} {year}")
        return "success"
    except Exception as e:
        print(f"❌ 更新失败: {company_code} {year}, {e}")
        if connection:
            try:
                connection.rollback()
            except Exception as rollback_error:
                print("⚠️ 回滚失败:", rollback_error)
    finally:
        if connection:
            try:
                connection.close()
            except Exception as close_error:
                print("⚠️ 关闭连接失败:", close_error)

