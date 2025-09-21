import dbConnector

#从annual_report表中查询公司信息company_code,company_name并且去重之后写入company表中
#company表中有id,company_code,company_name
def update_company_table():
    connection = None
    try:
        connection = dbConnector.run()
        with connection.cursor() as cursor:
            # 执行查询语句
            sql = "SELECT DISTINCT company_code, company_name FROM annual_report"
            cursor.execute(sql)
            # 获取所有结果
            results = cursor.fetchall()
            for row in results:
                try:
                    sql_insert = "INSERT INTO company (company_code, company_name) VALUES (%s, %s)"
                    cursor.execute(sql_insert, (row['company_code'], row['company_name']))
                except Exception as e:
                    print(f"⚠️ 插入公司 {row['company_code']} {row['company_name']} 失败，可能已存在: {e}")
            connection.commit()
            print("✅ 公司信息已成功写入 company 表")
    except Exception as e:
        print("❌ 操作失败:", e)
    finally:
        if connection:
            try:
                connection.close()
            except Exception as close_error:
                print("⚠️ 关闭连接失败:", close_error)

if __name__ == "__main__":
    update_company_table()
