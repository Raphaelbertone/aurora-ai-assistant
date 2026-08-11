import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()


RAIZ_PROJETO = Path(
    __file__
).resolve().parents[2]


DIRETORIO_DADOS = (
    RAIZ_PROJETO
    / "data"
)


DIRETORIO_DADOS.mkdir(
    parents=True,
    exist_ok=True,
)


CAMINHO_SQLITE_PADRAO = (
    DIRETORIO_DADOS
    / "aurora.db"
)


URL_SQLITE_PADRAO = (
    f"sqlite:///"
    f"{CAMINHO_SQLITE_PADRAO.as_posix()}"
)


URL_BANCO = (
    os.getenv(
        "DATABASE_URL",
        "",
    ).strip()
    or URL_SQLITE_PADRAO
)


# ============================================================
# BASE DOS MODELOS
# ============================================================

class Base(DeclarativeBase):
    """
    Classe base utilizada pelos modelos
    SQLAlchemy da Central de Reservas.
    """

    pass


# ============================================================
# ENGINE
# ============================================================

def criar_motor_banco() -> Engine:
    """
    Cria o engine SQLAlchemy.

    SQLite recebe uma configuração específica para permitir
    seu uso pelo Streamlit, que pode executar código em
    diferentes threads.

    Outros bancos, como PostgreSQL, podem ser utilizados
    através da variável DATABASE_URL.
    """

    argumentos_conexao = {}

    if URL_BANCO.startswith(
        "sqlite"
    ):
        argumentos_conexao = {
            "check_same_thread": False,
            "timeout": 30,
        }

    return create_engine(
        URL_BANCO,
        connect_args=argumentos_conexao,
        pool_pre_ping=True,
    )


motor_banco = criar_motor_banco()


# ============================================================
# FÁBRICA DE SESSÕES
# ============================================================

SessaoLocal = sessionmaker(
    bind=motor_banco,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


# ============================================================
# CONTEXTO DE SESSÃO
# ============================================================

@contextmanager
def abrir_sessao() -> Generator[
    Session,
    None,
    None,
]:
    """
    Abre uma sessão de banco e garante
    seu fechamento ao final da operação.

    O commit permanece responsabilidade da camada
    de serviço, evitando gravações implícitas.
    """

    sessao = SessaoLocal()

    try:
        yield sessao

    except Exception:
        sessao.rollback()
        raise

    finally:
        sessao.close()


# ============================================================
# TESTE DE CONECTIVIDADE
# ============================================================

def testar_conexao() -> bool:
    """
    Executa uma consulta mínima para verificar
    se o banco está acessível.
    """

    with motor_banco.connect() as conexao:
        resultado = conexao.execute(
            text(
                "SELECT 1"
            )
        )

        valor = resultado.scalar_one()

    return valor == 1