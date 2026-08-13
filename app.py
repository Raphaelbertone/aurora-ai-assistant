from html import unescape
import inspect
import logging
import re
from time import perf_counter

import streamlit as st
import streamlit.components.v1 as components

from src.gallery import (
    e_pedido_apenas_visual,
    obter_caminho_imagem,
    selecionar_imagens,
)
from src.rag import gerar_resposta

from src.reservas.ui import (
    exibir_central_reservas,
    resetar_estado_central,
)


logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="Agente Aurora | Pousada Mirante do Pôr do Sol",
    page_icon="🌄",
    layout="centered",
    initial_sidebar_state="auto",
)


st.html(
    """
    <style>

    :root {
        --aurora-background: #F7F3EC;
        --aurora-surface: #FFFFFF;
        --aurora-surface-soft: #FBF8F3;
        --aurora-text: #292622;
        --aurora-text-soft: #6E675F;
        --aurora-primary: #49372B;
        --aurora-sunset: #D9903D;
        --aurora-sunset-soft: #F1C58D;
        --aurora-green: #435546;
        --aurora-green-dark: #29382E;
        --aurora-border: #E5DDD2;
    }

    *,
    *::before,
    *::after {
        box-sizing: border-box;
    }

    html,
    body,
    .stApp {
        max-width: 100%;
        overflow-x: hidden !important;
    }

    img {
        max-width: 100%;
    }

    html,
    body,
    [class*="css"] {
        font-family:
            Inter,
            "Segoe UI",
            Arial,
            sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 93% 3%,
                rgba(217, 144, 61, 0.065),
                transparent 23%
            ),
            radial-gradient(
                circle at 4% 32%,
                rgba(67, 85, 70, 0.045),
                transparent 22%
            ),
            var(--aurora-background);
        color: var(--aurora-text);
    }

    .block-container {
        width: 100%;
        max-width: 960px;
        padding-top: 0.78rem;
        padding-left: 1.1rem;
        padding-right: 1.1rem;
        padding-bottom: 1.25rem;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }


    /* ==========================================================
       CONTROLE DE ABERTURA DA SIDEBAR
       ========================================================== */

    [data-testid="collapsedControl"] {
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }

    [data-testid="collapsedControl"] button {
        border:
            1px solid
            rgba(41, 56, 46, 0.18) !important;
        border-radius: 11px !important;
        background:
            rgba(255, 255, 255, 0.96) !important;
        box-shadow:
            0 4px 14px
            rgba(41, 56, 46, 0.12) !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="collapsedControl"] svg path {
        color: #29382E !important;
        fill: #29382E !important;
        stroke: #29382E !important;
    }


    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stDeployButton"] {
        display: none !important;
    }


    /* ==========================================================
       HERO PRINCIPAL
       ========================================================== */

    .aurora-hero {
        position: relative;
        width: 100%;
        overflow: hidden;
        margin: 0 0 0.75rem 0;
        padding: 0.9rem 1.3rem 1.05rem;
        border-radius: 18px;
        background:
            linear-gradient(
                126deg,
                #29382E 0%,
                #3C5041 58%,
                #6B553E 100%
            );
        box-shadow:
            0 10px 26px
            rgba(41, 56, 46, 0.11);
        color: #FFFFFF;
    }

    .aurora-hero::before {
        content: "";
        position: absolute;
        width: 235px;
        height: 235px;
        right: -68px;
        top: -158px;
        border-radius: 50%;
        background:
            radial-gradient(
                circle,
                rgba(241, 197, 141, 0.52) 0%,
                rgba(217, 144, 61, 0.23) 40%,
                transparent 72%
            );
        pointer-events: none;
    }

    .aurora-hero::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        width: 36%;
        height: 3px;
        background:
            linear-gradient(
                90deg,
                #D9903D,
                #F1C58D,
                transparent
            );
    }

    .aurora-hero-topline {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
        margin-bottom: 0.72rem;
    }

    .aurora-hero-eyebrow {
        flex: 0 0 auto;
        color: rgba(255, 255, 255, 0.76);
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.105em;
        text-transform: uppercase;
    }

    .aurora-hero-line {
        flex: 1 1 auto;
        height: 1px;
        background:
            linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.28),
                rgba(255, 255, 255, 0.05)
            );
    }

    .aurora-hero-grid {
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns:
            minmax(0, 1.04fr)
            minmax(0, 0.96fr);
        align-items: end;
        gap: 1.9rem;
    }

    .aurora-hero-left,
    .aurora-hero-right {
        min-width: 0;
    }

    .aurora-hero-right {
        padding-left: 1.55rem;
        border-left:
            1px solid
            rgba(255, 255, 255, 0.13);
        text-align: right;
    }

    .aurora-brand-row {
        display: flex;
        align-items: center;
        gap: 0.72rem;
    }

    .aurora-brand-icon {
        display: flex;
        flex: 0 0 40px;
        width: 40px;
        height: 40px;
        align-items: center;
        justify-content: center;
        border:
            1px solid
            rgba(255, 255, 255, 0.13);
        border-radius: 11px;
        background:
            rgba(255, 255, 255, 0.08);
        font-size: 1.25rem;
    }

    .aurora-title {
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
            clamp(1.85rem, 3.3vw, 2.45rem);
        font-weight: 500;
        line-height: 1;
        letter-spacing: -0.042em;
    }

    .aurora-hotel {
        margin-top: 0.38rem;
        color:
            rgba(255, 255, 255, 0.92);
        font-size:
            clamp(0.98rem, 1.6vw, 1.12rem);
        font-weight: 650;
        line-height: 1.3;
    }

    .aurora-slogan {
        margin: 0;
        color: #F4C98D;
        font-size:
            clamp(0.9rem, 1.45vw, 1.03rem);
        font-weight: 650;
        line-height: 1.4;
    }

    .aurora-description {
        margin: 0.45rem 0 0 auto;
        max-width: 430px;
        color:
            rgba(255, 255, 255, 0.72);
        font-size: 0.75rem;
        line-height: 1.5;
    }


    /* ==========================================================
       HERO COM CONVERSA
       ========================================================== */

    .aurora-hero-conversation {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        width: 100%;
        overflow: hidden;
        margin-bottom: 0.65rem;
        padding: 0.66rem 0.95rem;
        border-radius: 15px;
        background:
            linear-gradient(
                125deg,
                #29382E 0%,
                #3B4F40 62%,
                #65513D 100%
            );
        box-shadow:
            0 7px 19px
            rgba(41, 56, 46, 0.085);
        color: #FFFFFF;
    }

    .aurora-hero-conversation::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        width: 26%;
        height: 2px;
        background:
            linear-gradient(
                90deg,
                #D9903D,
                transparent
            );
    }

    .aurora-conversation-brand {
        display: flex;
        align-items: center;
        gap: 0.64rem;
        min-width: 0;
    }

    .aurora-conversation-icon {
        display: flex;
        flex: 0 0 36px;
        width: 36px;
        height: 36px;
        align-items: center;
        justify-content: center;
        border:
            1px solid
            rgba(255, 255, 255, 0.13);
        border-radius: 10px;
        background:
            rgba(255, 255, 255, 0.08);
        font-size: 1.08rem;
    }

    .aurora-conversation-title {
        color: #FFFFFF;
        font-family:
            "Ubuntu Mono",
            "Cascadia Mono",
            "SFMono-Regular",
            Consolas,
            "Liberation Mono",
            monospace;
        font-size: 1.13rem;
        font-weight: 500;
        line-height: 1.05;
        letter-spacing: -0.025em;
    }

    .aurora-conversation-hotel {
        margin-top: 0.13rem;
        color:
            rgba(255, 255, 255, 0.70);
        font-size: 0.67rem;
        font-weight: 600;
    }

    .aurora-conversation-slogan {
        max-width: 510px;
        color: #F4C98D;
        font-size: 0.88rem;
        font-weight: 600;
        line-height: 1.4;
        text-align: right;
    }


    /* ==========================================================
       BOAS-VINDAS
       ========================================================== */

    .aurora-welcome {
        width: 100%;
        margin-bottom: 0.7rem;
        padding: 0.76rem 0.9rem;
        border:
            1px solid
            var(--aurora-border);
        border-radius: 15px;
        background:
            rgba(255, 255, 255, 0.79);
        box-shadow:
            0 4px 15px
            rgba(55, 42, 31, 0.03);
    }

    .aurora-welcome-row {
        display: flex;
        align-items: flex-start;
        gap: 0.72rem;
    }

    .aurora-welcome-avatar {
        display: flex;
        flex: 0 0 34px;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        margin-top: 0.05rem;
        border-radius: 10px;
        background:
            linear-gradient(
                135deg,
                #435546,
                #29382E
            );
        font-size: 1rem;
    }

    .aurora-welcome-text {
        color: var(--aurora-text);
        font-size: 0.82rem;
        line-height: 1.48;
    }

    .aurora-welcome-text p {
        margin: 0 0 0.44rem;
    }

    .aurora-welcome-text p:last-child {
        margin-bottom: 0;
    }

    .aurora-welcome-text strong {
        color: var(--aurora-primary);
    }

    .aurora-section-label {
        margin: 0.72rem 0 0.44rem;
        color: var(--aurora-green);
        font-size: 0.64rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }


    /* ==========================================================
       BOTÕES
       ========================================================== */

    .stButton > button {
        width: 100%;
        min-height: 2.4rem;
        padding: 0.4rem 0.6rem;
        border:
            1px solid
            var(--aurora-border);
        border-radius: 12px;
        background:
            rgba(255, 255, 255, 0.84);
        color: var(--aurora-primary);
        font-size: 0.78rem;
        font-weight: 500;
        box-shadow:
            0 3px 10px
            rgba(55, 42, 31, 0.03);
        transition:
            transform 0.16s ease,
            border-color 0.16s ease,
            background 0.16s ease,
            box-shadow 0.16s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color:
            rgba(217, 144, 61, 0.62);
        background: #FFFFFF;
        color: var(--aurora-primary);
        box-shadow:
            0 5px 15px
            rgba(55, 42, 31, 0.06);
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.6rem;
    }


    /* ==========================================================
       CHAT
       ========================================================== */

    [data-testid="stChatMessage"] {
        width: 100%;
        scroll-margin-top: 0.8rem;
        margin-bottom: 0.56rem;
        padding: 0.8rem 0.9rem;
        border:
            1px solid
            var(--aurora-border);
        border-radius: 15px;
        background:
            rgba(255, 255, 255, 0.87);
        box-shadow:
            0 4px 15px
            rgba(55, 42, 31, 0.03);
    }

    [data-testid="stChatMessage"] p {
        margin-bottom: 0.4rem;
        font-size: 0.86rem;
        line-height: 1.54;
    }

    [data-testid="stChatMessage"] p:last-child {
        margin-bottom: 0;
    }

    [data-testid="stChatMessage"] strong {
        color: var(--aurora-primary);
    }

    [data-testid="stChatMessage"] ul {
        margin-top: 0.28rem;
        margin-bottom: 0.32rem;
    }

    [data-testid="stChatMessage"] li {
        margin-bottom: 0.16rem;
        font-size: 0.86rem;
    }


    /* ==========================================================
       BARRA DO CHAT
       ========================================================== */

    .st-key-aurora-chat-bar,
    .st-key-aurora-chat-bar-inicial {
        position: sticky;
        bottom: 0.45rem;
        z-index: 50;
        width: min(850px, 100%);
        margin-left: auto;
        margin-right: auto;
        padding: 0.18rem;
        background: transparent !important;
    }

    .st-key-aurora-chat-bar {
        margin-top: 0.7rem;
    }

    .st-key-aurora-chat-bar-inicial {
        margin-top:
            clamp(2rem, 9vh, 5rem);
    }

    .st-key-aurora-chat-bar [data-testid="stChatInput"],
    .st-key-aurora-chat-bar-inicial [data-testid="stChatInput"] {
        width: 100%;
        overflow: hidden;
        border:
            1px solid
            var(--aurora-border);
        border-radius: 16px;
        background:
            rgba(255, 255, 255, 0.96);
        box-shadow:
            0 8px 23px
            rgba(55, 42, 31, 0.08);
    }

    .st-key-aurora-chat-bar [data-testid="stChatInput"] textarea,
    .st-key-aurora-chat-bar-inicial [data-testid="stChatInput"] textarea {
        color: var(--aurora-text);
        font-size: 0.84rem;
    }


    /* ==========================================================
       GALERIA
       ========================================================== */

    [data-testid="stImage"] {
        overflow: hidden;
        border:
            1px solid
            var(--aurora-border);
        border-radius: 14px;
        background: #FFFFFF;
        box-shadow:
            0 4px 15px
            rgba(55, 42, 31, 0.05);
    }

    [data-testid="stImage"] img {
        border-radius: 13px;
    }

    [data-testid="stImageCaption"] {
        padding: 0.22rem 0.15rem;
        color: var(--aurora-text-soft);
        font-size: 0.72rem;
    }

    .aurora-gallery-title {
        margin: 0.75rem 0 0.45rem;
        color: var(--aurora-green);
        font-size: 0.77rem;
        font-weight: 700;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--aurora-text-soft);
        font-size: 0.69rem;
    }


    /* ==========================================================
       SIDEBAR
       ========================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #29382E 0%,
                #35483A 58%,
                #44372E 100%
            );
        border-right:
            1px solid
            rgba(255, 255, 255, 0.07);
    }

    [data-testid="stSidebar"]
    [data-testid="stSidebarContent"],
    [data-testid="stSidebar"]
    [data-testid="stSidebarUserContent"] {
        padding-top: 0.78rem !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 0.78rem !important;
    }

    [data-testid="stSidebar"] hr {
        margin: 0.62rem 0;
        border-color:
            rgba(255, 255, 255, 0.10);
    }

    [data-testid="stSidebar"]
    .stButton > button {
        min-height: 2.05rem;
        padding-top: 0.28rem;
        padding-bottom: 0.28rem;
        border:
            1px solid
            rgba(255, 255, 255, 0.13);
        background:
            rgba(255, 255, 255, 0.065);
        color: #FFFFFF;
        font-size: 0.70rem;
        box-shadow: none;
    }

    [data-testid="stSidebar"]
    .stButton > button:hover {
        border-color:
            rgba(241, 197, 141, 0.52);
        background:
            rgba(255, 255, 255, 0.115);
        color: #FFFFFF;
    }

    .aurora-sidebar-brand {
        padding: 0;

        /*
        Compensa o espaço superior nativo reservado pelo
        Streamlit na sidebar e alinha a marca ao card principal.
        */
        margin-top: -4.25rem;
    }

    .aurora-sidebar-icon {
        margin-bottom: 0.18rem;
        font-size: 1.52rem;
    }

    .aurora-sidebar-title {
        margin: 0;
        color: #FFFFFF;
        font-family:
            "Ubuntu Mono",
            "Cascadia Mono",
            "SFMono-Regular",
            Consolas,
            "Liberation Mono",
            monospace;
        font-size: 1.16rem;
        font-weight: 500;
        letter-spacing: -0.025em;
    }

    .aurora-sidebar-hotel {
        margin-top: 0.23rem;
        color: #F1C58D;
        font-size: 0.7rem;
        font-weight: 600;
        line-height: 1.35;
    }

    .aurora-sidebar-slogan {
        max-width: 245px;
        margin-top: 0.46rem;
        color:
            rgba(255, 255, 255, 0.65);
        font-size: 0.68rem;
        font-style: italic;
        line-height: 1.43;
    }

    .aurora-sidebar-box {
        margin: 0.32rem 0 0.56rem;
        padding: 0.68rem 0.76rem;
        border:
            1px solid
            rgba(255, 255, 255, 0.085);
        border-radius: 13px;
        background:
            rgba(255, 255, 255, 0.04);
    }

    .aurora-sidebar-box-title {
        margin-bottom: 0.42rem;
        color: #F1C58D;
        font-size: 0.61rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .aurora-sidebar-item {
        margin: 0.3rem 0;
        color:
            rgba(255, 255, 255, 0.80);
        font-size: 0.7rem;
        line-height: 1.35;
    }

    .aurora-sidebar-footnote {
        margin-top: 0.56rem;
        color:
            rgba(255, 255, 255, 0.45);
        font-size: 0.62rem;
        line-height: 1.42;
    }

    .aurora-sidebar-shortcuts {
        margin: 0.2rem 0 0.43rem;
        color: #F1C58D;
        font-size: 0.61rem;
        font-weight: 800;
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }


    /* ==========================================================
       MOBILE
       ========================================================== */

    @media (max-width: 768px) {

        .aurora-sidebar-brand {
            margin-top: 0;
        }

        [data-testid="collapsedControl"] {
            position: fixed !important;
            top: 0.7rem !important;
            left: 0.7rem !important;
            z-index: 999999 !important;
        }

        [data-testid="collapsedControl"] button {
            width: 42px !important;
            min-width: 42px !important;
            height: 42px !important;
            min-height: 42px !important;
            padding: 0 !important;
            border:
                1px solid
                rgba(241, 197, 141, 0.35) !important;
            border-radius: 12px !important;
            background: #29382E !important;
            box-shadow:
                0 5px 16px
                rgba(41, 56, 46, 0.22) !important;
        }

        [data-testid="collapsedControl"] svg,
        [data-testid="collapsedControl"] svg path {
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
            stroke: #FFFFFF !important;
        }

        .block-container {
            padding-top: 0.58rem;
            padding-left: 0.72rem;
            padding-right: 0.72rem;
            padding-bottom: 0.8rem;
        }

        .aurora-hero {
            padding: 0.85rem 0.9rem 0.95rem;
            border-radius: 16px;
        }

        .aurora-hero-grid {
            grid-template-columns: 1fr;
            gap: 0.7rem;
        }

        .aurora-hero-right {
            padding-top: 0.62rem;
            padding-left: 0;
            border-top:
                1px solid
                rgba(255, 255, 255, 0.13);
            border-left: none;
            text-align: left;
        }

        .aurora-description {
            margin-left: 0;
        }

        .aurora-title {
            font-size: 1.72rem;
        }

        .aurora-hotel {
            font-size: 0.84rem;
        }

        .aurora-slogan {
            font-size: 0.82rem;
        }

        .aurora-hero-conversation {
            display: block;
        }

        .aurora-conversation-slogan {
            margin-top: 0.48rem;
            text-align: left;
            font-size: 0.76rem;
        }

        .aurora-welcome {
            padding: 0.66rem 0.74rem;
        }

        [data-testid="stChatMessage"] {
            padding: 0.72rem 0.78rem;
            border-radius: 14px;
        }

        .st-key-aurora-chat-bar,
        .st-key-aurora-chat-bar-inicial {
            bottom: 0.25rem;
            width: 100%;
        }

        .st-key-aurora-chat-bar-inicial {
            margin-top: 1.5rem;
        }
    }

    </style>
    """
)


