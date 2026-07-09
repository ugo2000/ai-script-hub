# 使用 Python 3.12 作为基础镜像
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制项目文件
COPY . .

# Zeabur 通过 PORT 环境变量指定端口
EXPOSE 3722

# 启动服务
CMD ["python", "server.py"]
