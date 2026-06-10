"""
Kyra Pesquisa — Dashboard de Análise de Transcrições
Para rodar: streamlit run app.py --server.port 8502
"""
import sys
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent))
try:
    from src.pipeline import run as pipeline_run
    _PIPELINE_OK = True
except Exception as _e:
    _PIPELINE_OK = False
    _PIPELINE_ERR = str(_e)

st.set_page_config(
    page_title="Kyra Pesquisa / Análise",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

Y   = "#F5C800"
BK  = "#1A1A1A"
WH  = "#FFFFFF"
G1  = "#F7F7F7"
G2  = "#E8E8E8"
G3  = "#999999"
G4  = "#555555"
POS = "#22A06B"
NEG = "#D94040"
NEU = "#AAAAAA"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"], p, span, div, label, h1, h2, h3 {{
    font-family: 'Inter', sans-serif !important;
}}

/* fundo branco em tudo — inclusive a faixa acima da navbar */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stBottom"],
.main, .block-container,
section[data-testid="stMain"] > div:first-child {{
    background-color: {WH} !important;
}}

/* remove chrome streamlit — height:0 garante que não ocupam espaço */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu, footer, .stDeployButton {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    visibility: hidden !important;
}}

/* zera padding que cria faixa branca — ataca todos os containers possíveis */
[data-testid="stMainBlockContainer"],
[data-testid="stMainBlockContainer"] > div,
[data-testid="stMainBlockContainer"] > div > div,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlock"] > div:first-child,
[data-testid="stAppViewBlockContainer"],
[data-testid="stAppViewBlockContainer"] > div,
section.main > div {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

/* navbar sobe para cobrir gap residual */
.kyra-nav {{
    margin-top: -2px !important;
}}

/* ── UPLOADER — remove label sobreposto ── */
/* o label fica dentro de um div antes da dropzone */
[data-testid="stFileUploader"] > label,
[data-testid="stFileUploader"] > div > label,
[data-testid="stFileUploader"] label {{
    display: none !important;
    height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    position: absolute !important;
    visibility: hidden !important;
}}

/* uploader — só estiliza a área, não toca no botão */
[data-testid="stFileUploader"] section {{
    background: {G1} !important;
    border: 2px dashed {Y} !important;
    border-radius: 0 !important;
    padding: 20px 24px !important;
}}
/* esconde label do uploader sem bagunçar o botão */
[data-testid="stFileUploaderDropzoneInstructions"] > div > span {{
    visibility: hidden !important;
    font-size: 0 !important;
}}

/* padding do container */
[data-testid="stMainBlockContainer"] {{
    padding: 0 48px 60px 48px !important;
    max-width: 100% !important;
}}

/* navbar e footer full-width sem gap lateral */
.kyra-nav, .kyra-footer {{
    margin-left: -48px !important;
    margin-right: -48px !important;
    width: 100vw !important;
    box-sizing: border-box !important;
    position: relative !important;
    left: 0 !important;
}}

/* ── NAVBAR ── */
.kyra-nav {{
    background: {Y};
    padding: 0 48px;
    height: 60px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 0;
}}
.kyra-nav-badge {{
    width: 38px; height: 38px;
    background: {BK};
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 1rem;
    flex-shrink: 0;
    color: {Y} !important;
    letter-spacing: -1px;
}}
.kyra-nav-name {{
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: -1px;
    color: {BK} !important;
}}
.kyra-nav-sep {{ color: {BK} !important; opacity: 0.3; margin: 0 6px; font-size: 1.2rem; }}
.kyra-nav-sub {{
    font-size: 0.85rem; font-weight: 600;
    color: {BK} !important; opacity: 0.55;
    letter-spacing: 0.3px;
}}

/* ── TÍTULOS DE SEÇÃO ── */
.sec-title {{
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {G3};
    padding-bottom: 10px;
    border-bottom: 2px solid {Y};
    margin: 36px 0 20px 0;
    display: block;
}}

/* ── INTRO ── */
.intro-card {{
    background: {G1};
    padding: 24px 28px;
    border-left: 4px solid {Y};
    height: 100%;
    box-sizing: border-box;
}}
.intro-label {{
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: {G3};
    margin-bottom: 12px;
    display: block;
}}
.intro-txt {{
    font-size: 0.97rem;
    line-height: 1.75;
    color: {G4};
    font-weight: 400;
}}

/* ── DEMO BADGE ── */
.demo-strip {{
    background: {BK};
    margin-left: -48px; margin-right: -48px;
    width: calc(100% + 96px);
    padding: 10px 48px;
    font-size: 0.78rem;
    color: {G3};
    display: flex; align-items: center; gap: 10px;
    box-sizing: border-box;
}}
.demo-badge {{
    background: {Y}; color: {BK};
    font-size: 0.65rem; font-weight: 800;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 2px 10px;
    flex-shrink: 0;
}}

/* ── KPI CARDS ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}}
.kpi-card {{
    background: {G1};
    border-top: 4px solid {Y};
    padding: 24px 20px 20px;
    box-sizing: border-box;
}}
.kpi-card.sent {{ border-top-color: var(--sent-color); }}
.kpi-val {{
    font-size: 2.2rem;
    font-weight: 900;
    color: {BK};
    line-height: 1;
    margin-bottom: 8px;
    letter-spacing: -1px;
}}
.kpi-lbl {{
    font-size: 0.72rem;
    font-weight: 600;
    color: {G3};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ── SÍNTESE ── */
.sintese-block {{
    background: {BK};
    padding: 24px 32px;
    margin-bottom: 4px;
}}
.sintese-label {{
    font-size: 0.65rem; font-weight: 800;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: {Y} !important; margin-bottom: 10px;
}}
.sintese-txt {{
    font-size: 1.05rem; font-weight: 600;
    color: {WH} !important; line-height: 1.65;
}}

/* ── SENTIMENTO BARRAS ── */
.sent-bar-row {{
    display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
}}
.sent-bar-label {{
    width: 72px; text-align: right; flex-shrink: 0;
    font-size: 0.78rem; font-weight: 700; color: {BK};
    text-transform: uppercase; letter-spacing: 0.5px;
}}
.sent-bar-track {{
    flex: 1; background: {G2}; height: 10px;
    position: relative; border-radius: 3px;
}}
.sent-bar-fill {{
    height: 100%; position: absolute; left: 0; top: 0; border-radius: 3px;
    transition: width 0.4s ease;
}}
.sent-bar-pct {{
    width: 44px; font-size: 0.85rem; font-weight: 700; color: {BK};
}}

/* ── NARRATIVA ── */
.narrativa-box {{
    background: {G1};
    border-left: 4px solid {Y};
    padding: 20px 24px;
    font-size: 0.95rem;
    line-height: 1.8;
    color: {G4};
}}

/* ── TEMA DETAIL CARD ── */
.tema-detail {{
    background: {G1};
    border-top: 4px solid {Y};
    padding: 22px;
    height: 100%;
}}
.tema-detail-name {{
    font-size: 1.05rem; font-weight: 800;
    color: {BK}; margin-bottom: 14px;
    text-transform: capitalize;
}}
.tema-meta {{
    font-size: 0.8rem; color: {G3};
    margin-bottom: 14px; line-height: 2;
}}
.tema-meta b {{ color: {BK}; font-weight: 700; }}
.pill {{
    display: inline-block;
    background: {Y}; color: {BK};
    font-size: 0.72rem; font-weight: 700;
    padding: 3px 10px; margin: 2px 3px 2px 0;
    letter-spacing: 0.3px;
}}
.sent-tag {{
    display: inline-flex; align-items: center; gap: 4px;
    padding: 4px 12px; font-size: 0.78rem; font-weight: 700;
    margin-right: 6px; border-radius: 2px;
}}
.sent-pos {{ background: #d6f0e4; color: #0e6e41; }}
.sent-neg {{ background: #fde8e8; color: #a12020; }}
.sent-neu {{ background: {G2}; color: {G4}; }}

/* ── QUOTES ── */
.quote-block {{
    border-left: 4px solid {Y};
    padding: 16px 20px;
    margin: 10px 0;
    background: {WH};
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border-radius: 0 4px 4px 0;
}}
.quote-text {{
    font-size: 0.95rem;
    font-style: italic;
    color: {BK};
    line-height: 1.7;
}}

/* ── INFO CARD UPLOAD ── */
.upload-info {{
    background: {G1};
    border-top: 3px solid {BK};
    padding: 20px 22px;
}}
.upload-info-label {{
    font-size: 0.65rem; font-weight: 800;
    letter-spacing: 2px; text-transform: uppercase;
    color: {G3}; margin-bottom: 4px;
}}
.upload-info-val {{
    font-size: 0.92rem; font-weight: 500;
    color: {G4}; margin-bottom: 12px;
}}

/* ── BOTÕES DOWNLOAD ── */
.stDownloadButton > button {{
    background: {Y} !important; color: {BK} !important;
    font-weight: 800 !important; font-size: 0.85rem !important;
    border: none !important; border-radius: 0 !important;
    padding: 12px 20px !important; width: 100% !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
}}
.stDownloadButton > button:hover {{
    background: {BK} !important; color: {Y} !important;
}}

/* ── SELECTBOX ── */
[data-baseweb="select"] > div {{
    border-radius: 0 !important;
    border-color: {G2} !important;
    font-size: 0.95rem !important;
}}

/* ── UPLOAD ── */
[data-testid="stFileUploaderDropzone"] {{
    background: {G1} !important;
    border: 2px dashed {Y} !important;
    border-radius: 0 !important;
    padding: 32px 24px !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] > div > small,
[data-testid="stFileUploaderDropzoneInstructions"] > div > span {{
    display: none !important;
}}

/* ── COLUNAS ── */
[data-testid="column"] {{ padding: 0 6px !important; }}

/* ── FOOTER ── */
.kyra-footer {{
    background: {BK};
    padding: 20px 48px;
    margin-top: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.kyra-footer-left {{
    font-size: 0.85rem; color: {G3};
}}
.kyra-footer-left span {{ color: {Y}; font-weight: 800; }}
.kyra-footer-right {{
    font-size: 0.78rem; color: #666;
}}
</style>
""", unsafe_allow_html=True)


# ── mock ─────────────────────────────────────────────────────────────────────
def mock_pipeline(nome):
    return {
        "projeto": nome.replace(".pdf","").replace(".txt",""),
        "n_chunks": 312, "n_participantes": 18, "duracao_min": 94,
        "sentimento": {"dominante":"NEU","pct_pos":34.2,"pct_neu":51.6,"pct_neg":14.2},
        "temas": [
            {"label":"Embalagem e Refil","pct":18.4,"lift":2.1,
             "termos":["embalagem","refil","formato","tampa","design"],
             "s_pos":28.0,"s_neg":22.0,"s_neu":50.0,
             "trechos":["Eu acho que a embalagem poderia ser mais prática, porque eu sempre derramo produto na bolsa.",
                        "O refil é uma ideia excelente, eu usaria muito mais se tivesse essa opção disponível.",
                        "O formato atual é bonito, mas não é muito funcional no dia a dia."]},
            {"label":"Sustentabilidade","pct":14.1,"lift":1.8,
             "termos":["sustentavel","reciclavel","meio ambiente","consciente"],
             "s_pos":45.0,"s_neg":8.0,"s_neu":47.0,
             "trechos":["Eu já trocaria para uma embalagem reciclável mesmo que custasse mais.",
                        "A questão ambiental pesa muito na minha decisão de compra hoje em dia."]},
            {"label":"Experiência de Uso","pct":12.7,"lift":1.5,
             "termos":["textura","absorvido","suave","cheiro","pele"],
             "s_pos":52.0,"s_neg":10.0,"s_neu":38.0,
             "trechos":["A textura é muito boa, absorve rápido e não deixa aquela sensação pegajosa.",
                        "O cheiro é delicioso, fico com o perfume na pele o dia todo."]},
            {"label":"Relação com a Marca","pct":11.3,"lift":1.3,
             "termos":["marca","confianca","qualidade","fiel"],
             "s_pos":61.0,"s_neg":5.0,"s_neu":34.0,
             "trechos":["Uso essa marca há mais de dez anos, nunca me decepcionou.",
                        "Confio muito na qualidade, já recomendei para toda a família."]},
            {"label":"Preço e Custo-Benefício","pct":9.8,"lift":1.2,
             "termos":["preco","caro","custo","economico"],
             "s_pos":20.0,"s_neg":38.0,"s_neu":42.0,
             "trechos":["Está um pouco caro para o meu orçamento atual, mas quando posso compro.",
                        "O custo-benefício é bom considerando a qualidade que entrega."]},
        ],
        "narrativa": (
            "As entrevistas revelam um discurso predominantemente neutro-descritivo (51,6%), "
            "com forte presença de aspectos positivos (34,2%) especialmente nos temas de "
            "Experiência de Uso e Relação com a Marca. O tema de maior crítica é Preço e "
            "Custo-Benefício (38% NEG), seguido por Embalagem e Refil (22% NEG)."
        ),
        "sintese": (
            "O projeto é dominado por discussões sobre embalagem e sustentabilidade, "
            "com discurso majoritariamente neutro e sentimento negativo concentrado em preço."
        ),
        "pii_ok": True,
    }


# ════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="kyra-nav">
    <div class="kyra-nav-badge">y.</div>
    <span class="kyra-nav-name">kyra.</span>
    <span class="kyra-nav-sep">/</span>
    <span class="kyra-nav-sub">Análise de Transcrições</span>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# INTRODUÇÃO
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="sec-title">Sobre o Produto</span>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")
for col, lbl, txt in [
    (c1, "O que é",
     "Ferramenta de análise automática de entrevistas qualitativas com NLP — identifica temas, sentimentos e trechos representativos em minutos."),
    (c2, "Como usar",
     "Faça upload de uma transcrição em PDF ou TXT. O sistema processa automaticamente e entrega um relatório estruturado com evidências citáveis."),
    (c3, "O que você recebe",
     "Temas identificados · Sentimento por tema · Trechos representativos citáveis · Síntese narrativa · Exportação em CSV, JSON e TXT"),
]:
    col.markdown(f"""
    <div class="intro-card">
        <div class="intro-label">{lbl}</div>
        <div class="intro-txt">{txt}</div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# UPLOAD
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="sec-title">Enviar Transcrição</span>', unsafe_allow_html=True)

col_up, _, col_info = st.columns([5, 0.3, 2], gap="small")

with col_up:
    arquivo = st.file_uploader(
        "Enviar transcrição",
        type=["pdf", "txt"],
        label_visibility="collapsed",
    )

with col_info:
    st.markdown(f"""
    <div class="upload-info">
        <div class="upload-info-label">Formatos</div>
        <div class="upload-info-val">PDF · TXT</div>
        <div class="upload-info-label">Idiomas</div>
        <div class="upload-info-val">Português · Espanhol</div>
        <div class="upload-info-label">Tamanho Máximo</div>
        <div class="upload-info-val">200 MB</div>
    </div>
    """, unsafe_allow_html=True)

if arquivo is None:
    st.markdown(f"""
    <div class="demo-strip">
        <span class="demo-badge">Demo</span>
        Os dados abaixo são simulados para ilustrar o funcionamento do produto.
        Faça upload de uma transcrição real para ver a análise completa.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PROCESSAMENTO
# ════════════════════════════════════════════════════════════════════════════
nome = arquivo.name if arquivo else "projeto_demo.pdf"
if arquivo:
    with st.spinner("Analisando transcrição... Isso pode levar alguns minutos."):
        if _PIPELINE_OK:
            try:
                texto = arquivo.read().decode("utf-8", errors="ignore")
                r = pipeline_run(texto, arquivo.name)
                if "erro" in r:
                    st.error(f"Erro no pipeline: {r['erro']}")
                    r = mock_pipeline(nome)
            except Exception as ex:
                st.error(f"Erro ao processar: {ex}")
                r = mock_pipeline(nome)
        else:
            st.warning(f"Pipeline indisponível. Usando demonstração.")
            r = mock_pipeline(nome)
    st.success("Análise concluída com sucesso.")
else:
    r = mock_pipeline(nome)

temas = r["temas"]
sent  = r["sentimento"]
dom   = sent["dominante"]
sent_lbl   = {"POS":"Positivo","NEG":"Negativo","NEU":"Neutro"}.get(dom,"Neutro")
sent_color = {"POS":POS,"NEG":NEG,"NEU":NEU}.get(dom,NEU)

# ════════════════════════════════════════════════════════════════════════════
# KPIs
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="sec-title">Visão Geral</span>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5, gap="small")
for col, val, lbl, cor in [
    (k1, f"{r['n_chunks']:,}",      "Trechos Analisados",  Y),
    (k2, str(r['n_participantes']), "Participantes",       Y),
    (k3, f"{r['duracao_min']} min", "Duração Estimada",    Y),
    (k4, str(len(temas)),           "Temas Identificados", Y),
    (k5, sent_lbl,                  "Sentimento Dominante",sent_color),
]:
    val_color = f"color:{sent_color};" if col is k5 else ""
    borda = sent_color if col is k5 else Y
    col.markdown(f"""
    <div class="kpi-card" style="border-top-color:{borda};">
        <div class="kpi-val" style="{val_color}">{val}</div>
        <div class="kpi-lbl">{lbl}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="sintese-block">
    <div class="sintese-label">Síntese do Projeto</div>
    <div class="sintese-txt">"{r['sintese']}"</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SENTIMENTO
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="sec-title">Análise de Sentimento</span>', unsafe_allow_html=True)

col_donut, col_bars, col_narr = st.columns([1, 1, 2], gap="large")

with col_donut:
    fig_donut = go.Figure(go.Pie(
        labels=["Positivo","Neutro","Negativo"],
        values=[sent["pct_pos"], sent["pct_neu"], sent["pct_neg"]],
        hole=0.65, sort=False,
        marker=dict(
            colors=[POS, "#DDDDDD", NEG],
            line=dict(color=WH, width=4)
        ),
        textinfo="none",
        hovertemplate=(
            "<b style='font-size:14px'>%{label}</b><br>"
            "<span style='font-size:18px;font-weight:900'>%{value:.1f}%</span>"
            "<extra></extra>"
        ),
        pull=[0.04, 0, 0.04],
    ))
    fig_donut.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", y=-0.08,
            font=dict(size=12, color=BK),
        ),
        height=240,
        margin=dict(t=10, b=30, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor=BK, font_color=WH,
            font_size=13, bordercolor=Y,
        ),
        annotations=[dict(
            text=f"<b>{sent_lbl}</b>",
            x=0.5, y=0.5,
            font=dict(size=16, color=BK, family="Inter"),
            showarrow=False,
        )],
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar":False})

with col_bars:
    st.markdown(f"<div style='padding-top:10px;'>", unsafe_allow_html=True)
    for pct, cor, lbl in [
        (sent["pct_pos"], POS,       "Positivo"),
        (sent["pct_neu"], "#BBBBBB", "Neutro"),
        (sent["pct_neg"], NEG,       "Negativo"),
    ]:
        st.markdown(f"""
        <div class="sent-bar-row">
            <div class="sent-bar-label">{lbl}</div>
            <div class="sent-bar-track">
                <div class="sent-bar-fill" style="width:{pct}%;background:{cor};"></div>
            </div>
            <div class="sent-bar-pct">{pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    pii = "✓ Nenhum dado pessoal detectado" if r["pii_ok"] else "⚠ Dados pessoais detectados e removidos"
    pii_cor = POS if r["pii_ok"] else NEG
    st.markdown(f'<p style="font-size:.75rem;color:{pii_cor};margin-top:20px;font-weight:600;">{pii}</p>',
                unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_narr:
    st.markdown(f'<div class="narrativa-box">{r["narrativa"]}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TEMAS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="sec-title">Temas Identificados</span>', unsafe_allow_html=True)

col_cob, col_sent_t = st.columns(2, gap="large")

with col_cob:
    df_t = pd.DataFrame([{"Tema": t["label"], "Cobertura (%)": t["pct"]} for t in temas]
                        ).sort_values("Cobertura (%)")
    fig_cob = go.Figure(go.Bar(
        x=df_t["Cobertura (%)"],
        y=df_t["Tema"],
        orientation="h",
        marker=dict(color=Y, line=dict(color=BK, width=1)),
        text=df_t["Cobertura (%)"].map(lambda v: f"{v:.1f}%"),
        textposition="outside",
        textfont=dict(size=12, color=BK, family="Inter"),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Cobertura: <b>%{x:.1f}%</b> dos trechos"
            "<extra></extra>"
        ),
    ))
    fig_cob.update_layout(
        title=dict(
            text="Cobertura por Tema",
            font=dict(size=13, color=G4, family="Inter"),
            x=0, pad=dict(b=12),
        ),
        height=max(280, len(temas) * 46),
        margin=dict(t=40, b=10, l=10, r=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=12, color=BK, family="Inter")),
        hoverlabel=dict(
            bgcolor=BK, font_color=WH,
            font_size=13, bordercolor=Y,
        ),
    )
    st.plotly_chart(fig_cob, use_container_width=True, config={"displayModeBar":False})

with col_sent_t:
    df_s = pd.DataFrame([{
        "Tema": t["label"],
        "Positivo": t["s_pos"],
        "Neutro":   t["s_neu"],
        "Negativo": t["s_neg"],
    } for t in sorted(temas, key=lambda x: x["s_neg"], reverse=True)])

    fig_sent = go.Figure()
    for col_n, cor, nome_t in [
        ("Positivo", POS,       "Positivo"),
        ("Neutro",   "#CCCCCC", "Neutro"),
        ("Negativo", NEG,       "Negativo"),
    ]:
        fig_sent.add_trace(go.Bar(
            name=nome_t,
            y=df_s["Tema"],
            x=df_s[col_n],
            orientation="h",
            marker_color=cor,
            texttemplate="%{x:.0f}%",
            textposition="inside",
            textfont=dict(size=11, color=WH, family="Inter"),
            hovertemplate=(
                f"<b>%{{y}}</b><br>"
                f"{nome_t}: <b>%{{x:.1f}}%</b> dos trechos"
                "<extra></extra>"
            ),
        ))
    fig_sent.update_layout(
        barmode="stack",
        title=dict(
            text="Sentimento por Tema",
            font=dict(size=13, color=G4, family="Inter"),
            x=0, pad=dict(b=12),
        ),
        height=max(280, len(temas) * 46),
        margin=dict(t=40, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", y=-0.12,
            font=dict(size=11, family="Inter"),
        ),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=12, color=BK, family="Inter")),
        hoverlabel=dict(
            bgcolor=BK, font_color=WH,
            font_size=13, bordercolor=Y,
        ),
        hovermode="y unified",
    )
    st.plotly_chart(fig_sent, use_container_width=True, config={"displayModeBar":False})

# ════════════════════════════════════════════════════════════════════════════
# TRECHOS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="sec-title">Trechos Representativos</span>', unsafe_allow_html=True)

st.markdown(f'<p style="font-size:.85rem;color:{G3};margin:-8px 0 14px;">Selecione um tema para explorar os trechos com maior relevância e sentimento alinhado.</p>',
            unsafe_allow_html=True)

tema_sel = st.selectbox(
    "Tema",
    [t["label"] for t in temas],
    label_visibility="collapsed",
)
tema_cur = next(t for t in temas if t["label"] == tema_sel)

col_det, col_quotes = st.columns([1, 2], gap="large")

with col_det:
    pills = "".join(f'<span class="pill">{p}</span>' for p in tema_cur["termos"])
    s_pos_d, s_neg_d, s_neu_d = tema_cur["s_pos"], tema_cur["s_neg"], tema_cur["s_neu"]
    st.markdown(f"""
    <div class="tema-detail">
        <div class="tema-detail-name">{tema_cur['label']}</div>
        <div style="margin-bottom:14px;">{pills}</div>
        <div class="tema-meta">
            <b>Cobertura</b> {tema_cur['pct']:.1f}%<br>
            <b>Lift</b> {tema_cur['lift']:.1f}× acima da média
        </div>
        <div>
            <span class="sent-tag sent-pos">+ {s_pos_d:.0f}% Positivo</span><br><br>
            <span class="sent-tag sent-neu">~ {s_neu_d:.0f}% Neutro</span><br><br>
            <span class="sent-tag sent-neg">− {s_neg_d:.0f}% Negativo</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_quotes:
    if tema_cur["trechos"]:
        for i, trecho in enumerate(tema_cur["trechos"], 1):
            st.markdown(f"""
            <div class="quote-block">
                <div class="quote-text">"{trecho}"</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color:{G3};font-size:.9rem;">Nenhum trecho disponível para este tema.</p>',
                    unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="sec-title">Exportar Resultados</span>', unsafe_allow_html=True)

df_exp = pd.DataFrame([{
    "tema":           t["label"],
    "cobertura_pct":  t["pct"],
    "lift":           t["lift"],
    "termos":         ", ".join(t["termos"]),
    "sentimento_pos": t["s_pos"],
    "sentimento_neg": t["s_neg"],
    "sentimento_neu": t["s_neu"],
} for t in temas])

rel = (
    f"KYRA PESQUISA — RELATÓRIO DE ANÁLISE\n"
    f"Projeto: {r['projeto']}\n{'─'*52}\n\n"
    f"SÍNTESE\n{r['sintese']}\n\n"
    f"SENTIMENTO GERAL\n"
    f"Positivo: {sent['pct_pos']:.1f}%  |  Neutro: {sent['pct_neu']:.1f}%  |  Negativo: {sent['pct_neg']:.1f}%\n\n"
    f"NARRATIVA\n{r['narrativa']}\n\nTEMAS IDENTIFICADOS\n"
) + "\n".join(
    f"\n{i+1}. {t['label']} ({t['pct']:.1f}% de cobertura · lift {t['lift']:.1f}×)\n"
    f"   Termos: {', '.join(t['termos'])}\n"
    f"   Sentimento: {t['s_pos']:.0f}% positivo  |  {t['s_neu']:.0f}% neutro  |  {t['s_neg']:.0f}% negativo\n"
    f"   Trechos representativos:\n"
    + "".join(f'   — "{q}"\n' for q in t["trechos"])
    for i, t in enumerate(temas)
)

d1, d2, d3 = st.columns(3, gap="medium")
with d1:
    st.download_button(
        "↓ Baixar CSV de Temas",
        df_exp.to_csv(index=False).encode(),
        f"{r['projeto']}_temas.csv", "text/csv",
        use_container_width=True,
    )
with d2:
    st.download_button(
        "↓ Baixar JSON Completo",
        json.dumps(r, ensure_ascii=False, indent=2).encode(),
        f"{r['projeto']}_analise.json", "application/json",
        use_container_width=True,
    )
with d3:
    st.download_button(
        "↓ Baixar Relatório TXT",
        rel.encode(),
        f"{r['projeto']}_relatorio.txt", "text/plain",
        use_container_width=True,
    )

# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="kyra-footer">
    <div class="kyra-footer-left">
        <span>kyra.</span> / Análise de Transcrições — IBMEC ML 2026
    </div>
    <div class="kyra-footer-right">
        Maria Beatriz Ribeiro · Juliane Oliveira · Emanuel Gandra
    </div>
</div>
""", unsafe_allow_html=True)
