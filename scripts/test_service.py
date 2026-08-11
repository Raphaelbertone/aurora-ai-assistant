from datetime import date

from src.reservas.database import abrir_sessao
from src.reservas.repository import obter_categoria_por_nome
from src.reservas.service import (
    cancelar_reserva,
    consultar_disponibilidade,
    consultar_reserva,
    criar_reserva,
)


CHECKIN = date(2026, 8, 20)
CHECKOUT = date(2026, 8, 23)


with abrir_sessao() as sessao:

    categoria = obter_categoria_por_nome(
        sessao,
        "Standard Casal",
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

    assert len(antes) == 3

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
        f"Tarifa: R$ {reserva.tarifa_diaria_aplicada}"
    )

    print(
        f"Total: R$ {reserva.valor_total_estimado}"
    )

    assert (
        reserva.valor_total_estimado
        == 1260
    )

    # --------------------------------------------------------
    # Durante o mesmo período
    # --------------------------------------------------------

    durante = consultar_disponibilidade(
        sessao=sessao,
        checkin=CHECKIN,
        checkout=CHECKOUT,
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    print(
        f"Disponíveis após reserva: {len(durante)}"
    )

    assert len(durante) == 2

    # --------------------------------------------------------
    # Checkout = próximo check-in
    # Deve continuar permitido.
    # --------------------------------------------------------

    adjacente = consultar_disponibilidade(
        sessao=sessao,
        checkin=CHECKOUT,
        checkout=date(2026, 8, 25),
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    print(
        f"Disponíveis em período adjacente: "
        f"{len(adjacente)}"
    )

    assert len(adjacente) == 3

    # --------------------------------------------------------
    # Consulta
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
        f"Status antes do cancelamento: "
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
        f"Status após cancelamento: "
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
        f"Disponíveis após cancelamento: "
        f"{len(depois)}"
    )

    assert len(depois) == 3


print()
print(
    "Todos os testes da camada de serviço passaram."
)