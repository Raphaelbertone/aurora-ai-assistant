from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.reservas.database import Base


# ============================================================
# CATEGORIA DE ACOMODAÇÃO
# ============================================================

class CategoriaAcomodacao(Base):
    """
    Representa um tipo comercial de acomodação.

    Exemplos:
    - Standard Casal
    - Standard Família
    - Suíte Superior
    - Suíte Premium
    - Suíte Master
    - Chalé Família Luxo

    A categoria define características compartilhadas,
    como capacidade e tarifa de referência.

    As unidades físicas ficam separadas em
    UnidadeAcomodacao.
    """

    __tablename__ = "categorias_acomodacao"

    __table_args__ = (
        CheckConstraint(
            "capacidade > 0",
            name="ck_categoria_capacidade_positiva",
        ),
        CheckConstraint(
            "tarifa_referencia >= 0",
            name="ck_categoria_tarifa_nao_negativa",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    capacidade: Mapped[int] = mapped_column(
        nullable=False,
    )

    tarifa_referencia: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=10,
            scale=2,
        ),
        nullable=False,
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ativa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    criada_em: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=False,
        server_default=func.now(),
    )

    atualizada_em: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    unidades: Mapped[list["UnidadeAcomodacao"]] = relationship(
        back_populates="categoria",
    )

    def __repr__(self) -> str:
        return (
            f"<CategoriaAcomodacao("
            f"id={self.id}, "
            f"nome='{self.nome}'"
            f")>"
        )


# ============================================================
# UNIDADE FÍSICA
# ============================================================

class UnidadeAcomodacao(Base):
    """
    Representa uma unidade física individual
    disponível para reserva.

    Exemplo:

    Categoria:
        Suíte Premium

    Unidades:
        PREMIUM-01
        PREMIUM-02
        PREMIUM-03

    A disponibilidade é calculada por unidade
    e por intervalo de datas.
    """

    __tablename__ = "unidades_acomodacao"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categorias_acomodacao.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    codigo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )

    ativa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    criada_em: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=False,
        server_default=func.now(),
    )

    atualizada_em: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    categoria: Mapped["CategoriaAcomodacao"] = relationship(
        back_populates="unidades",
    )

    reservas: Mapped[list["Reserva"]] = relationship(
        back_populates="unidade",
    )

    def __repr__(self) -> str:
        return (
            f"<UnidadeAcomodacao("
            f"id={self.id}, "
            f"codigo='{self.codigo}', "
            f"categoria_id={self.categoria_id}"
            f")>"
        )


# ============================================================
# RESERVA
# ============================================================

class Reserva(Base):
    """
    Representa uma reserva fictícia realizada
    na Central de Reservas do Agente Aurora.

    As reservas são persistidas para demonstrar:
    - banco relacional;
    - CRUD;
    - regras de disponibilidade;
    - histórico;
    - cancelamento;
    - persistência transacional.

    Nenhuma reserva criada pelo projeto corresponde
    a uma hospedagem real.
    """

    __tablename__ = "reservas"

    __table_args__ = (

        # O checkout precisa acontecer
        # depois do check-in.
        CheckConstraint(
            "checkout > checkin",
            name="ck_reserva_periodo_valido",
        ),

        # Não podemos criar reserva
        # sem hóspedes.
        CheckConstraint(
            "quantidade_hospedes > 0",
            name="ck_reserva_hospedes_positivo",
        ),

        # Valores monetários nunca podem
        # ser negativos.
        CheckConstraint(
            "tarifa_diaria_aplicada >= 0",
            name="ck_reserva_tarifa_nao_negativa",
        ),

        CheckConstraint(
            "valor_total_estimado >= 0",
            name="ck_reserva_total_nao_negativo",
        ),

        # Estados permitidos para o MVP.
        CheckConstraint(
            "status IN "
            "('CONFIRMADA', 'CANCELADA')",
            name="ck_reserva_status_valido",
        ),

        # Otimiza justamente a consulta que
        # usaremos para disponibilidade.
        Index(
            "ix_reservas_disponibilidade",
            "unidade_id",
            "status",
            "checkin",
            "checkout",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    codigo_reserva: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
    )

    unidade_id: Mapped[int] = mapped_column(
        ForeignKey(
            "unidades_acomodacao.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # --------------------------------------------------------
    # HÓSPEDE
    # --------------------------------------------------------

    nome_hospede: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    telefone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # --------------------------------------------------------
    # ESTADIA
    # --------------------------------------------------------

    checkin: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    checkout: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    quantidade_hospedes: Mapped[int] = mapped_column(
        nullable=False,
    )

    # --------------------------------------------------------
    # PREÇO
    # --------------------------------------------------------

    tarifa_diaria_aplicada: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=10,
            scale=2,
        ),
        nullable=False,
    )

    valor_total_estimado: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=12,
            scale=2,
        ),
        nullable=False,
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="CONFIRMADA",
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    criada_em: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=False,
        server_default=func.now(),
    )

    atualizada_em: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    cancelada_em: Mapped[datetime | None] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=True,
    )

    unidade: Mapped["UnidadeAcomodacao"] = relationship(
        back_populates="reservas",
    )

    def __repr__(self) -> str:
        return (
            f"<Reserva("
            f"id={self.id}, "
            f"codigo='{self.codigo_reserva}', "
            f"status='{self.status}'"
            f")>"
        )