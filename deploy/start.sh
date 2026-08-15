#!/usr/bin/env bash

set -euo pipefail


echo "============================================================"
echo "AGENTE AURORA"
echo "INICIALIZAÇÃO DO AMBIENTE"
echo "============================================================"


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PORT="${PORT:-8501}"

OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"


# ============================================================
# VALIDAÇÃO DAS VARIÁVEIS OBRIGATÓRIAS
# ============================================================

if [ -z "${DATABASE_URL:-}" ]; then
    echo
    echo "ERRO: DATABASE_URL não foi configurada."
    exit 1
fi


if [ -z "${GROQ_API_KEY:-}" ]; then
    echo
    echo "ERRO: GROQ_API_KEY não foi configurada."
    exit 1
fi


echo
echo "Configuração básica validada."


# ============================================================
# OLLAMA
# ============================================================

echo
echo "Verificando serviço Ollama em:"
echo "${OLLAMA_BASE_URL}"

tentativa=1
max_tentativas=30

until curl \
    --silent \
    --fail \
    "${OLLAMA_BASE_URL}/api/tags" \
    > /dev/null
do

    if [ "${tentativa}" -ge "${max_tentativas}" ]; then

        echo
        echo "ERRO: Ollama não ficou disponível."
        exit 1
    fi

    echo \
        "Aguardando Ollama... " \
        "(${tentativa}/${max_tentativas})"

    tentativa=$((tentativa + 1))

    sleep 2

done

echo "Ollama disponível."


# ============================================================
# POSTGRESQL
# ============================================================

echo
echo "Verificando PostgreSQL..."

tentativa=1
max_tentativas=30

until python -c \
    "from src.reservas.database import testar_conexao; assert testar_conexao()"
do

    if [ "${tentativa}" -ge "${max_tentativas}" ]; then

        echo
        echo "ERRO: PostgreSQL não ficou disponível."
        exit 1
    fi

    echo \
        "Aguardando PostgreSQL... " \
        "(${tentativa}/${max_tentativas})"

    tentativa=$((tentativa + 1))

    sleep 2

done

echo "PostgreSQL disponível."


# ============================================================
# BANCO DA CENTRAL
# ============================================================

echo
echo "Inicializando tabelas..."

python -m scripts.init_database


echo
echo "Sincronizando catálogo..."

python -m scripts.seed_database


# ============================================================
# FAISS
# ============================================================

echo
echo "Verificando índice FAISS..."

if (
    [ ! -d "data/faiss" ] ||
    [ -z "$(find data/faiss -maxdepth 1 -type f -print -quit 2>/dev/null)" ]
); then

    echo
    echo "Índice não encontrado."
    echo "Construindo FAISS..."

    python -m scripts.build_index

else

    echo "Índice FAISS existente."

fi


# ============================================================
# STREAMLIT
# ============================================================

echo
echo "============================================================"
echo "INICIANDO AGENTE AURORA"
echo "Porta: ${PORT}"
echo "============================================================"
echo


exec streamlit run app.py \
    --server.address=0.0.0.0 \
    --server.port="${PORT}" \
    --server.headless=true