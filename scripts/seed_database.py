from decimal import Decimal

from sqlalchemy import select

from src.reservas.database import (
    abrir_sessao,
    motor_banco,
)
from src.reservas.models import (
    CategoriaAcomodacao,
    UnidadeAcomodacao,
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def gerar_codigos(
    prefixo: str,
    quantidade: int,
) -> list[str]:
    """
    Gera códigos sequenciais para as unidades.
    """

    return [
        f"{prefixo}-{indice:02d}"
        for indice in range(
            1,
            quantidade + 1,
        )
    ]


# ============================================================
# CATÁLOGO OFICIAL
# ============================================================

CATEGORIAS = [
    {
        "nome": "Quarto Standard Casal",
        "aliases": (
            "Standard Casal",
        ),
        "capacidade": 2,
        "tarifa_referencia": Decimal("420.00"),
        "descricao": (
            "Categoria oficial para até dois hóspedes."
        ),
        "unidades": gerar_codigos(
            "STD-CASAL",
            8,
        ),
    },
    {
        "nome": "Quarto Standard Família",
        "aliases": (
            "Standard Família",
        ),
        "capacidade": 4,
        "tarifa_referencia": Decimal("560.00"),
        "descricao": (
            "Categoria oficial para famílias "
            "de até quatro hóspedes."
        ),
        "unidades": gerar_codigos(
            "STD-FAM",
            6,
        ),
    },
    {
        "nome": "Suíte Superior",
        "aliases": (
            "Superior",
        ),
        "capacidade": 2,
        "tarifa_referencia": Decimal("690.00"),
        "descricao": (
            "Categoria oficial com conforto ampliado "
            "para até dois hóspedes."
        ),
        "unidades": gerar_codigos(
            "SUP",
            6,
        ),
    },
    {
        "nome": "Suíte Premium",
        "aliases": (
            "Premium",
        ),
        "capacidade": 2,
        "tarifa_referencia": Decimal("890.00"),
        "descricao": (
            "Categoria oficial premium "
            "para até dois hóspedes."
        ),
        "unidades": gerar_codigos(
            "PREM",
            4,
        ),
    },
    {
        "nome": "Suíte Master Pôr do Sol",
        "aliases": (
            "Master",
        ),
        "capacidade": 2,
        "tarifa_referencia": Decimal("1250.00"),
        "descricao": (
            "Categoria oficial de experiência "
            "premium para até dois hóspedes."
        ),
        "unidades": gerar_codigos(
            "MASTER",
            4,
        ),
    },
    {
        "nome": "Chalé Família Luxo",
        "aliases": (
            "Chalé",
        ),
        "capacidade": 5,
        "tarifa_referencia": Decimal("1450.00"),
        "descricao": (
            "Categoria oficial para famílias "
            "e pequenos grupos de até cinco hóspedes."
        ),
        "unidades": gerar_codigos(
            "CHALE",
            2,
        ),
    },
]


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_postgresql() -> None:
    """
    Garante que o seed oficial seja aplicado
    ao PostgreSQL da Central de Reservas.
    """

    if motor_banco.dialect.name != "postgresql":
        raise RuntimeError(
            "Seed cancelado. "
            "A Central de Reservas exige PostgreSQL."
        )


# ============================================================
# CATEGORIAS
# ============================================================

def obter_ou_criar_categoria(
    sessao,
    dados: dict,
) -> CategoriaAcomodacao:
    """
    Localiza a categoria pelo nome oficial ou
    por um nome utilizado anteriormente.

    Dessa forma, o seed consegue atualizar
    o banco existente sem duplicar categorias.
    """

    nomes_busca = [
        dados["nome"],
        *dados.get(
            "aliases",
            (),
        ),
    ]

    encontradas = list(
        sessao.scalars(
            select(
                CategoriaAcomodacao
            ).where(
                CategoriaAcomodacao.nome.in_(
                    nomes_busca
                )
            )
        ).all()
    )

    if len(encontradas) > 1:
        raise RuntimeError(
            "Foram encontradas categorias duplicadas "
            f"para {dados['nome']}: "
            f"{[c.nome for c in encontradas]}"
        )

    categoria = (
        encontradas[0]
        if encontradas
        else None
    )

    if categoria is None:

        categoria = CategoriaAcomodacao(
            nome=dados["nome"],
            capacidade=dados["capacidade"],
            tarifa_referencia=dados[
                "tarifa_referencia"
            ],
            descricao=dados["descricao"],
            ativa=True,
        )

        sessao.add(
            categoria
        )

        sessao.flush()

        print(
            f"[CRIADA] {categoria.nome}"
        )

    else:

        nome_anterior = categoria.nome

        categoria.nome = dados["nome"]
        categoria.capacidade = dados[
            "capacidade"
        ]
        categoria.tarifa_referencia = dados[
            "tarifa_referencia"
        ]
        categoria.descricao = dados[
            "descricao"
        ]
        categoria.ativa = True

        if nome_anterior != categoria.nome:
            print(
                f"[ATUALIZADA] "
                f"{nome_anterior} -> {categoria.nome}"
            )
        else:
            print(
                f"[OK] {categoria.nome}"
            )

    return categoria


# ============================================================
# UNIDADES
# ============================================================

def sincronizar_unidades(
    sessao,
    categoria: CategoriaAcomodacao,
    codigos_esperados: list[str],
) -> None:
    """
    Sincroniza as unidades físicas da categoria.

    Unidades esperadas são criadas ou ativadas.
    Unidades extras são apenas desativadas,
    nunca excluídas, preservando histórico.
    """

    unidades_existentes = list(
        sessao.scalars(
            select(
                UnidadeAcomodacao
            ).where(
                UnidadeAcomodacao.categoria_id
                == categoria.id
            )
        ).all()
    )

    por_codigo = {
        unidade.codigo: unidade
        for unidade in unidades_existentes
    }

    codigos_esperados_set = set(
        codigos_esperados
    )

    for codigo in codigos_esperados:

        unidade = por_codigo.get(
            codigo
        )

        if unidade is None:

            unidade = UnidadeAcomodacao(
                categoria_id=categoria.id,
                codigo=codigo,
                ativa=True,
            )

            sessao.add(
                unidade
            )

            print(
                f"    [CRIADA] {codigo}"
            )

        else:

            unidade.categoria_id = categoria.id
            unidade.ativa = True

            print(
                f"    [OK] {codigo}"
            )

    for unidade in unidades_existentes:

        if (
            unidade.codigo
            not in codigos_esperados_set
        ):
            unidade.ativa = False

            print(
                f"    [INATIVADA] "
                f"{unidade.codigo}"
            )


# ============================================================
# SEED
# ============================================================

def executar_seed() -> None:
    """
    Sincroniza o catálogo relacional da Central
    com as acomodações da Base Oficial.
    """

    validar_postgresql()

    print(
        "Sincronizando catálogo oficial..."
    )

    print()

    with abrir_sessao() as sessao:

        for dados in CATEGORIAS:

            categoria = (
                obter_ou_criar_categoria(
                    sessao,
                    dados,
                )
            )

            sincronizar_unidades(
                sessao,
                categoria,
                dados["unidades"],
            )

        sessao.commit()

    print()
    print(
        "Catálogo sincronizado com sucesso."
    )


if __name__ == "__main__":
    executar_seed()