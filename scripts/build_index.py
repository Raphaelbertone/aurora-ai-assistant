from src.config import DIRETORIO_FAISS
from src.loader import (
    listar_arquivos_pdf,
    carregar_documentos,
)
from src.splitter import fragmentar_documentos
from src.vectorstore import construir_base_vetorial


def main():

    print("=" * 70)
    print("AGENTE AURORA")
    print("CONSTRUÇÃO DO ÍNDICE VETORIAL")
    print("=" * 70)

    print(
        "\n1. Localizando a Base Oficial de Conhecimento..."
    )

    arquivos_pdf = listar_arquivos_pdf()

    print(
        f"Arquivos PDF encontrados: "
        f"{len(arquivos_pdf)}"
    )

    for arquivo_pdf in arquivos_pdf:
        print(
            f"  - {arquivo_pdf.name}"
        )

    print(
        "\n2. Carregando os documentos..."
    )

    documentos = carregar_documentos()

    print(
        f"Páginas com texto carregadas: "
        f"{len(documentos)}"
    )

    print(
        "\n3. Fragmentando os documentos..."
    )

    fragmentos = fragmentar_documentos(
        documentos
    )

    print(
        f"Fragmentos gerados: "
        f"{len(fragmentos)}"
    )

    print(
        "\n4. Gerando embeddings com BGE-M3..."
    )

    print(
        "O processamento será realizado "
        "localmente pelo Ollama."
    )

    construir_base_vetorial(
        fragmentos
    )

    print(
        "\n5. Índice FAISS persistido com sucesso."
    )

    print(
        f"Diretório: {DIRETORIO_FAISS}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "BASE VETORIAL DO AGENTE AURORA "
        "CONSTRUÍDA COM SUCESSO."
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()