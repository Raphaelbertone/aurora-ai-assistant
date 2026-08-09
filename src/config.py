from pathlib import Path
import os


# Diretório raiz do projeto
DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent

# Base Oficial de Conhecimento
DIRETORIO_DOCUMENTOS = DIRETORIO_RAIZ / "documentos"

# Índice vetorial persistido
DIRETORIO_FAISS = DIRETORIO_RAIZ / "data" / "faiss"


# Modelos utilizados pelo Ollama
MODELO_VETORIZACAO_OLLAMA = os.getenv(
    "MODELO_VETORIZACAO_OLLAMA",
    "bge-m3:567m",
)

MODELO_LINGUAGEM_OLLAMA = os.getenv(
    "MODELO_LINGUAGEM_OLLAMA",
    "qwen3:4b",
)


# Configuração inicial da fragmentação
TAMANHO_FRAGMENTO = int(
    os.getenv("TAMANHO_FRAGMENTO", "1000")
)

SOBREPOSICAO_FRAGMENTO = int(
    os.getenv("SOBREPOSICAO_FRAGMENTO", "100")
)


# Quantidade padrão de resultados recuperados
QUANTIDADE_RESULTADOS = int(
    os.getenv("QUANTIDADE_RESULTADOS", "4")
)