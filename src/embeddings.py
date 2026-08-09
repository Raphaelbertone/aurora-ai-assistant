from langchain_ollama import OllamaEmbeddings

from src.config import MODELO_VETORIZACAO_OLLAMA


def obter_modelo_embeddings() -> OllamaEmbeddings:
    """
    Cria e retorna o modelo de embeddings utilizado pelo Agente Aurora.

    O modelo é executado localmente por meio do Ollama e será
    responsável por transformar os fragmentos da Base Oficial
    de Conhecimento em representações vetoriais.
    """

    modelo_embeddings = OllamaEmbeddings(
        model=MODELO_VETORIZACAO_OLLAMA
    )

    return modelo_embeddings