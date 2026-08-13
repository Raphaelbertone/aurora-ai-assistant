from datetime import date, timedelta
from uuid import uuid4

from src.reservas.database import abrir_sessao
from src.reservas.repository import (
    obter_categoria_por_nome,
)
from src.reservas.schemas import (
    SolicitacaoRecuperacaoReserva,
)
from src.reservas.service import (
    DadosReservaInvalidos,
    cancelar_reserva,
    criar_reserva,
    recuperar_reservas_detalhadas,
)


identificador = (
    uuid4().hex[:8].upper()
)

nome = (
    f"Hóspede Flexível {identificador}"
)

email = (
    f"flexivel-{identificador.lower()}"
    "@aurora.local"
)

checkin = (
    date.today()
    + timedelta(days=150)
)

checkout = (
    checkin
    + timedelta(days=2)
)


print()
print(
    "Criando reserva de teste..."
)


with abrir_sessao() as sessao:

    categoria = (
        obter_categoria_por_nome(
            sessao,
            "Quarto Standard Casal",
        )
    )

    assert categoria is not None

    reserva = criar_reserva(
        sessao=sessao,
        nome_hospede=nome,
        email=email,
        checkin=checkin,
        checkout=checkout,
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    codigo = (
        reserva.codigo_reserva
    )


print(
    f"Reserva criada: {codigo}"
)


# ============================================================
# TESTE 1
# SOMENTE NOME
# ============================================================

print()
print(
    "TESTE 1 — Somente nome"
)

with abrir_sessao() as sessao:

    resultados = (
        recuperar_reservas_detalhadas(
            sessao,
            SolicitacaoRecuperacaoReserva(
                nome_hospede=nome,
            ),
        )
    )

    assert any(
        item.codigo_reserva == codigo
        for item in resultados
    )

print(
    "Somente nome: OK"
)


# ============================================================
# TESTE 2
# SOMENTE E-MAIL
# ============================================================

print()
print(
    "TESTE 2 — Somente e-mail"
)

with abrir_sessao() as sessao:

    resultados = (
        recuperar_reservas_detalhadas(
            sessao,
            SolicitacaoRecuperacaoReserva(
                email=email,
            ),
        )
    )

    assert any(
        item.codigo_reserva == codigo
        for item in resultados
    )

print(
    "Somente e-mail: OK"
)


# ============================================================
# TESTE 3
# SOMENTE CHECK-IN
# ============================================================

print()
print(
    "TESTE 3 — Somente check-in"
)

with abrir_sessao() as sessao:

    resultados = (
        recuperar_reservas_detalhadas(
            sessao,
            SolicitacaoRecuperacaoReserva(
                checkin=checkin,
            ),
        )
    )

    assert any(
        item.codigo_reserva == codigo
        for item in resultados
    )

print(
    "Somente check-in: OK"
)


# ============================================================
# TESTE 4
# NOME + E-MAIL
# ============================================================

print()
print(
    "TESTE 4 — Nome + e-mail"
)

with abrir_sessao() as sessao:

    resultados = (
        recuperar_reservas_detalhadas(
            sessao,
            SolicitacaoRecuperacaoReserva(
                nome_hospede=nome,
                email=email,
            ),
        )
    )

    assert any(
        item.codigo_reserva == codigo
        for item in resultados
    )

print(
    "Nome + e-mail: OK"
)


# ============================================================
# TESTE 5
# TODOS OS CAMPOS
# ============================================================

print()
print(
    "TESTE 5 — Todos os campos"
)

with abrir_sessao() as sessao:

    resultados = (
        recuperar_reservas_detalhadas(
            sessao,
            SolicitacaoRecuperacaoReserva(
                nome_hospede=nome,
                email=email,
                checkin=checkin,
            ),
        )
    )

    assert any(
        item.codigo_reserva == codigo
        for item in resultados
    )

print(
    "Todos os campos: OK"
)


# ============================================================
# TESTE 6
# NENHUM CAMPO
# ============================================================

print()
print(
    "TESTE 6 — Nenhum campo"
)

with abrir_sessao() as sessao:

    try:

        recuperar_reservas_detalhadas(
            sessao,
            SolicitacaoRecuperacaoReserva(),
        )

        raise AssertionError(
            "A consulta sem critérios "
            "deveria ter sido rejeitada."
        )

    except DadosReservaInvalidos:

        pass

print(
    "Consulta vazia rejeitada: OK"
)


# ============================================================
# LIMPEZA
# ============================================================

print()
print(
    "Cancelando reserva de teste..."
)

with abrir_sessao() as sessao:

    cancelar_reserva(
        sessao,
        codigo,
    )


print()
print(
    "=" * 60
)

print(
    "Todos os testes de recuperação "
    "flexível passaram."
)

print(
    "=" * 60
)