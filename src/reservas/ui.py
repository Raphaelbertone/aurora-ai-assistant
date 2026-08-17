from __future__ import annotations

import inspect
import logging
from datetime import date, timedelta
from decimal import Decimal

import streamlit as st
import streamlit.components.v1 as components

from src.reservas.database import abrir_sessao
from src.reservas.repository import listar_categorias_ativas

from src.reservas.schemas import (
    DetalheReserva,
    ResultadoDisponibilidade,
    SolicitacaoDisponibilidade,
    SolicitacaoRecuperacaoReserva,
    SolicitacaoReserva,
)

from src.reservas.service import (
    DadosReservaInvalidos,
    ReservaNaoEncontrada,
    SemDisponibilidade,
    cancelar_reserva_detalhada,
    consultar_disponibilidade_detalhada,
    consultar_reserva_detalhada,
    criar_reserva_detalhada,
    recuperar_reservas_detalhadas,
)

logger = logging.getLogger(__name__)

ABA_DISPONIBILIDADE = "🔎 Disponibilidade"
ABA_NOVA_RESERVA = "✅ Nova reserva"
ABA_CONSULTA = "📄 Consultar"
ABA_CANCELAMENTO = "❌ Cancelar"

CHAVES_ESTADO_CENTRAL = (
    # Navegação
    "aba_central",

    # Scroll
    "central_scroll_pendente",

    # Pré-preenchimento
    "central_prefill_reserva",

    # Disponibilidade
    "disponibilidade_checkin",
    "disponibilidade_checkout",
    "disponibilidade_hospedes",
    "disponibilidade_categoria",

    # Nova reserva
    "reserva_categoria_rotulo",
    "reserva_checkin",
    "reserva_checkout",
    "reserva_hospedes",
    "reserva_nome_hospede",
    "reserva_email",
    "reserva_telefone",
    "reserva_observacoes",

    # Consulta
    "modo_consulta_reserva",
    "codigo_consulta_manual",
    "recuperacao_nome",
    "recuperacao_email",
    "recuperacao_checkin",

    # Cancelamento
    "codigo_cancelamento_manual",
    "confirmar_cancelamento",

    # Chaves antigas que podem existir
    "ultima_reserva_codigo",
    "codigo_consulta_reserva",
    "codigo_cancelamento",
)


def resetar_estado_central() -> None:
    """
    Limpa somente o estado temporário
    da Central de Reservas.

    Não altera reservas persistidas no banco
    e não interfere no histórico do Assistente.
    """

    for chave in CHAVES_ESTADO_CENTRAL:
        st.session_state.pop(
            chave,
            None,
        )


def obter_id_resultado(
    identificador: str,
) -> str:
    """
    Retorna o ID HTML padronizado utilizado
    como destino do scroll da Central.
    """

    return (
        f"aurora-reservas-resultado-"
        f"{identificador}"
    )


def exibir_ancora_resultado(
    identificador: str,
) -> None:
    """
    Renderiza a âncora imediatamente antes
    do resultado de uma operação.
    """

    marcador = obter_id_resultado(
        identificador
    )

    st.html(
        f"""
        <div
            id="{marcador}"
            style="
                height: 1px;
                width: 1px;
                scroll-margin-top: 0.85rem;
            "
        ></div>
        """
    )


def solicitar_scroll_resultado(
    identificador: str,
) -> None:
    """
    Registra um scroll para ser executado
    somente depois que o conteúdo da Central
    estiver completamente renderizado.
    """

    st.session_state[
        "central_scroll_pendente"
    ] = obter_id_resultado(
        identificador
    )


