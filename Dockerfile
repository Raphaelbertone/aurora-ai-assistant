FROM python:3.13-slim-bookworm


# ============================================================
# CONFIGURAÇÃO
# ============================================================

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app


# ============================================================
# DEPENDÊNCIAS DO SISTEMA
# ============================================================

RUN apt-get update \
    && apt-get install -y \
        --no-install-recommends \
        curl \
        ca-certificates \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# DEPENDÊNCIAS PYTHON
# ============================================================

COPY requirements.txt .

RUN python -m pip install \
        --no-cache-dir \
        --upgrade pip \
    && python -m pip install \
        --no-cache-dir \
        -r requirements.txt


# ============================================================
# APLICAÇÃO
# ============================================================

COPY . .


# ============================================================
# SCRIPT DE START
# ============================================================

RUN sed -i 's/\r$//' /app/deploy/start.sh \
    && chmod +x /app/deploy/start.sh


# ============================================================
# STREAMLIT
# ============================================================

EXPOSE 8501


HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=30s \
    --retries=3 \
    CMD curl --fail "http://localhost:${PORT:-8501}/_stcore/health" || exit 1


CMD ["/app/deploy/start.sh"]