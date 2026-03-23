import copy
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import random

from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import folium

from algoritmo_genetico.algoritmo_genetico import order_crossover, mutacao, calculo_fitness_matriz_distancia, matriz_distancia
from database.endereco_service import listar_coordenadas_por_veiculo, buscar_rota_por_id, listar_rotas, listar_rotas_por_veiculo, buscar_rota_por_endereco, cadastrar_rota, excluir_rota
from database.produto_service import buscar_detalhes_insumo_e_veiculo, buscar_insumos, cadastrar_insumo, excluir_insumo
from database.veiculo_service import atualizar_capacidade_veiculo, buscar_veiculo_por_id, buscar_veiculo_por_placa, buscar_veiculos, cadastrar_veiculo, capacidade_disponivel_veiculo, excluir_veiculo
from database.base_service import buscar_enderecos_bases, buscar_ponto_base_por_veiculo, cadastrar_ponto_base, excluir_ponto_base
from llm.llm_service import gerar_instrucoes_motorista, gerar_relatorio_eficiencia, responder_pergunta

geolocator = Nominatim(user_agent="logistica_hospitalar", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2, max_retries=3, swallow_exceptions=False)

def converter_endereco_para_coords(endereco):
    try:
        location = geocode(endereco)
        if location is None:
            return None, None
        return location.latitude, location.longitude
    except Exception as e:
        print(f"Erro ao geocodificar endereço '{endereco}': {e}")
        return None, None

def preparar_coordenadas_geograficas(veiculo_id):
    coords = listar_coordenadas_por_veiculo(veiculo_id)
    if not coords:
        return None, "Nenhuma coordenada encontrada"
    return coords, []

def fmt_br(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

horarios = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]

# ── Configuração ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Logística Hospitalar", page_icon="🏥", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #0f2744; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "📦 Insumos"

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital.png", width=64)
    st.title("Logística de Rota Hospitalar")
    st.caption("Otimização de rotas com Algoritmos Genéticos")
    st.divider()

    for label in ["📦 Insumos", "🚛 Veículos"]:
        if st.button(label, use_container_width=True, key=f"nav_{label}"):
            st.session_state["pagina"] = label

    st.divider()

    for label in ["📍 Rota dos Veículos", "🏠 Partida Inicial de Veículos"]:
        if st.button(label, use_container_width=True, key=f"nav_{label}"):
            st.session_state["pagina"] = label

    st.divider()

    if st.button("🚀 Otimização", use_container_width=True, key="nav_otimizacao"):
        st.session_state["pagina"] = "🚀 Otimização"

pagina = st.session_state["pagina"]

