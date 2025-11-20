# 使用官方轻量版 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 将项目文件复制到容器中
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置容器启动命令
CMD ["python", "main.py"]
