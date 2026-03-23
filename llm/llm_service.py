import anthropic
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"


def _client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _api_disponivel():
    return bool(os.getenv("ANTHROPIC_API_KEY")) and os.getenv("ANTHROPIC_API_KEY") != "sua_chave_aqui"


# ── Fallbacks (geração local sem API) ────────────────────────────────────────

def _instrucoes_fallback(placa, ponto_base, paradas_ordenadas):
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    paradas_txt = "\n".join([
        f"  **Parada {i+1}:** {p['rua']}, {p['numero']} — {p['cidade']} (CEP {p['cep']})"
        + (f"\n  > Referência: {p['complemento']}" if p.get('complemento') else "")
        for i, p in enumerate(paradas_ordenadas)
    ])
    return f"""## 📋 Instruções de Rota — Veículo {placa}
**Data:** {hoje}

---

### 👋 Briefing Inicial
Bom dia, motorista(s)! Você realizará hoje **{len(paradas_ordenadas)} entregas** de insumos hospitalares partindo da base em **{ponto_base['rua']}, {ponto_base['numero']} — {ponto_base['cidade']}**.

A rota foi otimizada por Algoritmo Genético para minimizar distância e respeitar janelas de entrega. Siga a ordem indicada.

---

### 🗺️ Sequência de Entregas

{paradas_txt}

---

### ⚠️ Lembretes Importantes
- Confirme a identidade do destinatário antes de entregar insumos controlados
- Insumos refrigerados devem ser entregues com prioridade máxima
- Em caso de ausência no destino, acione a central imediatamente
- Mantenha o veículo trancado durante as entregas
- Registre a assinatura do recebedor em cada parada

---

### ✅ Encerramento
Ao concluir todas as entregas, retorne à base e registre a conclusão da rota no sistema. Bom trabalho!

> *Relatório gerado automaticamente pelo sistema de logística hospitalar.*
"""


def _relatorio_fallback(placa, n_paradas, custo_inicial, custo_otimizado, melhoria_pct, tempo_s, populacao, geracoes, mutacao):
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    economia_pct = melhoria_pct
    return f"""## 📊 Relatório de Eficiência — {hoje}

---

### 1. Resumo Executivo
O Algoritmo Genético otimizou a rota do veículo **{placa}** com **{n_paradas} paradas**, obtendo uma redução de **{melhoria_pct:.1f}%** no custo total em relação à rota aleatória inicial. O processamento foi concluído em **{tempo_s:.2f} segundos**.

---

### 2. Análise dos Resultados

| Métrica | Valor |
|---|---|
| Custo inicial (aleatório) | {custo_inicial:,.2f} |
| Custo otimizado (AG) | {custo_otimizado:,.2f} |
| Redução absoluta | {custo_inicial - custo_otimizado:,.2f} |
| Melhoria percentual | {melhoria_pct:.1f}% |
| Tempo de processamento | {tempo_s:.2f} s |

---

### 3. Impacto Operacional Estimado
- **Redução de {economia_pct:.1f}%** no custo de roteamento indica economia proporcional em combustível e tempo
- Com {n_paradas} paradas otimizadas, o motorista percorre um trajeto significativamente mais eficiente
- A otimização reduz o tempo ocioso entre entregas, aumentando a pontualidade

---

### 4. Avaliação do Algoritmo Genético

| Parâmetro | Valor |
|---|---|
| Tamanho da população | {populacao} |
| Número de gerações | {geracoes} |
| Taxa de mutação | {mutacao:.0%} |

{'✅ Configuração adequada para o problema.' if melhoria_pct > 10 else '⚠️ Considere aumentar gerações ou população para maior melhoria.'}

---

### 5. Recomendações
- Executar a otimização diariamente antes do início das rotas
- Testar com população maior (≥ 100) para rotas com mais de 15 paradas
- Monitorar a taxa de melhoria ao longo do tempo para detectar sazonalidades

> *Relatório gerado automaticamente pelo sistema de logística hospitalar.*
"""


def _chat_fallback(pergunta, contexto_rota):
    return (
        f"⚠️ A IA não está disponível no momento (sem créditos na API). "
        f"Dados disponíveis: veículo **{contexto_rota['placa']}**, "
        f"**{contexto_rota['n_paradas']} paradas**, custo otimizado **{contexto_rota['custo_otimizado']:.2f}**, "
        f"melhoria de **{contexto_rota['melhoria']:.1f}%**."
    )


