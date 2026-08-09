from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from src.config import DIRETORIO_DOCUMENTOS


def listar_arquivos_pdf(
    diretorio: Path = DIRETORIO_DOCUMENTOS,
) -> list[Path]:
    """
    Localiza todos os arquivos PDF da Base Oficial de Conhecimento.
    """

    if not diretorio.exists():
        raise FileNotFoundError(
            f"Diretório não encontrado: {diretorio}"
        )

    arquivos_pdf = sorted(
        diretorio.glob("*.pdf")
    )

    if not arquivos_pdf:
        raise FileNotFoundError(
            f"Nenhum arquivo PDF foi encontrado em: {diretorio}"
        )

    return arquivos_pdf


def carregar_documentos(
    diretorio: Path = DIRETORIO_DOCUMENTOS,
) -> list[Document]:
    """
    Carrega todos os PDFs página por página.

    Os metadados são preservados e complementados
    para permitir o rastreamento da origem das informações.
    """

    arquivos_pdf = listar_arquivos_pdf(
        diretorio
    )

    documentos: list[Document] = []

    for caminho_pdf in arquivos_pdf:

        carregador = PyPDFLoader(
            str(caminho_pdf),
            mode="page",
        )

        paginas = carregador.load()

        for pagina in paginas:

            texto = (
                pagina.page_content or ""
            ).strip()

            if not texto:
                continue

            numero_pagina_original = (
                pagina.metadata.get("page")
            )

            if isinstance(
                numero_pagina_original,
                int,
            ):
                numero_pagina = (
                    numero_pagina_original + 1
                )
            else:
                numero_pagina = None

            pagina.metadata.update(
                {
                    "arquivo_origem": caminho_pdf.name,
                    "nome_documento": caminho_pdf.stem,
                    "volume": caminho_pdf.stem,
                    "numero_pagina": numero_pagina,
                }
            )

            pagina.page_content = texto

            documentos.append(
                pagina
            )

    if not documentos:
        raise ValueError(
            "Os arquivos PDF foram encontrados, "
            "mas nenhum conteúdo textual utilizável "
            "pôde ser extraído."
        )

    return documentos