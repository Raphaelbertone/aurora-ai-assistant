# 🌄 Agente Aurora

> **Assistente inteligente para atendimento hoteleiro com RAG, busca vetorial, contexto conversacional, galeria contextual e Central de Reservas.**



O **Agente Aurora** é uma aplicação de Inteligência Artificial desenvolvida para simular o atendimento digital de uma pousada fictícia.

O projeto combina uma **Base Oficial de Conhecimento em PDF**, arquitetura **RAG (Retrieval-Augmented Generation)**, embeddings locais com **BGE-M3**, busca vetorial com **FAISS**, modelos de linguagem via **Groq**, uma **galeria contextual de imagens** e uma **Central de Reservas demonstrativa com PostgreSQL**.

A aplicação foi desenvolvida para o **Challenge Agente Alura** e está publicada em ambiente de nuvem utilizando a **Oracle Cloud Infrastructure (OCI)**.

---

## 🌐 Aplicação publicada

### Acesse o Agente Aurora

**[http://150.230.82.222:8501](http://150.230.82.222:8501)**

> A aplicação está hospedada em uma máquina virtual na Oracle Cloud Infrastructure.

---

## 📸 Demonstração

### Tela principal

<p align="center">
  <img src="docs/imagens/app_aurora_tela1.png"
       alt="Tela principal do Agente Aurora"
       width="900">
</p>

### Assistente e galeria contextual

<p align="center">
  <img src="docs/imagens/app_aurora_tela3.png"
       alt="Assistente e galeria contextual do Agente Aurora"
       width="900">
</p>

### Central de Reservas

<p align="center">
  <img src="docs/imagens/app_aurora_tela2.png"
       alt="Central de Reservas do Agente Aurora"
       width="900">
</p>


> As imagens exibidas pela aplicação são ilustrativas e foram geradas exclusivamente para demonstração do projeto.

---

# 🎯 Objetivo do projeto

O objetivo do Agente Aurora é demonstrar como técnicas modernas de Inteligência Artificial podem ser aplicadas em um cenário de atendimento hoteleiro.

O sistema foi projetado para responder perguntas utilizando informações recuperadas de uma **Base Oficial de Conhecimento**, evitando que o modelo dependa exclusivamente de conhecimento genérico.

Além do atendimento informacional, a aplicação também demonstra funcionalidades que poderiam fazer parte de uma solução real de atendimento digital:

- consulta de informações da pousada;
- informações sobre acomodações;
- tarifas de referência;
- interpretação de perguntas contextuais;
- consulta visual por meio de galeria;
- consulta de disponibilidade;
- criação de reservas fictícias;
- consulta de reservas;
- cancelamento;
- recuperação de código de reserva.

---

# ✨ Funcionalidades

## 🧠 Assistente baseado em RAG

O Aurora utiliza a arquitetura **Retrieval-Augmented Generation (RAG)**.

Em vez de enviar diretamente a pergunta do usuário para um modelo de linguagem, o sistema primeiro pesquisa os trechos mais relevantes da Base Oficial de Conhecimento.

Fluxo simplificado:

```text
Pergunta do usuário
        ↓
Normalização e análise
        ↓
Embedding da pergunta
        ↓
Busca semântica no FAISS
        ↓
Recuperação dos trechos relevantes
        ↓
Construção do contexto
        ↓
LLM
        ↓
Resposta fundamentada
```

Esse processo permite que as respostas permaneçam relacionadas ao conteúdo disponível nos documentos utilizados pelo projeto.

---

## 📚 Base Oficial de Conhecimento

A Base Oficial de Conhecimento utilizada pelo Agente Aurora é composta por quatro documentos:

```text
documentos/
├── VOLUME 1.pdf
├── VOLUME 2.pdf
├── VOLUME 3.pdf
└── VOLUME 4.pdf
```

Na versão atualmente utilizada em produção:

```text
PDFs processados:       4
Páginas com conteúdo:   136
Fragmentos gerados:     235
```

Os documentos são carregados, fragmentados e posteriormente transformados em representações vetoriais.


### 📘 Volume 5 — Documentação complementar

O projeto também possui um quinto documento:

```text
docs/VOLUME 5.pdf
```

O **Volume 5** reúne documentação complementar relacionada ao desenvolvimento e à estrutura técnica do Agente Aurora.

Diferentemente dos Volumes 1 a 4, o Volume 5 **não faz parte da Base Oficial de Conhecimento consultada pelo agente**. Por esse motivo, ele não é processado pelo pipeline de embeddings e não integra o índice vetorial FAISS.

A separação dos documentos fica da seguinte forma:

| Documento | Finalidade | Utilizado pelo RAG |
|---|---|:---:|
| Volume 1 | Base Oficial de Conhecimento | ✅ |
| Volume 2 | Base Oficial de Conhecimento | ✅ |
| Volume 3 | Base Oficial de Conhecimento | ✅ |
| Volume 4 | Base Oficial de Conhecimento | ✅ |
| Volume 5 | Documentação técnica e complementar | ❌ |

Essa separação mantém o corpus utilizado para responder às perguntas do usuário restrito aos documentos definidos como Base Oficial de Conhecimento, enquanto o Volume 5 permanece disponível no repositório como documentação complementar do projeto.
---

## 🔎 Busca vetorial

A busca semântica utiliza:

- **BGE-M3**
- **Ollama**
- **FAISS**
- `chunk_size = 1000`
- `chunk_overlap = 100`
- `k = 6`

O modelo utilizado para embeddings é:

```text
bge-m3:567m
```

Cada embedding possui:

```text
1024 dimensões
```

O índice vetorial é persistido em:

```text
data/faiss/
```

Dessa forma, ele não precisa ser reconstruído sempre que a aplicação ou o container for reiniciado.

---

## 🛡️ Fallback para informações inexistentes

Quando uma informação não é encontrada adequadamente na Base Oficial de Conhecimento, o agente possui um fallback controlado.

Resposta padrão:

> **Não encontrei essa informação na Base Oficial de Conhecimento.**

Exemplo:

```text
Usuário:
Tem cassino?

Aurora:
Não encontrei essa informação na Base Oficial de Conhecimento.
```

Isso reduz a possibilidade de respostas inventadas para informações que deveriam estar restritas à documentação do projeto.

---

# 💬 Contexto conversacional

O Agente Aurora possui uma camada determinística de **contexto conversacional curto**.

Ela permite compreender perguntas dependentes da interação anterior sem utilizar todo o histórico indiscriminadamente.

Exemplo:

```text
Usuário:
Tem restaurante e piscina?

Aurora:
Sim. A pousada possui restaurante próprio e oferece piscina aquecida.

Usuário:
Tem fotos?

Aurora:
[exibe imagens da piscina e do restaurante]
```

Outro exemplo:

```text
Usuário:
Me fale sobre a Suíte Premium.

Usuário:
Tem fotos?

Aurora:
[exibe a imagem relacionada à Suíte Premium]
```

A estratégia mantém apenas o contexto necessário para interpretar determinadas continuidades de conversa.

---

# 🖼️ Galeria contextual

O Agente Aurora possui uma galeria de imagens independente da base vetorial.

A galeria utiliza:

```text
data/galeria_imagens.json
```

para relacionar:

- identificadores;
- títulos;
- categorias;
- caminhos das imagens;
- termos associados;
- gatilhos contextuais;
- ordem de exibição.

As imagens ficam armazenadas em:

```text
assets/imagens/
```

---

## Exemplos de pedidos visuais

O usuário pode realizar pedidos como:

```text
Tem fotos dos quartos?
```

```text
Tem fotos das acomodações?
```

```text
Tem fotos da Suíte Premium?
```

```text
Fotos do chalé
```

```text
Fotos da pousada
```

O sistema também interpreta pedidos contextuais:

```text
Usuário:
Tem restaurante e piscina?

Usuário:
Tem fotos?
```

Nesse cenário, a galeria apresenta imagens relacionadas aos dois assuntos mencionados anteriormente.

---

## Conteúdo visual disponível

A galeria demonstrativa possui imagens de:

### Acomodações

- Quarto Standard Casal;
- Quarto Standard Família;
- Suíte Superior;
- Suíte Premium;
- Suíte Master Pôr do Sol;
- Chalé Família Luxo.

### Estrutura e experiências

- Piscina Aquecida;
- Restaurante Mirante;
- Deck do Pôr do Sol;
- Jardins e Área Externa;
- fachada da pousada.

> Todas as imagens utilizadas são ilustrativas e geradas para demonstração do projeto.

---

# 🏨 Central de Reservas

O projeto também possui uma **Central de Reservas demonstrativa** integrada à aplicação.

Ela utiliza um banco de dados PostgreSQL separado da base RAG.

A Central de Reservas permite:

- consultar disponibilidade;
- criar reserva fictícia;
- consultar reserva existente;
- cancelar reserva;
- recuperar código de reserva.

---

## 🔍 Consulta de disponibilidade

O sistema verifica as unidades físicas disponíveis para determinado intervalo de datas.

Cada categoria possui unidades individuais cadastradas.

Exemplo:

```text
Quarto Standard Casal
├── STD-CASAL-01
├── STD-CASAL-02
├── STD-CASAL-03
├── ...
└── STD-CASAL-08
```

Dessa forma, o sistema não controla apenas uma quantidade abstrata de quartos.

Ele verifica a disponibilidade de cada unidade física.

---

# 🛏️ Catálogo demonstrativo

| Categoria | Unidades | Capacidade | Tarifa de referência |
|---|---:|---:|---:|
| Quarto Standard Casal | 8 | 2 pessoas | R$ 420,00 |
| Quarto Standard Família | 6 | 4 pessoas | R$ 560,00 |
| Suíte Superior | 6 | 2 pessoas | R$ 690,00 |
| Suíte Premium | 4 | 2 pessoas | R$ 890,00 |
| Suíte Master Pôr do Sol | 4 | 2 pessoas | R$ 1.250,00 |
| Chalé Família Luxo | 2 | 5 pessoas | R$ 1.450,00 |

Total demonstrativo:

```text
30 unidades de acomodação
```

> As tarifas apresentadas são valores fictícios de referência utilizados exclusivamente para demonstração.

---

# 🧮 Regra de conflito de reservas

Uma unidade é considerada ocupada quando existe sobreposição entre o período solicitado e uma reserva já confirmada.

A condição utilizada é:

```text
reserva_existente.checkin < novo_checkout

AND

reserva_existente.checkout > novo_checkin
```

Isso permite reservas adjacentes.

Exemplo:

```text
Reserva A
10/09 → 13/09

Reserva B
13/09 → 15/09
```

Esse cenário é permitido porque o checkout da primeira reserva coincide com o check-in da segunda.

---

# 📝 Criação de reserva

Quando existe disponibilidade, a Central de Reservas:

1. seleciona uma unidade disponível;
2. registra as informações da reserva;
3. salva a tarifa utilizada naquele momento;
4. calcula o valor total;
5. gera um código de reserva.

Formato:

```text
AUR-AAAAMMDD-XXXXXXXX
```

Exemplo:

```text
AUR-20260816-7EC30D9E
```

> Os códigos e reservas são fictícios e possuem finalidade exclusivamente demonstrativa.

---

# 💰 Snapshot da tarifa

A reserva armazena uma cópia da tarifa utilizada no momento de sua criação.

Exemplo:

```text
Tarifa atual da categoria:
R$ 420,00

Reserva realizada:
R$ 420,00

Tarifa posteriormente alterada:
R$ 450,00
```

A reserva anterior continua registrada com:

```text
R$ 420,00
```

Isso impede alterações retroativas no valor de reservas já realizadas.

---

# ❌ Cancelamento

Reservas podem possuir os seguintes estados principais:

```text
CONFIRMADA
CANCELADA
```

Quando uma reserva é cancelada, a unidade correspondente volta a ficar disponível para novas reservas naquele período.

---

# 🔎 Recuperação de reserva

O sistema possui rotinas demonstrativas para recuperação de código e consulta de reserva.

Existem testes específicos para:

- recuperação de reserva;
- recuperação flexível;
- cenários negativos.

---

# 🤖 Modelos utilizados

## Embeddings

Modelo:

```text
bge-m3:567m
```

Execução:

```text
Ollama
```

Dimensão:

```text
1024
```

---

## Modelo principal de linguagem

O provedor principal utilizado em produção é:

```text
Groq
```

Modelo:

```text
openai/gpt-oss-120b
```

---

## Fallback de LLM

Em caso de limite de requisições do provedor principal, existe fallback para:

```text
openai/gpt-oss-20b
```

O fallback é utilizado especificamente para tratamento de limite de requisições.

---

## LLM local opcional

O projeto também possui suporte manual a:

```text
qwen3:4b
```

via Ollama.

O modelo local pode ser selecionado por configuração, principalmente para desenvolvimento.

Ele não é utilizado automaticamente como fallback da Groq.

---

# 🏗️ Arquitetura da aplicação

```mermaid
flowchart TD

    U[Usuário] --> UI[Interface Streamlit]

    UI --> D{Análise da solicitação}

    D -->|Pergunta informacional| R[RAG]
    D -->|Pedido visual| G[Galeria]
    D -->|Operação de reserva| C[Central de Reservas]

    R --> EMB[BGE-M3]
    EMB --> O[Ollama]

    R --> F[FAISS]
    F --> L[Groq / GPT-OSS]
    L --> UI

    G --> IMG[Imagens locais]
    IMG --> UI

    C --> DB[(PostgreSQL)]
    DB --> UI
```

---

# 🔄 Fluxo RAG

```mermaid
flowchart LR

    A[Documentos PDF] --> B[Carregamento]
    B --> C[Fragmentação]
    C --> D[BGE-M3]
    D --> E[Embeddings]
    E --> F[FAISS]

    G[Pergunta] --> H[Embedding da pergunta]
    H --> F

    F --> I[Trechos relevantes]
    I --> J[Prompt contextual]
    J --> K[Groq]
    K --> L[Resposta]
```

---

# ☁️ Arquitetura de produção

A versão pública do Agente Aurora está hospedada na **Oracle Cloud Infrastructure**.

Arquitetura:

```text
Internet
   │
   │ TCP 8501
   ▼
Oracle Cloud Infrastructure
   │
   ▼
VM Ubuntu 22.04
   │
   ├── Docker Engine
   │      │
   │      └── Container Agente Aurora
   │              │
   │              └── Streamlit
   │
   ├── PostgreSQL 18
   │      │
   │      └── Central de Reservas
   │
   └── Ollama
          │
          └── BGE-M3
```

---

# 🔐 Rede em produção

As seguintes portas são utilizadas:

| Porta | Serviço | Exposição |
|---:|---|---|
| 22 | SSH | Pública |
| 8501 | Streamlit / Aurora | Pública |
| 5432 | PostgreSQL | Apenas local |
| 11434 | Ollama | Apenas local |

PostgreSQL:

```text
127.0.0.1:5432
```

Ollama:

```text
127.0.0.1:11434
```

Esses serviços não são expostos diretamente à internet.

---

# 🖥️ Servidor de produção

Ambiente utilizado:

```text
Oracle Cloud Infrastructure
Ubuntu 22.04 LTS
Arquitetura x86_64
Docker Engine
PostgreSQL 18
Ollama
```

A aplicação é executada dentro de container Docker.

PostgreSQL e Ollama são executados diretamente no host.

---

# 🐳 Docker

O projeto possui um `Dockerfile` para criação de uma imagem reproduzível da aplicação.

Arquivo:

```text
Dockerfile
```

Ambiente base:

```text
Python 3.13
linux/amd64
```

---

## Construção da imagem

```bash
docker build \
  --progress=plain \
  -t aurora-ai:prod \
  .
```

---

## Execução utilizada em produção

```bash
docker run -d \
  --name aurora-ai \
  --restart unless-stopped \
  --network host \
  --env-file .env \
  --mount type=bind,source="$PWD/data/faiss",target=/app/data/faiss \
  aurora-ai:prod
```

---

## Persistência do FAISS

O diretório:

```text
data/faiss
```

é montado dentro do container como:

```text
/app/data/faiss
```

Isso permite preservar o índice mesmo que o container seja removido ou recriado.

---

# 🔄 Inicialização automática

O container utiliza:

```text
deploy/start.sh
```

como script de inicialização.

Ele executa automaticamente:

```text
1. Validação das configurações
2. Verificação do Ollama
3. Verificação do PostgreSQL
4. Inicialização das tabelas
5. Sincronização do catálogo de acomodações
6. Verificação do índice FAISS
7. Construção do FAISS quando necessário
8. Inicialização do Streamlit
```

Quando o índice já existe:

```text
Índice FAISS existente.
```

a aplicação não realiza uma nova vetorização dos documentos.

---

# 🔁 Reinicialização automática

O container utiliza:

```text
--restart unless-stopped
```

Isso permite que o Agente Aurora volte automaticamente após uma reinicialização do servidor ou do Docker, exceto quando o container é explicitamente interrompido pelo administrador.

---

# 🩺 Healthcheck

A imagem Docker possui healthcheck para verificar o funcionamento do Streamlit.

Endpoint:

```text
/_stcore/health
```

Teste manual:

```bash
curl -fsS http://127.0.0.1:8501/_stcore/health
```

Resposta esperada:

```text
ok
```

Também é possível verificar o estado pelo Docker:

```bash
docker ps
```

Exemplo:

```text
aurora-ai   Up (...) (healthy)
```

Ou:

```bash
docker inspect \
  --format '{{.State.Status}} | health={{.State.Health.Status}}' \
  aurora-ai
```

Resultado esperado:

```text
running | health=healthy
```

---

# 🗄️ PostgreSQL

A Central de Reservas utiliza:

```text
PostgreSQL 18
SQLAlchemy 2
psycopg 3
```

Banco utilizado:

```text
aurora_reservas
```

---

## Principais tabelas

```text
categorias_acomodacao
unidades_acomodacao
reservas
```

---

## Inicialização

```bash
python -m scripts.init_database
```

---

## População do catálogo

```bash
python -m scripts.seed_database
```

O processo foi desenvolvido para sincronizar o catálogo demonstrativo.

Quando os dados já existem, a execução identifica os registros existentes:

```text
[OK] Quarto Standard Casal
[OK] STD-CASAL-01
...
```

evitando recriações desnecessárias.

---

# 📁 Estrutura do projeto

```text
aurora-ai-assistant/
│
├── app.py
├── Dockerfile
├── requirements.txt
├── .env.exemplo
├── .dockerignore
├── .gitignore
│
├── assets/
│   └── imagens/
│       ├── acomodacoes/
│       ├── deck/
│       ├── estrutura/
│       └── pousada/
│
├── data/
│   ├── galeria_imagens.json
│   └── faiss/
│
├── deploy/
│   └── start.sh
│
├── docs/
│   └── imagens/
│       └── agente-aurora-producao.png
│       └── app_aurora_tela1.png
│       └── app_aurora_tela2.png
│       └── app_aurora_tela3.png
│       └── Volume 5.pdf
│
├── documentos/
│   ├── VOLUME 1.pdf
│   ├── VOLUME 2.pdf
│   ├── VOLUME 3.pdf
│   └── VOLUME 4.pdf
│
├── scripts/
│   ├── build_index.py
│   ├── init_database.py
│   ├── seed_database.py
│   ├── test_service.py
│   ├── test_schemas.py
│   ├── test_recuperacao_reserva.py
│   ├── test_recuperacao_negativa.py
│   └── test_recuperacao_flexivel.py
│
└── src/
    ├── config.py
    ├── embeddings.py
    ├── gallery.py
    ├── llm.py
    │
    └── reservas/
        ├── __init__.py
        ├── database.py
        ├── models.py
        ├── repository.py
        ├── schemas.py
        ├── service.py
        └── ui.py
```

---

# ⚙️ Variáveis de ambiente

O projeto utiliza um arquivo:

```text
.env
```


Existe um modelo em:

```text
.env.exemplo
```

Exemplo:

```dotenv
PROVEDOR_LLM=groq

GROQ_API_KEY=sua_chave_groq_aqui

MODELO_LINGUAGEM_GROQ=openai/gpt-oss-120b
MODELO_LINGUAGEM_GROQ_FALLBACK=openai/gpt-oss-20b

MODELO_LINGUAGEM_OLLAMA=qwen3:4b

MODELO_VETORIZACAO_OLLAMA=bge-m3:567m
OLLAMA_BASE_URL=http://localhost:11434

DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/aurora_reservas
```


---

# 💻 Execução local

## 1. Clone o repositório

```bash
git clone https://github.com/Raphaelbertone/aurora-ai-assistant.git
cd aurora-ai-assistant
```

---

## 2. Crie um ambiente virtual

### Windows

```powershell
python -m venv .venv
```

Ativação:

```powershell
.venv\Scripts\Activate.ps1
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

# 🦙 Ollama

O projeto utiliza Ollama para execução local do modelo de embeddings.

Instale o modelo:

```bash
ollama pull bge-m3:567m
```

Confirme:

```bash
ollama list
```

O modelo deverá aparecer como:

```text
bge-m3:567m
```

---

## Modelo local opcional

Para utilização manual do LLM local:

```bash
ollama pull qwen3:4b
```

Depois configure:

```dotenv
PROVEDOR_LLM=ollama
```

---

# 🗃️ Configuração do banco

Crie um banco PostgreSQL:

```text
aurora_reservas
```

e configure a conexão por meio de:

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/aurora_reservas
```

---

## Inicialize as tabelas

```bash
python -m scripts.init_database
```

---

## Popule o catálogo

```bash
python -m scripts.seed_database
```

---

# 🧠 Construção do índice FAISS

Com o Ollama ativo e o BGE-M3 instalado:

```bash
python -m scripts.build_index
```

O processo realiza:

```text
PDFs
  ↓
Carregamento
  ↓
Fragmentação
  ↓
BGE-M3
  ↓
Embeddings
  ↓
FAISS
```

O resultado é persistido em:

```text
data/faiss/
```

---

# ▶️ Executando a aplicação

Após configurar todas as dependências:

```bash
streamlit run app.py
```

Por padrão:

```text
http://localhost:8501
```

---

# 🧪 Testes

## Teste da camada de serviço

```bash
python -m scripts.test_service
```

Esse teste verifica, entre outros pontos:

- disponibilidade inicial;
- criação de reserva;
- indisponibilidade da unidade reservada;
- períodos adjacentes;
- consulta;
- cancelamento;
- retorno da unidade ao estoque.

---

## Testes de schemas

```bash
python -m scripts.test_schemas
```

---

## Teste de recuperação

```bash
python -m scripts.test_recuperacao_reserva
```

---

## Recuperação negativa

```bash
python -m scripts.test_recuperacao_negativa
```

---

## Recuperação flexível

```bash
python -m scripts.test_recuperacao_flexivel
```

---

## Verificação de sintaxe

```bash
python -m compileall app.py src scripts
```

---

## Verificação do Git

```bash
git diff --check
```

---

# 💡 Exemplos de utilização

## Perguntas informacionais

```text
Qual o horário do check-in?
```

```text
Quais são os valores das acomodações?
```

```text
Onde assistir ao pôr do sol?
```

```text
Tem restaurante e piscina?
```

```text
O que vem no banheiro?
```

```text
O que fazer com crianças?
```

```text
O que fazer em uma viagem romântica?
```

---

## Pedidos de imagens

```text
Tem fotos dos quartos?
```

```text
Tem foto das acomodações?
```

```text
Tem fotos da Suíte Premium?
```

```text
Fotos do chalé
```

```text
Fotos da pousada
```

---

## Contexto visual

```text
Usuário:
Tem restaurante e piscina?

Usuário:
Tem fotos?
```

O Aurora interpreta o contexto anterior e apresenta:

```text
Piscina Aquecida
Restaurante Mirante
```

---

## Informação inexistente

```text
Usuário:
Tem cassino?

Aurora:
Não encontrei essa informação na Base Oficial de Conhecimento.
```

---

# 🔐 Segurança

Algumas medidas adotadas no projeto:

- segredos armazenados fora do código;
- utilização de `.env`;
- `.env` ignorado pelo Git;
- PostgreSQL sem exposição pública;
- Ollama sem exposição pública;
- separação entre RAG, galeria e reservas;
- ausência de armazenamento de cartões;
- ausência de processamento de pagamentos;
- reservas exclusivamente demonstrativas;
- fallback para informações não encontradas;
- proteção contra solicitações de prompts e instruções internas;
- execução isolada da aplicação em container Docker.

---

# 🚫 Proteção de instruções internas

Solicitações relacionadas a prompts, instruções internas ou dados internos de processamento recebem uma resposta controlada:

> **Não posso fornecer prompts, instruções internas ou dados internos de processamento do Agente Aurora.**

---

# 🧩 Separação de responsabilidades

O projeto separa diferentes tipos de funcionalidades.

```text
RAG
└── informações presentes nos documentos

Galeria
└── seleção e apresentação de imagens

Contexto conversacional
└── continuidade curta da conversa

Central de Reservas
└── operações transacionais

PostgreSQL
└── persistência das reservas

FAISS
└── busca vetorial

Groq
└── geração das respostas

Ollama
└── execução local dos embeddings
```

Essa separação reduz o acoplamento entre os componentes.

---

# 🧰 Tecnologias utilizadas

## Inteligência Artificial

- Groq
- GPT-OSS
- Ollama
- BGE-M3
- LangChain
- FAISS

## Backend

- Python
- SQLAlchemy
- psycopg

## Banco de dados

- PostgreSQL

## Interface

- Streamlit

## Infraestrutura

- Docker
- Oracle Cloud Infrastructure
- Ubuntu Server

## Versionamento

- Git
- GitHub

---

# ☁️ Deploy

A aplicação pública utiliza:

```text
Oracle Cloud Infrastructure
        ↓
Ubuntu 22.04
        ↓
Docker
        ↓
Agente Aurora
```

Serviços auxiliares:

```text
PostgreSQL 18
Ollama
BGE-M3
Groq
```

---

# ✅ Validações realizadas em produção

A implantação foi validada diretamente na infraestrutura de produção.

## Docker

```text
linux/amd64
Docker Engine
Container healthy
```

## PostgreSQL

```text
PostgreSQL 18
Banco aurora_reservas
Conexão validada
```

## Ollama

```text
Serviço ativo
127.0.0.1:11434
bge-m3:567m
```

## Embeddings

```text
Quantidade de vetores: 1
Dimensão: 1024
```

## FAISS

```text
PDFs existentes no projeto:       5
PDFs utilizados pelo RAG:         4
Páginas processadas pelo RAG:     136
Chunks vetoriais:                 235

> Embora o repositório possua cinco volumes de documentação, somente os **Volumes 1 a 4** compõem o corpus RAG. O Volume 5 possui finalidade documental/técnica e permanece fora do índice vetorial.

## Streamlit

```text
0.0.0.0:8501
Healthcheck: ok
```

## Persistência

Após reinicialização do container:

```text
Índice FAISS existente.
```

confirmando que a base vetorial não precisou ser reconstruída.

---

# ✅ Status do projeto

| Componente | Status |
|---|:---:|
| Interface Streamlit | ✅ |
| Base Oficial em PDF | ✅ |
| RAG | ✅ |
| BGE-M3 | ✅ |
| Ollama | ✅ |
| FAISS | ✅ |
| Persistência FAISS | ✅ |
| Groq | ✅ |
| GPT-OSS 120B | ✅ |
| Fallback GPT-OSS 20B | ✅ |
| Contexto conversacional curto | ✅ |
| Galeria contextual | ✅ |
| PostgreSQL | ✅ |
| Central de Reservas | ✅ |
| Consulta de disponibilidade | ✅ |
| Criação de reserva | ✅ |
| Consulta de reserva | ✅ |
| Cancelamento | ✅ |
| Recuperação de reserva | ✅ |
| Docker | ✅ |
| Healthcheck | ✅ |
| Deploy OCI | ✅ |
| Aplicação pública | ✅ |

---

# ⚠️ Natureza demonstrativa

A **Pousada Mirante do Pôr do Sol** apresentada pelo Agente Aurora é fictícia.

Os seguintes elementos foram criados exclusivamente para fins acadêmicos e demonstrativos:

- nome da pousada;
- acomodações;
- tarifas;
- disponibilidade;
- reservas;
- códigos de reserva;
- serviços;
- estrutura;
- informações operacionais;
- imagens;
- catálogo da Central de Reservas.

Nenhuma reserva criada pelo sistema possui validade comercial.

Nenhum pagamento real é processado.

---

# 📌 Limitações

O Agente Aurora é um projeto demonstrativo e não pretende substituir um sistema comercial completo de hotelaria.

Entre as limitações da versão atual estão:

- disponibilidade baseada exclusivamente no banco demonstrativo;
- ausência de gateway de pagamento;
- ausência de integração com PMS real;
- ausência de integração com canais de venda;
- ausência de envio real de confirmação de reserva;
- imagens ilustrativas;
- conteúdo limitado à Base Oficial de Conhecimento fornecida ao projeto.

---

# 🚀 Possíveis evoluções

Algumas extensões possíveis:

- autenticação de usuários;
- painel administrativo;
- integração com sistemas PMS;
- integração com meios de pagamento;
- envio automático de e-mails;
- notificações por WhatsApp;
- integração com calendários;
- monitoramento e observabilidade;
- proxy reverso com HTTPS;
- domínio próprio;
- API REST;
- painel de métricas;
- atualização dinâmica da base de conhecimento;
- armazenamento de documentos em object storage;
- escalabilidade horizontal.

---

# ©️ Direitos autorais e licenciamento

**© 2026 Raphael Bertone. Todos os direitos reservados.**

O **Agente Aurora** foi desenvolvido como projeto acadêmico e demonstrativo para o **Challenge Agente Alura**.

O código-fonte, a arquitetura desenvolvida para o projeto, os textos autorais, a organização da Base Oficial de Conhecimento, a identidade do Agente Aurora, a estrutura da Central de Reservas e os demais materiais originais produzidos especificamente para este repositório são de autoria de **Raphael Bertone**, salvo quando indicado de outra forma.

A disponibilização pública deste repositório tem finalidade de:

- apresentação acadêmica;
- demonstração técnica;
- avaliação do projeto;
- composição de portfólio profissional;
- estudo e consulta do funcionamento da solução.

A publicação do código no GitHub não implica, por si só, autorização para comercialização, redistribuição, sublicenciamento ou utilização integral do projeto em produtos ou serviços de terceiros.

Para utilização do projeto ou de partes substanciais de seu conteúdo fora dessas finalidades, entre em contato com o autor para autorização.

---

## Tecnologias e componentes de terceiros

O Agente Aurora utiliza bibliotecas, frameworks, modelos e serviços desenvolvidos por terceiros, incluindo, entre outros:

- Python;
- Streamlit;
- LangChain;
- FAISS;
- SQLAlchemy;
- PostgreSQL;
- psycopg;
- Docker;
- Ollama;
- BGE-M3;
- Groq;
- GPT-OSS.

Esses componentes permanecem sujeitos às suas próprias licenças, termos de uso e direitos de propriedade intelectual.

A inclusão dessas tecnologias neste projeto não transfere ao autor quaisquer direitos sobre marcas, softwares, modelos ou serviços pertencentes aos respectivos titulares.

---

## Imagens e conteúdo demonstrativo

As imagens utilizadas na galeria do Agente Aurora foram produzidas para fins ilustrativos e demonstrativos do projeto.

A **Pousada Mirante do Pôr do Sol**, suas acomodações, tarifas, reservas, serviços, estrutura e demais informações apresentadas pela aplicação fazem parte de um cenário fictício criado para demonstração.

Nenhuma informação apresentada deve ser interpretada como oferta comercial ou representação de um estabelecimento hoteleiro real.

---

## Uso do nome Agente Aurora

O nome **Agente Aurora**, sua identidade dentro deste projeto e os elementos autorais associados à aplicação fazem parte da apresentação acadêmica e profissional desenvolvida pelo autor.

O uso desses elementos por terceiros não deve sugerir parceria, autorização, endosso ou vínculo com o autor sem consentimento prévio.

---

## Aviso sobre o projeto

Este software é fornecido para fins educacionais e demonstrativos.

O projeto não oferece garantia de adequação para utilização em ambientes comerciais, financeiros ou de produção real e não deve ser utilizado como sistema hoteleiro real sem revisão técnica, jurídica, de segurança e de conformidade apropriada.

---

# 👨‍💻 Autor

**Raphael Bertone**

Projeto desenvolvido para o:

**Challenge Agente Alura**

---

# 🌄 Agente Aurora

> **Onde cada pôr do sol se transforma em uma lembrança inesquecível.**
