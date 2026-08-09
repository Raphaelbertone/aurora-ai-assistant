from src.loader import (
    listar_arquivos_pdf,
    carregar_documentos,
)


def main():

    print("=" * 70)
    print("AGENTE AURORA")
    print("TESTE DE CARREGAMENTO DA BASE DE CONHECIMENTO")
    print("=" * 70)

    arquivos_pdf = listar_arquivos_pdf()

    print(
        f"\nArquivos PDF encontrados: "
        f"{len(arquivos_pdf)}"
    )

    for arquivo_pdf in arquivos_pdf:
        print(
            f"  - {arquivo_pdf.name}"
        )

    print("\nCarregando documentos...")

    documentos = carregar_documentos()

    print(
        f"\nPáginas com texto carregadas: "
        f"{len(documentos)}"
    )

    primeiro_documento = documentos[0]

    print("\nExemplo do primeiro documento:")

    print("\nMetadados:")
    print(primeiro_documento.metadata)

    print("\nTrecho inicial:")
    print("-" * 70)

    print(
        primeiro_documento.page_content[:1000]
    )

    print("-" * 70)

    print(
        "\nTESTE DE CARREGAMENTO "
        "CONCLUÍDO COM SUCESSO."
    )


if __name__ == "__main__":
    main()