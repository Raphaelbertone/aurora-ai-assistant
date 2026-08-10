from html import unescape
import logging
import re
from time import perf_counter



import streamlit as st


from src.gallery import (
    e_pedido_apenas_visual,
    obter_caminho_imagem,
    selecionar_imagens,
)

from src.rag import gerar_resposta

logger = logging.getLogger(__name__)


def preparar_markdown(texto: str) -> str:
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

    # Converte marcadores inline do modelo
    # em uma lista Markdown vertical.
    texto = re.sub(
        r"\s*•\s*",
        "\n- ",
        texto,
    )

    return texto.strip()


st.set_page_config(
    page_title="Agente Aurora",
    page_icon="🌄",
    layout="centered",
)


def mensagem_inicial() -> dict:
    """
    Retorna a mensagem inicial exibida
    ao começar uma nova conversa.
    """

    return {
        "role": "assistant",
        "content": (
            "Oi! 👋 Eu sou o **Agente Aurora**, assistente virtual da "
            "**Pousada Mirante do Pôr do Sol**. 🌄\n\n"
            "Estou por aqui para deixar seu planejamento mais fácil: "
            "posso ajudar com **acomodações, valores de referência, "
            "serviços, experiências da pousada e passeios em "
            "Campos do Jordão**.\n\n"
            "Pode perguntar do seu jeito — eu te ajudo a encontrar "
            "a melhor opção para a sua estadia. 😊"
        ),
        "fontes": [],
        "imagens": [],
    }



def inicializar_estado() -> None:
    """
    Inicializa as informações persistidas durante
    a sessão atual da interface.
    """

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            mensagem_inicial()
        ]


def exibir_fontes(
    fontes: list[dict[str, object]],
) -> None:
    """
    Exibe as fontes consultadas de forma opcional,
    sem poluir a resposta principal.
    """

    if not fontes:
        return

    with st.expander(
        "📚 Ver fontes consultadas",
        expanded=False,
    ):
        for fonte in fontes:
            volume = fonte.get(
                "volume",
                "Não informado",
            )

            pagina = fonte.get(
                "pagina",
                "Não informada",
            )

            st.markdown(
                f"- **{volume}** — página {pagina}"
            )


def exibir_imagens(
    imagens: list[dict],
) -> None:
    """
    Exibe imagens relacionadas à pergunta
    feita pelo usuário.
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
        imagem, caminho = imagens_validas[0]

        st.markdown(
            "**📷 Imagem relacionada**"
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
        st.markdown(
            "**📷 Galeria relacionada**"
        )

        colunas = st.columns(
            2,
            gap="small",
        )

        for indice, (
            imagem,
            caminho,
        ) in enumerate(imagens_validas):
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
    Seleciona imagens sem permitir que uma falha
    da galeria interrompa a resposta textual.
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
    Gera uma resposta curta para solicitações
    que pedem exclusivamente imagens.
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



def exibir_historico() -> None:
    """
    Exibe todas as mensagens armazenadas
    durante a sessão atual.
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


def limpar_conversa() -> None:
    """
    Remove o histórico da conversa atual.
    """

    st.session_state.mensagens = [
        mensagem_inicial()
    ]


inicializar_estado()


with st.sidebar:
    st.title(
        "🌄 Agente Aurora"
    )

    st.caption(
        "Assistente inteligente da "
        "Pousada Mirante do Pôr do Sol"
    )

    st.divider()

    st.markdown(
        """
        **Você pode perguntar sobre:**

        - acomodações;
        - serviços da pousada;
        - check-in e check-out;
        - políticas de hospedagem;
        - estrutura e lazer;
        - turismo em Campos do Jordão.
        """
    )

    st.divider()

    if st.button(
        "🗑️ Nova conversa",
        width="stretch",
    ):
        limpar_conversa()
        st.rerun()

    st.caption(
        "As respostas são geradas com base "
        "na Base Oficial de Conhecimento."
    )


st.title(
    "🌄 Agente Aurora"
)

st.markdown(
    """
    Tire suas dúvidas sobre a **Pousada Mirante do Pôr do Sol**
    e descubra informações úteis para sua estadia em
    **Campos do Jordão**.
    """
)

st.divider()


def responder_interacao_social(
        pergunta: str,
) -> str | None:
    """
        Responde interações sociais simples sem
        consultar o RAG ou o provedor de linguagem.
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


exibir_historico()


pergunta = st.chat_input(
    "Digite sua pergunta sobre a pousada ou Campos do Jordão..."
)


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
            pergunta
        )

    # Verifica primeiro se é uma interação social simples.
    resposta_social = responder_interacao_social(
        pergunta
    )

    # Interações sociais não precisam consultar
    # nem a galeria nem o RAG.
    if resposta_social:
        imagens = []
    else:
        imagens = selecionar_imagens_seguras(
            pergunta
        )

    with st.chat_message(
        "assistant",
        avatar="🌄",
    ):
        try:
            inicio = perf_counter()

            # Interações sociais simples são respondidas
            # localmente, sem consultar RAG ou Groq.
            if resposta_social:
                resposta = resposta_social
                fontes = []

            # Pedidos exclusivamente visuais também
            # podem ser respondidos sem consultar o RAG.
            elif (
                e_pedido_apenas_visual(pergunta)
                and imagens
            ):
                resposta = gerar_resposta_visual(
                    imagens
                )

                fontes = []

            # Perguntas informacionais utilizam
            # o fluxo RAG completo.
            else:
                with st.spinner(
                    "Consultando a Base Oficial "
                    "de Conhecimento..."
                ):
                    resultado = gerar_resposta(
                        pergunta
                    )

                resposta = resultado[
                    "resposta"
                ]

                fontes = resultado.get(
                    "fontes",
                    [],
                )

            tempo_resposta = (
                perf_counter() - inicio
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

        except Exception:
            logger.exception(
                "Erro ao processar pergunta no Agente Aurora."
            )

            mensagem_erro = (
                "Não foi possível processar sua pergunta "
                "neste momento. Tente novamente em instantes."
            )

            st.error(
                mensagem_erro
            )

            # Mesmo que o provedor de linguagem falhe,
            # uma imagem já localizada continua disponível.
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

