# Agente Aurora

## Recepcionista Virtual Inteligente

Projeto de conclusão da Formação Agentes de Inteligência Artificial da Alura.

O Agente Aurora é um recepcionista virtual inteligente desenvolvido para responder perguntas sobre uma pousada utilizando uma arquitetura baseada em RAG (Retrieval-Augmented Generation).

A aplicação utiliza uma Base Oficial de Conhecimento composta por documentos institucionais da pousada e utiliza recuperação semântica para fornecer contexto ao modelo de linguagem antes da geração das respostas.

---

## Status do projeto

🚧 Em desenvolvimento

O projeto está sendo desenvolvido de forma incremental, seguindo uma arquitetura modular e utilizando os notebooks do Google Colab fornecidos como referência para a implementação.

---

## Objetivo

Desenvolver um agente virtual capaz de atuar como recepcionista digital, oferecendo informações sobre:

- acomodações;
- preços;
- benefícios;
- serviços;
- políticas da pousada;
- reservas;
- check-in e check-out;
- cancelamentos;
- passeios;
- perguntas frequentes.

A aplicação deverá utilizar a Base Oficial de Conhecimento como principal fonte de informação para suas respostas.

---

## Arquitetura

A arquitetura oficial do Agente Aurora utiliza:

- Python;
- LangChain;
- Ollama;
- Ollama Embeddings;
- FAISS;
- Streamlit;
- Oracle Cloud Infrastructure (OCI).

Fluxo principal:

Usuário

↓

Streamlit

↓

Agente Aurora

↓

LangChain

↓

Busca semântica no FAISS

↓

Recuperação dos trechos relevantes

↓

Ollama

↓

Resposta ao usuário

---

## Pipeline RAG

A construção da Base de Conhecimento seguirá o fluxo:

PDFs

↓

Leitura dos documentos

↓

Fragmentação dos textos

↓

Embeddings

↓

FAISS

↓

Índice vetorial

Durante o atendimento:

Pergunta do usuário

↓

Busca semântica

↓

Recuperação dos melhores trechos

↓

Contexto enviado ao modelo

↓

Resposta do Agente Aurora

---

## Tecnologias

| Tecnologia | Utilização |
|---|---|
| Python | Linguagem principal |
| Google Colab | Prototipação e referência |
| LangChain | Orquestração do pipeline |
| Ollama | Modelo de linguagem local |
| Ollama Embeddings | Geração dos embeddings |
| FAISS | Índice vetorial |
| Streamlit | Interface Web |
| OCI | Ambiente de implantação |

---

## Estrutura do projeto

```text
aurora-ai-assistant/

├── app.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
│
├── documentos/
├── embeddings/
├── src/
├── tests/
├── docs/
├── imagens/
└── capturas_tela/