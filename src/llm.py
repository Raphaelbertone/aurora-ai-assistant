import logging
import os
from functools import lru_cache

from groq import RateLimitError
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from src.config import (
    PROVEDOR_LLM,
    MODELO_LINGUAGEM_GROQ,
    MODELO_LINGUAGEM_GROQ_FALLBACK,
    MODELO_LINGUAGEM_OLLAMA,
)


logger = logging.getLogger(__name__)


def criar_modelo_groq(
    modelo: str,
) -> ChatGroq:
    """
    Cria uma instância de modelo hospedado
    na Groq com as configurações do Aurora.
    """

    return ChatGroq(
        model=modelo,
        temperature=0.0,
        reasoning_effort="low",
        timeout=30,
        max_retries=0,
        model_kwargs={
            "max_completion_tokens": 1024,
            "include_reasoning": False,
        },
    )


@lru_cache(maxsize=1)
def obter_modelo_linguagem():
    """
    Retorna o modelo de linguagem principal
    configurado para o Agente Aurora.
    """

    if PROVEDOR_LLM == "groq":
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError(
                "A variável GROQ_API_KEY não foi configurada."
            )

        return criar_modelo_groq(
            MODELO_LINGUAGEM_GROQ
        )

    if PROVEDOR_LLM == "ollama":
        return ChatOllama(
            model=MODELO_LINGUAGEM_OLLAMA,
            temperature=0.1,
            reasoning=False,
            num_predict=256,
            keep_alive="10m",
        )

    raise ValueError(
        f"Provedor de linguagem não suportado: "
        f"{PROVEDOR_LLM}"
    )


@lru_cache(maxsize=1)
def obter_modelo_linguagem_fallback():
    """
    Retorna o modelo alternativo da Groq
    utilizado quando o modelo principal
    atingir seu limite de requisições ou tokens.
    """

    if PROVEDOR_LLM != "groq":
        return None

    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError(
            "A variável GROQ_API_KEY não foi configurada."
        )

    return criar_modelo_groq(
        MODELO_LINGUAGEM_GROQ_FALLBACK
    )


def invocar_modelo_linguagem(
    mensagens,
):
    """
    Invoca o modelo principal e utiliza o
    modelo alternativo da Groq caso o principal
    atinja um limite de uso.
    """

    modelo_principal = (
        obter_modelo_linguagem()
    )

    try:
        return modelo_principal.invoke(
            mensagens
        )

    except RateLimitError:
        if PROVEDOR_LLM != "groq":
            raise

        logger.warning(
            "Limite do modelo principal %s atingido. "
            "Tentando modelo fallback %s.",
            MODELO_LINGUAGEM_GROQ,
            MODELO_LINGUAGEM_GROQ_FALLBACK,
        )

        modelo_fallback = (
            obter_modelo_linguagem_fallback()
        )

        return modelo_fallback.invoke(
            mensagens
        )