def executar_scroll_pendente() -> None:
    """
    Executa o scroll solicitado pela operação
    atualmente exibida na Central.

    Em versões do Streamlit com suporte a
    JavaScript em st.html, executa diretamente
    no documento principal.

    Em versões anteriores, utiliza
    components.html como compatibilidade.
    """

    marcador = st.session_state.pop(
        "central_scroll_pendente",
        None,
    )

    if not marcador:
        return

    script_direto = f"""
    <script>
    (() => {{

        const rolar = () => {{

            const alvo =
                document.getElementById(
                    "{marcador}"
                );

            if (!alvo) {{
                return;
            }}

            alvo.scrollIntoView({{
                behavior: "smooth",
                block: "start"
            }});
        }};

        window.setTimeout(
            rolar,
            120
        );

        window.setTimeout(
            rolar,
            320
        );

        window.setTimeout(
            rolar,
            650
        );

    }})();
    </script>
    """

    parametros_html = inspect.signature(
        st.html
    ).parameters

    if (
        "unsafe_allow_javascript"
        in parametros_html
    ):

        st.html(
            script_direto,
            width="content",
            unsafe_allow_javascript=True,
        )

        return

    script_iframe = f"""
    <script>
    (() => {{

        const documento = (
            window.parent &&
            window.parent.document
        )
            ? window.parent.document
            : document;

        const rolar = () => {{

            const alvo =
                documento.getElementById(
                    "{marcador}"
                );

            if (!alvo) {{
                return;
            }}

            alvo.scrollIntoView({{
                behavior: "smooth",
                block: "start"
            }});
        }};

        window.setTimeout(
            rolar,
            120
        );

        window.setTimeout(
            rolar,
            320
        );

        window.setTimeout(
            rolar,
            650
        );

    }})();
    </script>
    """

    components.html(
        script_iframe,
        height=0,
        scrolling=False,
    )




# ============================================================
# FORMATAÇÃO
# ============================================================

def formatar_moeda(
    valor: Decimal,
) -> str:
    """
    Formata valores monetários no padrão brasileiro.
    """

    valor_formatado = (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"


def formatar_data(
    valor: date,
) -> str:
    """
    Formata datas no padrão brasileiro.
    """

    return valor.strftime(
        "%d/%m/%Y"
    )


# ============================================================
# CATEGORIAS
# ============================================================

def carregar_categorias() -> list[dict]:
    """
    Carrega as categorias ativas e converte
    os objetos ORM em estruturas simples.
    """

    with abrir_sessao() as sessao:

        categorias = (
            listar_categorias_ativas(
                sessao
            )
        )

        return [
            {
                "id": categoria.id,
                "nome": categoria.nome,
                "capacidade": categoria.capacidade,
                "tarifa": Decimal(
                    categoria.tarifa_referencia
                ),
            }
            for categoria in categorias
        ]


def obter_opcoes_categorias(
    categorias: list[dict],
    incluir_todas: bool = False,
) -> dict[str, int | None]:
    """
    Cria as opções exibidas nos selects
    da Central de Reservas.
    """

    opcoes: dict[
        str,
        int | None,
    ] = {}

    if incluir_todas:
        opcoes[
            "Todas as categorias"
        ] = None

    for categoria in categorias:

        rotulo = (
            f"{categoria['nome']} "
            f"— até {categoria['capacidade']} hóspedes "
            f"— {formatar_moeda(categoria['tarifa'])}/diária"
        )

        opcoes[
            rotulo
        ] = categoria["id"]

    return opcoes


def preparar_reserva_por_disponibilidade(
    categoria_id: int,
    checkin: date,
    checkout: date,
    quantidade_hospedes: int,
) -> None:
    """
    Guarda temporariamente os dados escolhidos
    na consulta de disponibilidade e direciona
    o usuário para a aba de nova reserva.
    """

    st.session_state[
        "central_prefill_reserva"
    ] = {
        "categoria_id": categoria_id,
        "checkin": checkin,
        "checkout": checkout,
        "quantidade_hospedes": quantidade_hospedes,
    }

    st.session_state[
        "aba_central"
    ] = ABA_NOVA_RESERVA


# ============================================================
# APRESENTAÇÃO DA DISPONIBILIDADE
# ============================================================

def agrupar_disponibilidade(
    resultado: ResultadoDisponibilidade,
) -> list[dict]:
    """
    Agrupa unidades disponíveis por categoria
    para não expor desnecessariamente os códigos
    internos de todas as unidades.
    """

    agrupadas: dict[
        int,
        dict,
    ] = {}

    for unidade in resultado.unidades:

        if unidade.categoria_id not in agrupadas:

            agrupadas[
                unidade.categoria_id
            ] = {
                "categoria_id": unidade.categoria_id,
                "categoria": unidade.categoria_nome,
                "capacidade": unidade.capacidade,
                "tarifa": unidade.tarifa_referencia,
                "total": unidade.valor_total_estimado,
                "unidades": 0,
            }

        agrupadas[
            unidade.categoria_id
        ]["unidades"] += 1

    return list(
        agrupadas.values()
    )


def exibir_resultado_disponibilidade(
    resultado: ResultadoDisponibilidade,
) -> None:
    """
    Apresenta a disponibilidade encontrada
    em formato amigável.
    """

    if resultado.total_unidades == 0:

        st.warning(
            "Não foram encontradas acomodações disponíveis "
            "para os critérios informados."
        )

        return

    st.success(
        f"{resultado.total_unidades} unidade(s) disponível(is) "
        f"para {resultado.quantidade_diarias} diária(s)."
    )

    st.caption(
        f"Período: "
        f"{formatar_data(resultado.checkin)} a "
        f"{formatar_data(resultado.checkout)} • "
        f"{resultado.quantidade_hospedes} hóspede(s)"
    )

    agrupadas = agrupar_disponibilidade(
        resultado
    )

    for indice in range(
        0,
        len(agrupadas),
        2,
    ):

        colunas = st.columns(
            2,
            gap="medium",
        )

        grupo = agrupadas[
            indice:indice + 2
        ]

        for coluna, categoria in zip(
            colunas,
            grupo,
        ):

            with coluna:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {categoria['categoria']}"
                    )

                    st.caption(
                        f"Até {categoria['capacidade']} hóspedes"
                    )

                    st.metric(
                        "Unidades disponíveis",
                        categoria["unidades"],
                    )

                    st.write(
                        "**Diária de referência:** "
                        f"{formatar_moeda(categoria['tarifa'])}"
                    )

                    st.write(
                        f"**Estimativa para "
                        f"{resultado.quantidade_diarias} diária(s):** "
                        f"{formatar_moeda(categoria['total'])}"
                    )

                    st.button(
                        "Reservar esta opção",
                        key=(
                            f"reservar_opcao_"
                            f"{categoria['categoria_id']}"
                        ),
                        type="primary",
                        width="stretch",
                        on_click=(
                            preparar_reserva_por_disponibilidade
                        ),
                        args=(
                            categoria["categoria_id"],
                            resultado.checkin,
                            resultado.checkout,
                            resultado.quantidade_hospedes,
                        ),
                    )


