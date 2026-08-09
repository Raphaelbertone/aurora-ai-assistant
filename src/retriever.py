from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from src.config import QUANTIDADE_RESULTADOS
from src.vectorstore import carregar_base_vetorial

from functools import lru_cache


@lru_cache(maxsize=4)
def obter_retriever(
    quantidade_resultados: int = QUANTIDADE_RESULTADOS,
) -> VectorStoreRetriever:
    """
    Cria e retorna o Retriever utilizado pelo Agente Aurora.

    O Retriever consulta a base vetorial FAISS utilizando
    busca por similaridade semântica e retorna os fragmentos
    mais relevantes para a pergunta realizada.
    """

    if quantidade_resultados <= 0:
        raise ValueError(
            "A quantidade de resultados deve ser maior que zero."
        )

    base_vetorial = carregar_base_vetorial()

    recuperador = base_vetorial.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": quantidade_resultados,
        },
    )

    return recuperador


def recuperar_documentos(
    pergunta: str,
    quantidade_resultados: int = QUANTIDADE_RESULTADOS,
) -> list[Document]:
    """
    Recupera os fragmentos mais relevantes da Base Oficial
    de Conhecimento para uma determinada pergunta.
    """

    pergunta = pergunta.strip()

    if not pergunta:
        raise ValueError(
            "A pergunta não pode estar vazia."
        )

    recuperador = obter_retriever(
        quantidade_resultados=quantidade_resultados
    )

    documentos_recuperados = recuperador.invoke(
        pergunta
    )

    return documentos_recuperados