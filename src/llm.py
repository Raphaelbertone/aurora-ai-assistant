import os

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from functools import lru_cache

from src.config import (
    PROVEDOR_LLM,
    MODELO_LINGUAGEM_GROQ,
    MODELO_LINGUAGEM_OLLAMA,
)


@lru_cache(maxsize=1)
def obter_modelo_linguagem():
    """
    Cria e retorna o modelo de linguagem utilizado pelo Agente Aurora.

    O provedor é definido pela variável PROVEDOR_LLM.

    Provedores suportados:
    - groq: inferência em nuvem
    - ollama: inferência local
    """

    if PROVEDOR_LLM == "groq":

        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError(
                "A variável GROQ_API_KEY não foi configurada."
            )

        return ChatGroq(
            model=MODELO_LINGUAGEM_GROQ,
            temperature=0.1,
            max_tokens=256,
            timeout=30,
            max_retries=2,
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
        f"Provedor de LLM não suportado: {PROVEDOR_LLM}. "
        "Utilize 'groq' ou 'ollama'."
    )