# ============================================================
# APRESENTAÇÃO DE RESERVA
# ============================================================

def exibir_detalhe_reserva(
    reserva: DetalheReserva,
) -> None:
    """
    Exibe os dados principais de uma reserva.
    """

    status_icone = (
        "✅"
        if reserva.status == "CONFIRMADA"
        else "❌"
    )

    st.markdown(
        f"### {status_icone} {reserva.codigo_reserva}"
    )

    coluna_1, coluna_2 = st.columns(
        2,
        gap="medium",
    )

    with coluna_1:

        st.write(
            f"**Status:** {reserva.status}"
        )

        st.write(
            f"**Acomodação:** "
            f"{reserva.categoria_nome}"
        )

        st.write(
            f"**Unidade atribuída:** "
            f"{reserva.unidade_codigo}"
        )

        st.write(
            f"**Hóspede:** "
            f"{reserva.nome_hospede}"
        )

    with coluna_2:

        st.write(
            f"**Check-in:** "
            f"{formatar_data(reserva.checkin)}"
        )

        st.write(
            f"**Check-out:** "
            f"{formatar_data(reserva.checkout)}"
        )

        st.write(
            f"**Hóspedes:** "
            f"{reserva.quantidade_hospedes}"
        )

        st.write(
            f"**Diárias:** "
            f"{reserva.quantidade_diarias}"
        )

    st.divider()

    coluna_3, coluna_4 = st.columns(
        2
    )

    with coluna_3:

        st.metric(
            "Tarifa aplicada",
            formatar_moeda(
                reserva.tarifa_diaria_aplicada
            ),
        )

    with coluna_4:

        st.metric(
            "Valor total estimado",
            formatar_moeda(
                reserva.valor_total_estimado
            ),
        )

    if reserva.telefone:

        st.write(
            f"**Telefone:** {reserva.telefone}"
        )

    st.write(
        f"**E-mail:** {reserva.email}"
    )

    if reserva.observacoes:

        st.write(
            f"**Observações:** "
            f"{reserva.observacoes}"
        )

    if reserva.cancelada_em:

        st.caption(
            "Reserva cancelada em "
            f"{reserva.cancelada_em:%d/%m/%Y %H:%M}."
        )


# ============================================================
# CONSULTA DE DISPONIBILIDADE
# ============================================================

