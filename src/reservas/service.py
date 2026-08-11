from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from src.reservas.models import Reserva, UnidadeAcomodacao
from src.reservas.repository import (
    adicionar_reserva,
    listar_unidades_disponiveis,
    obter_categoria_por_id,
    obter_reserva_por_codigo,
)


# ============================================================
# EXCEÇÕES
# ============================================================

class ErroReserva(Exception):
    """Erro base da Central de Reservas."""


class DadosReservaInvalidos(ErroReserva):
    """Dados fornecidos para a reserva são inválidos."""


class SemDisponibilidade(ErroReserva):
    """Não existem unidades disponíveis para a solicitação."""


class ReservaNaoEncontrada(ErroReserva):
    """Reserva não encontrada pelo código informado."""


# ============================================================
# VALIDAÇÕES
# ============================================================

def validar_periodo(
    checkin: date,
    checkout: date,
) -> None:
    """
    Valida o intervalo solicitado para hospedagem.
    """

    if checkin < date.today():
        raise DadosReservaInvalidos(
            "A data de check-in não pode estar no passado."
        )

    if checkout <= checkin:
        raise DadosReservaInvalidos(
            "A data de check-out deve ser posterior ao check-in."
        )


def validar_quantidade_hospedes(
    quantidade_hospedes: int,
) -> None:
    """
    Valida a quantidade informada de hóspedes.
    """

    if quantidade_hospedes <= 0:
        raise DadosReservaInvalidos(
            "A quantidade de hóspedes deve ser maior que zero."
        )


def validar_dados_hospede(
    nome_hospede: str,
    email: str,
) -> None:
    """
    Realiza validações básicas dos dados do hóspede.
    """

    if not nome_hospede.strip():
        raise DadosReservaInvalidos(
            "O nome do hóspede é obrigatório."
        )

    email_normalizado = email.strip()

    if (
        not email_normalizado
        or "@" not in email_normalizado
    ):
        raise DadosReservaInvalidos(
            "Informe um endereço de e-mail válido."
        )


# ============================================================
# CÁLCULOS
# ============================================================

def calcular_quantidade_diarias(
    checkin: date,
    checkout: date,
) -> int:
    """
    Calcula a quantidade de diárias da hospedagem.
    """

    validar_periodo(
        checkin,
        checkout,
    )

    return (
        checkout - checkin
    ).days


def calcular_valor_total(
    tarifa_diaria: Decimal,
    quantidade_diarias: int,
) -> Decimal:
    """
    Calcula o valor estimado da hospedagem.
    """

    return (
        tarifa_diaria
        * Decimal(quantidade_diarias)
    ).quantize(
        Decimal("0.01")
    )


# ============================================================
# CÓDIGO DA RESERVA
# ============================================================

def gerar_codigo_reserva() -> str:
    """
    Gera um identificador público curto
    para a reserva.
    """

    data_atual = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d"
    )

    identificador = (
        uuid4()
        .hex[:8]
        .upper()
    )

    return (
        f"AUR-{data_atual}-{identificador}"
    )


# ============================================================
# DISPONIBILIDADE
# ============================================================

def consultar_disponibilidade(
    sessao: Session,
    checkin: date,
    checkout: date,
    quantidade_hospedes: int,
    categoria_id: int | None = None,
) -> list[UnidadeAcomodacao]:
    """
    Consulta unidades disponíveis após validar
    as regras básicas da solicitação.
    """

    validar_periodo(
        checkin,
        checkout,
    )

    validar_quantidade_hospedes(
        quantidade_hospedes
    )

    if categoria_id is not None:

        categoria = obter_categoria_por_id(
            sessao,
            categoria_id,
        )

        if (
            categoria is None
            or not categoria.ativa
        ):
            raise DadosReservaInvalidos(
                "A categoria informada não existe "
                "ou está inativa."
            )

        if (
            quantidade_hospedes
            > categoria.capacidade
        ):
            return []

    return listar_unidades_disponiveis(
        sessao=sessao,
        checkin=checkin,
        checkout=checkout,
        quantidade_hospedes=quantidade_hospedes,
        categoria_id=categoria_id,
    )


# ============================================================
# CRIAÇÃO DE RESERVA
# ============================================================

def criar_reserva(
    sessao: Session,
    nome_hospede: str,
    email: str,
    checkin: date,
    checkout: date,
    quantidade_hospedes: int,
    categoria_id: int | None = None,
    telefone: str | None = None,
    observacoes: str | None = None,
) -> Reserva:
    """
    Cria uma reserva fictícia confirmada.

    A tarifa aplicada é armazenada na própria reserva
    para preservar o valor utilizado naquele momento.
    """

    validar_dados_hospede(
        nome_hospede,
        email,
    )

    unidades = consultar_disponibilidade(
        sessao=sessao,
        checkin=checkin,
        checkout=checkout,
        quantidade_hospedes=quantidade_hospedes,
        categoria_id=categoria_id,
    )

    if not unidades:
        raise SemDisponibilidade(
            "Não existem unidades disponíveis "
            "para o período e critérios informados."
        )

    # O repository já ordena pela menor tarifa
    # quando nenhuma categoria específica é solicitada.
    unidade = unidades[0]

    tarifa_diaria = Decimal(
        unidade.categoria.tarifa_referencia
    )

    quantidade_diarias = (
        calcular_quantidade_diarias(
            checkin,
            checkout,
        )
    )

    valor_total = calcular_valor_total(
        tarifa_diaria,
        quantidade_diarias,
    )

    reserva = Reserva(
        codigo_reserva=gerar_codigo_reserva(),
        unidade_id=unidade.id,
        nome_hospede=nome_hospede.strip(),
        email=email.strip().lower(),
        telefone=(
            telefone.strip()
            if telefone
            else None
        ),
        checkin=checkin,
        checkout=checkout,
        quantidade_hospedes=quantidade_hospedes,
        tarifa_diaria_aplicada=tarifa_diaria,
        valor_total_estimado=valor_total,
        status="CONFIRMADA",
        observacoes=(
            observacoes.strip()
            if observacoes
            else None
        ),
    )

    adicionar_reserva(
        sessao,
        reserva,
    )

    sessao.commit()

    sessao.refresh(
        reserva
    )

    return reserva


# ============================================================
# CONSULTA DE RESERVA
# ============================================================

def consultar_reserva(
    sessao: Session,
    codigo_reserva: str,
) -> Reserva:
    """
    Consulta uma reserva pelo código público.
    """

    codigo = (
        codigo_reserva
        .strip()
        .upper()
    )

    if not codigo:
        raise DadosReservaInvalidos(
            "Informe o código da reserva."
        )

    reserva = obter_reserva_por_codigo(
        sessao,
        codigo,
    )

    if reserva is None:
        raise ReservaNaoEncontrada(
            "Reserva não encontrada."
        )

    return reserva


# ============================================================
# CANCELAMENTO
# ============================================================

def cancelar_reserva(
    sessao: Session,
    codigo_reserva: str,
) -> Reserva:
    """
    Cancela uma reserva confirmada.

    Uma reserva cancelada deixa automaticamente
    de bloquear a disponibilidade da unidade.
    """

    reserva = consultar_reserva(
        sessao,
        codigo_reserva,
    )

    # Operação idempotente:
    # cancelar novamente não gera inconsistência.
    if reserva.status == "CANCELADA":
        return reserva

    reserva.status = "CANCELADA"

    reserva.cancelada_em = datetime.now(
        timezone.utc
    )

    sessao.commit()

    sessao.refresh(
        reserva
    )

    return reserva