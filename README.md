# 🏥 Logística de Rota Hospitalar — Tech Challenge Fase 2 (FIAP)

Integrantes do grupo: 19
O grupo é composto pelos seguintes alunos:

Wellson Almeida dos Santos (rm369201) (wellson.digital@gmail.com)

Nelson Seiji Takahashi (rm370089) (seiji8503@gmail.com)

Youtube:  https://www.youtube.com/watch?v=lEDjC7cFKpI




Sistema inteligente de otimização de rotas para entrega de insumos hospitalares, utilizando **Algoritmo Genético** para roteamento e **IA (Claude da Anthropic)** para geração de instruções e relatórios.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Fluxo da Aplicação](#fluxo-da-aplicação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Stack Tecnológica](#stack-tecnológica)
- [Banco de Dados](#banco-de-dados)
- [Como Rodar com Docker](#como-rodar-com-docker)
- [Funcionalidades](#funcionalidades)

---

## Visão Geral

O sistema resolve o problema de **roteirização de veículos com janelas de tempo** (VRPTW) aplicado à logística hospitalar, otimizando as rotas de entrega de:

- Medicamentos
- Vacinas
- Kits cirúrgicos
- Oxigênio e equipamentos médicos

Cada veículo sai de um **ponto base (armazém)** e realiza entregas em hospitais e clínicas, respeitando:

| Restrição | Descrição |
|---|---|
| Capacidade de carga | Peso máximo por veículo (kg) |
| Autonomia | Distância máxima percorrida (km) |
| Janela de entrega | Horário permitido para cada parada |
| Criticidade | Prioridade dos insumos (baixa/média/alta) |

---

## Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
│                                                              │
│  ┌─────────────────────────┐    ┌────────────────────────┐  │
│  │   app (Streamlit:8501)  │───▶│   db (Postgres:5433)   │  │
│  │                         │    │                         │  │
│  │  ┌───────────────────┐  │    │   rota_hospitalar DB    │  │
│  │  │    main.py (UI)   │  │    │                         │  │
│  │  └────────┬──────────┘  │    │  - veiculo              │  │
│  │           │             │    │  - rota                 │  │
│  │  ┌────────▼──────────┐  │    │  - produto              │  │
│  │  │ database/         │  │    │  - ponto_base           │  │
│  │  │  conexao.py       │  │    │                         │  │
│  │  │  *_service.py     │◀─┼────│                         │  │
│  │  └────────┬──────────┘  │    └────────────────────────┘  │
│  │           │             │                                  │
│  │  ┌────────▼──────────┐  │    ┌────────────────────────┐  │
│  │  │ algoritmo_        │  │    │   Anthropic Claude API  │  │
│  │  │ genetico/         │  │    │   (claude-haiku-4-5)    │  │
│  │  │ algoritmo_        │  │    └───────────▲────────────┘  │
│  │  │ genetico.py       │  │                │                │
│  │  └───────────────────┘  │    ┌───────────┴────────────┐  │
│  │                         │    │ llm/                    │  │
│  │                         │───▶│  llm_service.py         │  │
│  └─────────────────────────┘    └────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## Fluxo da Aplicação

### Fluxo Completo (Usuário → Sistema → Resultado)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUÁRIO (Browser)                           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
          ┌────────────────────▼─────────────────────┐
          │              CADASTRO DE DADOS             │
          │                                            │
          │  1. Cadastra Veículos (modelo, placa,      │
          │     capacidade, autonomia)                 │
          │                                            │
          │  2. Define Ponto Base (armazém de partida  │
          │     por veículo, com geocoding)            │
          │                                            │
          │  3. Cadastra Rotas (endereços de entrega   │
          │     por veículo, com geocoding automático) │
          │                                            │
          │  4. Cadastra Insumos (nome, peso,          │
          │     criticidade, janela de entrega)        │
          └────────────────────┬─────────────────────┘
                               │
          ┌────────────────────▼─────────────────────┐
          │           MÓDULO DE OTIMIZAÇÃO             │
          │                                            │
          │  Usuário seleciona:                        │
          │  - Veículo a otimizar                      │
          │  - Tamanho da população (GA)               │
          │  - Número de gerações                      │
          │  - Taxa de mutação                         │
          └────────────────────┬─────────────────────┘
                               │
          ┌────────────────────▼─────────────────────┐
          │          ALGORITMO GENÉTICO (GA)           │
          │                                            │
          │  Entrada:                                  │
          │  - Coordenadas GPS das paradas             │
          │  - Dados dos insumos por parada            │
          │  - Configurações do veículo                │
          │                                            │
          │  Processo (por geração):                   │
          │  ┌──────────────────────────────────┐      │
          │  │  Inicializa população aleatória  │      │
          │  └──────────────┬───────────────────┘      │
          │                 │                           │
          │  ┌──────────────▼───────────────────┐      │
          │  │  Calcula fitness de cada rota:   │      │
          │  │  - Distância total               │      │
          │  │  - Penalidade de janela de tempo │      │
          │  │  - Penalidade de capacidade      │      │
          │  │  - Penalidade de autonomia       │      │
          │  └──────────────┬───────────────────┘      │
          │                 │                           │
          │  ┌──────────────▼───────────────────┐      │
          │  │  Seleção + Crossover (OX) +      │      │
          │  │  Mutação                         │      │
          │  └──────────────┬───────────────────┘      │
          │                 │                           │
          │         ┌───────▼───────┐                  │
          │         │ Convergiu?    │──Não──┐           │
          │         └───────┬───────┘       │           │
          │                 │ Sim           │           │
          │          próxima geração ◀──────┘           │
          └────────────────────┬─────────────────────┘
                               │
          ┌────────────────────▼─────────────────────┐
          │              RESULTADO + IA               │
          │                                            │
          │  - Mapa interativo com rota otimizada      │
          │  - Curva de convergência do GA             │
          │  - Distância total percorrida              │
          │  - Instruções ao motorista (Claude AI)     │
          │  - Relatório de eficiência (Claude AI)     │
          │  - Chat interativo sobre a rota            │
          └───────────────────────────────────────────┘
```

### Fluxo do Algoritmo Genético (detalhado)

```
Geração 0
    │
    ├─► Cria N indivíduos (permutações aleatórias das paradas)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Para cada indivíduo, calcular fitness:                  │
│                                                          │
│  fitness = distância_total                               │
│           + (penalidade_janela × 100)                    │
│           + (penalidade_capacidade × 1000)               │
│           + (penalidade_autonomia × 5000)                │
│                                                          │
│  Menor fitness = melhor solução                          │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
             Selecionar os melhores
                        │
                        ▼
         Order Crossover (OX) entre pares
         ┌────────────────────────────────┐
         │  Parent 1: [A,B,C,D,E,F,G,H]  │
         │  Parent 2: [B,D,F,H,A,C,E,G]  │
         │                                │
         │  Filho:    [C,D,F,H,A,?,?,?]  │
         │  (preserva sub-sequência e     │
         │   preenche com genes do P2)    │
         └────────────────────────────────┘
                        │
                        ▼
         Mutação aleatória (troca de 2 genes)
                        │
                        ▼
            Nova geração formada
                        │
         ┌──────────────▼──────────────┐
         │  Mais gerações disponíveis?  │
         │  Sim ──► volta ao fitness    │
         │  Não ──► retorna melhor rota │
         └─────────────────────────────┘
```

---

## Estrutura do Projeto

```
Tech-Challenge-Fase-2/
│
├── main.py                       # Interface Streamlit (UI principal)
├── requirements.txt              # Dependências Python
├── Dockerfile                    # Imagem Docker da aplicação
├── docker-compose.yml            # Orquestração dos serviços
├── run.sh                        # Script de inicialização
├── .env                          # Variáveis de ambiente
│
├── database/                     # Camada de acesso a dados
│   ├── conexao.py                # Gerenciador de conexão PostgreSQL
│   ├── base_service.py           # CRUD de pontos base (armazéns)
│   ├── endereco_service.py       # CRUD de rotas/endereços
│   ├── produto_service.py        # CRUD de insumos/produtos
│   ├── veiculo_service.py        # CRUD de veículos
│   └── script.sql                # DDL + dados iniciais
│
├── algoritmo_genetico/           # Motor de otimização
│   ├── algoritmo_genetico.py     # Implementação do GA
│   └── utils/
│       └── utils.py              # Conversão de horários
│
└── llm/                          # Integração com IA
    ├── __init__.py
    └── llm_service.py            # Cliente Claude (Anthropic)
```

---

## Stack Tecnológica

| Categoria | Tecnologia | Uso |
|---|---|---|
| **Interface** | Streamlit | Web UI |
| **Banco de Dados** | PostgreSQL 16 | Persistência |
| **Driver DB** | psycopg2-binary | Conexão Python→Postgres |
| **Mapas** | folium + streamlit-folium | Visualização de rotas |
| **Geocoding** | geopy (Nominatim) | Endereço → coordenadas GPS |
| **IA/LLM** | Anthropic Claude (Haiku) | Instruções e relatórios |
| **Otimização** | Algoritmo Genético (custom) | Roteamento de veículos |
| **Dados** | pandas + numpy | Manipulação de dados |
| **Gráficos** | matplotlib | Curva de convergência |
| **Container** | Docker + Docker Compose | Deploy |

---

## Banco de Dados

### Modelo de Dados (ER Simplificado)

```
┌─────────────┐         ┌─────────────────┐
│   veiculo   │         │   ponto_base    │
│─────────────│         │─────────────────│
│ veiculo_id  │◀────────│ veiculo_id (FK) │
│ modelo      │    1    │ ponto_base_id   │
│ placa       │    │    │ nome_da_base    │
│ capacidade_ │    │    │ rua, numero     │
│  maxima     │    │    │ cidade, cep     │
│ capacidade_ │    │    │ latitude        │
│  disponivel │    │    │ longitude       │
│ autonomia_  │    │    └─────────────────┘
│  total      │    │
└──────┬──────┘    │    ┌─────────────────┐
       │           │    │      rota       │
       │ 1:N       │    │─────────────────│
       │           └───▶│ veiculo_desig.  │
       │                │ rota_id         │
       │                │ rua, numero     │
       │                │ cidade, cep     │
       │                │ complemento     │
       │                │ latitude        │
       │                │ longitude       │
       └────────────────┤                 │
              1:N        └────────┬────────┘
                                  │ 1:N
                         ┌────────▼────────┐
                         │     produto     │
                         │─────────────────│
                         │ produto_id      │
                         │ nome            │
                         │ quantidade      │
                         │ peso            │
                         │ nivel_          │
                         │  criticidade    │
                         │ janela_entrega  │
                         │ rota_designada  │
                         │ veiculo_desig.  │
                         └─────────────────┘
```

### Dados Pré-carregados

| Entidade | Quantidade | Regiões |
|---|---|---|
| Veículos | 3 | Mercedes Accelo, Ford Cargo, VW Delivery |
| Pontos Base | 3 | Goiânia (GO), Palmas (TO), Belo Horizonte (MG) |
| Rotas | 49 | GO, TO, MG |
| Insumos | 50+ | Medicamentos, vacinas, equipamentos |

---

## Como Rodar com Docker

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado e em execução
- [Docker Compose](https://docs.docker.com/compose/) (incluso no Docker Desktop)
- Chave da API Anthropic (Claude) — obtenha em [console.anthropic.com](https://console.anthropic.com)

### Passo a Passo

**1. Clone o repositório**
```bash
git clone <url-do-repositorio>
cd Tech-Challenge-Fase-2
```

**2. Configure as variáveis de ambiente**

Edite o arquivo `.env` na raiz do projeto:

```env
DB_HOST=db
DB_USER=postgres
DB_PASS=postgres
DB_NAME=rota_hospitalar
ANTHROPIC_API_KEY=sk-ant-<sua-chave-aqui>
```

> **Importante:** Nunca commite o arquivo `.env` com sua chave real.

**3. Inicie os containers**

Opção A — usando o script incluído:
```bash
chmod +x run.sh
./run.sh
```

Opção B — diretamente com Docker Compose:
```bash
docker compose up --build
```

**4. Acesse a aplicação**

| Serviço | URL / Endereço |
|---|---|
| Aplicação Web | http://localhost:8501 |
| PostgreSQL | localhost:5433 |

### O que acontece ao subir

```
docker compose up --build
        │
        ├─► Build da imagem Python (Dockerfile)
        │       - FROM python:3.11-slim
        │       - pip install -r requirements.txt
        │       - COPY . /app
        │
        ├─► Inicia container db (PostgreSQL)
        │       - Cria banco rota_hospitalar
        │       - Executa script.sql (DDL + seed data)
        │       - Health check: pg_isready
        │
        └─► Inicia container app (aguarda db healthy)
                - streamlit run main.py
                - Disponível em :8501
```

### Comandos Úteis

```bash
# Parar os containers
docker compose down

# Parar e remover volumes (apaga dados do banco)
docker compose down -v

# Ver logs em tempo real
docker compose logs -f

# Ver logs apenas da aplicação
docker compose logs -f app

# Reiniciar apenas a aplicação (sem rebuild)
docker compose restart app

# Acessar o banco de dados
docker compose exec db psql -U postgres -d rota_hospitalar
```

---

## Funcionalidades

### 1. Gerenciamento de Frota (🚛 Veículos)
- Cadastro de veículos com capacidade e autonomia
- Monitoramento visual da capacidade disponível
- Validação de capacidade ao adicionar insumos

### 2. Gerenciamento de Rotas (📍 Rota dos Veículos)
- Cadastro de pontos de entrega por endereço
- Geocoding automático (endereço → latitude/longitude) via OpenStreetMap
- Visualização no mapa

### 3. Pontos Base (🏠 Partida Inicial)
- Definição do armazém de saída por veículo
- Suporte a geocoding

### 4. Insumos (📦 Insumos)
- Cadastro com nível de criticidade (1=Baixo, 2=Médio, 3=Alto)
- Janela de entrega (ex: "08:00 - 12:00")
- Verificação automática de capacidade do veículo

### 5. Otimização de Rota (🚀 Otimização)
- Seleção do veículo a otimizar
- Configuração dos parâmetros do Algoritmo Genético
- Visualização em tempo real da evolução
- Mapa interativo com a rota otimizada
- Geração de instruções ao motorista via IA
- Relatório de eficiência via IA
- Chat interativo sobre a rota

---

## Variáveis de Ambiente

| Variável | Descrição | Valor Padrão |
|---|---|---|
| `DB_HOST` | Host do PostgreSQL (nome do serviço Docker) | `db` |
| `DB_USER` | Usuário do banco | `postgres` |
| `DB_PASS` | Senha do banco | `postgres` |
| `DB_NAME` | Nome do banco | `rota_hospitalar` |
| `ANTHROPIC_API_KEY` | Chave da API Claude | — |

> Se `ANTHROPIC_API_KEY` não estiver configurada, as funcionalidades de IA são desabilitadas graciosamente — o sistema continua funcionando sem elas.
