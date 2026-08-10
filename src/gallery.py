import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_CATALOGO = RAIZ_PROJETO / "data" / "galeria_imagens.json"

TERMOS_VISUAIS = (
    "foto",
    "fotos",
    "imagem",
    "imagens",
    "galeria",
    "mostrar",
    "mostra",
    "mostre",
    "quero ver",
    "ver foto",
    "ver fotos",
    "visualizar",
    "como e",
)

TERMOS_OPERACIONAIS = (
    "quanto custa",
    "preco",
    "valor",
    "tarifa",
    "diaria",
    "check-in",
    "check in",
    "check-out",
    "check out",
    "cancelamento",
    "cancelar",
    "horario",
    "que horas",
    "abre",
    "fecha",
    "disponibilidade",
)


def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparação semântica simples por termos."""

    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    texto = re.sub(r"[^\w\s-]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


@lru_cache(maxsize=1)
def carregar_galeria() -> list[dict]:
    """Carrega o catálogo de imagens da aplicação."""

    if not CAMINHO_CATALOGO.exists():
        raise FileNotFoundError(
            f"Catálogo de imagens não encontrado: {CAMINHO_CATALOGO}"
        )

    with CAMINHO_CATALOGO.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    imagens = dados.get("imagens", [])

    if not isinstance(imagens, list):
        raise ValueError(
            "O campo 'imagens' de galeria_imagens.json deve ser uma lista."
        )

    return imagens


def validar_galeria() -> list[str]:
    """Valida estrutura do catálogo e existência dos arquivos."""

    erros = []
    identificadores = set()

    for imagem in carregar_galeria():
        identificador = imagem.get("id")
        titulo = imagem.get("titulo")
        arquivo = imagem.get("arquivo")

        if not identificador:
            erros.append("Existe uma imagem sem campo 'id'.")
            continue

        if identificador in identificadores:
            erros.append(f"ID duplicado: {identificador}")

        identificadores.add(identificador)

        if not titulo:
            erros.append(f"Imagem '{identificador}' sem título.")

        if not arquivo:
            erros.append(f"Imagem '{identificador}' sem caminho de arquivo.")
            continue

        caminho = RAIZ_PROJETO / arquivo

        if not caminho.exists():
            erros.append(
                f"Arquivo da imagem '{identificador}' não encontrado: {caminho}"
            )

    return erros


def _contem_algum(texto: str, termos: tuple[str, ...] | list[str]) -> bool:
    texto_normalizado = normalizar_texto(texto)

    return any(
        normalizar_texto(termo) in texto_normalizado
        for termo in termos
    )


def _pontuar_imagem(
    imagem: dict,
    pergunta_normalizada: str,
    pedido_visual: bool,
) -> int:
    pontuacao = 0

    if pedido_visual:
        termos = imagem.get("termos", [])
        peso = 10
    else:
        termos = imagem.get("gatilhos_automaticos", [])
        peso = 15

    for termo in termos:
        termo_normalizado = normalizar_texto(termo)

        if termo_normalizado and termo_normalizado in pergunta_normalizada:
            numero_palavras = len(termo_normalizado.split())
            pontuacao += peso + numero_palavras

    return pontuacao


def _selecionar_grupo_visual(
    pergunta_normalizada: str,
    imagens: list[dict],
) -> list[dict]:
    """Seleciona coleções para pedidos visuais amplos."""

    termos_acomodacoes = (
        "quartos",
        "acomodacoes",
        "acomodacao",
        "suites",
    )

    if any(
        termo in pergunta_normalizada
        for termo in termos_acomodacoes
    ):
        grupo = [
            imagem
            for imagem in imagens
            if imagem.get("categoria") == "acomodacao"
        ]

        return sorted(
            grupo,
            key=lambda imagem: imagem.get(
                "ordem_galeria",
                99,
            ),
        )

    termos_pousada = (
        "pousada",
        "hotel",
        "propriedade",
    )

    if any(
        termo in pergunta_normalizada
        for termo in termos_pousada
    ):
        ids = {
            "fachada",
            "jardins_area_externa",
            "deck_por_do_sol",
        }

        grupo = [
            imagem
            for imagem in imagens
            if imagem.get("id") in ids
        ]

        return sorted(
            grupo,
            key=lambda imagem: imagem.get(
                "ordem_galeria",
                99,
            ),
        )

    return []


def _e_pedido_galeria_ampla(pergunta_normalizada: str) -> bool:
    """Identifica pedidos explícitos por uma coleção de imagens."""

    padroes = (
        "fotos dos quartos",
        "fotos das acomodacoes",
        "imagens dos quartos",
        "imagens das acomodacoes",
        "galeria dos quartos",
        "galeria das acomodacoes",
        "fotos da pousada",
        "imagens da pousada",
        "galeria da pousada",
    )

    return any(
        padrao in pergunta_normalizada
        for padrao in padroes
    )


def selecionar_imagens(
    pergunta: str,
    limite: int = 2,
) -> list[dict]:
    """
    Seleciona imagens relacionadas à intenção do usuário.

    Pedidos explicitamente visuais podem usar termos amplos.
    Consultas operacionais não exibem mídia automaticamente.
    """

    if not pergunta or not pergunta.strip():
        return []

    imagens = carregar_galeria()
    pergunta_normalizada = normalizar_texto(pergunta)

    pedido_visual = _contem_algum(
        pergunta_normalizada,
        TERMOS_VISUAIS,
    )

    pedido_galeria_ampla = _e_pedido_galeria_ampla(
        pergunta_normalizada
    )

    grupo_visual = []

    if pedido_visual:
        grupo_visual = _selecionar_grupo_visual(
            pergunta_normalizada,
            imagens,
        )

    intencao_operacional = _contem_algum(
        pergunta_normalizada,
        TERMOS_OPERACIONAIS,
    )

    # Não mostrar mídia automaticamente em perguntas operacionais.
    # Um pedido explícito de foto continua tendo prioridade.
    if intencao_operacional and not pedido_visual:
        return []

    # Galerias amplas possuem sua própria ordem de apresentação.
    if pedido_visual and pedido_galeria_ampla and grupo_visual:
        return grupo_visual[:limite]

    resultados = []

    for imagem in imagens:
        pontuacao = _pontuar_imagem(
            imagem,
            pergunta_normalizada,
            pedido_visual,
        )

        if pontuacao > 0:
            resultados.append(
                {
                    **imagem,
                    "_pontuacao": pontuacao,
                }
            )

    resultados.sort(
        key=lambda imagem: (
            -imagem.get("_pontuacao", 0),
            imagem.get("prioridade", 99),
        )
    )

    # Evita resultados secundários causados apenas por termos genéricos.
    # Exemplo:
    # "foto da Suíte Master Pôr do Sol"
    # deve priorizar a suíte, sem exibir também o Deck.
    if resultados:
        maior_pontuacao = resultados[0]["_pontuacao"]

        resultados = [
            imagem
            for imagem in resultados
            if imagem["_pontuacao"] >= maior_pontuacao - 1
        ]

    selecionadas = []

    for imagem in resultados[:limite]:
        imagem_limpa = {
            chave: valor
            for chave, valor in imagem.items()
            if chave != "_pontuacao"
        }

        selecionadas.append(imagem_limpa)

    return selecionadas


def obter_caminho_imagem(imagem: dict) -> Path:
    """Retorna o caminho absoluto de uma imagem do catálogo."""

    return RAIZ_PROJETO / imagem["arquivo"]