# ── Funções públicas ──────────────────────────────────────────────────────────

def gerar_instrucoes_motorista(placa, ponto_base, paradas_ordenadas, custo_otimizado):
    if not _api_disponivel():
        return _instrucoes_fallback(placa, ponto_base, paradas_ordenadas)

    lista = "\n".join([
        f"  {i+1}. {p['rua']}, {p['numero']} — {p['cidade']} | CEP: {p['cep']}"
        + (f" | Ref: {p['complemento']}" if p.get('complemento') else "")
        for i, p in enumerate(paradas_ordenadas)
    ])

    prompt = f"""Você é um assistente de logística hospitalar. Gere instruções claras para o motorista do veículo **{placa}**.

**Ponto de partida:** {ponto_base['rua']}, {ponto_base['numero']} — {ponto_base['cidade']}

**Rota otimizada — {len(paradas_ordenadas)} paradas:**
{lista}

Gere:
1. Briefing inicial (saudação + resumo da missão)
2. Instruções parada a parada (ordem de chegada, cuidados com insumos hospitalares, procedimento de entrega)
3. Lembretes de segurança e boas práticas hospitalares
4. Mensagem de encerramento ao concluir a rota

Use linguagem direta e profissional."""

    try:
        response = _client().messages.create(
            model=MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception:
        return _instrucoes_fallback(placa, ponto_base, paradas_ordenadas)


def gerar_relatorio_eficiencia(placa, n_paradas, custo_inicial, custo_otimizado, melhoria_pct, tempo_s, populacao, geracoes, mutacao):
    if not _api_disponivel():
        return _relatorio_fallback(placa, n_paradas, custo_inicial, custo_otimizado, melhoria_pct, tempo_s, populacao, geracoes, mutacao)

    prompt = f"""Você é um analista de logística hospitalar. Gere um relatório técnico de eficiência.

**Dados da otimização:**
- Veículo: {placa}
- Número de paradas: {n_paradas}
- Custo inicial (rota aleatória): {custo_inicial:.2f}
- Custo otimizado (Algoritmo Genético): {custo_otimizado:.2f}
- Melhoria obtida: {melhoria_pct:.1f}%
- Tempo de processamento: {tempo_s:.2f} s
- Parâmetros do AG: população={populacao}, gerações={geracoes}, mutação={mutacao}

Estruture o relatório com:
1. **Resumo Executivo** (3 linhas)
2. **Análise dos Resultados** (interpretação dos números)
3. **Impacto Operacional** (economia estimada de tempo, combustível e recursos)
4. **Avaliação do Algoritmo** (qualidade dos parâmetros utilizados)
5. **Recomendações** para próximas otimizações

Use linguagem técnica acessível para gestores hospitalares."""

    try:
        response = _client().messages.create(
            model=MODEL,
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception:
        return _relatorio_fallback(placa, n_paradas, custo_inicial, custo_otimizado, melhoria_pct, tempo_s, populacao, geracoes, mutacao)


def responder_pergunta(pergunta, contexto_rota, historico):
    if not _api_disponivel():
        return _chat_fallback(pergunta, contexto_rota)

    system = f"""Você é um assistente especializado em logística hospitalar. Responda perguntas sobre a rota otimizada com base nos dados abaixo.

**Contexto:**
- Veículo: {contexto_rota['placa']}
- Paradas em ordem: {contexto_rota['paradas']}
- Custo otimizado: {contexto_rota['custo_otimizado']:.2f}
- Melhoria em relação à rota aleatória: {contexto_rota['melhoria']:.1f}%
- Total de paradas: {contexto_rota['n_paradas']}

Responda de forma direta. Se a informação não estiver no contexto, informe que não tem esse dado."""

    messages = historico + [{"role": "user", "content": pergunta}]

    try:
        response = _client().messages.create(
            model=MODEL,
            max_tokens=600,
            system=system,
            messages=messages
        )
        return response.content[0].text
    except Exception:
        return _chat_fallback(pergunta, contexto_rota)
