from datetime import date, timedelta
from decimal import Decimal

from src.reservas.database import abrir_sessao
from src.reservas.repository import obter_categoria_por_nome
from src.reservas.service import (
    cancelar_reserva,
    consultar_disponibilidade,
    consultar_reserva,
    criar_reserva,
)


# ============================================================
# PERÍODO DE TESTE
# ============================================================

CHECKIN = date.today() + timedelta(days=30)
CHECKOUT = CHECKIN + timedelta(days=3)


# ============================================================
# TESTE DA CAMADA DE SERVIÇO
# ============================================================

with abrir_sessao() as sessao:

    categoria = obter_categoria_por_nome(
        sessao,
        "Quarto Standard Casal",
    )

    assert categoria is not None

    print(
        f"Categoria: {categoria.nome}"
    )

    # --------------------------------------------------------
    # Antes da reserva
    # --------------------------------------------------------

    antes = consultar_disponibilidade(
        sessao=sessao,
        checkin=CHECKIN,
        checkout=CHECKOUT,
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    print(
        f"Disponíveis antes: {len(antes)}"
    )

    assert len(antes) == 8

    # --------------------------------------------------------
    # Criar reserva
    # --------------------------------------------------------

    reserva = criar_reserva(
        sessao=sessao,
        nome_hospede="Hóspede de Teste",
        email="teste@aurora.local",
        checkin=CHECKIN,
        checkout=CHECKOUT,
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    print(
        f"Reserva criada: {reserva.codigo_reserva}"
    )

    print(
        f"Unidade: {reserva.unidade_id}"
    )

    print(
        f"Tarifa: R$ "
        f"{reserva.tarifa_diaria_aplicada}"
    )

    print(
        f"Total: R$ "
        f"{reserva.valor_total_estimado}"
    )

    assert (
        reserva.valor_total_estimado
        == Decimal("1260.00")
    )

    # --------------------------------------------------------
    # Mesmo período
    # --------------------------------------------------------

    durante = consultar_disponibilidade(
        sessao=sessao,
        checkin=CHECKIN,
        checkout=CHECKOUT,
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    print(
        f"Disponíveis após reserva: "
        f"{len(durante)}"
    )

    assert len(durante) == 7

    # --------------------------------------------------------
    # Período adjacente
    # Checkout anterior = novo check-in
    # --------------------------------------------------------

    adjacente = consultar_disponibilidade(
        sessao=sessao,
        checkin=CHECKOUT,
        checkout=CHECKOUT + timedelta(days=2),
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    print(
        "Disponíveis em período adjacente: "
        f"{len(adjacente)}"
    )

    assert len(adjacente) == 8

    # --------------------------------------------------------
    # Consulta da reserva
    # --------------------------------------------------------

    encontrada = consultar_reserva(
        sessao,
        reserva.codigo_reserva,
    )

    assert (
        encontrada.codigo_reserva
        == reserva.codigo_reserva
    )

    assert encontrada.status == "CONFIRMADA"

    print(
        "Status antes do cancelamento: "
        f"{encontrada.status}"
    )

    # --------------------------------------------------------
    # Cancelamento
    # --------------------------------------------------------

    cancelar_reserva(
        sessao,
        reserva.codigo_reserva,
    )

    cancelada = consultar_reserva(
        sessao,
        reserva.codigo_reserva,
    )

    assert cancelada.status == "CANCELADA"

    print(
        "Status após cancelamento: "
        f"{cancelada.status}"
    )

    # --------------------------------------------------------
    # Disponibilidade restaurada
    # --------------------------------------------------------

    depois = consultar_disponibilidade(
        sessao=sessao,
        checkin=CHECKIN,
        checkout=CHECKOUT,
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    print(
        "Disponíveis após cancelamento: "
        f"{len(depois)}"
    )

    assert len(depois) == 8


print()
print(
    "Todos os testes da camada de serviço passaram."
)