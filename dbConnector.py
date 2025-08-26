import pymysql
from pymysql.cursors import DictCursor  # 引入 DictCursor


def run():
    # 数据库连接配置
    config = {
        "host": "114.55.40.205",  # 数据库主机地址
        "port": 3306,  # 端口号（默认 3306）
        "user": "root",  # 用户名
        "password": "802642wzxgx",  # 密码
        "database": "fin_analysis",  # 数据库名称
        "charset": "utf8",  #编码
        "cursorclass": DictCursor
    }

    # 建立连接
    connection = pymysql.connect(**config)
    return connection



