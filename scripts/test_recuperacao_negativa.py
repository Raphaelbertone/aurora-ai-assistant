from datetime import date

from src.reservas.database import abrir_sessao
from src.reservas.schemas import (
    SolicitacaoRecuperacaoReserva,
)
from src.reservas.service import (
    ReservaNaoEncontrada,
    recuperar_reservas_detalhadas,
)


solicitacao = SolicitacaoRecuperacaoReserva(
    nome_hospede="Pessoa Inexistente",
    email="naoexiste@aurora.local",
    checkin=date(2026, 12, 10),
)


with abrir_sessao() as sessao:

    try:

        recuperar_reservas_detalhadas(
            sessao,
            solicitacao,
        )

        raise AssertionError(
            "A busca deveria ter retornado "
            "ReservaNaoEncontrada."
        )

    except ReservaNaoEncontrada:

        print(
            "Teste negativo passou: "
            "reserva não encontrada."
        )