def exibir_consulta_disponibilidade(
    categorias: list[dict],
) -> None:
    """
    Interface da consulta de disponibilidade.
    """

    st.subheader(
        "Consultar disponibilidade"
    )

    st.caption(
        "Consulte as acomodações disponíveis no banco "
        "demonstrativo da Pousada Mirante do Pôr do Sol."
    )

    opcoes = obter_opcoes_categorias(
        categorias,
        incluir_todas=True,
    )

    hoje = date.today()

    with st.form(
        "form_disponibilidade"
    ):

        coluna_1, coluna_2 = st.columns(
            2
        )

        with coluna_1:

            checkin = st.date_input(
                "Check-in",
                value=hoje + timedelta(days=1),
                min_value=hoje,
                format="DD/MM/YYYY",
                key="disponibilidade_checkin",
            )

        with coluna_2:

            checkout = st.date_input(
                "Check-out",
                value=hoje + timedelta(days=3),
                min_value=hoje + timedelta(days=1),
                format="DD/MM/YYYY",
                key="disponibilidade_checkout",
            )

        quantidade_hospedes = st.number_input(
            "Quantidade de hóspedes",
            min_value=1,
            max_value=5,
            value=2,
            step=1,
            key="disponibilidade_hospedes",
        )

        categoria_rotulo = st.selectbox(
            "Categoria",
            options=list(
                opcoes.keys()
            ),
            key="disponibilidade_categoria",
        )

        consultar = (
            st.form_submit_button(
                "🔎 Consultar disponibilidade",
                width="stretch",
            )
        )

    if not consultar:
        return

    try:

        solicitacao = (
            SolicitacaoDisponibilidade(
                checkin=checkin,
                checkout=checkout,
                quantidade_hospedes=int(
                    quantidade_hospedes
                ),
                categoria_id=opcoes[
                    categoria_rotulo
                ],
            )
        )

        with abrir_sessao() as sessao:

            resultado = (
                consultar_disponibilidade_detalhada(
                    sessao,
                    solicitacao,
                )
            )

        exibir_ancora_resultado(
            "disponibilidade"
        )

        exibir_resultado_disponibilidade(
            resultado
        )

        solicitar_scroll_resultado(
            "disponibilidade"
        )

    except DadosReservaInvalidos as erro:

        st.warning(
            str(erro)
        )

    except Exception:

        logger.exception(
            "Erro ao consultar disponibilidade."
        )

        st.error(
            "Não foi possível consultar a disponibilidade "
            "neste momento."
        )


# ============================================================
# NOVA RESERVA
# ============================================================

