"""
Kyra Pesquisa — Dashboard de Análise de Transcrições
Para rodar: streamlit run app.py --server.port 8502
"""
import sys
import json
import re
import html
import unicodedata
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent))

# ── Status do pipeline principal ─────────────────────────────────────────────
# O app usa dois níveis de análise:
# 1) src.pipeline: temas/sentimento com modelos .pkl treinados em src/models.
# 2) fallback + personas/JTBD: análise por dicionários, sempre disponível para o texto enviado.
def _inspect_pipeline_model():
    """Importa o pipeline e diagnostica se os artefatos principais parecem treinados."""
    status = {
        "pipeline_importado": False,
        "pipeline_ok": False,
        "erro": "",
        "models_dir": "",
        "tfidf_ok": False,
        "tfidf_vocab_size": 0,
        "tfidf_has_idf": False,
        "nmf_ok": False,
        "nmf_components": 0,
        "nmf_topics_ok": False,
        "evidencias_ok": False,
        "arquivos_modelo": {},
    }
    try:
        import src.pipeline as pipeline_module
        status["pipeline_importado"] = True
        status["models_dir"] = str(getattr(pipeline_module, "_MODELS", ""))

        for fn in ["tfidf.pkl", "nmf.pkl", "kmeans.pkl", "taxonomy_nb.pkl"]:
            try:
                path = getattr(pipeline_module, "_MODELS", Path("")) / fn
                status["arquivos_modelo"][fn] = bool(path.exists())
            except Exception:
                status["arquivos_modelo"][fn] = False

        tfidf = getattr(pipeline_module, "_tfidf", None)
        nmf = getattr(pipeline_module, "_nmf", None)
        nmf_topics = getattr(pipeline_module, "_nmf_topics", None)
        evidencias = getattr(pipeline_module, "_evidencias", None)

        # TF-IDF: em algumas versões do scikit-learn o atributo idf_ pode não aparecer
        # diretamente no objeto, mas o modelo ainda estar treinado. Por isso a checagem
        # confiável aqui é: existe vocabulário e um transform de teste roda sem erro.
        status["tfidf_vocab_size"] = int(len(getattr(tfidf, "vocabulary_", {}) or {})) if tfidf is not None else 0
        status["tfidf_has_idf"] = bool(
            tfidf is not None and (
                hasattr(tfidf, "idf_") or
                hasattr(getattr(tfidf, "_tfidf", None), "idf_") or
                getattr(tfidf, "use_idf", False) is False
            )
        )
        status["tfidf_transform_ok"] = False
        status["tfidf_transform_error"] = ""
        if tfidf is not None and status["tfidf_vocab_size"] > 0:
            try:
                _ = tfidf.transform(["teste natura boticario produto preco loja consultora pele cheiro"])
                status["tfidf_transform_ok"] = True
            except Exception as _tfidf_exc:
                status["tfidf_transform_error"] = str(_tfidf_exc)
        status["tfidf_ok"] = bool(status["tfidf_vocab_size"] > 0 and status["tfidf_transform_ok"])

        status["nmf_components"] = int(getattr(nmf, "n_components", 0) or 0) if nmf is not None else 0
        status["nmf_ok"] = bool(nmf is not None and hasattr(nmf, "components_") and status["nmf_components"] > 0)
        status["nmf_topics_ok"] = bool(nmf_topics is not None and hasattr(nmf_topics, "empty") and not nmf_topics.empty)
        status["evidencias_ok"] = bool(isinstance(evidencias, dict) and len(evidencias) > 0)

        status["pipeline_ok"] = bool(status["tfidf_ok"] and status["nmf_ok"] and status["nmf_topics_ok"])
        if not status["pipeline_ok"]:
            missing = []
            if not status["tfidf_ok"]:
                missing.append("TF-IDF não treinado/carregado")
            if not status["nmf_ok"]:
                missing.append("NMF não treinado/carregado")
            if not status["nmf_topics_ok"]:
                missing.append("tabela nmf_topics não encontrada/vazia")
            status["erro"] = "; ".join(missing)
        return pipeline_module, status
    except Exception as exc:
        status["erro"] = str(exc)
        return None, status

_pipeline_module, _MODEL_STATUS = _inspect_pipeline_model()
pipeline_run = getattr(_pipeline_module, "run", None) if _pipeline_module is not None else None
_PIPELINE_OK = bool(_MODEL_STATUS.get("pipeline_ok"))
_PIPELINE_ERR = _MODEL_STATUS.get("erro", "")