coords = []

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: INSUMOS
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "📦 Insumos":
    st.title("📦 Gestão de Insumos")
    st.caption("Cadastre e monitore os insumos hospitalares por veículo e rota")
    st.divider()

    # Formulário
    with st.container(border=True):
        st.subheader("Novo Insumo")

        veiculos_lista = buscar_veiculos()
        opcoes_veiculos = ["Nenhum"] + [v['placa'] for v in veiculos_lista]
        veiculo = st.selectbox("Veículo Designado", opcoes_veiculos, key="veiculo")

        if veiculo != "Nenhum":
            veiculo_id = buscar_veiculo_por_placa(veiculo)
            rotas = listar_rotas_por_veiculo(veiculo_id['veiculo_id'])
            opcoes_rotas = [f"{r['rua']}, {r['numero']} — {r['cidade']} ({r['cep']})" for r in rotas]
            rota = st.selectbox("Rota de Entrega", opcoes_rotas, key=f"rota_{veiculo}")
        else:
            st.selectbox("Rota de Entrega", [], key="rota_vazia", disabled=True)

        with st.form("form_insumo", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            nome    = c1.text_input("Nome do Insumo", placeholder="Ex: Soro 500ml")
            qtd     = c1.number_input("Quantidade", min_value=0)
            peso    = c2.number_input("Peso Unitário (kg)", min_value=0.0)
            crit    = c2.selectbox("Criticidade", ["Baixo", "Médio", "Alto"])
            c_ini, c_fim = c3.columns(2)
            hora_inicio = c_ini.selectbox("Início", horarios, index=16)
            hora_fim    = c_fim.selectbox("Fim", horarios, index=36)

            if st.form_submit_button("Cadastrar Insumo", type="primary", use_container_width=True):
                if nome and qtd:
                    capacidade_atual = capacidade_disponivel_veiculo(veiculo)
                    rota_id = buscar_rota_por_endereco(
                        rota.split(",")[0],
                        int(rota.split(",")[1].split("—")[0].strip()),
                        rota.split("(")[1].replace(")", "").strip()
                    )['rota_id'] if veiculo != "Nenhum" else None
                    janela = f"{hora_inicio} - {hora_fim}"
                    if capacidade_atual > 0 and (peso * qtd) > capacidade_atual:
                        st.error(f"Capacidade excedida! O veículo suporta até {capacidade_atual} kg.")
                    else:
                        atualizar_capacidade_veiculo(veiculo, capacidade_atual - (peso * qtd))
                        cadastrar_insumo(nome, qtd, peso, crit, janela, rota_id, veiculo)
                        st.toast("Insumo cadastrado!", icon="✅")
                        st.rerun()

    st.divider()
    st.subheader("Insumos Cadastrados")

    insumos = buscar_insumos()
    if not insumos:
        st.info("Nenhum insumo cadastrado ainda.")
    else:
        CRITICO_ICONE = {"Alto": "🔴", "Médio": "🟡", "Baixo": "🟢"}
        for item in insumos:
            endereco = buscar_rota_por_id(item['rota_designada_produto'])
            icone = CRITICO_ICONE.get(item['nivel_criticidade'], "⚪")
            with st.container(border=True):
                col_info, col_del = st.columns([0.94, 0.06])
                with col_info:
                    st.markdown(f"**{icone} {item['nome']}**")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Quantidade", item['quantidade'])
                    c2.metric("Peso unit.", f"{item['peso']} kg")
                    c3.metric("Criticidade", item['nivel_criticidade'])
                    c4.metric("Janela", item['janela_entrega'])
                    if endereco:
                        st.caption(f"📍 {endereco['rua']}, {endereco['numero']} — {endereco['cidade']} ({endereco['cep']})")
                with col_del:
                    st.write("")
                    st.write("")
                    if st.button("🗑️", key=f"del_ins_{item['produto_id']}", help="Excluir"):
                        excluir_insumo(item['produto_id'])
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: VEÍCULOS
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🚛 Veículos":
    st.title("🚛 Gestão de Frotas")
    st.caption("Cadastre e monitore os veículos de entrega")
    st.divider()

    with st.container(border=True):
        st.subheader("Novo Veículo")
        with st.form("form_veiculo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            modelo     = c1.text_input("Modelo", placeholder="Ex: Mercedes Accelo 1016")
            placa      = c1.text_input("Placa", placeholder="Ex: ABC-1234")
            capacidade = c2.number_input("Capacidade Máxima (kg)", min_value=0.0)
            autonomia  = c2.number_input("Autonomia Total (km)", min_value=0)

            if st.form_submit_button("Cadastrar Veículo", type="primary", use_container_width=True):
                if modelo and placa:
                    try:
                        cadastrar_veiculo(modelo, placa, capacidade, capacidade, autonomia)
                        st.toast(f"Veículo {placa} cadastrado!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    st.divider()
    st.subheader("Veículos Cadastrados")

    veiculos = buscar_veiculos()
    if not veiculos:
        st.info("Nenhum veículo cadastrado ainda.")
    else:
        for v in veiculos:
            with st.container(border=True):
                col_info, col_del = st.columns([0.94, 0.06])
                with col_info:
                    st.markdown(f"**🚛 {v['modelo_caminhao']}** — `{v['placa']}`")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Capacidade máx.", f"{v['capacidade_maxima']} kg")
                    c2.metric("Disponível", f"{v['capacidade_disponivel']} kg")
                    c3.metric("Autonomia", f"{v['autonomia_total']} km")
                    uso = v['capacidade_maxima'] - v['capacidade_disponivel']
                    pct = uso / v['capacidade_maxima'] if v['capacidade_maxima'] else 0
                    st.progress(pct, text=f"Carga ocupada: {uso:.1f} kg ({pct*100:.0f}%)")
                with col_del:
                    st.write("")
                    st.write("")
                    st.write("")
                    if st.button("🗑️", key=f"del_v_{v['veiculo_id']}", help="Excluir veículo"):
                        excluir_veiculo(v['veiculo_id'])
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: ROTAS
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📍 Rota dos Veículos":
    st.title("📍 Rota dos Veículos")
    st.caption("Cadastre os pontos de entrega vinculados a cada veículo")
    st.divider()

    with st.container(border=True):
        st.subheader("Novo Ponto de Entrega")
        with st.form("form_rota", clear_on_submit=True):
            c1, c2 = st.columns([3, 1])
            rua    = c1.text_input("Rua", placeholder="Ex: Av. Paulista")
            numero = c2.number_input("Número", min_value=0, step=1)

            c3, c4 = st.columns(2)
            complemento = c3.text_input("Complemento", placeholder="Ex: Bloco A")
            veiculos = buscar_veiculos()
            lista_placas = [v['placa'] for v in veiculos]
            veiculo_selecionado = c4.selectbox("Veículo", lista_placas)

            c5, c6 = st.columns(2)
            cidade = c5.text_input("Cidade", placeholder="Ex: São Paulo")
            cep    = c6.text_input("CEP", placeholder="Ex: 01311-000")

            if st.form_submit_button("Cadastrar Endereço", type="primary", use_container_width=True):
                if rua and numero:
                    placa_envio = None if veiculo_selecionado == "Nenhum" else veiculo_selecionado
                    endereco_str = f"{rua}, {numero}, {cidade}, {cep}"
                    latitude, longitude = converter_endereco_para_coords(endereco_str)
                    if latitude is None:
                        st.warning(f"Endereço não encontrado: {endereco_str}")
                    else:
                        try:
                            sucesso = cadastrar_rota(rua, numero, complemento, cidade, cep, placa_envio, latitude, longitude)
                            if sucesso:
                                st.toast(f"Endereço cadastrado!", icon="📍")
                                st.rerun()
                            else:
                                st.error("Erro ao salvar no banco.")
                        except Exception as e:
                            st.error(f"Erro: {e}")
                else:
                    st.warning("Preencha a rua e o número.")

    st.divider()
    st.subheader("Pontos de Entrega Cadastrados")

    rotas = listar_rotas()
    if not rotas:
        st.info("Nenhum endereço cadastrado ainda.")
    else:
        for r in rotas:
            placa_v = buscar_veiculo_por_id(r['veiculo_designado_rota'])['placa'] if r['veiculo_designado_rota'] else "—"
            with st.container(border=True):
                col_info, col_del = st.columns([0.94, 0.06])
                with col_info:
                    st.markdown(f"**📍 {r['rua']}, {r['numero']}** — {r['cidade']}")
                    c1, c2, c3 = st.columns(3)
                    c1.caption(f"CEP: {r['cep']}")
                    c2.caption(f"Complemento: {r['complemento'] or '—'}")
                    c3.caption(f"Veículo: {placa_v}")
                with col_del:
                    st.write("")
                    if st.button("🗑️", key=f"del_rota_{r['rota_id']}", help="Remover"):
                        if excluir_rota(r['rua'], r['numero']):
                            st.toast("Endereço removido!", icon="🗑️")
                            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: PONTO DE PARTIDA
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🏠 Partida Inicial de Veículos":
    st.title("🏠 Ponto de Partida")
    st.caption("Defina a base/depósito de onde cada veículo iniciará a rota")
    st.divider()

    with st.container(border=True):
        st.subheader("Nova Base")
        with st.form("form_ponto_base"):
            c1, c2 = st.columns([3, 1])
            rua_b    = c1.text_input("Rua", placeholder="Ex: Av. Paulista")
            numero_b = c2.number_input("Número", min_value=0, step=1)

            veiculos = buscar_veiculos()
            lista_placas = [v['placa'] for v in veiculos]
            placa_v = st.selectbox("Veículo", lista_placas)

            c3, c4 = st.columns(2)
            cidade_b = c3.text_input("Cidade", placeholder="Ex: São Paulo")
            cep_b    = c4.text_input("CEP", placeholder="Ex: 01311-000")
            nome_b   = st.text_input("Nome da Base", placeholder="Ex: Depósito Central")

            if st.form_submit_button("Salvar Ponto Base", type="primary", use_container_width=True):
                id_v = next(v['veiculo_id'] for v in veiculos if v['placa'] == placa_v)
                if buscar_ponto_base_por_veiculo(id_v):
                    st.error(f"O veículo {placa_v} já possui um ponto base cadastrado.")
                else:
                    endereco_str = f"{rua_b}, {numero_b}, {cidade_b}, {cep_b}"
                    latitude, longitude = converter_endereco_para_coords(endereco_str)
                    if latitude is None:
                        st.warning(f"Endereço inválido: {endereco_str}")
                    else:
                        cadastrar_ponto_base(rua_b, numero_b, cidade_b, id_v, cep_b, nome_b, latitude, longitude)
                        st.success("Ponto base salvo com sucesso!")
                        st.rerun()

    st.divider()
    st.subheader("Bases Cadastradas")

    bases = buscar_enderecos_bases()
    if not bases:
        st.info("Nenhuma base cadastrada ainda.")
    else:
        for r in bases:
            placa_v = buscar_veiculo_por_id(r['veiculo_id'])['placa'] if r['veiculo_id'] else "—"
            with st.container(border=True):
                col_info, col_del = st.columns([0.94, 0.06])
                with col_info:
                    st.markdown(f"**🏠 {r['nome_da_base']}**")
                    c1, c2 = st.columns(2)
                    c1.caption(f"📍 {r['rua']}, {r['numero']} — {r['cidade']} ({r['cep']})")
                    c2.caption(f"🚛 Veículo: {placa_v}")
                with col_del:
                    st.write("")
                    if st.button("🗑️", key=f"del_base_{r['ponto_base_id']}", help="Remover"):
                        if excluir_ponto_base(r['rua'], r['numero'], r['cep']):
                            st.toast("Base removida!", icon="🗑️")
                            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: OTIMIZAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🚀 Otimização":
    st.title("🚀 Otimização de Rotas")
    st.caption("Algoritmo Genético aplicado à entrega de insumos hospitalares")
    st.divider()

    # ── Seleção de veículo ────────────────────────────────────────────────────
    with st.container(border=True):
        st.subheader("1. Selecione o Veículo")
        veiculos = buscar_veiculos()
        dict_veiculos = {v['placa']: v['veiculo_id'] for v in veiculos}
        placa_selecionada = st.selectbox("Veículo", list(dict_veiculos.keys()), label_visibility="collapsed")

        veiculo_id = dict_veiculos[placa_selecionada]
        rota_id_para_indice = {
            rota['rota_id']: idx + 1
            for idx, rota in enumerate(listar_rotas_por_veiculo(veiculo_id))
        }
        ponto_saida      = buscar_ponto_base_por_veiculo(veiculo_id)
        rotas_do_veiculo = listar_rotas_por_veiculo(veiculo_id)

        if not ponto_saida:
            st.error(f"O veículo **{placa_selecionada}** não tem Ponto Base cadastrado.")
        elif not rotas_do_veiculo:
            st.warning(f"O veículo **{placa_selecionada}** não tem destinos vinculados.")
        else:
            c1, c2 = st.columns(2)
            c1.success(f"🏠 **Base:** {ponto_saida['rua']}, {ponto_saida['numero']} — {ponto_saida['cidade']}")
            c2.info(f"📦 **{len(rotas_do_veiculo)} destinos** cadastrados para este veículo")

            with st.expander("Ver lista de destinos"):
                for i, r in enumerate(rotas_do_veiculo, 1):
                    st.write(f"{i}. {r['rua']}, {r['numero']} — {r['cidade']}")

            if st.button("🗺️ Carregar Dados da Rota", type="primary", use_container_width=True):
                veiculo_selecionado = next(v for v in veiculos if v['veiculo_id'] == veiculo_id)
                dados_produtos      = buscar_detalhes_insumo_e_veiculo(veiculo_id)
                produtos_por_parada = {}

                for produto in dados_produtos:
                    rota_id = produto['rota_designada_produto']
                    if rota_id not in rota_id_para_indice:
                        continue
                    indice_ag = rota_id_para_indice[rota_id]
                    produtos_por_parada.setdefault(indice_ag, []).append(produto)

                mapa_dados_por_indice = {}
                carga_total = 0
                for indice_ag in range(1, len(rotas_do_veiculo) + 1):
                    insumos = produtos_por_parada.get(indice_ag, [])
                    if insumos:
                        peso_total       = sum(float(p['peso']) for p in insumos)
                        criticidade_max  = max(int(p['nivel_criticidade']) for p in insumos)
                        item_critico     = max(insumos, key=lambda x: int(x['nivel_criticidade']))
                        janela_inicio    = item_critico['janela_entrega'].split(" - ")[0]
                        janela_fim       = item_critico['janela_entrega'].split(" - ")[1]
                        mapa_dados_por_indice[indice_ag] = {
                            'peso': peso_total, 'janela_inicio': janela_inicio,
                            'janela_fim': janela_fim, 'nivel_criticidade': criticidade_max,
                            'qtd_itens': len(insumos)
                        }
                        carga_total += peso_total
                    else:
                        mapa_dados_por_indice[indice_ag] = {
                            'peso': 0, 'janela_inicio': "08:00",
                            'janela_fim': "18:00", 'nivel_criticidade': 0, 'qtd_itens': 0
                        }

                if carga_total > veiculo_selecionado['capacidade_maxima']:
                    st.warning(f"Carga total ({carga_total} kg) excede a capacidade ({veiculo_selecionado['capacidade_maxima']} kg).")

                st.session_state['dados_otimizacao'] = {
                    'ponto_base': ponto_saida, 'destinos': rotas_do_veiculo,
                    'veiculo': veiculo_selecionado, 'mapa_dados': mapa_dados_por_indice,
                    'info_veiculo': {
                        'capacidade_maxima': veiculo_selecionado['capacidade_maxima'],
                        'autonomia_total':   veiculo_selecionado['autonomia_total']
                    }
                }
                st.success(f"✅ {len(dados_produtos)} insumos em {len(rotas_do_veiculo)} paradas. Pronto para otimizar!")

    # ── Parâmetros do GA ──────────────────────────────────────────────────────
    st.divider()
    with st.container(border=True):
        st.subheader("2. Parâmetros do Algoritmo Genético")
        c1, c2, c3 = st.columns(3)
        populacao_size = c1.slider("Tamanho da População", 10, 200, 50)
        n_geracoes     = c2.slider("Número de Gerações",   10, 500, 100)
        mutation_prob  = c3.slider("Taxa de Mutação",       0.0, 1.0, 0.2)
        btn_processar  = st.button("▶ Executar Algoritmo Genético", type="primary", use_container_width=True)

    # ── Execução ──────────────────────────────────────────────────────────────
    if btn_processar:
        if 'dados_otimizacao' not in st.session_state:
            st.error("Clique em **Carregar Dados da Rota** antes de executar.")
            st.stop()

        dados       = st.session_state['dados_otimizacao']
        dados_paradas = dados['mapa_dados']
        info_veiculo  = dados['info_veiculo']

        dados_geo, nao_encontrados = preparar_coordenadas_geograficas(veiculo_id)
        if nao_encontrados:
            st.error("Endereços inválidos impedem a execução.")
            st.stop()

        coords       = listar_coordenadas_por_veiculo(veiculo_id)
        dist_matrix  = matriz_distancia(coords)
        indices_entregas = list(range(1, len(coords)))

        populacao = [[0] + random.sample(indices_entregas, len(indices_entregas)) + [0]
                     for _ in range(populacao_size)]

        scores_iniciais      = [calculo_fitness_matriz_distancia(ind, dist_matrix, dados_paradas, info_veiculo) for ind in populacao]
        initial_best_fitness = min(scores_iniciais)
        best_fitness_values  = []
        start_time           = time.time()

        def selecao_torneio(pop, fits, k=3):
            sel = random.sample(list(zip(fits, pop)), k)
            sel.sort(key=lambda x: x[0])
            return copy.deepcopy(sel[0][1])

        st.divider()
        st.subheader("3. Evolução em Tempo Real")
        col_mapa, col_grafico = st.columns(2)
        with col_mapa:
            st.caption("Visualização da Rota")
            mapa_placeholder = st.empty()
        with col_grafico:
            st.caption("Curva de Convergência")
            grafico_placeholder = st.empty()
        metric_placeholder = st.empty()

        melhor_ind   = None
        melhor_score = None

        for generation in range(n_geracoes):
            scores       = [calculo_fitness_matriz_distancia(ind, dist_matrix, dados_paradas, info_veiculo) for ind in populacao]
            melhor_score = min(scores)
            melhor_ind   = populacao[scores.index(melhor_score)]
            best_fitness_values.append(melhor_score)

            nova_populacao = [melhor_ind]
            while len(nova_populacao) < populacao_size:
                filho = order_crossover(selecao_torneio(populacao, scores), selecao_torneio(populacao, scores))
                nova_populacao.append(mutacao(filho, mutation_prob))
            populacao = nova_populacao

            if generation % 5 == 0 or generation == n_geracoes - 1:
                coords_np   = np.array(coords)
                rota_coords = coords_np[melhor_ind]

                fig_mapa, ax = plt.subplots(figsize=(7, 5))
                fig_mapa.patch.set_facecolor("white")
                ax.set_facecolor("#f8fafc")
                ax.plot(rota_coords[:, 1], rota_coords[:, 0], '-', color="#94a3b8", linewidth=1.2, zorder=1)
                ax.scatter(coords_np[1:, 1], coords_np[1:, 0], c="#3b82f6", s=60, zorder=2, label="Entregas")
                ax.scatter(coords_np[0, 1], coords_np[0, 0], c="#ef4444", marker="*", s=250, zorder=3, label="Base")
                ax.set_title(f"Geração {generation} | Custo: {fmt_br(melhor_score)}", fontsize=11, fontweight="bold")
                ax.legend(fontsize=9, framealpha=0.8)
                ax.tick_params(labelsize=8)
                for spine in ax.spines.values():
                    spine.set_edgecolor("#e2e8f0")
                fig_mapa.tight_layout()
                mapa_placeholder.pyplot(fig_mapa)
                plt.close(fig_mapa)

                fig_fit, ax2 = plt.subplots(figsize=(7, 5))
                fig_fit.patch.set_facecolor("white")
                ax2.set_facecolor("#f8fafc")
                ax2.plot(best_fitness_values, color="#3b82f6", linewidth=2)
                ax2.fill_between(range(len(best_fitness_values)), best_fitness_values, alpha=0.1, color="#3b82f6")
                ax2.set_title("Curva de Convergência", fontsize=11, fontweight="bold")
                ax2.set_xlabel("Geração", fontsize=9)
                ax2.set_ylabel("Custo", fontsize=9)
                ax2.tick_params(labelsize=8)
                for spine in ax2.spines.values():
                    spine.set_edgecolor("#e2e8f0")
                fig_fit.tight_layout()
                grafico_placeholder.pyplot(fig_fit)
                plt.close(fig_fit)

                diff = melhor_score - initial_best_fitness
                metric_placeholder.metric("Fitness Atual", fmt_br(melhor_score), delta=fmt_br(diff), delta_color="inverse")
                time.sleep(0.02)

        metric_placeholder.empty()

        total_time  = time.time() - start_time
        improvement = ((initial_best_fitness - melhor_score) / initial_best_fitness) * 100
        paradas_ordenadas = [dados['destinos'][idx - 1] for idx in melhor_ind[1:-1]]

        # Salva tudo no session_state para persistir entre reruns
        st.session_state['resultado_otimizacao'] = {
            'placa':               placa_selecionada,
            'ponto_base':          dados['ponto_base'],
            'destinos':            dados['destinos'],
            'paradas_ordenadas':   paradas_ordenadas,
            'custo_inicial':       initial_best_fitness,
            'custo_otimizado':     melhor_score,
            'melhoria':            improvement,
            'total_time':          total_time,
            'n_paradas':           len(paradas_ordenadas),
            'populacao':           populacao_size,
            'geracoes':            n_geracoes,
            'mutacao':             mutation_prob,
            'coords':              coords,
            'melhor_ind':          melhor_ind,
            'best_fitness_values': best_fitness_values,
        }

    # ── Resultado + Mapa + IA (fora do btn_processar — persiste entre reruns) ─
    if 'resultado_otimizacao' in st.session_state:
        res = st.session_state['resultado_otimizacao']

        # ── Gráficos da evolução ──────────────────────────────────────────────
        st.divider()
        st.subheader("📈 Evolução do Algoritmo Genético")

        _coords_np    = np.array(res['coords'])
        _rota_coords  = _coords_np[res['melhor_ind']]
        _fitness_vals = res['best_fitness_values']

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.caption("Melhor rota encontrada")
            fig_r, ax_r = plt.subplots(figsize=(7, 5))
            fig_r.patch.set_facecolor("white")
            ax_r.set_facecolor("#f8fafc")
            ax_r.plot(_rota_coords[:, 1], _rota_coords[:, 0], '-', color="#94a3b8", linewidth=1.2, zorder=1)
            ax_r.scatter(_coords_np[1:, 1], _coords_np[1:, 0], c="#3b82f6", s=60, zorder=2, label="Entregas")
            ax_r.scatter(_coords_np[0, 1], _coords_np[0, 0], c="#ef4444", marker="*", s=250, zorder=3, label="Base")
            ax_r.set_title(f"Rota final | Custo: {fmt_br(res['custo_otimizado'])}", fontsize=11, fontweight="bold")
            ax_r.legend(fontsize=9, framealpha=0.8)
            ax_r.tick_params(labelsize=8)
            for spine in ax_r.spines.values():
                spine.set_edgecolor("#e2e8f0")
            fig_r.tight_layout()
            st.pyplot(fig_r)
            plt.close(fig_r)

        with col_g2:
            st.caption("Curva de convergência")
            fig_f, ax_f = plt.subplots(figsize=(7, 5))
            fig_f.patch.set_facecolor("white")
            ax_f.set_facecolor("#f8fafc")
            ax_f.plot(_fitness_vals, color="#3b82f6", linewidth=2)
            ax_f.fill_between(range(len(_fitness_vals)), _fitness_vals, alpha=0.1, color="#3b82f6")
            ax_f.set_title("Curva de Convergência", fontsize=11, fontweight="bold")
            ax_f.set_xlabel("Geração", fontsize=9)
            ax_f.set_ylabel("Custo", fontsize=9)
            ax_f.tick_params(labelsize=8)
            for spine in ax_f.spines.values():
                spine.set_edgecolor("#e2e8f0")
            fig_f.tight_layout()
            st.pyplot(fig_f)
            plt.close(fig_f)

        # ── Métricas de resultado ─────────────────────────────────────────────
        st.divider()
        st.subheader("4. Resultado Final")

        c1, c2, c3 = st.columns(3)
        c1.metric("⏱️ Tempo de Execução", f"{res['total_time']:.2f} s")
        c2.metric("🎲 Fitness Inicial (km + penalidades)", fmt_br(res['custo_inicial']))
        c3.metric("✅ Distância Otimizada (km)",          fmt_br(res['custo_otimizado']), delta=f"-{res['melhoria']:.1f}%", delta_color="inverse")

        st.divider()
        st.caption("**Parâmetros utilizados no Algoritmo Genético**")
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("👥 População",  res['populacao'])
        p2.metric("🔁 Gerações",   res['geracoes'])
        p3.metric("🧬 Mutação",    f"{res['mutacao']:.0%}")
        p4.metric("📍 Paradas",    res['n_paradas'])
        p5.metric("📈 Melhoria",   f"{res['melhoria']:.1f}%")

        if res['custo_otimizado'] > 5000:
            st.warning("⚠️ A rota viola restrições de carga ou autonomia. Tente outro veículo ou reduza as paradas.")

        # ── Mapa Folium ───────────────────────────────────────────────────────
        st.divider()
        st.subheader("🗺️ Rota Otimizada no Mapa")

        _coords    = res['coords']
        _melhor    = res['melhor_ind']
        _destinos  = res['destinos']
        centro     = [_coords[0][0], _coords[0][1]]

        m = folium.Map(location=centro, zoom_start=13, tiles="CartoDB positron")

        folium.Marker(
            location=centro,
            tooltip="Base de Partida",
            popup=f"{res['ponto_base']['rua']}, {res['ponto_base']['numero']}",
            icon=folium.Icon(color="red", icon="home", prefix="fa")
        ).add_to(m)

        for i, idx in enumerate(_melhor[1:-1], 1):
            dest    = _destinos[idx - 1]
            lat, lon = _coords[idx]
            folium.Marker(
                location=[lat, lon],
                tooltip=f"Parada {i}: {dest['rua']}, {dest['numero']}",
                popup=f"<b>#{i}</b> — {dest['rua']}, {dest['numero']}<br>{dest['cidade']}",
                icon=folium.DivIcon(
                    html=f'<div style="background:#3b82f6;color:white;border-radius:50%;'
                         f'width:26px;height:26px;display:flex;align-items:center;'
                         f'justify-content:center;font-weight:bold;font-size:11px;'
                         f'border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4)">{i}</div>',
                    icon_size=(26, 26), icon_anchor=(13, 13)
                )
            ).add_to(m)

        rota_coords = [(_coords[i][0], _coords[i][1]) for i in _melhor]
        folium.PolyLine(rota_coords, color="#3b82f6", weight=3, opacity=0.8, dash_array="6").add_to(m)

        st_folium(m, use_container_width=True, height=460)

        # ── IA ────────────────────────────────────────────────────────────────
        st.divider()
        st.subheader("5. Relatório & Instruções com IA 🤖")

        tab_instrucoes, tab_relatorio, tab_chat = st.tabs([
            "📋 Instruções para Motorista",
            "📊 Relatório de Eficiência",
            "💬 Perguntas sobre a Rota"
        ])

        # ── Tab: Instruções ───────────────────────────────────────────────────
        with tab_instrucoes:
            if st.button("Gerar Instruções", type="primary", use_container_width=True):
                with st.spinner("Gerando instruções com IA..."):
                    try:
                        instrucoes = gerar_instrucoes_motorista(
                            res['placa'],
                            res['ponto_base'],
                            res['paradas_ordenadas'],
                            res['custo_otimizado']
                        )
                        st.session_state['instrucoes_llm'] = instrucoes
                    except Exception as e:
                        st.error(f"Erro ao chamar a IA: {e}")

            if 'instrucoes_llm' in st.session_state:
                st.markdown(st.session_state['instrucoes_llm'])

        # ── Tab: Relatório ────────────────────────────────────────────────────
        with tab_relatorio:
            if st.button("Gerar Relatório", type="primary", use_container_width=True):
                with st.spinner("Gerando relatório com IA..."):
                    try:
                        relatorio = gerar_relatorio_eficiencia(
                            res['placa'],
                            res['n_paradas'],
                            res['custo_inicial'],
                            res['custo_otimizado'],
                            res['melhoria'],
                            res['total_time'],
                            res['populacao'],
                            res['geracoes'],
                            res['mutacao']
                        )
                        st.session_state['relatorio_llm'] = relatorio
                    except Exception as e:
                        st.error(f"Erro ao chamar a IA: {e}")

            if 'relatorio_llm' in st.session_state:
                st.markdown(st.session_state['relatorio_llm'])

        # ── Tab: Chat ─────────────────────────────────────────────────────────
        with tab_chat:
            st.caption("Faça perguntas em linguagem natural sobre a rota otimizada.")

            if 'chat_history' not in st.session_state:
                st.session_state['chat_history'] = []

            for msg in st.session_state['chat_history']:
                with st.chat_message(msg['role']):
                    st.write(msg['content'])

            if pergunta := st.chat_input("Ex: Qual é a primeira entrega? Quais são os insumos críticos?"):
                st.session_state['chat_history'].append({"role": "user", "content": pergunta})
                with st.chat_message("user"):
                    st.write(pergunta)

                contexto = {
                    'placa':           res['placa'],
                    'paradas':         ", ".join([f"{p['rua']}, {p['numero']}" for p in res['paradas_ordenadas']]),
                    'custo_otimizado': res['custo_otimizado'],
                    'melhoria':        res['melhoria'],
                    'n_paradas':       res['n_paradas'],
                }

                with st.chat_message("assistant"):
                    with st.spinner("Pensando..."):
                        try:
                            historico_api = [
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state['chat_history'][:-1]
                            ]
                            resposta = responder_pergunta(pergunta, contexto, historico_api)
                            st.write(resposta)
                            st.session_state['chat_history'].append({"role": "assistant", "content": resposta})
                        except Exception as e:
                            st.error(f"Erro ao chamar a IA: {e}")
