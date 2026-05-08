# ---- Stage 1: Build dependencies ----
FROM python:3.12-slim AS builder
WORKDIR /build

# 安装编译依赖（部分 Python 包需要 gcc）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.12-slim AS runtime
WORKDIR /app

# 复制安装好的 pip 包
COPY --from=builder /install /usr/local

# 创建非 root 用户
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid 1001 --no-create-home appuser && \
    mkdir -p chroma_db uploads && \
    chown -R appuser:appuser /app

# 复制应用源码
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
