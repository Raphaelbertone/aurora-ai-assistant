from pathlib import Path
import os

from dotenv import load_dotenv


# Diretório raiz do projeto
DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent

# Carrega variáveis locais do arquivo .env, quando existente
load_dotenv(DIRETORIO_RAIZ / ".env")

# Base Oficial de Conhecimento
DIRETORIO_DOCUMENTOS = DIRETORIO_RAIZ / "documentos"

# Índice vetorial persistido
DIRETORIO_FAISS = DIRETORIO_RAIZ / "data" / "faiss"

# Provedor utilizado para geração das respostas
PROVEDOR_LLM = os.getenv(
    "PROVEDOR_LLM",
    "groq",
).strip().lower()

# Modelo de embeddings utilizado pelo Ollama
MODELO_VETORIZACAO_OLLAMA = os.getenv(
    "MODELO_VETORIZACAO_OLLAMA",
    "bge-m3:567m",
)

# Modelo de linguagem local
MODELO_LINGUAGEM_OLLAMA = os.getenv(
    "MODELO_LINGUAGEM_OLLAMA",
    "qwen3:4b",
)

# Modelo de linguagem utilizado pela Groq
MODELO_LINGUAGEM_GROQ = os.getenv(
    "MODELO_LINGUAGEM_GROQ",
    "llama-3.3-70b-versatile",
)

# Configuração da fragmentação
TAMANHO_FRAGMENTO = int(
    os.getenv(
        "TAMANHO_FRAGMENTO",
        "1000",
    )
)

SOBREPOSICAO_FRAGMENTO = int(
    os.getenv(
        "SOBREPOSICAO_FRAGMENTO",
        "100",
    )
)

# Quantidade padrão de resultados recuperados
QUANTIDADE_RESULTADOS = int(
    os.getenv(
        "QUANTIDADE_RESULTADOS",
        "6",
    )
)