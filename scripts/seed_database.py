from decimal import Decimal

from sqlalchemy import select

from src.reservas.database import abrir_sessao
from src.reservas.models import (
    CategoriaAcomodacao,
    UnidadeAcomodacao,
)


# ============================================================
# DADOS INICIAIS
# ============================================================

CATEGORIAS = [
    {
        "nome": "Standard Casal",
        "capacidade": 2,
        "tarifa_referencia": Decimal("420.00"),
        "descricao": (
            "Categoria Standard Casal. "
            "Capacidade utilizada exclusivamente para "
            "demonstração da Central de Reservas."
        ),
        "unidades": [
            "STD-CASAL-01",
            "STD-CASAL-02",
            "STD-CASAL-03",
        ],
    },
    {
        "nome": "Standard Família",
        "capacidade": 4,
        "tarifa_referencia": Decimal("560.00"),
        "descricao": (
            "Categoria Standard Família. "
            "Capacidade utilizada exclusivamente para "
            "demonstração da Central de Reservas."
        ),
        "unidades": [
            "STD-FAM-01",
            "STD-FAM-02",
            "STD-FAM-03",
        ],
    },
    {
        "nome": "Superior",
        "capacidade": 3,
        "tarifa_referencia": Decimal("690.00"),
        "descricao": (
            "Categoria Superior. "
            "Capacidade utilizada exclusivamente para "
            "demonstração da Central de Reservas."
        ),
        "unidades": [
            "SUP-01",
            "SUP-02",
        ],
    },
    {
        "nome": "Premium",
        "capacidade": 2,
        "tarifa_referencia": Decimal("890.00"),
        "descricao": (
            "Categoria Premium. "
            "Capacidade utilizada exclusivamente para "
            "demonstração da Central de Reservas."
        ),
        "unidades": [
            "PREM-01",
            "PREM-02",
        ],
    },
    {
        "nome": "Master",
        "capacidade": 2,
        "tarifa_referencia": Decimal("1250.00"),
        "descricao": (
            "Categoria Master. "
            "Capacidade utilizada exclusivamente para "
            "demonstração da Central de Reservas."
        ),
        "unidades": [
            "MASTER-01",
        ],
    },
    {
        "nome": "Chalé",
        "capacidade": 4,
        "tarifa_referencia": Decimal("1450.00"),
        "descricao": (
            "Categoria Chalé. "
            "Capacidade utilizada exclusivamente para "
            "demonstração da Central de Reservas."
        ),
        "unidades": [
            "CHALE-01",
            "CHALE-02",
        ],
    },
]


# ============================================================
# CATEGORIAS
# ============================================================

def obter_ou_criar_categoria(
    sessao,
    dados: dict,
) -> CategoriaAcomodacao:
    """
    Obtém uma categoria existente pelo nome.

    Caso não exista, cria uma nova.

    Caso exista, sincroniza os dados principais
    definidos pelo seed.
    """

    categoria = sessao.scalar(
        select(
            CategoriaAcomodacao
        ).where(
            CategoriaAcomodacao.nome
            == dados["nome"]
        )
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

        # Garante que categoria.id esteja
        # disponível antes da criação das unidades.
        sessao.flush()

        print(
            f"[CRIADA] Categoria: "
            f"{categoria.nome}"
        )

    else:
        categoria.capacidade = (
            dados["capacidade"]
        )

        categoria.tarifa_referencia = (
            dados["tarifa_referencia"]
        )

        categoria.descricao = (
            dados["descricao"]
        )

        categoria.ativa = True

        print(
            f"[OK] Categoria existente: "
            f"{categoria.nome}"
        )

    return categoria


# ============================================================
# UNIDADES
# ============================================================

def obter_ou_criar_unidade(
    sessao,
    categoria: CategoriaAcomodacao,
    codigo: str,
) -> UnidadeAcomodacao:
    """
    Obtém uma unidade existente pelo código
    ou cria uma nova.

    O código único torna a operação idempotente.
    """

    unidade = sessao.scalar(
        select(
            UnidadeAcomodacao
        ).where(
            UnidadeAcomodacao.codigo
            == codigo
        )
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
            f"    [CRIADA] Unidade: "
            f"{codigo}"
        )

    else:
        unidade.categoria_id = (
            categoria.id
        )

        unidade.ativa = True

        print(
            f"    [OK] Unidade existente: "
            f"{codigo}"
        )

    return unidade


# ============================================================
# SEED
# ============================================================

def executar_seed() -> None:
    """
    Popula o banco com categorias e unidades
    demonstrativas da Central de Reservas.

    A operação pode ser executada repetidamente
    sem duplicar registros.
    """

    print(
        "Iniciando seed da Central de Reservas..."
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

            for codigo in dados[
                "unidades"
            ]:

                obter_ou_criar_unidade(
                    sessao,
                    categoria,
                    codigo,
                )

        sessao.commit()

    print()
    print(
        "Seed concluído com sucesso."
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    executar_seed()