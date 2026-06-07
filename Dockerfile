# HBBSS 账号管理系统 - Dockerfile

FROM python:3.11-slim

LABEL maintainer="HBBSS"
LABEL description="HBBSS Account Management System"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements-server.txt /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-server.txt

# 复制应用文件
COPY server.py /app/
COPY cloud_sync_client.py /app/
COPY .env.example /app/.env

# 创建非root用户
RUN useradd -m -u 1000 hbbss
RUN chown -R hbbss:hbbss /app
USER hbbss

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# 启动应用
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "--timeout", "60", "server:app"]
