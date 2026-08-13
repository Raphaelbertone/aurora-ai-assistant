from datetime import date, timedelta
from decimal import Decimal

from src.reservas.database import abrir_sessao
from src.reservas.schemas import (
    SolicitacaoDisponibilidade,
    SolicitacaoReserva,
)
from src.reservas.service import (
    consultar_disponibilidade_detalhada,
)


# ============================================================
# PERÍODO DE TESTE
# ============================================================

CHECKIN = date.today() + timedelta(days=60)
CHECKOUT = CHECKIN + timedelta(days=3)


# ============================================================
# TESTE DE DISPONIBILIDADE
# ============================================================

solicitacao = SolicitacaoDisponibilidade(
    checkin=CHECKIN,
    checkout=CHECKOUT,
    quantidade_hospedes=2,
)


with abrir_sessao() as sessao:

    resultado = (
        consultar_disponibilidade_detalhada(
            sessao,
            solicitacao,
        )
    )

    print(
        f"Diárias: "
        f"{resultado.quantidade_diarias}"
    )

    print(
        f"Unidades disponíveis: "
        f"{resultado.total_unidades}"
    )

    assert (
        resultado.quantidade_diarias
        == 3
    )

    assert (
        resultado.total_unidades
        == 30
    )

    primeira = resultado.unidades[0]

    print(
        f"Primeira categoria: "
        f"{primeira.categoria_nome}"
    )

    print(
        f"Tarifa: "
        f"R$ {primeira.tarifa_referencia}"
    )

    print(
        f"Total estimado: "
        f"R$ {primeira.valor_total_estimado}"
    )

    assert (
        primeira.categoria_nome
        == "Quarto Standard Casal"
    )

    assert (
        primeira.tarifa_referencia
        == Decimal("420.00")
    )

    assert (
        primeira.valor_total_estimado
        == Decimal("1260.00")
    )


# ============================================================
# TESTE DO SCHEMA DE RESERVA
# ============================================================

solicitacao_reserva = SolicitacaoReserva(
    nome_hospede="Hóspede Demonstração",
    email="demo@aurora.local",
    checkin=CHECKIN,
    checkout=CHECKOUT,
    quantidade_hospedes=2,
)

assert (
    solicitacao_reserva.nome_hospede
    == "Hóspede Demonstração"
)

assert (
    solicitacao_reserva.quantidade_hospedes
    == 2
)


print()
print(
    "Todos os testes dos schemas passaram."
)