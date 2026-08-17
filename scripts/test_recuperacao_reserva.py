from datetime import date, timedelta
from uuid import uuid4

from src.reservas.database import abrir_sessao
from src.reservas.repository import obter_categoria_por_nome
from src.reservas.schemas import (
    SolicitacaoRecuperacaoReserva,
)
from src.reservas.service import (
    cancelar_reserva,
    criar_reserva,
    recuperar_reservas_detalhadas,
)


# ============================================================
# DADOS ÚNICOS DO TESTE
# ============================================================

identificador = uuid4().hex[:8].upper()

NOME_HOSPEDE = (
    f"Hóspede Recuperação {identificador}"
)

EMAIL = (
    f"recuperacao-{identificador.lower()}"
    "@aurora.local"
)

CHECKIN = (
    date.today()
    + timedelta(days=120)
)

CHECKOUT = (
    CHECKIN
    + timedelta(days=3)
)


# ============================================================
# ETAPA 1
# CRIAR RESERVA EM UMA SESSÃO
# ============================================================

print()
print(
    "ETAPA 1 — Criando reserva..."
)

with abrir_sessao() as sessao:

    categoria = obter_categoria_por_nome(
        sessao,
        "Quarto Standard Casal",
    )

    assert categoria is not None, (
        "Categoria Quarto Standard Casal "
        "não encontrada."
    )

    reserva = criar_reserva(
        sessao=sessao,
        nome_hospede=NOME_HOSPEDE,
        email=EMAIL,
        checkin=CHECKIN,
        checkout=CHECKOUT,
        quantidade_hospedes=2,
        categoria_id=categoria.id,
    )

    codigo_reserva = (
        reserva.codigo_reserva
    )

    print(
        f"Reserva criada: "
        f"{codigo_reserva}"
    )

    print(
        f"Hóspede: "
        f"{NOME_HOSPEDE}"
    )

    print(
        f"E-mail: "
        f"{EMAIL}"
    )

    print(
        f"Check-in: "
        f"{CHECKIN:%d/%m/%Y}"
    )


# ============================================================
# IMPORTANTE:
#
# A sessão utilizada para criar a reserva terminou acima.
#
# A partir daqui não dependemos mais daquele objeto Reserva
# nem do Session State do Streamlit.
# ============================================================

print()
print(
    "Sessão de criação encerrada."
)


# ============================================================
# ETAPA 2
# RECUPERAR EM UMA NOVA SESSÃO
# ============================================================

print()
print(
    "ETAPA 2 — Recuperando reserva "
    "sem utilizar o código..."
)

solicitacao = (
    SolicitacaoRecuperacaoReserva(
        nome_hospede=NOME_HOSPEDE,
        email=EMAIL,
        checkin=CHECKIN,
    )
)

with abrir_sessao() as sessao:

    reservas_encontradas = (
        recuperar_reservas_detalhadas(
            sessao,
            solicitacao,
        )
    )

    assert len(
        reservas_encontradas
    ) == 1, (
        "Era esperada exatamente uma "
        "reserva para os dados de teste."
    )

    reserva_recuperada = (
        reservas_encontradas[0]
    )

    print(
        f"Reserva recuperada: "
        f"{reserva_recuperada.codigo_reserva}"
    )

    print(
        f"Status: "
        f"{reserva_recuperada.status}"
    )

    print(
        f"Acomodação: "
        f"{reserva_recuperada.categoria_nome}"
    )

    print(
        f"Check-in: "
        f"{reserva_recuperada.checkin:%d/%m/%Y}"
    )

    print(
        f"Check-out: "
        f"{reserva_recuperada.checkout:%d/%m/%Y}"
    )

    assert (
        reserva_recuperada.codigo_reserva
        == codigo_reserva
    ), (
        "O código recuperado não corresponde "
        "à reserva originalmente criada."
    )

    assert (
        reserva_recuperada.nome_hospede
        == NOME_HOSPEDE
    )

    assert (
        reserva_recuperada.email
        == EMAIL.lower()
    )

    assert (
        reserva_recuperada.checkin
        == CHECKIN
    )

    assert (
        reserva_recuperada.checkout
        == CHECKOUT
    )

    assert (
        reserva_recuperada.status
        == "CONFIRMADA"
    )


print()
print(
    "Sessão de recuperação encerrada."
)


# ============================================================
# ETAPA 3
# TESTAR NORMALIZAÇÃO DO E-MAIL
# ============================================================

print()
print(
    "ETAPA 3 — Testando busca "
    "sem diferenciação de maiúsculas..."
)

solicitacao_normalizada = (
    SolicitacaoRecuperacaoReserva(
        nome_hospede=NOME_HOSPEDE,
        email=EMAIL.upper(),
        checkin=CHECKIN,
    )
)

with abrir_sessao() as sessao:

    reservas_normalizadas = (
        recuperar_reservas_detalhadas(
            sessao,
            solicitacao_normalizada,
        )
    )

    assert len(
        reservas_normalizadas
    ) == 1

    assert (
        reservas_normalizadas[0].codigo_reserva
        == codigo_reserva
    )

print(
    "Busca com e-mail em maiúsculas: OK"
)


# ============================================================
# ETAPA 4
# CANCELAR RESERVA DE TESTE
# ============================================================

print()
print(
    "ETAPA 4 — Limpando reserva "
    "de teste..."
)

with abrir_sessao() as sessao:

    reserva_cancelada = (
        cancelar_reserva(
            sessao,
            codigo_reserva,
        )
    )

    assert (
        reserva_cancelada.status
        == "CANCELADA"
    )

    print(
        f"Reserva cancelada: "
        f"{reserva_cancelada.codigo_reserva}"
    )


# ============================================================
# ETAPA 5
# COMPROVAR QUE O HISTÓRICO CONTINUA NO POSTGRESQL
# ============================================================

print()
print(
    "ETAPA 5 — Recuperando novamente "
    "após o cancelamento..."
)

with abrir_sessao() as sessao:

    reservas_apos_cancelamento = (
        recuperar_reservas_detalhadas(
            sessao,
            solicitacao,
        )
    )

    assert len(
        reservas_apos_cancelamento
    ) == 1

    reserva_final = (
        reservas_apos_cancelamento[0]
    )

    assert (
        reserva_final.codigo_reserva
        == codigo_reserva
    )

    assert (
        reserva_final.status
        == "CANCELADA"
    )

    print(
        f"Reserva localizada novamente: "
        f"{reserva_final.codigo_reserva}"
    )

    print(
        f"Status persistido: "
        f"{reserva_final.status}"
    )


# ============================================================
# RESULTADO
# ============================================================

print()
print(
    "=" * 60
)

print(
    "Todos os testes de recuperação "
    "de reserva passaram."
)

print(
    "=" * 60
)