# ============================================================
# FORMATAÇÃO
# ============================================================

def preparar_markdown(
    texto: str,
) -> str:
    """
    Prepara textos do agente para exibição
    no Markdown do Streamlit.
    """

    texto = unescape(
        texto
    )

    texto = texto.replace(
        "R$",
        r"R\$",
    )

    texto = re.sub(
        r"\s*•\s*",
        "\n- ",
        texto,
    )

    return texto.strip()


# ============================================================
# ESTADO
# ============================================================

def inicializar_estado() -> None:
    """
    Inicializa os dados persistidos
    durante a sessão.
    """

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    if "pergunta_pendente" not in st.session_state:
        st.session_state.pergunta_pendente = None

    if "area_ativa" not in st.session_state:
        st.session_state.area_ativa = "chat"


def limpar_conversa() -> None:
    """
    Limpa exclusivamente o histórico
    do Assistente Virtual.
    """

    st.session_state.mensagens = []
    st.session_state.pergunta_pendente = None


def definir_pergunta_sugerida(
    pergunta: str,
) -> None:
    """
    Armazena uma pergunta de atalho no estado.
    """

    st.session_state.pergunta_pendente = pergunta


def definir_area(
    area: str,
) -> None:
    """
    Alterna entre o Assistente Virtual
    e a Central de Reservas.
    """

    st.session_state.area_ativa = area

    if area == "reservas":
        st.session_state.pergunta_pendente = None


