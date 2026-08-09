from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.config import DIRETORIO_FAISS
from src.embeddings import obter_modelo_embeddings


def construir_base_vetorial(
    fragmentos: list[Document],
    diretorio_persistencia: Path = DIRETORIO_FAISS,
) -> FAISS:
    """
    Constrói a base vetorial FAISS utilizando os fragmentos
    da Base Oficial de Conhecimento do Agente Aurora.

    Após a criação, o índice é persistido em disco para evitar
    a geração dos embeddings novamente a cada execução.
    """

    if not fragmentos:
        raise ValueError(
            "Nenhum fragmento foi fornecido "
            "para a construção da base vetorial."
        )

    modelo_embeddings = obter_modelo_embeddings()

    base_vetorial = FAISS.from_documents(
        documents=fragmentos,
        embedding=modelo_embeddings,
    )

    diretorio_persistencia.mkdir(
        parents=True,
        exist_ok=True,
    )

    base_vetorial.save_local(
        str(diretorio_persistencia)
    )

    return base_vetorial


def carregar_base_vetorial(
    diretorio_persistencia: Path = DIRETORIO_FAISS,
) -> FAISS:
    """
    Carrega do disco a base vetorial FAISS criada
    anteriormente pelo próprio projeto.
    """

    arquivo_indice = (
        diretorio_persistencia / "index.faiss"
    )

    arquivo_metadados = (
        diretorio_persistencia / "index.pkl"
    )

    if (
        not arquivo_indice.exists()
        or not arquivo_metadados.exists()
    ):
        raise FileNotFoundError(
            "O índice FAISS ainda não foi construído. "
            "Execute o script de construção do índice."
        )

    modelo_embeddings = obter_modelo_embeddings()

    base_vetorial = FAISS.load_local(
        str(diretorio_persistencia),
        modelo_embeddings,
        allow_dangerous_deserialization=True,
    )

    return base_vetorial