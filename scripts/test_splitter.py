from src.loader import carregar_documentos
from src.splitter import fragmentar_documentos
from src.config import (
    TAMANHO_FRAGMENTO,
    SOBREPOSICAO_FRAGMENTO,
)


def main():

    print("=" * 70)
    print("AGENTE AURORA")
    print("TESTE DE FRAGMENTAÇÃO")
    print("=" * 70)

    print(
        "\nCarregando a Base de Conhecimento..."
    )

    documentos = carregar_documentos()

    print(
        f"Páginas carregadas: "
        f"{len(documentos)}"
    )

    print("\nConfiguração:")

    print(
        f"Tamanho do fragmento: "
        f"{TAMANHO_FRAGMENTO}"
    )

    print(
        f"Sobreposição: "
        f"{SOBREPOSICAO_FRAGMENTO}"
    )

    print("\nGerando fragmentos...")

    fragmentos = fragmentar_documentos(
        documentos
    )

    print(
        f"\nFragmentos gerados: "
        f"{len(fragmentos)}"
    )

    tamanhos = [
        len(fragmento.page_content)
        for fragmento in fragmentos
    ]

    print(
        "\nEstatísticas dos fragmentos:"
    )

    print(
        f"Menor fragmento: "
        f"{min(tamanhos)} caracteres"
    )

    print(
        f"Maior fragmento: "
        f"{max(tamanhos)} caracteres"
    )

    print(
        f"Média: "
        f"{sum(tamanhos) / len(tamanhos):.2f} caracteres"
    )

    primeiro_fragmento = fragmentos[0]

    print("\nPrimeiro fragmento:")
    print("-" * 70)

    print(
        primeiro_fragmento.page_content
    )

    print("-" * 70)

    print("\nMetadados:")
    print(
        primeiro_fragmento.metadata
    )

    fragmentos_pequenos = [
        fragmento
        for fragmento in fragmentos
        if len(fragmento.page_content) < 100
    ]

    print(
        "\nFragmentos com menos de "
        f"100 caracteres: "
        f"{len(fragmentos_pequenos)}"
    )

    for fragmento in fragmentos_pequenos:

        print("\n" + "-" * 70)

        print(
            fragmento.metadata.get(
                "identificador_fragmento"
            )
        )

        print(
            repr(
                fragmento.page_content
            )
        )

    print(
        "\nTESTE DE FRAGMENTAÇÃO "
        "CONCLUÍDO COM SUCESSO."
    )


if __name__ == "__main__":
    main()