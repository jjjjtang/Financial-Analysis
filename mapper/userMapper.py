import dbConnector
import entity


def selectAllUser():
    connection = None
    try:
        connection = dbConnector.run()
        with connection.cursor() as cursor:
            # 执行查询语句
            sql = "SELECT * FROM user"
            cursor.execute(sql)
            # 获取所有结果
            results = cursor.fetchall()
            return results
    finally:
        # 关闭连接
        connection.close()


def insertUser(user: entity.User):
    connection = None
    try:
        connection = dbConnector.run()
        with connection.cursor() as cursor:
            sql = "INSERT INTO user (user_id, username, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user.user_id, user.username, user.password))
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