def abrir_central_reservas() -> None:
    """
    Abre a Central de Reservas.

    Se o usuário já estiver na Central e clicar
    novamente no acesso principal, inicia uma
    nova operação.
    """

    ja_estava_na_central = (
        st.session_state.area_ativa
        == "reservas"
    )

    st.session_state.area_ativa = (
        "reservas"
    )

    st.session_state.pergunta_pendente = (
        None
    )

    if ja_estava_na_central:
        resetar_estado_central()


# ============================================================
# GALERIA
# ============================================================

def exibir_imagens(
    imagens: list[dict],
) -> None:
    """
    Exibe imagens relacionadas à pergunta.
    """

    if not imagens:
        return

    imagens_validas = []

    for imagem in imagens:

        caminho = obter_caminho_imagem(
            imagem
        )

        if caminho.exists():

            imagens_validas.append(
                (
                    imagem,
                    caminho,
                )
            )

    if not imagens_validas:
        return

    if len(imagens_validas) == 1:

        imagem, caminho = (
            imagens_validas[0]
        )

        st.html(
            """
            <div class="aurora-gallery-title">
                📷 Imagem relacionada
            </div>
            """
        )

        st.image(
            caminho,
            caption=imagem.get(
                "titulo",
                "",
            ),
            width="stretch",
        )

    else:

        st.html(
            """
            <div class="aurora-gallery-title">
                📷 Galeria relacionada
            </div>
            """
        )

        colunas = st.columns(
            2,
            gap="small",
        )

        for indice, (
            imagem,
            caminho,
        ) in enumerate(
            imagens_validas
        ):

            coluna = colunas[
                indice % 2
            ]

            with coluna:

                st.image(
                    caminho,
                    caption=imagem.get(
                        "titulo",
                        "",
                    ),
                    width="stretch",
                )

    st.caption(
        "Imagens ilustrativas geradas para "
        "demonstração do projeto."
    )


