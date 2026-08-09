from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    TAMANHO_FRAGMENTO,
    SOBREPOSICAO_FRAGMENTO,
)


def fragmentar_documentos(
    documentos: list[Document],
    tamanho_fragmento: int = TAMANHO_FRAGMENTO,
    sobreposicao_fragmento: int = SOBREPOSICAO_FRAGMENTO,
) -> list[Document]:
    """
    Divide os documentos em fragmentos menores,
    preservando os metadados de origem.
    """

    if not documentos:
        raise ValueError(
            "Nenhum documento foi fornecido para fragmentação."
        )

    if tamanho_fragmento <= 0:
        raise ValueError(
            "O tamanho do fragmento deve ser maior que zero."
        )

    if sobreposicao_fragmento < 0:
        raise ValueError(
            "A sobreposição não pode ser negativa."
        )

    if sobreposicao_fragmento >= tamanho_fragmento:
        raise ValueError(
            "A sobreposição deve ser menor "
            "que o tamanho do fragmento."
        )

    fragmentador = RecursiveCharacterTextSplitter(
        chunk_size=tamanho_fragmento,
        chunk_overlap=sobreposicao_fragmento,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    fragmentos = fragmentador.split_documents(
        documentos
    )

    for indice_fragmento, fragmento in enumerate(
        fragmentos
    ):

        nome_documento = fragmento.metadata.get(
            "nome_documento",
            "documento",
        )

        numero_pagina = fragmento.metadata.get(
            "numero_pagina",
            "x",
        )

        fragmento.metadata[
            "indice_fragmento"
        ] = indice_fragmento

        fragmento.metadata[
            "identificador_fragmento"
        ] = (
            f"{nome_documento}"
            f"-p{numero_pagina}"
            f"-f{indice_fragmento}"
        )

    if not fragmentos:
        raise ValueError(
            "Nenhum fragmento foi produzido."
        )

    return fragmentos