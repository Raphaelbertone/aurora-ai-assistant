from src.retriever import obter_retriever


def exibir_resultado(
    indice: int,
    documento,
) -> None:
    """
    Exibe um fragmento recuperado e seus metadados
    de origem de forma organizada.
    """

    metadados = documento.metadata

    print("\n" + "=" * 70)

    print(
        f"RESULTADO {indice}"
    )

    print(
        f"Volume: "
        f"{metadados.get('volume', 'Não informado')}"
    )

    print(
        f"Arquivo: "
        f"{metadados.get('arquivo_origem', 'Não informado')}"
    )

    print(
        f"Página: "
        f"{metadados.get('numero_pagina', 'Não informada')}"
    )

    print(
        f"Fragmento: "
        f"{metadados.get('identificador_fragmento', 'Não informado')}"
    )

    print("-" * 70)

    print(
        documento.page_content
    )


def main():

    print("=" * 70)
    print("AGENTE AURORA")
    print("TESTE DE RECUPERAÇÃO SEMÂNTICA")
    print("=" * 70)

    print(
        "\nCarregando a base vetorial..."
    )

    recuperador = obter_retriever()

    print(
        "Base vetorial carregada com sucesso."
    )

    while True:

        pergunta = input(
            "\nDigite uma pergunta "
            "(ou 'sair' para encerrar): "
        ).strip()

        if pergunta.lower() in {
            "sair",
            "exit",
            "quit",
        }:
            print(
                "\nTeste encerrado."
            )
            break

        if not pergunta:
            print(
                "Digite uma pergunta válida."
            )
            continue

        print(
            "\nRealizando busca semântica..."
        )

        documentos_recuperados = (
            recuperador.invoke(pergunta)
        )

        print(
            f"\nFragmentos recuperados: "
            f"{len(documentos_recuperados)}"
        )

        for indice, documento in enumerate(
            documentos_recuperados,
            start=1,
        ):
            exibir_resultado(
                indice,
                documento,
            )


if __name__ == "__main__":
    main()