def exibir_nova_reserva(
    categorias: list[dict],
) -> None:
    """
    Interface para criação de reserva fictícia.
    """

    st.subheader(
        "Criar reserva fictícia"
    )

    st.info(
        "Esta funcionalidade é exclusivamente demonstrativa. "
        "Utilize dados fictícios. Nenhum pagamento será processado."
    )

    opcoes = obter_opcoes_categorias(
        categorias
    )

    hoje = date.today()


    prefill = st.session_state.pop(
        "central_prefill_reserva",
        None,
    )

    if prefill is not None:

        categoria_rotulo_prefill = next(
            (
                rotulo
                for rotulo, categoria_id
                in opcoes.items()
                if categoria_id
                == prefill["categoria_id"]
            ),
            None,
        )

        if categoria_rotulo_prefill is not None:

            st.session_state[
                "reserva_categoria_rotulo"
            ] = categoria_rotulo_prefill

        st.session_state[
            "reserva_checkin"
        ] = prefill["checkin"]

        st.session_state[
            "reserva_checkout"
        ] = prefill["checkout"]

        st.session_state[
            "reserva_hospedes"
        ] = prefill[
            "quantidade_hospedes"
        ]


    with st.form(
        "form_nova_reserva",
        clear_on_submit=False,
    ):

        categoria_rotulo = st.selectbox(
            "Categoria desejada",
            options=list(
                opcoes.keys()
            ),
            key="reserva_categoria_rotulo",
        )

        coluna_1, coluna_2 = st.columns(
            2
        )

        with coluna_1:

            checkin = st.date_input(
                "Check-in",
                value=hoje + timedelta(days=1),
                min_value=hoje,
                format="DD/MM/YYYY",
                key="reserva_checkin",
            )

        with coluna_2:

            checkout = st.date_input(
                "Check-out",
                value=hoje + timedelta(days=3),
                min_value=hoje + timedelta(days=1),
                format="DD/MM/YYYY",
                key="reserva_checkout",
            )

        quantidade_hospedes = st.number_input(
            "Quantidade de hóspedes",
            min_value=1,
            max_value=5,
            value=2,
            step=1,
            key="reserva_hospedes",
        )

        st.divider()

        nome_hospede = st.text_input(
            "Nome do hóspede",
            placeholder="Ex.: Hóspede Demonstração",
            key="reserva_nome_hospede",
        )

        email = st.text_input(
            "E-mail",
            placeholder="Ex.: demo@aurora.local",
            key="reserva_email",
        )

        telefone = st.text_input(
            "Telefone (opcional)",
            placeholder="Ex.: (11) 99999-9999",
            key="reserva_telefone",
        )

        observacoes = st.text_area(
            "Observações (opcional)",
            max_chars=500,
            key="reserva_observacoes",
        )

        criar = st.form_submit_button(
            "✅ Confirmar reserva fictícia",
            width="stretch",
        )

    if not criar:
        return

    try:

        solicitacao = SolicitacaoReserva(
            nome_hospede=nome_hospede,
            email=email,
            telefone=(
                telefone
                if telefone.strip()
                else None
            ),
            checkin=checkin,
            checkout=checkout,
            quantidade_hospedes=int(
                quantidade_hospedes
            ),
            categoria_id=opcoes[
                categoria_rotulo
            ],
            observacoes=(
                observacoes
                if observacoes.strip()
                else None
            ),
        )

        with abrir_sessao() as sessao:

            reserva = (
                criar_reserva_detalhada(
                    sessao,
                    solicitacao,
                )
            )
        
        exibir_ancora_resultado(
            "nova-reserva"
        )

        st.success(
            "Reserva fictícia criada com sucesso."
        )

        st.warning(
            "Anote ou copie o código da reserva. "
            "Ele será necessário para consultas "
            "e cancelamentos."
        )

        st.code(
            reserva.codigo_reserva,
            language=None,
        )
        
        exibir_detalhe_reserva(
            reserva
        )

        solicitar_scroll_resultado(
            "nova-reserva"
        )

    except (
        DadosReservaInvalidos,
        SemDisponibilidade,
    ) as erro:

        st.warning(
            str(erro)
        )

    except Exception:

        logger.exception(
            "Erro ao criar reserva."
        )

        st.error(
            "Não foi possível criar a reserva "
            "neste momento."
        )


# ============================================================
# CONSULTA DE RESERVA
# ============================================================

def exibir_consulta_reserva() -> None:
    """
    Interface de consulta e recuperação
    de reservas demonstrativas.
    """

    st.subheader(
        "Consultar reserva"
    )

    st.caption(
        "Consulte sua reserva pelo código ou "
        "recupere-a utilizando os dados informados "
        "no momento da reserva."
    )

    modo_consulta = st.radio(
        "Como deseja consultar?",
        options=[
            "Tenho o código",
            "Não lembro o código",
        ],
        horizontal=True,
        key="modo_consulta_reserva",
    )

    # ========================================================
    # CONSULTA PELO CÓDIGO
    # ========================================================

    if modo_consulta == "Tenho o código":

        with st.form(
            "form_consultar_reserva"
        ):

            codigo = st.text_input(
                "Código da reserva",
                placeholder="AUR-20260812-XXXXXXXX",
                key="codigo_consulta_manual",
            )

            consultar = (
                st.form_submit_button(
                    "🔎 Consultar reserva",
                    width="stretch",
                )
            )

        if not consultar:
            return

        try:

            with abrir_sessao() as sessao:

                reserva = (
                    consultar_reserva_detalhada(
                        sessao,
                        codigo,
                    )
                )

            exibir_ancora_resultado(
                "consulta-reserva"
            )

            exibir_detalhe_reserva(
                reserva
            )

            solicitar_scroll_resultado(
                "consulta-reserva"
            )

        except (
            DadosReservaInvalidos,
            ReservaNaoEncontrada,
        ) as erro:

            st.warning(
                str(erro)
            )

        except Exception:

            logger.exception(
                "Erro ao consultar reserva."
            )

            st.error(
                "Não foi possível consultar "
                "a reserva neste momento."
            )

        return

    # ========================================================
    # RECUPERAÇÃO SEM O CÓDIGO
    # ========================================================

    st.info(
        "Preencha pelo menos um dos campos abaixo. "
        "Quanto mais informações você fornecer, "
        "mais precisa será a busca."
    )

    st.caption(
        "Use apenas os dados que lembrar com segurança. "
        "Não é necessário preencher todos os campos."
    )

    with st.form(
        "form_recuperar_reserva"
    ):

        nome_hospede = st.text_input(
            "Nome do hóspede (opcional)",
            placeholder="Ex.: Hóspede Demonstração",
            key="recuperacao_nome",
        )

        email = st.text_input(
            "E-mail utilizado na reserva (opcional)",
            placeholder="Ex.: demo@aurora.local",
            key="recuperacao_email",
        )

        checkin = st.date_input(
            "Data de check-in (opcional)",
            value=None,
            format="DD/MM/YYYY",
            key="recuperacao_checkin",
        )

        recuperar = (
            st.form_submit_button(
                "🔎 Localizar minha reserva",
                width="stretch",
            )
        )

    if not recuperar:
        return

    try:

        solicitacao = (
            SolicitacaoRecuperacaoReserva(
                nome_hospede=(
                    nome_hospede
                    if nome_hospede.strip()
                    else None
                ),
                email=(
                    email
                    if email.strip()
                    else None
                ),
                checkin=checkin,
            )
        )

        with abrir_sessao() as sessao:

            reservas = (
                recuperar_reservas_detalhadas(
                    sessao,
                    solicitacao,
                )
            )

        exibir_ancora_resultado(
            "recuperacao-reserva"
        )

        if len(reservas) == 1:

            st.success(
                "Reserva localizada com sucesso."
            )

        else:

            st.success(
                f"{len(reservas)} reservas foram "
                "localizadas com os dados informados."
            )

            st.info(
                "Mais de uma reserva corresponde à busca. "
                "Confira os resultados abaixo ou informe "
                "mais dados para refinar a consulta."
            )

        for reserva in reservas:

            with st.container(
                border=True
            ):

                exibir_detalhe_reserva(
                    reserva
                )

        solicitar_scroll_resultado(
            "recuperacao-reserva"
        )

    except (
        DadosReservaInvalidos,
        ReservaNaoEncontrada,
    ) as erro:

        st.warning(
            str(erro)
        )

    except Exception:

        logger.exception(
            "Erro ao recuperar reserva."
        )

        st.error(
            "Não foi possível localizar "
            "a reserva neste momento."
        )