st.set_page_config(
    page_title="Kyra Pesquisa / Análise",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="expanded",
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

/* Restaura a fonte de ÍCONES do Streamlit. A regra Inter acima atinge todo
   <span> com !important e sobrescrevia os ícones (Material Symbols), fazendo
   a ligadura aparecer como texto cru ("keyboard_double_arrow", "arrow_right",
   "add"). Aqui devolvemos a fonte correta para os spans de ícone. */
span[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"],
.material-symbols-rounded,
[data-testid="stExpanderToggleIcon"] {{
    font-family: 'Material Symbols Rounded' !important;
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

/* Mantém header/toolbar nativos do Streamlit visíveis para aparecer o botão Deploy.
   Esconde apenas elementos que poluem a página. */
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu, footer {{
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

.model-status {{
    margin-top: 14px;
    background: #FFF7D6;
    border-left: 4px solid #D94040;
    padding: 14px 16px;
    font-size: .82rem;
    line-height: 1.5;
    color: #1A1A1A;
    overflow-wrap: anywhere;
}}
.model-status b {{ color: #D94040; }}

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

/* ── FOOTER compacto ── */
.kyra-footer {{
    background: {BK};
    padding: 10px 48px;
    margin-top: 28px;
    min-height: 42px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}}
.kyra-footer-left {{
    font-size: 0.74rem; color: {G3};
    line-height: 1.2;
}}
.kyra-footer-left span {{ color: {Y}; font-weight: 800; }}
.kyra-footer-right {{
    font-size: 0.70rem; color: #666;
    line-height: 1.2;
}}

/* ── AJUSTES DE SOBREPOSIÇÃO / RESPONSIVIDADE ── */
* {{ box-sizing: border-box; }}
.intro-card, .kpi-card, .tema-detail, .upload-info, .narrativa-box,
.persona-card, .jtbd-card, .mini-card, .analysis-card {{
    overflow-wrap: anywhere !important;
    word-break: normal !important;
    min-height: auto !important;
}}
.intro-txt, .sintese-txt, .narrativa-box, .quote-text, .upload-info-val,
.persona-desc, .analysis-txt, .mini-card-val {{
    max-width: 100% !important;
    overflow: visible !important;
}}
.kpi-val {{ font-size: clamp(1.25rem, 2.2vw, 2.2rem) !important; }}
.kpi-lbl {{ line-height: 1.35 !important; }}
.stPlotlyChart {{ overflow: visible !important; }}
[data-testid="column"] {{ min-width: 0 !important; }}

/* ── PERSONAS / JTBD ── */
.analysis-grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 18px;
}}
.analysis-grid-2 {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 18px;
}}
.persona-card, .jtbd-card, .mini-card, .analysis-card {{
    background: #F7F7F7;
    border-top: 4px solid #F5C800;
    padding: 18px 20px;
}}
.persona-card-main {{ background: #1A1A1A; color: #FFFFFF !important; border-top-color: #F5C800; }}
.persona-name {{
    font-size: 1.1rem;
    line-height: 1.25;
    font-weight: 900;
    color: #1A1A1A;
    margin-bottom: 8px;
}}
.persona-card-main .persona-name {{ color: #F5C800 !important; }}
.persona-pct {{
    font-size: 2.05rem;
    line-height: 1;
    font-weight: 900;
    letter-spacing: -1px;
    color: #1A1A1A;
    margin-bottom: 10px;
}}
.persona-card-main .persona-pct {{ color: #FFFFFF !important; }}
.persona-desc, .analysis-txt {{
    color: #555555;
    font-size: .9rem;
    line-height: 1.65;
}}
.persona-card-main .persona-desc {{ color: #E8E8E8 !important; }}
.mini-card-label {{
    font-size: .64rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    color: #999999;
    margin-bottom: 6px;
}}
.mini-card-val {{
    font-size: 1rem;
    font-weight: 800;
    line-height: 1.4;
    color: #1A1A1A;
}}
.analysis-note {{
    font-size: .78rem;
    color: #999999;
    line-height: 1.55;
    margin: 8px 0 18px 0;
}}
.progress-track {{
    background: #E8E8E8;
    height: 9px;
    width: 100%;
    border-radius: 3px;
    overflow: hidden;
    margin-top: 8px;
}}
.progress-fill {{
    background: #F5C800;
    height: 100%;
    border-radius: 3px;
}}

.model-status-ok {{
    background: #e8f5ee;
    border-left: 4px solid #22A06B;
    padding: 12px 14px;
    margin-top: 14px;
    font-size: .78rem;
    line-height: 1.55;
    color: #1A1A1A;
}}
.model-status-ok b {{ color: #0e6e41; }}
.subsec-title {{
    font-size: .66rem;
    font-weight: 900;
    letter-spacing: 2.2px;
    text-transform: uppercase;
    color: #1A1A1A;
    margin: 8px 0 12px 0;
    padding-left: 12px;
    border-left: 4px solid #F5C800;
}}
.card-separator {{
    height: 1px;
    background: #E8E8E8;
    margin: 22px 0 22px 0;
}}

.persona-block-wrapper {{
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-top: 6px solid #F5C800;
    padding: 18px 18px 22px 18px;
    margin: 8px 0 28px 0;
}}
.analysis-block-wrapper {{
    background: #FAFAFA;
    border: 1px solid #E8E8E8;
    padding: 18px;
    margin: 10px 0 24px 0;
}}
.persona-section-note {{
    color: #777777;
    font-size: .82rem;
    line-height: 1.55;
    margin: -4px 0 16px 0;
}}

@media (max-width: 1100px) {{
    .analysis-grid-3, .analysis-grid-2, .kpi-grid {{ grid-template-columns: 1fr !important; }}
    [data-testid="stMainBlockContainer"] {{ padding-left: 24px !important; padding-right: 24px !important; }}
    .kyra-nav, .kyra-footer, .demo-strip {{ margin-left: -24px !important; margin-right: -24px !important; padding-left: 24px !important; padding-right: 24px !important; }}
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
# ANÁLISES DE PERSONAS / TENSÕES / JTBD — baseadas nos notebooks 04 e 05
# ════════════════════════════════════════════════════════════════════════════

def _strip_accents(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", str(txt or ""))
    return "".join(ch for ch in txt if not unicodedata.combining(ch))


def normalize_text(txt: str) -> str:
    txt = _strip_accents(txt).lower()
    txt = re.sub(r"[^a-z0-9\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def word_count(txt: str) -> int:
    return max(1, len(re.findall(r"\b\w+\b", normalize_text(txt))))


def count_patterns(txt_norm: str, patterns) -> int:
    total = 0
    for pat in patterns:
        p = normalize_text(pat)
        if not p:
            continue
        if " " in p:
            total += txt_norm.count(p)
        else:
            total += len(re.findall(rf"\b{re.escape(p)}\b", txt_norm))
    return total


DIMENSION_PATTERNS = {
    "consciente_natural_sustentavel": ["natural", "sustentavel", "sustentabilidade", "vegano", "organico", "ingrediente", "ingredientes", "ecologico", "reciclavel", "refil", "refill", "meio ambiente", "ambiental", "biodegradavel", "plantar", "adubo"],
    "cuidado_pessoal_pele_corpo": ["pele", "piel", "corpo", "cuerpo", "rosto", "cara", "hidrata", "hidratacao", "hidratante", "skincare", "cuidado", "cuidados", "tratamento", "ressecada", "sensivel", "rosacea", "dermo", "oleosa", "macia"],
    "orientada_eficacia_resultado": ["resultado", "resultados", "funciona", "funcione", "eficaz", "eficacia", "melhora", "melhorar", "tratamento", "dura", "duracao", "prova", "beneficio", "beneficios", "resolver", "resolve", "efeito", "tecnologia"],
    "curiosa_inovacao_novidade": ["novo", "nova", "novidade", "diferente", "moderno", "moderna", "tecnologia", "inovacao", "inovador", "inovadora", "lancamento", "descobrir", "testar", "curiosa"],
    "identidade_representatividade": ["representatividade", "representa", "identidade", "pele negra", "negra", "morena", "diversidade", "inclusao", "para mim", "minha pele", "me representa"],
    "cetica_ou_indecisa": ["nao sei", "talvez", "depende", "duvida", "duvidas", "nao entendi", "confuso", "confusa", "acho que", "parece", "nao tenho certeza", "nao sei se", "sera"],
    "comparadora_de_marcas": ["boticario", "o boticario", "avon", "natura", "cacau show", "eudora", "concorrente", "marca", "marcas", "melhor que", "versus", "comparar", "comparo", "perfumaria"],
    "canal_loja_consultora": ["loja", "shopping", "consultora", "revista", "whatsapp", "online", "site", "app", "pedido", "entrega", "frete", "sacola", "vender", "vende", "comprar", "compra", "link", "marketplace"],
    "guiada_marca_confianca": ["confio", "confianca", "tradicao", "qualidade", "marca", "memoria", "sempre usei", "minha mae usava", "fiel", "recomendo", "recomendaria", "conheco"],
    "sensivel_preco_valor": ["preco", "caro", "cara", "barato", "barata", "promocao", "desconto", "oferta", "custo beneficio", "valor", "vale a pena", "economico", "rendimento", "pagar", "orcamento"],
    "social_familiar_indicacao": ["mae", "filho", "filha", "familia", "familiar", "amiga", "amigo", "indicacao", "recomendacao", "presente", "aniversario", "dia das maes", "sobrinho", "sobrinha"],
    "sensorial_prazer_uso": ["cheiro", "perfume", "textura", "toque", "sensacao", "macia", "suave", "absorve", "pegajosa", "prazer", "delicia", "gostoso", "ritual", "experiencia"],
    "estetica_presente_status": ["presente", "presentear", "bonito", "bonita", "chique", "sofisticado", "embalagem", "design", "status", "luxo", "especial", "ocasiao", "kit"],
    "critica_rejeicao_explicita": ["nao gostei", "nao compraria", "ruim", "problema", "critica", "rejeito", "rejeicao", "nao usaria", "decepcionei", "detestei"],
    "pratica_rotina": ["pratico", "pratica", "rapido", "facil", "rotina", "dia a dia", "conveniente", "tempo", "correria", "simples"],
}

PERSONA_PROFILES = {
    "Cuidadora Consciente": {"descricao": "Valoriza cuidado pessoal, pele/corpo, naturalidade, eficácia, inovação e segurança. Precisa de prova e confiança para acreditar nos claims.", "weights": {"consciente_natural_sustentavel": 2.3, "cuidado_pessoal_pele_corpo": 1.9, "orientada_eficacia_resultado": 1.7, "curiosa_inovacao_novidade": 1.6, "identidade_representatividade": 1.5, "cetica_ou_indecisa": 1.3, "sensorial_prazer_uso": 1.1}},
    "Comparadora Omnicanal": {"descricao": "Compara marcas e canais; avalia loja, consultora, WhatsApp, preço, disponibilidade, confiança e custo-benefício.", "weights": {"comparadora_de_marcas": 1.8, "canal_loja_consultora": 1.7, "guiada_marca_confianca": 1.7, "sensivel_preco_valor": 1.6, "estetica_presente_status": 1.4, "sensorial_prazer_uso": 1.3}},
    "Compradora Social e Presenteadora": {"descricao": "Compra em contexto social/familiar: presente, indicação, cuidado com outros, WhatsApp, consultora, família e amigas.", "weights": {"social_familiar_indicacao": 1.6, "critica_rejeicao_explicita": 1.3, "canal_loja_consultora": 1.3, "pratica_rotina": 1.2, "sensivel_preco_valor": 1.2, "estetica_presente_status": 1.1}},
}

MOTIVATOR_PATTERNS = {
    "marca_confianca_memoria": ["confio", "confianca", "qualidade", "marca", "tradicao", "sempre usei", "minha mae usava", "recomendo", "fiel"],
    "canal_conveniencia_consultora": ["loja", "consultora", "whatsapp", "online", "site", "app", "entrega", "frete", "pedido", "facil", "conveniente", "perto"],
    "presente_status_estetica": ["presente", "presentear", "kit", "embalagem", "bonito", "chique", "especial", "aniversario", "dia das maes"],
    "eficacia_resultado_prova": ["resultado", "funciona", "eficaz", "eficacia", "melhora", "tratamento", "duracao", "prova", "beneficio"],
    "sensorial_experiencia": ["cheiro", "perfume", "textura", "toque", "sensacao", "macia", "suave", "prazer", "ritual"],
    "preco_valor_promocao": ["preco", "barato", "promocao", "desconto", "oferta", "custo beneficio", "vale a pena", "rendimento"],
    "natural_sustentavel_ingredientes": ["natural", "sustentavel", "vegano", "ingrediente", "organico", "refil", "reciclavel"],
    "indicacao_social_familiar": ["indicacao", "recomendacao", "amiga", "familia", "mae", "filho", "filha", "consultora"],
}

BARRIER_PATTERNS = {
    "indecisao_excesso_opcoes": ["nao sei", "duvida", "muita opcao", "muitas opcoes", "qual escolher", "confuso", "confusa", "depende", "talvez", "nao entendi"],
    "preco_alto_sem_valor": ["caro", "cara", "preco alto", "nao vale", "muito caro", "pagar", "orcamento", "sem valor"],
    "canal_friccao_compra": ["frete", "demora", "entrega", "dificil comprar", "site ruim", "nao encontro", "indisponivel", "sacola", "pedido", "complicado"],
    "duvida_eficacia_claim": ["sera que funciona", "nao acredito", "claim", "promessa", "duvida se", "nao sei se funciona", "parece promessa", "duvido"],
    "sensorial_negativo": ["cheiro forte", "enjoativo", "pegajoso", "pegajosa", "oleoso", "oleosa", "textura ruim", "nao gostei do cheiro"],
    "comparacao_desfavoravel": ["boticario e melhor", "avon e melhor", "concorrente", "prefiro outra", "outra marca", "melhor que natura", "mais barato em outra"],
    "ceticismo_sustentabilidade": ["greenwashing", "nao e sustentavel", "sustentabilidade so marketing", "refil caro", "duvido que seja natural"],
}

JTBD_PATTERNS = {
    "compra_conveniente_e_acesso": ["comprar", "compra", "loja", "online", "site", "app", "whatsapp", "consultora", "entrega", "frete", "pedido", "perto", "facil", "disponivel"],
    "experiencia_sensorial_prazer_ritual": ["cheiro", "perfume", "textura", "toque", "sensacao", "macia", "suave", "ritual", "prazer", "experiencia", "delicia"],
    "presentear_e_demonstrar_cuidado": ["presente", "presentear", "aniversario", "dia das maes", "kit", "lembranca", "dar para", "minha mae", "amiga", "familia"],
    "eficacia_tratamento_resolver_problema": ["tratamento", "resolver", "resolve", "resultado", "funciona", "melhora", "eficaz", "beneficio", "pele sensivel", "rosacea"],
    "cuidado_familiar_e_social": ["familia", "filho", "filha", "mae", "pai", "amiga", "cuidar", "cuidado", "sobrinho", "crianca"],
    "praticidade_rotina_rapida": ["rotina", "dia a dia", "rapido", "pratico", "facil", "tempo", "correria", "simples"],
    "economizar_sem_perder_qualidade": ["economizar", "barato", "promocao", "desconto", "custo beneficio", "rende", "rendimento", "vale a pena"],
    "pertencimento_recomendacao_comunidade": ["recomendacao", "indicacao", "todo mundo", "comunidade", "grupo", "amigas", "rede", "compartilhar"],
    "autoestima_expressao_identidade": ["autoestima", "me sinto", "bonita", "identidade", "representa", "minha pele", "confiante", "expressao", "estilo"],
}

OPPORTUNITY_BY_PERSONA = {
    "Cuidadora Consciente": {"produto": "Claims funcionais, ativos/ingredientes, linhas de cuidado e demonstração de resultado.", "comunicacao": "Linguagem de prova, segurança, cuidado e explicação simples do benefício.", "canal": "Conteúdo educativo, consultora preparada e páginas com evidências claras.", "risco": "Claims genéricos podem gerar ceticismo; excesso de promessa reduz confiança."},
    "Comparadora Omnicanal": {"produto": "Bundles, kits comparáveis, disponibilidade e diferenciais claros versus concorrentes.", "comunicacao": "Custo-benefício, comparação, rendimento, facilidade e confiança de marca.", "canal": "Integração loja/consultora/digital, clareza de frete, sacola, estoque e pedido.", "risco": "Fricção de canal ou preço sem justificativa pode levar à troca por concorrente."},
    "Compradora Social e Presenteadora": {"produto": "Kits por ocasião, embalagens presenteáveis e curadoria por faixa de preço.", "comunicacao": "Mensagem de cuidado, acerto no presente, recomendação e ocasião de compra.", "canal": "WhatsApp, consultora, guia rápido de presente e recomendação por perfil.", "risco": "Excesso de opções pode travar a escolha; precisa de curadoria simples."},
}

OPPORTUNITY_BY_JTBD = {
    "compra_conveniente_e_acesso": "Reduzir fricção de compra: disponibilidade, frete claro, link direto, loja/consultora integradas e recomendação rápida.",
    "experiencia_sensorial_prazer_ritual": "Dar protagonismo a cheiro, textura, toque e ritual; usar amostras, demonstração e linguagem sensorial.",
    "presentear_e_demonstrar_cuidado": "Criar kits por ocasião, faixas de preço, embalagem presenteável e guia de presente por perfil.",
    "eficacia_tratamento_resolver_problema": "Explicitar prova, benefício, modo de uso, antes/depois responsável e credenciais do produto.",
    "cuidado_familiar_e_social": "Comunicar cuidado com outros, família, rotina compartilhada e recomendação afetiva.",
    "praticidade_rotina_rapida": "Simplificar escolha e uso: rotinas curtas, produtos multifuncionais e instruções diretas.",
    "economizar_sem_perder_qualidade": "Mostrar rendimento, custo por uso, promoção e comparação de valor sem parecer downgrade.",
    "pertencimento_recomendacao_comunidade": "Usar prova social, recomendações, depoimentos e dinâmica de comunidade/consultora.",
    "autoestima_expressao_identidade": "Conectar produto a confiança, identidade, expressão pessoal e representatividade.",
}

REFERENCE_MEDIAN_MOTIVATION = 42.59576901086334
REFERENCE_MEDIAN_BARRIER = 5.8830058830058825


def score_pattern_group(txt_norm: str, pattern_dict: dict, n_words: int):
    rows = []
    for name, pats in pattern_dict.items():
        hits = count_patterns(txt_norm, pats)
        per_1k = hits / max(n_words, 1) * 1000
        rows.append({"dimensao": name, "hits": hits, "per_1k": per_1k})
    return pd.DataFrame(rows).sort_values("per_1k", ascending=False)


def _to_pct(scores: dict) -> dict:
    clean = {k: max(float(v), 0.0) for k, v in scores.items()}
    total = sum(clean.values())
    if total <= 0:
        return {k: 100 / len(clean) for k in clean}
    return {k: 100 * v / total for k, v in clean.items()}


def classify_personas(dim_scores: dict):
    raw = {}
    for persona, cfg in PERSONA_PROFILES.items():
        raw[persona] = sum(dim_scores.get(dim, 0.0) * w for dim, w in cfg["weights"].items())
    pct = _to_pct(raw)
    return pd.DataFrame([{"persona": p, "aderencia_pct": pct[p], "score_bruto": raw[p], "descricao": PERSONA_PROFILES[p]["descricao"]} for p in pct]).sort_values("aderencia_pct", ascending=False)


def build_text_from_result(result: dict) -> str:
    parts = [result.get("sintese", ""), result.get("narrativa", "")]
    for t in result.get("temas", []):
        parts.append(t.get("label", ""))
        parts.extend(t.get("termos", []))
        parts.extend(t.get("trechos", []))
    return "\n".join(str(x) for x in parts if x)


def extract_text_from_uploaded_file(uploaded_file) -> str:
    raw = uploaded_file.read()
    name = (uploaded_file.name or "").lower()
    if name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        try:
            import io
            try:
                from pypdf import PdfReader
            except Exception:
                from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(raw))
            pages = [(page.extract_text() or "") for page in reader.pages]
            text = "\n".join(pages).strip()
            if text:
                return text
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")


def run_persona_jtbd_analysis(text: str, result=None) -> dict:
    text = text or ""
    txt_norm = normalize_text(text)
    n_words = word_count(text)
    dim_df = score_pattern_group(txt_norm, DIMENSION_PATTERNS, n_words)
    dim_scores = dict(zip(dim_df["dimensao"], dim_df["per_1k"]))
    persona_df = classify_personas(dim_scores)
    mot_df = score_pattern_group(txt_norm, MOTIVATOR_PATTERNS, n_words)
    bar_df = score_pattern_group(txt_norm, BARRIER_PATTERNS, n_words)
    jtbd_df = score_pattern_group(txt_norm, JTBD_PATTERNS, n_words)

    # Totais absolutos por 1.000 palavras usados no mapa de tensões.
    mot_total = float(mot_df["per_1k"].sum())
    bar_total = float(bar_df["per_1k"].sum())

    # Percentuais relativos usados nos gráficos.
    # Antes só o JTBD recebia aderencia_pct; por isso os gráficos de motivadores/barreiras
    # quebravam com KeyError: 'aderencia_pct'.
    mot_pct = _to_pct(dict(zip(mot_df["dimensao"], mot_df["per_1k"])))
    bar_pct = _to_pct(dict(zip(bar_df["dimensao"], bar_df["per_1k"])))
    jtbd_pct = _to_pct(dict(zip(jtbd_df["dimensao"], jtbd_df["per_1k"])))

    mot_df["aderencia_pct"] = mot_df["dimensao"].map(mot_pct)
    bar_df["aderencia_pct"] = bar_df["dimensao"].map(bar_pct)
    jtbd_df["aderencia_pct"] = jtbd_df["dimensao"].map(jtbd_pct)

    mot_df = mot_df.sort_values("aderencia_pct", ascending=False)
    bar_df = bar_df.sort_values("aderencia_pct", ascending=False)
    jtbd_df = jtbd_df.sort_values("aderencia_pct", ascending=False)

    mot_level = "Alta" if mot_total >= REFERENCE_MEDIAN_MOTIVATION else "Baixa"
    bar_level = "Alta" if bar_total >= REFERENCE_MEDIAN_BARRIER else "Baixa"
    if mot_level == "Alta" and bar_level == "Alta":
        quadrant = "Alta motivação + alta barreira"
        quadrant_desc = "Há desejo, mas existem objeções a destravar. É o território mais acionável para comunicação e redução de risco."
    elif mot_level == "Alta" and bar_level == "Baixa":
        quadrant = "Alta motivação + baixa barreira"
        quadrant_desc = "Entrevista próxima de conversão: vale ativação direta, oferta, kit ou recomendação simples."
    elif mot_level == "Baixa" and bar_level == "Alta":
        quadrant = "Baixa motivação + alta barreira"
        quadrant_desc = "Público mais resistente: precisa de educação, reposicionamento ou talvez menor prioridade comercial."
    else:
        quadrant = "Baixa motivação + baixa barreira"
        quadrant_desc = "Público morno: não rejeita fortemente, mas precisa de ocasião, estímulo ou benefício mais claro."

    top_persona = persona_df.iloc[0]["persona"]
    top_jtbd = jtbd_df.iloc[0]["dimensao"] if len(jtbd_df) else "n/d"
    top_mot = mot_df.iloc[0]["dimensao"] if len(mot_df) else "n/d"
    top_bar = bar_df.iloc[0]["dimensao"] if len(bar_df) else "n/d"
    synthesis = (
        f"A entrevista tem maior aderência à persona {top_persona} ({persona_df.iloc[0]['aderencia_pct']:.1f}%). "
        f"O JTBD dominante é {top_jtbd.replace('_', ' ')}, com motivador principal em {top_mot.replace('_', ' ')} "
        f"e principal barreira em {top_bar.replace('_', ' ')}. O quadrante de tensão é: {quadrant}."
    )
    return {
        "n_words": n_words,
        "dimensions": dim_df,
        "personas": persona_df,
        "motivators": mot_df,
        "barriers": bar_df,
        "jtbd": jtbd_df,
        "motivadores_total_per_1k": mot_total,
        "barreiras_total_per_1k": bar_total,
        "quadrante": quadrant,
        "quadrante_desc": quadrant_desc,
        "sintese_personas_jtbd": synthesis,
        "oportunidades_persona": OPPORTUNITY_BY_PERSONA.get(top_persona, {}),
        "oportunidade_jtbd": OPPORTUNITY_BY_JTBD.get(top_jtbd, ""),
    }


def pct_bar(label, pct, desc=""):
    desc_html = f'<div style="font-size:.75rem;color:{G3};line-height:1.45;margin-top:5px;">{html.escape(str(desc))}</div>' if desc else ''
    return f'''
    <div style="margin-bottom:13px;">
        <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-end;">
            <div style="font-size:.86rem;font-weight:800;color:{BK};line-height:1.35;">{html.escape(str(label))}</div>
            <div style="font-size:.86rem;font-weight:900;color:{BK};white-space:nowrap;">{pct:.1f}%</div>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:{min(max(pct,0),100):.1f}%;"></div></div>
        {desc_html}
    </div>
    '''


def pretty_dim(name: str) -> str:
    return str(name).replace("__", " — ").replace("_", " ").strip().capitalize()


# Pipeline leve de fallback para quando o pipeline principal não consegue rodar.
# Evita cair em dados demo quando a transcrição real foi lida corretamente.
def fallback_pipeline_from_text(text: str, nome: str = "entrevista") -> dict:
    text = text or ""
    txt_norm = normalize_text(text)
    n_words = word_count(text)

    topic_defs = {
        "Cuidado, pele e corpo": DIMENSION_PATTERNS.get("cuidado_pessoal_pele_corpo", []),
        "Preço e valor": DIMENSION_PATTERNS.get("sensivel_preco_valor", []),
        "Canal, loja e consultora": DIMENSION_PATTERNS.get("canal_loja_consultora", []),
        "Marca e confiança": DIMENSION_PATTERNS.get("guiada_marca_confianca", []),
        "Sensorialidade e experiência": DIMENSION_PATTERNS.get("sensorial_prazer_uso", []),
        "Naturalidade e sustentabilidade": DIMENSION_PATTERNS.get("consciente_natural_sustentavel", []),
        "Presente e estética": DIMENSION_PATTERNS.get("estetica_presente_status", []),
        "Eficácia e resultado": DIMENSION_PATTERNS.get("orientada_eficacia_resultado", []),
        "Social, família e indicação": DIMENSION_PATTERNS.get("social_familiar_indicacao", []),
        "Críticas e rejeições": DIMENSION_PATTERNS.get("critica_rejeicao_explicita", []),
    }

    pos_terms = ["gosto", "gostei", "adoro", "amo", "bom", "boa", "otimo", "otima", "excelente", "funciona", "recomendo", "qualidade", "bonito", "delicia"]
    neg_terms = ["nao gostei", "nao compraria", "ruim", "caro", "cara", "problema", "dificil", "demora", "duvida", "confuso", "pegajoso", "enjoativo"]
    pos_hits = count_patterns(txt_norm, pos_terms)
    neg_hits = count_patterns(txt_norm, neg_terms)
    total_sent = max(pos_hits + neg_hits, 1)
    pct_pos = min(70.0, 100 * pos_hits / total_sent) if (pos_hits + neg_hits) else 30.0
    pct_neg = min(70.0, 100 * neg_hits / total_sent) if (pos_hits + neg_hits) else 15.0
    if pct_pos + pct_neg > 95:
        scale = 95 / (pct_pos + pct_neg)
        pct_pos *= scale
        pct_neg *= scale
    pct_neu = max(0.0, 100.0 - pct_pos - pct_neg)
    dominante = "POS" if pct_pos >= pct_neu and pct_pos >= pct_neg else ("NEG" if pct_neg >= pct_pos and pct_neg >= pct_neu else "NEU")

    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    sentences = [x.strip() for x in raw_sentences if len(x.strip()) > 30]

    rows = []
    for label, pats in topic_defs.items():
        hits = count_patterns(txt_norm, pats)
        if hits <= 0:
            continue
        pct = min(45.0, hits / max(n_words, 1) * 1000)
        terms_found = []
        for pat in pats:
            if count_patterns(txt_norm, [pat]) > 0:
                terms_found.append(pat)
            if len(terms_found) >= 6:
                break
        quotes = []
        for sent in sentences:
            sn = normalize_text(sent)
            if any(count_patterns(sn, [p]) > 0 for p in pats):
                quotes.append(sent[:450])
            if len(quotes) >= 3:
                break
        rows.append({
            "label": label,
            "pct": pct,
            "lift": max(1.0, pct / 8.0),
            "termos": terms_found or pats[:5],
            "s_pos": pct_pos,
            "s_neg": pct_neg,
            "s_neu": pct_neu,
            "trechos": quotes,
        })

    rows = sorted(rows, key=lambda x: x["pct"], reverse=True)[:6]
    if not rows:
        rows = mock_pipeline(nome).get("temas", [])

    top_labels = ", ".join(t["label"].lower() for t in rows[:3])
    sintese = f"A entrevista apresenta maior concentração em {top_labels}."
    narrativa = (
        f"A leitura automática identificou {len(rows)} temas principais a partir da transcrição. "
        f"O sentimento estimado é {dominante}, com {pct_pos:.1f}% positivo, {pct_neu:.1f}% neutro e {pct_neg:.1f}% negativo."
    )

    return {
        "projeto": str(nome).replace(".pdf", "").replace(".txt", ""),
        "n_chunks": max(1, n_words // 90),
        "n_participantes": max(1, len(set(re.findall(r"\bparticipante\s*\d+\b", txt_norm))) or 1),
        "duracao_min": max(1, int(n_words / 130)),
        "sentimento": {"dominante": dominante, "pct_pos": pct_pos, "pct_neu": pct_neu, "pct_neg": pct_neg},
        "temas": rows,
        "narrativa": narrativa,
        "sintese": sintese,
        "pii_ok": True,
        "fallback_usado": True,
    }

# ════════════════════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════════════════════
# AJUSTES VERSÃO UX — análise crítica e layout redesenhado
# ════════════════════════════════════════════════════════════════════════════

# Reforços de dicionário a partir da avaliação qualitativa dos resultados
BARRIER_PATTERNS.setdefault("embalagem_design_baixa_diferenciacao", [])
BARRIER_PATTERNS["embalagem_design_baixa_diferenciacao"] = sorted(set(
    BARRIER_PATTERNS["embalagem_design_baixa_diferenciacao"] + [
        "sem graca", "sem graça", "antigo", "antiga", "comum", "normal", "nao chama atencao",
        "não chama atenção", "nao impressiona", "não impressiona", "parece barato", "parece barata",
        "parece garrafa", "garrafa de agua", "garrafa de água", "parece jequiti", "parece avon",
        "nao tem novidade", "não tem novidade", "nada de diferente", "nao compraria", "não compraria",
        "basico", "básico", "tampa", "embalagem feia", "design fraco"
    ]
))
BARRIER_PATTERNS["duvida_eficacia_claim"] = sorted(set(BARRIER_PATTERNS.get("duvida_eficacia_claim", []) + [
    "antes e depois", "ver se funciona", "ver como funciona", "quero ver", "quem usou", "quem ja usou",
    "quem já usou", "promete entregar", "vai ter eficacia", "vai ter eficácia", "provar", "prova",
    "comprovar", "resultado mesmo", "será que entrega", "sera que entrega", "precisa mostrar"
]))
MOTIVATOR_PATTERNS["eficacia_resultado_prova"] = sorted(set(MOTIVATOR_PATTERNS.get("eficacia_resultado_prova", []) + [
    "antes e depois", "provar", "comprovar", "quem usou", "resultado mesmo", "beneficio", "benefícios", "promete entregar"
]))

MODERATOR_FILLERS = [
    "muito bom", "muito bom gente", "legal", "perfeito", "ta bom", "tá bom", "otimo", "ótimo",
    "vamos la", "vamos lá", "me conta", "pode falar", "excelente"
]


def remove_moderator_bias(text: str) -> str:
    """Remove/atenua marcadores comuns de condução do moderador que inflavam sentimento."""
    out = str(text or "")
    for filler in MODERATOR_FILLERS:
        out = re.sub(rf"\b{re.escape(filler)}\b", " ", out, flags=re.IGNORECASE)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def estimate_speakers(text: str) -> dict:
    """
    Estimativa conservadora de participantes.

    Regra de UX: só mostramos número fechado quando há marcação explícita de falantes
    (Speaker 1, Speaker 2 etc.). Quando não há diarização, nomes chamados no texto
    viram apenas sinal auxiliar, porque transcrições coladas podem conter vários grupos
    e inflar muito a contagem.
    """
    text = str(text or "")

    # Caso confiável: transcrição diarizada
    speaker_tags = sorted(set(re.findall(r"\bSpeaker\s*(\d+)\b", text, flags=re.IGNORECASE)))
    if speaker_tags:
        total = len(speaker_tags)
        return {
            "estimativa": total,
            "label": f"{total}",
            "confianca": "alta",
            "metodo": "marcadores Speaker",
            "nomes": [],
            "display": f"{total}",
            "subtitulo": "marcadores Speaker"
        }

    # Sinal auxiliar: nomes chamados pelo moderador. Não transformar em participante estimado.
    candidates = re.findall(
        r"(?:^|[\.\?\!\n]\s*)([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]{2,})(?=,|\?|\s+me conta|\s+fala|\s+qual|\s+onde|\s+vitalidade)",
        text
    )
    blacklist = {
        "Natura", "Boticario", "Boticário", "Avon", "Dove", "Nive", "Johnson",
        "Dermotech", "BioXpert", "Bioeficiente", "Biomais", "Dermobalance",
        "Bioinovação", "Ecos", "Todo", "Dia", "Natal", "Brasil", "Salvador",
        "Agora", "Então", "Entao", "Gente", "Legal", "Muito", "Bom", "Tá", "Ta"
    }
    names = [c for c in candidates if c not in blacklist and c.lower() not in {"gente", "agora", "entao", "então", "voce", "você"}]
    unique_names = sorted(set(names))

    if len(unique_names) >= 3:
        return {
            "estimativa": None,
            "label": "n/d",
            "confianca": "baixa",
            "metodo": "nomes detectados, sem diarização",
            "nomes": unique_names[:18],
            "display": "n/d",
            "subtitulo": f"{len(unique_names)} nomes detectados"
        }

    return {
        "estimativa": None,
        "label": "n/d",
        "confianca": "baixa",
        "metodo": "sem marcação de falantes",
        "nomes": unique_names[:10],
        "display": "n/d",
        "subtitulo": "sem diarização"
    }


def html_escape(x):
    return html.escape(str(x if x is not None else ""))


def fmt_label(x: str) -> str:
    return pretty_dim(x).replace("Jtbd", "JTBD")


def wrap_plot_label(x, width: int = 34, max_lines: int = 3) -> str:
    """Quebra labels longos para gráficos Plotly sem destruir a legibilidade."""
    import textwrap
    txt = fmt_label(x)
    lines = textwrap.wrap(txt, width=width, break_long_words=False, replace_whitespace=False)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return "<br>".join(lines)


def make_bar_fig(df, label_col, value_col, title, x_title="%", top_n=8, color=Y, suffix="%"):
    d = df.copy()
    if d.empty:
        d = pd.DataFrame([{label_col: "Sem dados", value_col: 0.0}])
    if value_col not in d.columns:
        # fallback defensivo: usa per_1k quando aderencia_pct não existir
        if "per_1k" in d.columns:
            total = float(d["per_1k"].clip(lower=0).sum())
            d[value_col] = 100 * d["per_1k"].clip(lower=0) / total if total > 0 else 0.0
        else:
            d[value_col] = 0.0
    d = d.head(top_n).iloc[::-1]
    max_x = float(d[value_col].max()) if len(d) else 0.0
    fig = go.Figure(go.Bar(
        x=d[value_col], y=d[label_col].map(lambda v: wrap_plot_label(v, width=36, max_lines=3)), orientation="h",
        marker=dict(color=color, line=dict(color=BK, width=1)),
        text=d[value_col].map(lambda v: f"{v:.1f}{suffix}"), textposition="outside", cliponaxis=False,
        customdata=d[label_col].map(fmt_label),
        hovertemplate="<b>%{customdata}</b><br>Valor: <b>%{x:.1f}</b><extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=18, color=BK, family="Inter")),
        height=max(430, 62 * max(4, len(d))),
        margin=dict(l=20, r=110, t=58, b=58),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title=x_title, showgrid=True, gridcolor=G2, zeroline=False, range=[0, max_x * 1.25 if max_x > 0 else 1]),
        yaxis=dict(title="", tickfont=dict(size=13, color=BK)),
        bargap=0.34,
        hoverlabel=dict(bgcolor=BK, font_color=WH, bordercolor=Y),
        uniformtext=dict(minsize=11, mode="hide"),
    )
    return fig


def render_status_badge(ok: bool, text_ok="Modelo principal carregado", text_fail="Modelo principal em fallback"):
    cls = "status-ok" if ok else "status-warn"
    text = text_ok if ok else text_fail
    st.markdown(f'<div class="{cls}">{html_escape(text)}</div>', unsafe_allow_html=True)


def render_metric_card(label, value, note="", accent=Y):
    st.markdown(f"""
    <div class="ux-metric" style="border-top-color:{accent};">
        <div class="ux-metric-value">{html_escape(value)}</div>
        <div class="ux-metric-label">{html_escape(label)}</div>
        {f'<div class="ux-metric-note">{html_escape(note)}</div>' if note else ''}
    </div>
    """, unsafe_allow_html=True)


def render_persona_card(row, rank=1):
    persona = row["persona"]
    pct = float(row["aderencia_pct"])
    desc = row.get("descricao", PERSONA_PROFILES.get(persona, {}).get("descricao", ""))
    st.markdown(f"""
    <div class="persona-card-v2">
        <div class="persona-rank">#{rank}</div>
        <div class="persona-name-v2">{html_escape(persona)}</div>
        <div class="persona-pct-v2">{pct:.1f}%</div>
        <div class="persona-progress"><div style="width:{min(max(pct,0),100):.1f}%"></div></div>
        <div class="persona-desc-v2">{html_escape(desc)}</div>
    </div>
    """, unsafe_allow_html=True)


# CSS final da experiência redesenhada
st.markdown(f"""
<style>
/* UX RESET */
[data-testid="stMainBlockContainer"] {{ padding: 0 36px 52px 36px !important; max-width: 1440px !important; }}
[data-testid="stSidebar"] {{ background: {BK} !important; }}
[data-testid="stSidebar"] * {{ color: {WH}; }}

/* Trava o tamanho SÓ quando a barra está aberta (aria-expanded="true"):
   o usuário não consegue redimensionar arrastando. Não afeta o estado
   fechado, então o recolher/expandir continua funcionando. */
[data-testid="stSidebar"][aria-expanded="true"] {{
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
}}
/* Desabilita o handle de resize (div com cursor col-resize na borda). */
[data-testid="stSidebar"] > div:not([data-testid="stSidebarContent"]) {{
    pointer-events: none !important;
    cursor: default !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{ background: #242424 !important; border: 2px dashed {Y} !important; }}
[data-testid="stSidebar"] .stButton > button {{ background:{Y} !important; color:{BK} !important; border:0 !important; border-radius:0 !important; font-weight:900 !important; text-transform:uppercase; width:100%; }}
[data-testid="stSidebar"] .stDownloadButton > button {{ background:{Y} !important; color:{BK} !important; border-radius:0 !important; }}
[data-testid="stSidebar"] textarea {{ color:{BK} !important; }}
[data-testid="stSidebar"] [data-baseweb="select"] * {{ color:{BK} !important; }}

/* Botão de RECOLHER a sidebar (seta dentro da barra preta) */
[data-testid="stSidebarCollapseButton"] button {{ color:{Y} !important; }}

/* Aba de REABRIR a sidebar quando está fechada: aba BRANCA fixa, colada à
   esquerda, com o símbolo "y." da kyra — deixa claro que a barra existe e
   pode ser reaberta (o controle nativo some/fica invisível). */
[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"] button {{
    background: {WH} !important;
    color: {BK} !important;
    border: 2px solid {BK} !important;
    border-left: 0 !important;
    border-radius: 0 10px 10px 0 !important;
    box-shadow: 2px 2px 10px rgba(0,0,0,.22) !important;
    width: 46px !important;
    height: 46px !important;
    min-width: 46px !important;
    padding: 0 !important;
    opacity: 1 !important;
    z-index: 1001 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: fixed !important;
    top: 132px !important;
    left: 0 !important;
}}
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="collapsedControl"] button:hover {{
    background: {Y} !important;
}}
/* esconde a seta nativa e mostra o "y." da kyra no lugar */
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
[data-testid="collapsedControl"] [data-testid="stIconMaterial"] {{
    display: none !important;
}}
[data-testid="stExpandSidebarButton"]::after,
[data-testid="collapsedControl"] button::after {{
    content: "y." !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 900 !important;
    font-size: 1.35rem !important;
    letter-spacing: -1px !important;
    color: {BK} !important;
}}

/* header nativo fora do fluxo (não reserva espaço) — navbar cola no topo.
   NÃO usar display:none: o botão de reabrir a sidebar vive dentro do header. */
[data-testid="stHeader"] {{
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    overflow: visible !important;
    z-index: 1000 !important;
}}
[data-testid="stDecoration"] {{ display: none !important; height: 0 !important; }}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main,
.block-container {{
    padding-top: 0 !important;
    margin-top: 0 !important;
    top: 0 !important;
}}
/* Os blocos de CSS injetados via st.markdown("<style>…") criam containers
   vazios que, somados ao gap do bloco vertical, empurram a navbar para baixo.
   Removemos esses containers do layout (o CSS continua valendo) para a
   navbar colar de fato no topo. */
[data-testid="stMain"] [data-testid="stElementContainer"]:has(style) {{
    display: none !important;
}}

.ux-hero {{
    background: {Y}; color:{BK}; padding: 26px 32px; margin: 0 -36px 24px -36px;
    display:flex; align-items:center; justify-content:space-between; gap:24px;
    border-bottom: 6px solid {BK}; position:relative;
}}
.ux-brand {{ display:flex; align-items:center; gap:14px; min-width:0; }}
.ux-logo {{ width:44px; height:44px; background:{BK}; color:{Y}; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:1.15rem; flex-shrink:0; }}
.ux-title {{ font-size:1.75rem; font-weight:900; letter-spacing:-1.2px; line-height:1; }}
.ux-subtitle {{ font-size:.86rem; font-weight:700; opacity:.7; margin-top:5px; }}
.ux-hero-right {{ font-size:.78rem; font-weight:800; text-transform:uppercase; letter-spacing:1.6px; }}

.status-ok, .status-warn {{ padding:10px 14px; border-radius:0; font-size:.82rem; font-weight:800; margin: 8px 0 14px; }}
.status-ok {{ background:#DDF4E8; color:#0E6E41 !important; border-left:4px solid {POS}; }}
.status-warn {{ background:#FFF5CC; color:{BK} !important; border-left:4px solid {Y}; }}

.ux-section-head {{ margin: 26px 0 14px; display:flex; align-items:flex-end; justify-content:space-between; gap:16px; border-bottom:2px solid {Y}; padding-bottom:10px; }}
.ux-section-title {{ font-size:.78rem; font-weight:900; text-transform:uppercase; letter-spacing:2.2px; color:{BK}; }}
.ux-section-note {{ font-size:.82rem; color:{G3}; font-weight:600; }}

.ux-card {{ background:{G1}; border-left:4px solid {Y}; padding:20px 22px; margin-bottom:16px; overflow-wrap:anywhere; }}
.ux-card-dark {{ background:{BK}; color:{WH}; padding:22px 26px; margin-bottom:16px; border-left:4px solid {Y}; overflow-wrap:anywhere; }}
.ux-card-dark * {{ color:{WH}; }}
.ux-card-label {{ font-size:.68rem; color:{G3}; font-weight:900; text-transform:uppercase; letter-spacing:2px; margin-bottom:8px; }}
.ux-card-dark .ux-card-label {{ color:{Y}; }}
.ux-card-text {{ font-size:1rem; line-height:1.65; color:{G4}; }}
.ux-card-dark .ux-card-text {{ color:{WH}; font-weight:650; }}

.ux-metric {{ background:{G1}; border-top:4px solid {Y}; padding:18px 18px; min-height:118px; box-sizing:border-box; overflow-wrap:anywhere; }}
.ux-metric-value {{ font-size:1.85rem; font-weight:900; letter-spacing:-.8px; color:{BK}; line-height:1.1; }}
.ux-metric-label {{ margin-top:8px; font-size:.68rem; font-weight:900; color:{G3}; text-transform:uppercase; letter-spacing:1.2px; }}
.ux-metric-note {{ margin-top:8px; font-size:.75rem; color:{G4}; line-height:1.35; }}

.persona-zone {{ background:#fffdf0; border:2px solid {Y}; padding:22px; margin: 8px 0 26px 0; }}
.persona-card-v2 {{ background:{WH}; border:1px solid {G2}; border-top:5px solid {Y}; padding:20px; min-height:250px; box-shadow:0 6px 18px rgba(0,0,0,.04); position:relative; overflow-wrap:anywhere; }}
.persona-rank {{ position:absolute; top:12px; right:14px; font-size:.7rem; color:{G3}; font-weight:900; }}
.persona-name-v2 {{ font-size:1.05rem; font-weight:900; color:{BK}; line-height:1.2; padding-right:34px; min-height:48px; }}
.persona-pct-v2 {{ font-size:2.15rem; font-weight:900; color:{BK}; letter-spacing:-1px; margin:12px 0 8px; }}
.persona-progress {{ height:9px; background:{G2}; border-radius:999px; overflow:hidden; margin-bottom:14px; }}
.persona-progress div {{ height:100%; background:{Y}; border-right:2px solid {BK}; }}
.persona-desc-v2 {{ font-size:.88rem; line-height:1.55; color:{G4}; }}

.signal-list {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
.signal-item {{ background:{G1}; padding:13px 15px; border-left:3px solid {Y}; }}
.signal-title {{ font-size:.82rem; font-weight:900; color:{BK}; }}
.signal-val {{ font-size:.78rem; color:{G4}; margin-top:5px; }}

.quote-v2 {{ background:{WH}; border-left:4px solid {Y}; padding:15px 18px; margin:10px 0; box-shadow:0 2px 10px rgba(0,0,0,.04); }}
.quote-v2-text {{ font-size:.92rem; line-height:1.65; color:{BK}; font-style:italic; }}

.pill-v2 {{ display:inline-block; background:{Y}; color:{BK} !important; padding:4px 9px; margin:3px 4px 3px 0; font-size:.72rem; font-weight:850; }}
.small-muted {{ color:{G3}; font-size:.82rem; line-height:1.55; }}

/* ── INTRODUÇÃO (estado inicial, antes do upload) ── */
.intro-grid {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin-bottom:8px; }}
.intro-card {{ background:{G1}; border-left:4px solid {Y}; padding:22px 24px; }}
.intro-card-label {{ font-size:.68rem; color:{G3}; font-weight:900; text-transform:uppercase; letter-spacing:2px; margin-bottom:12px; }}
.intro-card-text {{ font-size:.96rem; line-height:1.65; color:{G4}; }}

.intro-send {{ display:grid; grid-template-columns:2fr 1fr; gap:16px; align-items:stretch; }}
.intro-send-main {{ background:{BK}; color:{WH}; padding:24px 28px; border-left:4px solid {Y}; }}
.intro-send-main * {{ color:{WH}; }}
.intro-send-label {{ font-size:.68rem; color:{Y} !important; font-weight:900; text-transform:uppercase; letter-spacing:2px; margin-bottom:10px; }}
.intro-send-text {{ font-size:1rem; line-height:1.7; font-weight:600; }}
.intro-send-text b {{ color:{Y} !important; }}
.spec-card {{ background:{G1}; border-top:4px solid {BK}; padding:22px 24px; }}
.spec-row {{ margin-bottom:14px; }}
.spec-row:last-child {{ margin-bottom:0; }}
.spec-label {{ font-size:.66rem; color:{G3}; font-weight:900; text-transform:uppercase; letter-spacing:1.6px; margin-bottom:4px; }}
.spec-val {{ font-size:1.05rem; font-weight:800; color:{BK}; }}

@media (max-width: 900px) {{
    [data-testid="stMainBlockContainer"] {{ padding:0 18px 42px 18px !important; }}
    .ux-hero {{ margin:0 -18px 18px -18px; padding:20px 18px; align-items:flex-start; flex-direction:column; }}
    .ux-hero-right {{ margin-top:10px; }}
    .ux-title {{ font-size:1.35rem; }}
    .signal-list {{ grid-template-columns:1fr; }}
    .persona-card-v2 {{ min-height:auto; }}
    .intro-grid {{ grid-template-columns:1fr; }}
    .intro-send {{ grid-template-columns:1fr; }}
}}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — entrada e controle
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"<div style='font-size:1.45rem;font-weight:900;color:{Y};letter-spacing:-1px;'>kyra.</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.78rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:18px;'>Análise de Transcrições</div>", unsafe_allow_html=True)

    input_mode = st.radio("Entrada", ["Upload de arquivo", "Colar texto", "Demonstração"], index=0)
    uploaded = None
    pasted_text = ""
    if input_mode == "Upload de arquivo":
        uploaded = st.file_uploader("PDF ou TXT", type=["pdf", "txt"], label_visibility="visible")
    elif input_mode == "Colar texto":
        pasted_text = st.text_area("Cole a transcrição", height=240, placeholder="Cole aqui a transcrição ou trecho da entrevista...")
    else:
        st.caption("Usa uma base simulada para visualizar a interface.")

    st.markdown("---")
    clean_moderator = st.checkbox("Reduzir viés de fala do moderador", value=True, help="Remove expressões de condução como 'muito bom', 'legal' e 'perfeito' antes dos scores leves.")
    show_diag = st.checkbox("Mostrar diagnóstico técnico", value=False)
    run_clicked = st.button("Analisar")

    st.markdown("---")
    render_status_badge(_PIPELINE_OK)
    if not _PIPELINE_OK:
        st.caption(f"Fallback ativo: {_PIPELINE_ERR or 'modelo principal indisponível'}")


# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="ux-hero">
  <div class="ux-brand">
    <div class="ux-logo">y.</div>
    <div>
      <div class="ux-title">Kyra Pesquisa</div>
      <div class="ux-subtitle">Temas · Sentimento · Personas · Tensões · Jobs-to-be-Done</div>
    </div>
  </div>
  <div class="ux-hero-right">IBMEC ML 2026</div>
</div>
""", unsafe_allow_html=True)

# Texto inicial amigável
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
    st.session_state.analysis_text = ""
    st.session_state.analysis_name = "projeto_demo"
    st.session_state.persona_jtbd = None
    st.session_state.speaker_info = None

should_process = run_clicked or (input_mode == "Demonstração" and st.session_state.analysis_result is None)

if should_process:
    texto_original = ""
    nome = "projeto_demo.txt"
    if input_mode == "Upload de arquivo" and uploaded is not None:
        nome = uploaded.name
        try:
            texto_original = extract_text_from_uploaded_file(uploaded)
        except Exception as exc:
            st.error(f"Não consegui ler o arquivo: {exc}")
            texto_original = ""
    elif input_mode == "Colar texto":
        nome = "texto_colado.txt"
        texto_original = pasted_text or ""
    elif input_mode == "Demonstração":
        nome = "projeto_demo.pdf"
        texto_original = ""

    if input_mode != "Demonstração" and not texto_original.strip():
        st.warning("Insira uma transcrição na barra lateral para iniciar a análise.")
    else:
        with st.spinner("Processando transcrição e gerando diagnóstico..."):
            if input_mode == "Demonstração":
                r = mock_pipeline(nome)
                texto_modelo = build_text_from_result(r)
            else:
                texto_modelo = remove_moderator_bias(texto_original) if clean_moderator else texto_original
                if _PIPELINE_OK and pipeline_run is not None:
                    try:
                        r = pipeline_run(texto_modelo, nome)
                        if not isinstance(r, dict) or "erro" in r or not r.get("temas"):
                            r = fallback_pipeline_from_text(texto_modelo, nome)
                            r["aviso_pipeline"] = "Pipeline principal não gerou saída completa; fallback leve usado."
                    except Exception as exc:
                        r = fallback_pipeline_from_text(texto_modelo, nome)
                        r["aviso_pipeline"] = f"Pipeline principal falhou; fallback leve usado. Detalhe: {exc}"
                else:
                    r = fallback_pipeline_from_text(texto_modelo, nome)
                    r["aviso_pipeline"] = "Modelo principal indisponível; fallback leve usado."

            speaker_info = estimate_speakers(texto_original or texto_modelo or build_text_from_result(r))
            # Participantes: só mostrar número quando há diarização explícita.
            # Sem Speaker tags, é melhor não inferir do que mostrar um número falso.
            if input_mode != "Demonstração":
                r["n_participantes"] = speaker_info.get("display", "n/d")
            elif speaker_info.get("confianca") == "alta":
                r["n_participantes"] = speaker_info.get("display", r.get("n_participantes", "n/d"))
            pj = run_persona_jtbd_analysis(texto_modelo or build_text_from_result(r), r)

            st.session_state.analysis_result = r
            st.session_state.analysis_text = texto_modelo or build_text_from_result(r)
            st.session_state.analysis_name = nome
            st.session_state.persona_jtbd = pj
            st.session_state.speaker_info = speaker_info

if st.session_state.analysis_result is None:
    st.markdown("""
    <div class="ux-section-head"><div class="ux-section-title">Sobre o produto</div></div>
    <div class="intro-grid">
        <div class="intro-card">
            <div class="intro-card-label">O que é</div>
            <div class="intro-card-text">Ferramenta de análise automática de entrevistas qualitativas com NLP — identifica temas, sentimentos e trechos representativos em minutos.</div>
        </div>
        <div class="intro-card">
            <div class="intro-card-label">Como usar</div>
            <div class="intro-card-text">Faça upload de uma transcrição em PDF ou TXT na barra lateral. O sistema processa automaticamente e entrega um relatório estruturado com evidências citáveis.</div>
        </div>
        <div class="intro-card">
            <div class="intro-card-label">O que você recebe</div>
            <div class="intro-card-text">Temas identificados · Sentimento por tema · Trechos representativos citáveis · Síntese narrativa · Exportação em CSV, JSON e TXT.</div>
        </div>
    </div>

    <div class="ux-section-head"><div class="ux-section-title">Enviar transcrição</div></div>
    <div class="intro-send">
        <div class="intro-send-main">
            <div class="intro-send-label">Comece agora</div>
            <div class="intro-send-text">Abra a <b>barra lateral à esquerda</b>, envie uma transcrição em PDF/TXT (ou cole o texto) e clique em <b>Analisar</b>. Você também pode usar o modo <b>Demonstração</b> para ver a interface com dados de exemplo.</div>
        </div>
        <div class="spec-card">
            <div class="spec-row"><div class="spec-label">Formatos</div><div class="spec-val">PDF · TXT</div></div>
            <div class="spec-row"><div class="spec-label">Idiomas</div><div class="spec-val">Português · Espanhol</div></div>
            <div class="spec-row"><div class="spec-label">Tamanho máximo</div><div class="spec-val">200 MB</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

r = st.session_state.analysis_result
analise_pj = st.session_state.persona_jtbd
texto_base = st.session_state.analysis_text
speaker_info = st.session_state.speaker_info or {}
temas = r.get("temas", [])
sent = r.get("sentimento", {"dominante":"NEU", "pct_pos":0, "pct_neu":100, "pct_neg":0})
dom = sent.get("dominante", "NEU")
sent_lbl = {"POS":"Positivo", "NEG":"Negativo", "NEU":"Neutro"}.get(dom, "Neutro")
sent_color = {"POS":POS, "NEG":NEG, "NEU":NEU}.get(dom, NEU)

# avisos úteis, mas discretos
if r.get("aviso_pipeline"):
    st.info(r["aviso_pipeline"])

if show_diag:
    with st.expander("Diagnóstico técnico do modelo principal", expanded=True):
        diag_rows = [
            {"item":"Importou src.pipeline", "status":"OK" if _MODEL_STATUS.get("pipeline_importado") else "Falhou", "detalhe":_MODEL_STATUS.get("erro", "") if not _MODEL_STATUS.get("pipeline_importado") else ""},
            {"item":"Pasta de modelos", "status":"OK" if _MODEL_STATUS.get("models_dir") else "Falhou", "detalhe":_MODEL_STATUS.get("models_dir", "")},
            {"item":"TF-IDF operacional", "status":"OK" if _MODEL_STATUS.get("tfidf_ok") else "Falhou", "detalhe":f"vocabulário={_MODEL_STATUS.get('tfidf_vocab_size',0)} | transform_teste={_MODEL_STATUS.get('tfidf_transform_ok', False)} | erro={_MODEL_STATUS.get('tfidf_transform_error','')}"},
            {"item":"NMF treinado", "status":"OK" if _MODEL_STATUS.get("nmf_ok") else "Falhou", "detalhe":f"componentes={_MODEL_STATUS.get('nmf_components',0)}"},
            {"item":"Tabela nmf_topics", "status":"OK" if _MODEL_STATUS.get("nmf_topics_ok") else "Falhou", "detalhe":"outputs/clusterizacao_insights_v2/.../tables/nmf_topics.csv"},
            {"item":"Evidências XAI", "status":"OK" if _MODEL_STATUS.get("evidencias_ok") else "Falhou", "detalhe":"outputs/xai/evidencias_por_topico.json"},
        ]
        st.dataframe(pd.DataFrame(diag_rows), hide_index=True, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab_resumo, tab_temas, tab_personas, tab_evidencias, tab_export = st.tabs([
    "1 · Resumo", "2 · Temas", "3 · Personas & JTBD", "4 · Evidências", "5 · Exportar"
])

with tab_resumo:
    st.markdown('<div class="ux-section-head"><div class="ux-section-title">Visão geral</div><div class="ux-section-note">Leitura executiva da transcrição</div></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1: render_metric_card("Trechos", f"{r.get('n_chunks', 0)}", "unidades analisadas")
    with c2: render_metric_card("Duração", f"{r.get('duracao_min', 0)} min", "estimada por palavras")
    with c3: render_metric_card("Temas", f"{len(temas)}", "detectados")
    with c4: render_metric_card("Sentimento", sent_lbl, "dominante", accent=sent_color)

    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1.35, 1], gap="large")
    with col_a:
        st.markdown(f"""
        <div class="ux-card-dark">
            <div class="ux-card-label">Síntese do projeto</div>
            <div class="ux-card-text">{html_escape(r.get('sintese',''))}</div>
        </div>
        <div class="ux-card">
            <div class="ux-card-label">Narrativa automática</div>
            <div class="ux-card-text">{html_escape(r.get('narrativa',''))}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        fig = go.Figure(go.Pie(
            labels=["Positivo", "Neutro", "Negativo"],
            values=[sent.get("pct_pos",0), sent.get("pct_neu",0), sent.get("pct_neg",0)],
            hole=.62, sort=False,
            marker=dict(colors=[POS, "#D8D8D8", NEG], line=dict(color=WH, width=4)),
            textinfo="percent", hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
        ))
        fig.update_layout(height=330, margin=dict(t=20,b=20,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=-.08), annotations=[dict(text=f"<b>{sent_lbl}</b>", x=.5, y=.5, showarrow=False, font=dict(size=17, color=BK))])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tab_temas:
    st.markdown('<div class="ux-section-head"><div class="ux-section-title">Temas e sentimento por tema</div><div class="ux-section-note">Clique nos gráficos para explorar</div></div>', unsafe_allow_html=True)
    if not temas:
        st.warning("Nenhum tema identificado.")
    else:
        df_t = pd.DataFrame(temas)
        # Gráficos em linhas separadas: em duas colunas eles ficavam estreitos e cortavam labels.
        fig_cob = make_bar_fig(
            df_t.sort_values("pct", ascending=False),
            "label", "pct", "Cobertura por tema",
            x_title="Cobertura estimada (%)", top_n=10, color=Y, suffix="%"
        )
        st.plotly_chart(fig_cob, use_container_width=True, config={"displayModeBar": False})

        df_s = pd.DataFrame([{ "Tema": t.get("label"), "Positivo": t.get("s_pos",0), "Neutro": t.get("s_neu",0), "Negativo": t.get("s_neg",0)} for t in temas]).iloc[::-1]
        fig_sent = go.Figure()
        for col, cor in [("Positivo", POS), ("Neutro", "#CFCFCF"), ("Negativo", NEG)]:
            fig_sent.add_trace(go.Bar(
                name=col,
                y=df_s["Tema"].map(lambda v: wrap_plot_label(v, width=38, max_lines=3)),
                x=df_s[col],
                orientation="h",
                marker_color=cor,
                texttemplate="%{x:.0f}%",
                textposition="inside",
                customdata=df_s["Tema"],
                hovertemplate="<b>%{customdata}</b><br>" + col + ": <b>%{x:.1f}%</b><extra></extra>",
            ))
        fig_sent.update_layout(
            barmode="stack",
            title=dict(text="Sentimento por tema", x=0, font=dict(size=18, color=BK, family="Inter")),
            height=max(430, 62*len(df_s)),
            margin=dict(t=58,b=78,l=20,r=35),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title="% dos trechos", range=[0, 100]),
            yaxis=dict(title="", tickfont=dict(size=13, color=BK)),
            legend=dict(orientation="h", y=-.16, x=0, font=dict(size=13, family="Inter")),
            bargap=0.34,
            uniformtext=dict(minsize=11, mode="hide"),
        )
        st.plotly_chart(fig_sent, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="ux-section-head"><div class="ux-section-title">Detalhe do tema</div><div class="ux-section-note">Termos e exemplos associados</div></div>', unsafe_allow_html=True)
        tema_sel = st.selectbox("Selecione um tema", [t.get("label") for t in temas])
        tema_cur = next((t for t in temas if t.get("label") == tema_sel), temas[0])
        cdet, cquotes = st.columns([1, 1.6], gap="large")
        with cdet:
            pills = "".join(f'<span class="pill-v2">{html_escape(p)}</span>' for p in tema_cur.get("termos", []))
            st.markdown(f"""
            <div class="ux-card">
                <div class="ux-card-label">{html_escape(tema_cur.get('label'))}</div>
                <div style="margin-bottom:14px;">{pills}</div>
                <div class="ux-card-text"><b>Cobertura:</b> {tema_cur.get('pct',0):.1f}%<br><b>Lift:</b> {tema_cur.get('lift',0):.1f}x<br><b>Sentimento:</b> +{tema_cur.get('s_pos',0):.0f}% / ~{tema_cur.get('s_neu',0):.0f}% / -{tema_cur.get('s_neg',0):.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with cquotes:
            for q in tema_cur.get("trechos", [])[:3]:
                st.markdown(f'<div class="quote-v2"><div class="quote-v2-text">“{html_escape(q)}”</div></div>', unsafe_allow_html=True)

with tab_personas:
    st.markdown('<div class="ux-section-head"><div class="ux-section-title">Classificação por persona</div><div class="ux-section-note">Aderência relativa aos perfis comportamentais</div></div>', unsafe_allow_html=True)
    persona_df = analise_pj["personas"].copy()
    pcols = st.columns(3, gap="medium")
    for i, (_, row) in enumerate(persona_df.head(3).iterrows()):
        with pcols[i]:
            render_persona_card(row, i+1)

    st.markdown('<div class="ux-section-head"><div class="ux-section-title">Síntese, tensão e intensidade</div><div class="ux-section-note">O que move, o que trava e qual job aparece</div></div>', unsafe_allow_html=True)
    col_s, col_q, col_i = st.columns([1.6, 1, 1], gap="large")
    with col_s:
        st.markdown(f"""
        <div class="ux-card-dark">
            <div class="ux-card-label">Síntese comportamental</div>
            <div class="ux-card-text">{html_escape(analise_pj['sintese_personas_jtbd'])}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_q:
        st.markdown(f"""
        <div class="ux-card">
            <div class="ux-card-label">Quadrante de tensão</div>
            <div class="ux-card-text"><b>{html_escape(analise_pj['quadrante'])}</b><br>{html_escape(analise_pj['quadrante_desc'])}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_i:
        st.markdown(f"""
        <div class="ux-card">
            <div class="ux-card-label">Intensidade</div>
            <div class="ux-card-text"><b>Motivação:</b> {analise_pj['motivadores_total_per_1k']:.1f}/1k<br><b>Barreiras:</b> {analise_pj['barreiras_total_per_1k']:.1f}/1k<br><span class='small-muted'>Referência histórica: 42,6 e 5,9 por 1k.</span></div>
        </div>
        """, unsafe_allow_html=True)

    col_m, col_b = st.columns(2, gap="large")
    with col_m:
        st.plotly_chart(make_bar_fig(analise_pj["motivators"], "dimensao", "aderencia_pct", "Principais motivadores", top_n=6, color=Y), use_container_width=True, config={"displayModeBar": False})
    with col_b:
        st.plotly_chart(make_bar_fig(analise_pj["barriers"], "dimensao", "aderencia_pct", "Principais barreiras", top_n=6, color=NEG), use_container_width=True, config={"displayModeBar": False})

    col_j, col_o = st.columns([1.1, 1], gap="large")
    with col_j:
        st.plotly_chart(make_bar_fig(analise_pj["jtbd"], "dimensao", "aderencia_pct", "Jobs-to-be-Done", top_n=7, color=Y), use_container_width=True, config={"displayModeBar": False})
    with col_o:
        opp = analise_pj.get("oportunidades_persona", {})
        st.markdown('<div class="ux-section-head"><div class="ux-section-title">Oportunidades acionáveis</div></div>', unsafe_allow_html=True)
        for k in ["produto", "comunicacao", "canal", "risco"]:
            if opp.get(k):
                st.markdown(f"<div class='signal-item'><div class='signal-title'>{fmt_label(k)}</div><div class='signal-val'>{html_escape(opp[k])}</div></div>", unsafe_allow_html=True)
        if analise_pj.get("oportunidade_jtbd"):
            st.markdown(f"<div class='signal-item' style='margin-top:12px;'><div class='signal-title'>Oportunidade pelo JTBD</div><div class='signal-val'>{html_escape(analise_pj['oportunidade_jtbd'])}</div></div>", unsafe_allow_html=True)

with tab_evidencias:
    st.markdown('<div class="ux-section-head"><div class="ux-section-title">Evidências citáveis</div><div class="ux-section-note">Trechos representativos dos temas detectados</div></div>', unsafe_allow_html=True)
    for t in temas:
        with st.expander(f"{t.get('label')} · {t.get('pct',0):.1f}% de cobertura", expanded=False):
            st.write("Termos:", ", ".join(t.get("termos", [])))
            for q in t.get("trechos", [])[:4]:
                st.markdown(f'<div class="quote-v2"><div class="quote-v2-text">“{html_escape(q)}”</div></div>', unsafe_allow_html=True)

with tab_export:
    st.markdown('<div class="ux-section-head"><div class="ux-section-title">Exportar resultados</div><div class="ux-section-note">Baixe CSV, JSON ou relatório TXT</div></div>', unsafe_allow_html=True)
    df_exp = pd.DataFrame([{
        "tema": t.get("label"), "cobertura_pct": t.get("pct"), "lift": t.get("lift"),
        "termos": ", ".join(t.get("termos", [])), "sentimento_pos": t.get("s_pos"), "sentimento_neg": t.get("s_neg"), "sentimento_neu": t.get("s_neu"),
    } for t in temas])
    export_obj = dict(r)
    export_obj["persona_jtbd"] = {
        "personas": analise_pj["personas"].to_dict(orient="records"),
        "motivadores": analise_pj["motivators"].to_dict(orient="records"),
        "barreiras": analise_pj["barriers"].to_dict(orient="records"),
        "jtbd": analise_pj["jtbd"].to_dict(orient="records"),
        "quadrante": analise_pj["quadrante"],
        "sintese": analise_pj["sintese_personas_jtbd"],
    }
    rel = (
        f"KYRA PESQUISA — RELATÓRIO DE ANÁLISE\nProjeto: {r.get('projeto','')}\n{'─'*52}\n\n"
        f"SÍNTESE\n{r.get('sintese','')}\n\nSENTIMENTO GERAL\n"
        f"Positivo: {sent.get('pct_pos',0):.1f}% | Neutro: {sent.get('pct_neu',0):.1f}% | Negativo: {sent.get('pct_neg',0):.1f}%\n\n"
        f"PERSONAS / JTBD\n{analise_pj['sintese_personas_jtbd']}\nQuadrante: {analise_pj['quadrante']}\n\nTEMAS\n"
    ) + "\n".join([f"- {t.get('label')} ({t.get('pct',0):.1f}%)" for t in temas])

    d1, d2, d3 = st.columns(3, gap="medium")
    with d1:
        st.download_button("↓ CSV de temas", df_exp.to_csv(index=False).encode(), f"{r.get('projeto','projeto')}_temas.csv", "text/csv", use_container_width=True)
    with d2:
        st.download_button("↓ JSON completo", json.dumps(export_obj, ensure_ascii=False, indent=2, default=str).encode(), f"{r.get('projeto','projeto')}_analise.json", "application/json", use_container_width=True)
    with d3:
        st.download_button("↓ Relatório TXT", rel.encode(), f"{r.get('projeto','projeto')}_relatorio.txt", "text/plain", use_container_width=True)

st.markdown(f"""
<div class="kyra-footer">
    <div class="kyra-footer-left"><span>kyra.</span> / Análise de Transcrições — IBMEC ML 2026</div>
    <div class="kyra-footer-right">Maria Beatriz Ribeiro · Juliane Oliveira · Emanuel Gandra</div>
</div>
""", unsafe_allow_html=True)
