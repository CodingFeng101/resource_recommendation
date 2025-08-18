# 使用官方 Python 3.11 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 1. 先换成清华完整镜像（包含 trixie）
RUN echo '\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ trixie main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ trixie-updates main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ trixie-security main contrib non-free non-free-firmware\n\
' > /etc/apt/sources.list

# 2. 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ libpq-dev libmariadb-dev pkg-config curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# ---------------- 换 pip 源（清华） ----------------
RUN mkdir -p /etc/pip && \
    echo '[global]\n\
index-url = http://pypi.tuna.tsinghua.edu.cn/simple\n\
trusted-host = pypi.tuna.tsinghua.edu.cn\n\
extra-index-url = http://mirrors.aliyun.com/pypi/simple/\n\
trusted-host = mirrors.aliyun.com\n\
' > /etc/pip/pip.conf

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host mirrors.aliyun.com && \
    pip install --no-cache-dir -r requirements.txt --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host mirrors.aliyun.com

# 复制项目代码
COPY . /app/backend

# 创建非 root 用户（可选，提高安全性）
RUN addgroup --system appgroup && \
    adduser --system --group appuser

# 更改文件权限
RUN chown -R appuser:appgroup /app

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]