# ============================================================
# CANCELAMENTO
# ============================================================

def exibir_cancelamento_reserva() -> None:
    """
    Interface de cancelamento de reserva fictícia.
    """

    st.subheader(
        "Cancelar reserva"
    )

    st.caption(
        "Informe o código da reserva que deseja cancelar. "
        "O cancelamento preserva o registro no banco e "
        "libera novamente a unidade para o período."
    )

    with st.form(
        "form_cancelar_reserva"
    ):

        codigo = st.text_input(
            "Código da reserva",
            key="codigo_cancelamento",
            placeholder="AUR-20260811-XXXXXXXX",
        )

        confirmar = st.checkbox(
            "Confirmo o cancelamento desta reserva fictícia.",
            key="confirmar_cancelamento",
        )

        cancelar = (
            st.form_submit_button(
                "❌ Cancelar reserva",
                width="stretch",
            )
        )

    if not cancelar:
        return

    if not confirmar:

        st.warning(
            "Marque a confirmação antes de cancelar."
        )

        return

    try:

        with abrir_sessao() as sessao:

            reserva = (
                cancelar_reserva_detalhada(
                    sessao,
                    codigo,
                )
            )

        exibir_ancora_resultado(
            "cancelamento"
        )

        st.success(
            "Reserva fictícia cancelada."
        )

        exibir_detalhe_reserva(
            reserva
        )

        solicitar_scroll_resultado(
            "cancelamento"
        )

    except (
        DadosReservaInvalidos,
        ReservaNaoEncontrada,
    ) as erro:

        st.warning(
            str(erro)
        )

    except Exception:

        logger.exception(
            "Erro ao cancelar reserva."
        )

        st.error(
            "Não foi possível cancelar a reserva "
            "neste momento."
        )


# ============================================================
# CENTRAL
# ============================================================

