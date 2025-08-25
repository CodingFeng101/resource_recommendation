# 1. 使用更轻量的 Alpine 基础镜像
FROM python:3.11-alpine

# 2. 工作目录和环境变量
WORKDIR /app/backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# 3. 使用阿里云 Alpine 源并安装系统依赖（合并为一层）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add --no-cache \
        gcc \
        g++ \
        libstdc++ \
        musl-dev \
        mariadb-connector-c-dev \
        postgresql-dev \
        curl \
        linux-headers

# 4. 配置 pip 源并安装依赖（合并为一层）
COPY requirements.txt .
RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 5. 复制代码 + 创建非 root 用户
COPY . /app/backend
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser
EXPOSE 8000

# 6. 健康检查（curl 已安装）
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 7. 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