def selecionar_imagens_seguras(
    pergunta: str,
) -> list[dict]:
    """
    Seleciona imagens sem permitir
    interrupção do chat em caso de erro.
    """

    try:

        return selecionar_imagens(
            pergunta,
            limite=6,
        )

    except Exception:

        logger.exception(
            "Erro ao selecionar imagens da galeria."
        )

        return []


def gerar_resposta_visual(
    imagens: list[dict],
) -> str:
    """
    Gera resposta curta para solicitações
    exclusivamente visuais.
    """

    if not imagens:

        return (
            "Não encontrei imagens relacionadas "
            "a essa solicitação."
        )

    if len(imagens) == 1:

        titulo = imagens[0].get(
            "titulo",
            "item solicitado",
        )

        return (
            f"Claro! Aqui está uma imagem "
            f"ilustrativa de **{titulo}**."
        )

    return (
        "Claro! Aqui estão as imagens "
        "ilustrativas solicitadas."
    )


# ============================================================
# INTERAÇÕES SOCIAIS
# ============================================================

def responder_interacao_social(
    pergunta: str,
) -> str | None:
    """
    Responde interações sociais simples
    sem usar RAG ou Groq.
    """

    texto = pergunta.casefold().strip()

    texto = re.sub(
        r"[!?.]+$",
        "",
        texto,
    ).strip()

    agradecimentos = {
        "obrigado",
        "obrigada",
        "muito obrigado",
        "muito obrigada",
        "valeu",
        "valeu mesmo",
        "agradeço",
        "agradeco",
        "brigado",
        "brigada",
    }

    saudacoes = {
        "oi",
        "olá",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite",
        "e aí",
        "e ai",
    }

    despedidas = {
        "tchau",
        "até mais",
        "ate mais",
        "até logo",
        "ate logo",
        "falou",
    }

    if texto in agradecimentos:

        return (
            "Por nada! 😊 Foi um prazer ajudar. "
            "Se pintar outra dúvida sobre a pousada ou sobre "
            "Campos do Jordão, é só me chamar. 🌄"
        )

    if texto in saudacoes:

        return (
            "Oi! 😊 Que bom ter você por aqui. "
            "Posso ajudar com acomodações, valores, experiências "
            "da pousada ou ideias do que fazer em Campos do Jordão. "
            "Por onde quer começar? 🌄"
        )

    if texto in despedidas:

        return (
            "Até mais! 😊 Foi um prazer ajudar. "
            "Espero que sua experiência em Campos do Jordão seja "
            "incrível — e que renda um belo pôr do sol. 🌄"
        )

    return None


