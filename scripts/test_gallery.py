from src.gallery import (
    selecionar_imagens,
    validar_galeria,
)


def mostrar_resultado(
    pergunta: str,
    limite: int = 2,
) -> None:
    imagens = selecionar_imagens(
        pergunta,
        limite=limite,
    )

    print("=" * 70)
    print(f"PERGUNTA: {pergunta}")
    print()

    if not imagens:
        print("IMAGENS: nenhuma")
        return

    print(f"IMAGENS ENCONTRADAS: {len(imagens)}")
    print()

    for indice, imagem in enumerate(imagens, start=1):
        print(
            f"{indice}. {imagem['titulo']} "
            f"({imagem['id']})"
        )


def main() -> None:
    erros = validar_galeria()

    print("\nVALIDAÇÃO DA GALERIA")
    print("-" * 70)

    if erros:
        print("Foram encontrados problemas:\n")

        for erro in erros:
            print(f"- {erro}")

        return

    print("Catálogo e arquivos validados com sucesso.\n")

    testes = [
        ("Tem foto da piscina?", 2),
        ("Mostra o deck do pôr do sol.", 2),
        ("Quero ver a Suíte Master Pôr do Sol.", 2),
        ("Onde é o melhor lugar para assistir ao pôr do sol?", 2),
        ("Qual suíte você recomenda para lua de mel?", 2),
        ("Como é a área externa da pousada?", 2),
        ("Qual é o horário do check-in?", 2),
        ("Quanto custa a Suíte Master Pôr do Sol?", 2),
        ("Quais são todas as categorias de acomodação?", 2),

        # Pedidos explícitos de galeria
        ("Tem fotos dos quartos?", 6),
        ("Mostre fotos da pousada.", 3),
        ("Tem foto do restaurante?", 2),
    ]

    for pergunta, limite in testes:
        mostrar_resultado(
            pergunta,
            limite=limite,
        )


if __name__ == "__main__":
    main()