def exibir_central_reservas() -> None:
    """
    Renderiza a Central de Reservas demonstrativa.
    """

    st.html(
        """
        <style>

        /* ======================================================
        CENTRAL DE RESERVAS — HERO
        ====================================================== */

        .aurora-reservas-hero {
            position: relative;
            overflow: hidden;

            margin-bottom: 0.82rem;
            padding: 1rem 1.25rem 1.08rem;

            border-radius: 18px;

            background:
                linear-gradient(
                    126deg,
                    #29382E 0%,
                    #3C5041 58%,
                    #6B553E 100%
                );

            color: #FFFFFF;

            box-shadow:
                0 10px 26px
                rgba(41, 56, 46, 0.11);
        }


        .aurora-reservas-hero::after {
            content: "";

            position: absolute;

            left: 0;
            bottom: 0;

            width: 31%;
            height: 3px;

            background:
                linear-gradient(
                    90deg,
                    #D9903D,
                    #F1C58D,
                    transparent
                );
        }


        .aurora-reservas-topline {
            position: relative;
            z-index: 2;

            display: flex;
            align-items: center;

            gap: 0.7rem;

            margin-bottom: 0.75rem;
        }


        .aurora-reservas-eyebrow {
            flex: 0 0 auto;

            color: #F1C58D;

            font-size: 0.64rem;
            font-weight: 800;

            letter-spacing: 0.09em;
            text-transform: uppercase;
        }


        .aurora-reservas-line {
            flex: 1 1 auto;

            height: 1px;

            background:
                linear-gradient(
                    90deg,
                    rgba(255, 255, 255, 0.25),
                    rgba(255, 255, 255, 0.04)
                );
        }


        .aurora-reservas-brand {
            position: relative;
            z-index: 2;

            display: flex;
            align-items: center;

            gap: 0.85rem;
        }


        .aurora-reservas-icon {
            display: flex;

            flex: 0 0 42px;

            width: 42px;
            height: 42px;

            align-items: center;
            justify-content: center;

            border:
                1px solid
                rgba(255, 255, 255, 0.14);

            border-radius: 11px;

            background:
                rgba(255, 255, 255, 0.08);

            font-size: 1.28rem;
        }


        .aurora-reservas-title {
            margin: 0;

            color: #FFFFFF;

            font-family:
                "Ubuntu Mono",
                "Cascadia Mono",
                "SFMono-Regular",
                Consolas,
                "Liberation Mono",
                monospace;

            font-size:
                clamp(
                    1.55rem,
                    3vw,
                    2rem
                );

            font-weight: 500;

            line-height: 1.05;

            letter-spacing: -0.035em;
        }


        .aurora-reservas-description {
            position: relative;
            z-index: 2;

            max-width: 760px;

            margin:
                0.55rem
                0
                0
                3.55rem;

            color:
                rgba(
                    255,
                    255,
                    255,
                    0.80
                );

            font-size: 0.79rem;
            line-height: 1.52;
        }


        /* ======================================================
        AVISO DEMONSTRATIVO
        ====================================================== */

        .aurora-reservas-notice {
            margin:
                0.15rem
                0
                0.82rem;

            color: #6E675F;

            font-size: 0.72rem;
            font-weight: 500;

            line-height: 1.45;
        }

        
        /* ======================================================
        TEXTOS SECUNDÁRIOS
        ====================================================== */

        [data-testid="stCaptionContainer"] {
            color: #6E675F !important;

            opacity: 1 !important;

            font-size: 0.73rem !important;

            line-height: 1.45 !important;
        }

        
        /* ======================================================
        CARDS E MÉTRICAS
        ====================================================== */
        
        [data-testid="stMetric"] {
            border:
                1px solid
                #DED5CA;

            border-radius: 12px;

            padding:
                0.65rem
                0.75rem;

            background:
                #F5EFE7;
        }


        [data-testid="stMetricLabel"] {
            color:
                #5C544C !important;

            font-weight:
                650 !important;
        }


        [data-testid="stMetricValue"] {
            color:
                #29382E !important;
        }


        /* ======================================================
            RÓTULOS DOS CAMPOS
           ====================================================== */

        [data-testid="stWidgetLabel"] p {
            color: #49372B !important;
            font-weight: 700 !important;
            letter-spacing: 0.005em;
        }


        /* Labels de checkbox */
        [data-testid="stCheckbox"] label p {
            color: #49372B !important;
            font-weight: 600 !important;
        }


        /* ======================================================
        BORDAS DOS FORMULÁRIOS
        ====================================================== */

        [data-testid="stForm"] {
            border:
                1px solid
                #C8B8A6 !important;

            border-radius:
                15px !important;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.46
                ) !important;
        }


        /* Cards com borda */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color:
                #C8B8A6 !important;
        }


        /* ======================================================
        BOTÕES PRINCIPAIS DOS FORMULÁRIOS
        ====================================================== */

        [data-testid="stFormSubmitButton"] button {
            min-height: 2.65rem !important;

            border:
                1px solid
                #D7A66F !important;

            border-radius:
                11px !important;

            background:
                linear-gradient(
                    135deg,
                    #F6E8D6 0%,
                    #F2DEC4 100%
                ) !important;

            color:
                #70471F !important;

            font-weight:
                750 !important;

            box-shadow:
                0 3px 10px
                rgba(112, 71, 31, 0.06) !important;

            transition:
                transform 0.16s ease,
                border-color 0.16s ease,
                background 0.16s ease,
                box-shadow 0.16s ease !important;
        }


        [data-testid="stFormSubmitButton"] button:hover {
            transform:
                translateY(-1px);

            border-color:
                #C98235 !important;

            background:
                linear-gradient(
                    135deg,
                    #F3DFC5 0%,
                    #EDD0A9 100%
                ) !important;

            color:
                #5C3819 !important;

            box-shadow:
                0 5px 14px
                rgba(112, 71, 31, 0.11) !important;
        }


        [data-testid="stFormSubmitButton"] button:focus {
            border-color:
                #D9903D !important;

            box-shadow:
                0 0 0 2px
                rgba(217, 144, 61, 0.16) !important;
        }


        /* ======================================================
        ABAS DA CENTRAL
        ====================================================== */

        button[data-baseweb="tab"] {
            color:
                #49372B !important;

            font-weight:
                700 !important;
        }


        button[data-baseweb="tab"][aria-selected="true"] {
            color:
                #A96124 !important;

            font-weight:
                800 !important;
        }


        /* ======================================================
        MOBILE
        ====================================================== */

        @media (max-width: 768px) {

            .aurora-reservas-hero {
                padding:
                    0.9rem
                    0.95rem
                    1rem;

                border-radius: 16px;
            }


            .aurora-reservas-brand {
                gap: 0.68rem;
            }


            .aurora-reservas-icon {
                flex-basis: 38px;

                width: 38px;
                height: 38px;

                font-size: 1.12rem;
            }


            .aurora-reservas-title {
                font-size: 1.55rem;
            }


            .aurora-reservas-description {
                margin-left: 0;

                font-size: 0.76rem;
            }


            button[data-baseweb="tab"] {
                font-size:
                    0.78rem !important;
            }

        }

        </style>


        <section class="aurora-reservas-hero">

            <div class="aurora-reservas-topline">

                <div class="aurora-reservas-eyebrow">
                    Pousada Mirante do Pôr do Sol
                </div>

                <div class="aurora-reservas-line"></div>

            </div>


            <div class="aurora-reservas-brand">

                <div class="aurora-reservas-icon">
                    🌄
                </div>

                <h1 class="aurora-reservas-title">
                    Central de Reservas
                </h1>

            </div>


            <p class="aurora-reservas-description">
                Consulte disponibilidade, escolha sua acomodação,
                crie reservas fictícias, acompanhe uma reserva
                pelo código e simule cancelamentos utilizando
                a base relacional do Agente Aurora.
            </p>

        </section>
        """
    )

    st.html(
        """
        <div class="aurora-reservas-notice">
            🔒 Ambiente demonstrativo •
            Não utilize dados pessoais reais •
            Nenhum pagamento é realizado.
        </div>
        """
    )

    try:

        categorias = carregar_categorias()

    except Exception:

        logger.exception(
            "Erro ao carregar categorias."
        )

        st.error(
            "A Central de Reservas não conseguiu "
            "acessar o banco de dados."
        )

        return

    if not categorias:

        st.warning(
            "Nenhuma categoria ativa foi encontrada."
        )

        return

    (
        aba_disponibilidade,
        aba_reserva,
        aba_consulta,
        aba_cancelamento,
    ) = st.tabs(
        [
            ABA_DISPONIBILIDADE,
            ABA_NOVA_RESERVA,
            ABA_CONSULTA,
            ABA_CANCELAMENTO,
        ],
        key="aba_central",
        default=ABA_DISPONIBILIDADE,
        on_change="rerun",
    )

    if aba_disponibilidade.open:

        with aba_disponibilidade:

            exibir_consulta_disponibilidade(
                categorias
            )

    elif aba_reserva.open:

        with aba_reserva:

            exibir_nova_reserva(
                categorias
            )

    elif aba_consulta.open:

        with aba_consulta:

            exibir_consulta_reserva()

    elif aba_cancelamento.open:

        with aba_cancelamento:

            exibir_cancelamento_reserva()

    executar_scroll_pendente()