# ============================================================
# HISTÓRICO
# ============================================================

def exibir_historico() -> None:
    """
    Exibe as mensagens armazenadas.
    """

    for mensagem in st.session_state.mensagens:

        role = mensagem["role"]

        avatar = (
            "🌄"
            if role == "assistant"
            else "👤"
        )

        with st.chat_message(
            role,
            avatar=avatar,
        ):

            st.markdown(
                preparar_markdown(
                    mensagem["content"]
                )
            )

            if role == "assistant":

                exibir_imagens(
                    mensagem.get(
                        "imagens",
                        [],
                    )
                )


def rolar_para_ultima_mensagem() -> None:
    """
    Move a página automaticamente para a mensagem mais recente
    após cada rerun da conversa.

    Em versões atuais do Streamlit, st.html pode executar
    JavaScript quando explicitamente autorizado. Para versões
    anteriores, usa o componente HTML como compatibilidade.

    O script é estático e não recebe conteúdo do usuário
    ou da LLM.
    """

    if not st.session_state.mensagens:
        return

    script = """
    <script>
    (() => {

        const rolar = () => {

            const documento = (
                window.parent &&
                window.parent.document
            )
                ? window.parent.document
                : document;

            const mensagens =
                documento.querySelectorAll(
                    '[data-testid="stChatMessage"]'
                );

            if (!mensagens.length) {
                return;
            }

            const ultimaMensagem =
                mensagens[
                    mensagens.length - 1
                ];

            ultimaMensagem.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        };

        window.setTimeout(
            rolar,
            120
        );

        window.setTimeout(
            rolar,
            320
        );

    })();
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
            script,
            width="content",
            unsafe_allow_javascript=True,
        )

    else:

        components.html(
            script,
            height=0,
            scrolling=False,
        )


# ============================================================
# ATALHOS DA SIDEBAR
# ============================================================

def exibir_atalhos_sidebar() -> None:
    """
    Exibe atalhos verticais durante
    a conversa.
    """

    st.html(
        """
        <div class="aurora-sidebar-shortcuts">
            Atalhos rápidos
        </div>
        """
    )

    st.button(
        "🛏️ Acomodação para casal",
        width="stretch",
        key="lateral_casal",
        on_click=definir_pergunta_sugerida,
        args=(
            "Qual acomodação é ideal para casal?",
        ),
    )

    st.button(
        "💰 Valores das acomodações",
        width="stretch",
        key="lateral_precos",
        on_click=definir_pergunta_sugerida,
        args=(
            "Quais são os valores das acomodações?",
        ),
    )

    st.button(
        "🌅 Onde ver o pôr do sol?",
        width="stretch",
        key="lateral_por_do_sol",
        on_click=definir_pergunta_sugerida,
        args=(
            "Onde assistir ao pôr do sol?",
        ),
    )

    st.button(
        "❤️ Viagem romântica",
        width="stretch",
        key="lateral_romantica",
        on_click=definir_pergunta_sugerida,
        args=(
            "O que fazer em uma viagem romântica?",
        ),
    )

    st.button(
        "👨‍👩‍👧 Passeios com crianças",
        width="stretch",
        key="lateral_criancas",
        on_click=definir_pergunta_sugerida,
        args=(
            "O que fazer com crianças?",
        ),
    )

    st.button(
        "📷 Fotos dos quartos",
        width="stretch",
        key="lateral_fotos",
        on_click=definir_pergunta_sugerida,
        args=(
            "Tem fotos dos quartos?",
        ),
    )


# ============================================================
# INICIALIZAÇÃO
# ============================================================

inicializar_estado()

tem_conversa = bool(
    st.session_state.mensagens
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # MARCA
    # ========================================================

    st.html(
        """
        <div class="aurora-sidebar-brand">

            <div class="aurora-sidebar-icon">
                🌄
            </div>

            <div class="aurora-sidebar-title">
                Agente Aurora
            </div>

            <div class="aurora-sidebar-hotel">
                Pousada Mirante do Pôr do Sol
            </div>

            <div class="aurora-sidebar-slogan">
                “Onde cada pôr do sol se transforma
                em uma lembrança inesquecível.”
            </div>

        </div>
        """
    )

    st.divider()


    # ========================================================
    # NAVEGAÇÃO PRINCIPAL
    # ========================================================

    st.button(
        "💬 Assistente virtual",
        width="stretch",
        key="abrir_assistente",
        on_click=definir_area,
        args=("chat",),
    )

    st.button(
        "📅 Central de Reservas",
        width="stretch",
        key="abrir_central_reservas",
        on_click=abrir_central_reservas,
    )

    st.divider()


    # ========================================================
    # CONTEÚDO DA SIDEBAR
    # ========================================================

    if (
        st.session_state.area_ativa
        == "reservas"
    ):

        st.html(
            """
            <div class="aurora-sidebar-box">

                <div class="aurora-sidebar-box-title">
                    Central demonstrativa
                </div>

                <div class="aurora-sidebar-item">
                    🔎 Consultar disponibilidade
                </div>

                <div class="aurora-sidebar-item">
                    ✅ Criar reserva fictícia
                </div>

                <div class="aurora-sidebar-item">
                    📄 Consultar por código
                </div>

                <div class="aurora-sidebar-item">
                    ❌ Simular cancelamento
                </div>

            </div>
            """
        )

    elif not tem_conversa:

        st.html(
            """
            <div class="aurora-sidebar-box">

                <div class="aurora-sidebar-box-title">
                    Posso ajudar com
                </div>

                <div class="aurora-sidebar-item">
                    🛏️ Acomodações e suítes
                </div>

                <div class="aurora-sidebar-item">
                    💰 Valores de referência
                </div>

                <div class="aurora-sidebar-item">
                    ☕ Serviços da pousada
                </div>

                <div class="aurora-sidebar-item">
                    🌅 Experiências e lazer
                </div>

                <div class="aurora-sidebar-item">
                    📍 Campos do Jordão
                </div>

                <div class="aurora-sidebar-item">
                    📷 Fotos ilustrativas
                </div>

            </div>
            """
        )

    else:

        exibir_atalhos_sidebar()


    # ========================================================
    # AÇÃO SECUNDÁRIA DA ÁREA ATIVA
    # ========================================================
    #
    # IMPORTANTE:
    #
    # Assistente Virtual:
    #     + Nova conversa
    #     → limpa somente o histórico do chat.
    #
    # Central de Reservas:
    #     + Nova operação
    #     → limpa somente o estado temporário da Central.
    #
    # Os dois fluxos são propositalmente separados.
    # ========================================================

    st.divider()

    if (
        st.session_state.area_ativa
        == "chat"
    ):

        st.button(
            "＋ Nova conversa",
            key="botao_nova_conversa",
            width="stretch",
            on_click=limpar_conversa,
        )

    else:

        st.button(
            "＋ Nova operação",
            key="botao_nova_operacao_central",
            width="stretch",
            on_click=resetar_estado_central,
        )


    # ========================================================
    # RODAPÉ DA SIDEBAR
    # ========================================================

    if (
        st.session_state.area_ativa
        == "reservas"
    ):

        st.html(
            """
            <div class="aurora-sidebar-footnote">
                Central fictícia desenvolvida para
                demonstração acadêmica do projeto.
                Não utilize dados pessoais reais.
            </div>
            """
        )

    else:

        st.html(
            """
            <div class="aurora-sidebar-footnote">
                As informações são fornecidas com base
                no conteúdo oficial da pousada.
            </div>
            """
        )


# ============================================================
# CENTRAL DE RESERVAS
# ============================================================

if (
    st.session_state.area_ativa
    == "reservas"
):

    exibir_central_reservas()

    # Impede a renderização do chat abaixo da Central.
    st.stop()


# ============================================================
# ASSISTENTE CONVERSACIONAL
# ============================================================

if not tem_conversa:

    st.html(
        """
        <section class="aurora-hero">

            <div class="aurora-hero-topline">

                <div class="aurora-hero-eyebrow">
                    Assistente virtual
                </div>

                <div class="aurora-hero-line"></div>

            </div>

            <div class="aurora-hero-grid">

                <div class="aurora-hero-left">

                    <div class="aurora-brand-row">

                        <div class="aurora-brand-icon">
                            🌄
                        </div>

                        <div>

                            <h1 class="aurora-title">
                                Agente Aurora
                            </h1>

                            <div class="aurora-hotel">
                                Pousada Mirante do Pôr do Sol
                            </div>

                        </div>

                    </div>

                </div>

                <div class="aurora-hero-right">

                    <div class="aurora-slogan">
                        “Onde cada pôr do sol se transforma
                        em uma lembrança inesquecível.”
                    </div>

                    <p class="aurora-description">
                        Seu concierge virtual para hospedagem,
                        experiências da pousada e passeios
                        em Campos do Jordão.
                    </p>

                </div>

            </div>

        </section>
        """
    )

else:

    st.html(
        """
        <section class="aurora-hero-conversation">

            <div class="aurora-conversation-brand">

                <div class="aurora-conversation-icon">
                    🌄
                </div>

                <div>

                    <div class="aurora-conversation-title">
                        Agente Aurora
                    </div>

                    <div class="aurora-conversation-hotel">
                        Pousada Mirante do Pôr do Sol
                    </div>

                </div>

            </div>

            <div class="aurora-conversation-slogan">
                “Onde cada pôr do sol se transforma
                em uma lembrança inesquecível.”
            </div>

        </section>
        """
    )


# ============================================================
# TELA INICIAL / HISTÓRICO
# ============================================================

if not tem_conversa:

    st.html(
        """
        <div class="aurora-welcome">

            <div class="aurora-welcome-row">

                <div class="aurora-welcome-avatar">
                    🌄
                </div>

                <div class="aurora-welcome-text">

                    <p>
                        Oi! 👋 Eu sou o
                        <strong>Agente Aurora</strong>,
                        assistente virtual da
                        <strong>
                            Pousada Mirante do Pôr do Sol
                        </strong>. 🌄
                    </p>

                    <p>
                        Estou por aqui para deixar seu planejamento
                        mais fácil: posso ajudar com
                        <strong>
                            acomodações, valores de referência,
                            serviços, experiências da pousada e
                            passeios em Campos do Jordão
                        </strong>.
                    </p>

                    <p>
                        Pode perguntar do seu jeito — eu te ajudo
                        a encontrar a melhor opção para a sua
                        estadia. 😊
                    </p>

                </div>

            </div>

        </div>
        """
    )

    st.html(
        """
        <div class="aurora-section-label">
            Experimente perguntar
        </div>
        """
    )

    coluna_1, coluna_2, coluna_3 = (
        st.columns(
            3,
            gap="small",
        )
    )

    with coluna_1:

        st.button(
            "🛏️ Acomodação para casal",
            width="stretch",
            key="inicio_casal",
            on_click=definir_pergunta_sugerida,
            args=(
                "Qual acomodação é ideal para casal?",
            ),
        )

        st.button(
            "📷 Fotos dos quartos",
            width="stretch",
            key="inicio_fotos",
            on_click=definir_pergunta_sugerida,
            args=(
                "Tem fotos dos quartos?",
            ),
        )

    with coluna_2:

        st.button(
            "💰 Valores das acomodações",
            width="stretch",
            key="inicio_precos",
            on_click=definir_pergunta_sugerida,
            args=(
                "Quais são os valores das acomodações?",
            ),
        )

        st.button(
            "🌅 Onde ver o pôr do sol?",
            width="stretch",
            key="inicio_por_do_sol",
            on_click=definir_pergunta_sugerida,
            args=(
                "Onde assistir ao pôr do sol?",
            ),
        )

    with coluna_3:

        st.button(
            "❤️ Viagem romântica",
            width="stretch",
            key="inicio_romantica",
            on_click=definir_pergunta_sugerida,
            args=(
                "O que fazer em uma viagem romântica?",
            ),
        )

        st.button(
            "👨‍👩‍👧 Passeios com crianças",
            width="stretch",
            key="inicio_criancas",
            on_click=definir_pergunta_sugerida,
            args=(
                "O que fazer com crianças?",
            ),
        )

else:

    exibir_historico()

    rolar_para_ultima_mensagem()


# ============================================================
# BARRA DO CHAT
# ============================================================

chave_barra_chat = (
    "aurora-chat-bar"
    if tem_conversa
    else "aurora-chat-bar-inicial"
)

with st.container(
    key=chave_barra_chat,
):

    pergunta_digitada = st.chat_input(
        "Pergunte sobre sua estadia, a pousada ou Campos do Jordão...",
        key="entrada_chat",
    )


# ============================================================
# PERGUNTA PENDENTE / DIGITADA
# ============================================================

pergunta_sugerida = (
    st.session_state.pergunta_pendente
)

if pergunta_sugerida:

    st.session_state.pergunta_pendente = (
        None
    )


pergunta = (
    pergunta_sugerida
    or pergunta_digitada
)


# ============================================================
# PROCESSAMENTO DA PERGUNTA
# ============================================================

if pergunta:

    st.session_state.mensagens.append(
        {
            "role": "user",
            "content": pergunta,
        }
    )

    with st.chat_message(
        "user",
        avatar="👤",
    ):

        st.markdown(
            preparar_markdown(
                pergunta
            )
        )


    resposta_social = (
        responder_interacao_social(
            pergunta
        )
    )


    if resposta_social:

        imagens = []

    else:

        imagens = (
            selecionar_imagens_seguras(
                pergunta
            )
        )


    with st.chat_message(
        "assistant",
        avatar="🌄",
    ):

        try:

            inicio = perf_counter()

            if resposta_social:

                resposta = (
                    resposta_social
                )

                fontes = []

            elif (
                e_pedido_apenas_visual(
                    pergunta
                )
                and imagens
            ):

                resposta = (
                    gerar_resposta_visual(
                        imagens
                    )
                )

                fontes = []

            else:

                with st.spinner(
                    "Consultando informações da pousada..."
                ):

                    resultado = (
                        gerar_resposta(
                            pergunta
                        )
                    )

                resposta = (
                    resultado[
                        "resposta"
                    ]
                )

                fontes = (
                    resultado.get(
                        "fontes",
                        [],
                    )
                )

            tempo_resposta = (
                perf_counter()
                - inicio
            )

            st.markdown(
                preparar_markdown(
                    resposta
                )
            )

            exibir_imagens(
                imagens
            )

            st.caption(
                f"Resposta gerada em "
                f"{tempo_resposta:.2f} s"
            )

            st.session_state.mensagens.append(
                {
                    "role": "assistant",
                    "content": resposta,
                    "fontes": fontes,
                    "imagens": imagens,
                }
            )

            st.rerun()

        except Exception:

            logger.exception(
                "Erro ao processar pergunta "
                "no Agente Aurora."
            )

            mensagem_erro = (
                "Não foi possível processar sua pergunta "
                "neste momento. Tente novamente em instantes."
            )

            st.error(
                mensagem_erro
            )

            exibir_imagens(
                imagens
            )

            st.session_state.mensagens.append(
                {
                    "role": "assistant",
                    "content": mensagem_erro,
                    "fontes": [],
                    "imagens": imagens,
                }
            )

            st.rerun()