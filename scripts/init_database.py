from sqlalchemy import inspect

from src.reservas.database import (
    Base,
    motor_banco,
)

# Necessário para registrar os modelos
# no metadata do SQLAlchemy.
import src.reservas.models  # noqa: F401


# ============================================================
# CONFIGURAÇÃO
# ============================================================

TABELAS_ESPERADAS = {
    "categorias_acomodacao",
    "unidades_acomodacao",
    "reservas",
}


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_postgresql() -> None:
    """
    Impede que o inicializador seja executado
    acidentalmente utilizando o fallback SQLite.
    """

    dialeto = motor_banco.dialect.name

    if dialeto != "postgresql":
        raise RuntimeError(
            "Inicialização cancelada. "
            f"O banco configurado utiliza '{dialeto}', "
            "mas a Central de Reservas exige PostgreSQL."
        )


# ============================================================
# CRIAÇÃO DAS TABELAS
# ============================================================

def criar_tabelas() -> None:
    """
    Cria todas as tabelas registradas
    no metadata do SQLAlchemy.
    """

    Base.metadata.create_all(
        bind=motor_banco
    )


# ============================================================
# VERIFICAÇÃO
# ============================================================

def obter_tabelas_existentes() -> set[str]:
    """
    Consulta o PostgreSQL e retorna os nomes
    das tabelas existentes.
    """

    inspetor = inspect(
        motor_banco
    )

    return set(
        inspetor.get_table_names()
    )


# ============================================================
# EXECUÇÃO
# ============================================================

def main() -> None:
    """
    Inicializa o banco de dados da
    Central de Reservas.
    """

    validar_postgresql()

    print(
        "Inicializando banco da Central de Reservas..."
    )

    print(
        f"Dialeto: {motor_banco.dialect.name}"
    )

    criar_tabelas()

    tabelas_existentes = (
        obter_tabelas_existentes()
    )

    tabelas_faltantes = (
        TABELAS_ESPERADAS
        - tabelas_existentes
    )

    if tabelas_faltantes:
        raise RuntimeError(
            "Falha na inicialização. "
            "As seguintes tabelas não foram encontradas: "
            f"{sorted(tabelas_faltantes)}"
        )

    print()
    print(
        "Banco inicializado com sucesso."
    )

    print(
        "Tabelas:"
    )

    for tabela in sorted(
        TABELAS_ESPERADAS
    ):
        print(
            f"  - {tabela}"
        )


if __name__ == "__main__":
    main()