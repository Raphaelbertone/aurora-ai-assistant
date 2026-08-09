from src.rag import gerar_resposta


def exibir_fontes(
    fontes: list[dict[str, object]],
) -> None:
    """
    Exibe as fontes utilizadas pelo fluxo RAG.
    """

    if not fontes:
        print("\nFontes: nenhuma.")
        return

    print("\nFontes consultadas:")

    for indice, fonte in enumerate(
        fontes,
        start=1,
    ):
        print(
            f"{indice}. "
            f"{fonte['volume']} — "
            f"página {fonte['pagina']} "
            f"({fonte['arquivo']})"
        )


def main():

    print("=" * 70)
    print("AGENTE AURORA")
    print("TESTE DO RAG COMPLETO")
    print("=" * 70)

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
            "\nConsultando o Agente Aurora..."
        )

        resultado = gerar_resposta(
            pergunta
        )

        print(
            "\nResposta:"
        )

        print(
            resultado["resposta"]
        )

        exibir_fontes(
            resultado["fontes"]
        )


if __name__ == "__main__":
    main()