from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


# ============================================================
# ENTRADAS
# ============================================================

@dataclass(frozen=True, slots=True)
class SolicitacaoDisponibilidade:
    """
    Dados necessários para consultar
    disponibilidade de acomodações.
    """

    checkin: date
    checkout: date
    quantidade_hospedes: int
    categoria_id: int | None = None


@dataclass(frozen=True, slots=True)
class SolicitacaoReserva:
    """
    Dados necessários para criar
    uma reserva fictícia.
    """

    nome_hospede: str
    email: str
    checkin: date
    checkout: date
    quantidade_hospedes: int

    categoria_id: int | None = None
    telefone: str | None = None
    observacoes: str | None = None

@dataclass(
    frozen=True,
    slots=True,
)
class SolicitacaoRecuperacaoReserva:
    """
    Critérios opcionais utilizados para
    localizar uma reserva sem o código.

    Pelo menos um critério deve ser informado.
    """

    nome_hospede: str | None = None
    email: str | None = None
    checkin: date | None = None


# ============================================================
# DISPONIBILIDADE
# ============================================================

@dataclass(frozen=True, slots=True)
class UnidadeDisponivel:
    """
    Representação segura de uma unidade
    disponível para apresentação na interface.
    """

    unidade_id: int
    codigo: str

    categoria_id: int
    categoria_nome: str
    capacidade: int

    tarifa_referencia: Decimal

    quantidade_diarias: int
    valor_total_estimado: Decimal


@dataclass(frozen=True, slots=True)
class ResultadoDisponibilidade:
    """
    Resultado completo de uma consulta
    de disponibilidade.
    """

    checkin: date
    checkout: date
    quantidade_hospedes: int
    quantidade_diarias: int

    unidades: tuple[UnidadeDisponivel, ...]

    @property
    def total_unidades(self) -> int:
        """
        Quantidade de unidades encontradas.
        """

        return len(
            self.unidades
        )


# ============================================================
# RESERVA
# ============================================================

@dataclass(frozen=True, slots=True)
class DetalheReserva:
    """
    Representação da reserva usada pelas
    camadas externas da aplicação.
    """

    codigo_reserva: str
    status: str

    unidade_id: int
    unidade_codigo: str

    categoria_id: int
    categoria_nome: str

    nome_hospede: str
    email: str
    telefone: str | None

    checkin: date
    checkout: date
    quantidade_hospedes: int
    quantidade_diarias: int

    tarifa_diaria_aplicada: Decimal
    valor_total_estimado: Decimal

    observacoes: str | None

    criada_em: datetime
    cancelada_em: datetime | None