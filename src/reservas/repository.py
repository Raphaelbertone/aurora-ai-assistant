from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from src.reservas.models import (
    CategoriaAcomodacao,
    Reserva,
    UnidadeAcomodacao,
)


# ============================================================
# CATEGORIAS
# ============================================================

def listar_categorias_ativas(
    sessao: Session,
) -> list[CategoriaAcomodacao]:
    """
    Retorna todas as categorias ativas,
    ordenadas por tarifa de referência.
    """

    consulta = (
        select(
            CategoriaAcomodacao
        )
        .where(
            CategoriaAcomodacao.ativa.is_(True)
        )
        .order_by(
            CategoriaAcomodacao.tarifa_referencia,
            CategoriaAcomodacao.nome,
        )
    )

    return list(
        sessao.scalars(
            consulta
        ).all()
    )


def obter_categoria_por_id(
    sessao: Session,
    categoria_id: int,
) -> CategoriaAcomodacao | None:
    """
    Obtém uma categoria pelo identificador.
    """

    return sessao.scalar(
        select(
            CategoriaAcomodacao
        ).where(
            CategoriaAcomodacao.id
            == categoria_id
        )
    )


def obter_categoria_por_nome(
    sessao: Session,
    nome: str,
) -> CategoriaAcomodacao | None:
    """
    Obtém uma categoria pelo nome exato.
    """

    return sessao.scalar(
        select(
            CategoriaAcomodacao
        ).where(
            CategoriaAcomodacao.nome
            == nome
        )
    )


# ============================================================
# UNIDADES
# ============================================================

def obter_unidade_por_id(
    sessao: Session,
    unidade_id: int,
) -> UnidadeAcomodacao | None:
    """
    Obtém uma unidade pelo ID,
    carregando também sua categoria.
    """

    consulta = (
        select(
            UnidadeAcomodacao
        )
        .options(
            selectinload(
                UnidadeAcomodacao.categoria
            )
        )
        .where(
            UnidadeAcomodacao.id
            == unidade_id
        )
    )

    return sessao.scalar(
        consulta
    )


def obter_unidade_por_codigo(
    sessao: Session,
    codigo: str,
) -> UnidadeAcomodacao | None:
    """
    Obtém uma unidade pelo código único.
    """

    consulta = (
        select(
            UnidadeAcomodacao
        )
        .options(
            selectinload(
                UnidadeAcomodacao.categoria
            )
        )
        .where(
            UnidadeAcomodacao.codigo
            == codigo
        )
    )

    return sessao.scalar(
        consulta
    )


# ============================================================
# DISPONIBILIDADE
# ============================================================

def listar_unidades_disponiveis(
    sessao: Session,
    checkin: date,
    checkout: date,
    quantidade_hospedes: int,
    categoria_id: int | None = None,
) -> list[UnidadeAcomodacao]:
    """
    Retorna as unidades disponíveis para determinado
    intervalo e número de hóspedes.

    Há conflito quando uma reserva CONFIRMADA satisfaz:

        reserva.checkin < novo_checkout

    e:

        reserva.checkout > novo_checkin

    Reservas canceladas não bloqueiam disponibilidade.
    """

    reserva_conflitante = (
        select(
            Reserva.id
        )
        .where(
            Reserva.unidade_id
            == UnidadeAcomodacao.id,
            Reserva.status
            == "CONFIRMADA",
            Reserva.checkin
            < checkout,
            Reserva.checkout
            > checkin,
        )
        .exists()
    )

    consulta = (
        select(
            UnidadeAcomodacao
        )
        .join(
            UnidadeAcomodacao.categoria
        )
        .options(
            selectinload(
                UnidadeAcomodacao.categoria
            )
        )
        .where(
            UnidadeAcomodacao.ativa.is_(True),
            CategoriaAcomodacao.ativa.is_(True),
            CategoriaAcomodacao.capacidade
            >= quantidade_hospedes,
            ~reserva_conflitante,
        )
    )

    if categoria_id is not None:
        consulta = consulta.where(
            UnidadeAcomodacao.categoria_id
            == categoria_id
        )

    consulta = consulta.order_by(
        CategoriaAcomodacao.tarifa_referencia,
        CategoriaAcomodacao.nome,
        UnidadeAcomodacao.codigo,
    )

    return list(
        sessao.scalars(
            consulta
        ).all()
    )


# ============================================================
# RESERVAS
# ============================================================

def obter_reserva_por_codigo(
    sessao: Session,
    codigo_reserva: str,
) -> Reserva | None:
    """
    Localiza uma reserva pelo código.
    """

    consulta = (
        select(
            Reserva
        )
        .options(
            selectinload(
                Reserva.unidade
            ).selectinload(
                UnidadeAcomodacao.categoria
            )
        )
        .where(
            Reserva.codigo_reserva
            == codigo_reserva
        )
    )

    return sessao.scalar(
        consulta
    )


def adicionar_reserva(
    sessao: Session,
    reserva: Reserva,
) -> Reserva:
    """
    Adiciona uma reserva à sessão.

    O commit continua sob responsabilidade
    da camada de serviço.
    """

    sessao.add(
        reserva
    )

    sessao.flush()

    return reserva