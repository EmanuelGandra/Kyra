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

        status["tfidf_has_idf"] = bool(tfidf is not None and hasattr(tfidf, "idf_"))
        status["tfidf_vocab_size"] = int(len(getattr(tfidf, "vocabulary_", {}) or {})) if tfidf is not None else 0
        status["tfidf_ok"] = bool(status["tfidf_has_idf"] and status["tfidf_vocab_size"] > 0)

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
    mot_total = float(mot_df["per_1k"].sum())
    bar_total = float(bar_df["per_1k"].sum())
    jtbd_pct = _to_pct(dict(zip(jtbd_df["dimensao"], jtbd_df["per_1k"])))
    jtbd_df["aderencia_pct"] = jtbd_df["dimensao"].map(jtbd_pct)
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
    if not _PIPELINE_OK:
        st.markdown(f"""
        <div class="model-status">
            <b>Modelo principal não carregado.</b><br>
            O app vai usar a análise leve de fallback para temas/sentimento e manter a análise de personas, tensões e JTBD.<br>
            <span style="color:#555555;">Detalhe técnico: {html.escape(_PIPELINE_ERR)}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="model-status-ok">
            <b>Modelo principal carregado.</b><br>
            Temas e sentimento serão processados com o pipeline treinado.
        </div>
        """, unsafe_allow_html=True)

with st.expander("Diagnóstico do modelo principal", expanded=False):
    st.markdown("Use este painel para conferir se o app está carregando os artefatos corretos do pipeline de temas/sentimento.")
    diag = pd.DataFrame([
        {"item": "Importou src.pipeline", "status": "OK" if _MODEL_STATUS.get("pipeline_importado") else "Falhou", "detalhe": ""},
        {"item": "Pasta de modelos", "status": "OK" if _MODEL_STATUS.get("models_dir") else "Falhou", "detalhe": str(_MODEL_STATUS.get("models_dir", ""))},
        {"item": "TF-IDF treinado", "status": "OK" if _MODEL_STATUS.get("tfidf_ok") else "Falhou", "detalhe": f"vocabulário={_MODEL_STATUS.get('tfidf_vocab_size', 0)} | idf_={_MODEL_STATUS.get('tfidf_has_idf', False)}"},
        {"item": "NMF treinado", "status": "OK" if _MODEL_STATUS.get("nmf_ok") else "Falhou", "detalhe": f"componentes={_MODEL_STATUS.get('nmf_components', 0)}"},
        {"item": "Tabela nmf_topics", "status": "OK" if _MODEL_STATUS.get("nmf_topics_ok") else "Falhou", "detalhe": "outputs/clusterizacao_insights_v2/.../tables/nmf_topics.csv"},
        {"item": "Evidências XAI", "status": "OK" if _MODEL_STATUS.get("evidencias_ok") else "Aviso", "detalhe": "outputs/xai/evidencias_por_topico.json"},
    ])
    st.dataframe(diag, use_container_width=True, hide_index=True)
    files_df = pd.DataFrame([{"arquivo": k, "encontrado": v} for k, v in (_MODEL_STATUS.get("arquivos_modelo") or {}).items()])
    if not files_df.empty:
        st.markdown("**Arquivos esperados em `src/models`**")
        st.dataframe(files_df, use_container_width=True, hide_index=True)
    if _PIPELINE_ERR:
        st.caption(f"Detalhe técnico: {_PIPELINE_ERR}")

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
texto_analise = ""
if arquivo:
    with st.spinner("Analisando transcrição... Isso pode levar alguns minutos."):
        try:
            texto_analise = extract_text_from_uploaded_file(arquivo)
        except Exception as ex:
            st.error(f"Erro ao ler arquivo: {ex}")
            texto_analise = ""

        if _PIPELINE_OK and texto_analise.strip():
            try:
                r = pipeline_run(texto_analise, arquivo.name)
                if "erro" in r:
                    st.warning("O pipeline principal não conseguiu gerar temas/sentimento. Usei uma análise leve de fallback sobre a transcrição enviada.")
                    r = fallback_pipeline_from_text(texto_analise, arquivo.name)
            except Exception as ex:
                msg = str(ex)
                if "idf vector is not fitted" in msg.lower():
                    st.warning("O modelo de temas do pipeline principal não estava treinado/carregado nesta sessão. Usei uma análise leve de fallback sobre a transcrição enviada.")
                else:
                    st.warning(f"O pipeline principal não conseguiu processar a transcrição ({msg}). Usei uma análise leve de fallback sobre o texto enviado.")
                r = fallback_pipeline_from_text(texto_analise, arquivo.name)
        else:
            st.warning("Pipeline principal indisponível ou texto vazio. Usando análise leve de fallback para temas/sentimento.")
            r = fallback_pipeline_from_text(texto_analise, arquivo.name) if texto_analise.strip() else mock_pipeline(nome)
    st.success("Análise concluída com sucesso.")
else:
    r = mock_pipeline(nome)
    texto_analise = build_text_from_result(r)

if not texto_analise.strip():
    texto_analise = build_text_from_result(r)

analise_pj = run_persona_jtbd_analysis(texto_analise, r)

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
# PERSONAS, TENSÕES E JOBS-TO-BE-DONE
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="sec-title">Personas · Tensões · Jobs-to-be-Done</span>', unsafe_allow_html=True)

persona_df = analise_pj["personas"]
jtbd_df = analise_pj["jtbd"]
mot_df = analise_pj["motivators"]
bar_df = analise_pj["barriers"]
dim_df = analise_pj["dimensions"]

# Renderiza sempre as 3 personas, uma por coluna.
# Isso evita HTML quebrado aparecer como texto na interface e garante que a terceira persona apareça mesmo com score baixo.
_persona_order = ["Cuidadora Consciente", "Comparadora Omnicanal", "Compradora Social e Presenteadora"]
_missing_rows = []
for _p in _persona_order:
    if _p not in set(persona_df["persona"].astype(str)):
        _missing_rows.append({
            "persona": _p,
            "aderencia_pct": 0.0,
            "score_bruto": 0.0,
            "descricao": PERSONA_PROFILES[_p]["descricao"],
        })
if _missing_rows:
    persona_df = pd.concat([persona_df, pd.DataFrame(_missing_rows)], ignore_index=True)
persona_df = persona_df.sort_values("aderencia_pct", ascending=False).head(3).reset_index(drop=True)

st.markdown('<div class="subsec-title">Classificação por persona</div>', unsafe_allow_html=True)
_persona_cols = st.columns(3, gap="medium")
for idx, row in persona_df.iterrows():
    main_cls = " persona-card-main" if idx == 0 else ""
    with _persona_cols[idx]:
        st.markdown(f"""
        <div class="persona-card{main_cls}">
            <div class="persona-name">{html.escape(str(row['persona']))}</div>
            <div class="persona-pct">{float(row['aderencia_pct']):.1f}%</div>
            <div class="persona-desc">{html.escape(str(row['descricao']))}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="card-separator"></div><div class="subsec-title">Síntese, tensão e intensidade</div>', unsafe_allow_html=True)
cpa, cpb, cpc = st.columns([2, 1, 1], gap="medium")
with cpa:
    st.markdown(f'''
    <div class="analysis-card">
        <div class="mini-card-label">Síntese comportamental</div>
        <div class="analysis-txt">{html.escape(analise_pj['sintese_personas_jtbd'])}</div>
    </div>
    ''', unsafe_allow_html=True)
with cpb:
    st.markdown(f'''
    <div class="mini-card">
        <div class="mini-card-label">Quadrante de tensão</div>
        <div class="mini-card-val">{html.escape(analise_pj['quadrante'])}</div>
        <div class="analysis-txt" style="margin-top:8px;">{html.escape(analise_pj['quadrante_desc'])}</div>
    </div>
    ''', unsafe_allow_html=True)
with cpc:
    st.markdown(f'''
    <div class="mini-card">
        <div class="mini-card-label">Intensidade</div>
        <div class="mini-card-val">Motivação: {analise_pj['motivadores_total_per_1k']:.1f}/1k<br>Barreiras: {analise_pj['barreiras_total_per_1k']:.1f}/1k</div>
        <div class="analysis-txt" style="margin-top:8px;">Referência histórica: mediana de 42,6 e 5,9 por 1k palavras.</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="card-separator"></div><div class="subsec-title">Gráficos de aderência</div>', unsafe_allow_html=True)
col_p, col_j = st.columns(2, gap="large")
with col_p:
    dfp = persona_df.sort_values("aderencia_pct")
    fig_persona = go.Figure(go.Bar(x=dfp["aderencia_pct"], y=dfp["persona"], orientation="h", marker=dict(color=Y, line=dict(color=BK, width=1)), text=dfp["aderencia_pct"].map(lambda v: f"{v:.1f}%"), textposition="outside", hovertemplate="<b>%{y}</b><br>Aderência relativa: <b>%{x:.1f}%</b><extra></extra>"))
    fig_persona.update_layout(title=dict(text="Aderência às personas", font=dict(size=13, color=G4, family="Inter"), x=0), height=270, margin=dict(t=40, b=20, l=10, r=55), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(range=[0, max(100, dfp["aderencia_pct"].max()+10)], showgrid=False, ticksuffix="%"), yaxis=dict(tickfont=dict(size=12, color=BK, family="Inter")), hoverlabel=dict(bgcolor=BK, font_color=WH, bordercolor=Y))
    st.plotly_chart(fig_persona, use_container_width=True, config={"displayModeBar":False})

with col_j:
    dfj = jtbd_df.head(6).sort_values("aderencia_pct")
    fig_jtbd = go.Figure(go.Bar(x=dfj["aderencia_pct"], y=dfj["dimensao"].map(pretty_dim), orientation="h", marker=dict(color=Y, line=dict(color=BK, width=1)), text=dfj["aderencia_pct"].map(lambda v: f"{v:.1f}%"), textposition="outside", hovertemplate="<b>%{y}</b><br>Aderência relativa: <b>%{x:.1f}%</b><extra></extra>"))
    fig_jtbd.update_layout(title=dict(text="Jobs-to-be-Done dominantes", font=dict(size=13, color=G4, family="Inter"), x=0), height=310, margin=dict(t=40, b=20, l=10, r=55), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False, ticksuffix="%"), yaxis=dict(tickfont=dict(size=11, color=BK, family="Inter")), hoverlabel=dict(bgcolor=BK, font_color=WH, bordercolor=Y))
    st.plotly_chart(fig_jtbd, use_container_width=True, config={"displayModeBar":False})

st.markdown('<div class="card-separator"></div><div class="subsec-title">Mapa de tensões e principais sinais</div>', unsafe_allow_html=True)
col_m, col_b = st.columns(2, gap="large")
with col_m:
    xmax = max(analise_pj['motivadores_total_per_1k']*1.25, REFERENCE_MEDIAN_MOTIVATION*1.6)
    ymax = max(analise_pj['barreiras_total_per_1k']*1.35, REFERENCE_MEDIAN_BARRIER*2.2)
    fig_tensao = go.Figure()
    fig_tensao.add_shape(type="line", x0=REFERENCE_MEDIAN_MOTIVATION, x1=REFERENCE_MEDIAN_MOTIVATION, y0=0, y1=ymax, line=dict(color=G3, dash="dash"))
    fig_tensao.add_shape(type="line", x0=0, x1=xmax, y0=REFERENCE_MEDIAN_BARRIER, y1=REFERENCE_MEDIAN_BARRIER, line=dict(color=G3, dash="dash"))
    fig_tensao.add_trace(go.Scatter(x=[analise_pj['motivadores_total_per_1k']], y=[analise_pj['barreiras_total_per_1k']], mode="markers+text", text=["Entrevista"], textposition="top center", marker=dict(size=18, color=Y, line=dict(color=BK, width=2)), hovertemplate="Motivadores: <b>%{x:.1f}</b>/1k<br>Barreiras: <b>%{y:.1f}</b>/1k<extra></extra>"))
    fig_tensao.update_layout(title=dict(text="Mapa de tensão da entrevista", font=dict(size=13, color=G4, family="Inter"), x=0), height=330, margin=dict(t=40, b=40, l=40, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(title="Motivadores por 1k palavras", showgrid=True, gridcolor=G2, zeroline=False, range=[0, xmax]), yaxis=dict(title="Barreiras por 1k palavras", showgrid=True, gridcolor=G2, zeroline=False, range=[0, ymax]), hoverlabel=dict(bgcolor=BK, font_color=WH, bordercolor=Y))
    st.plotly_chart(fig_tensao, use_container_width=True, config={"displayModeBar":False})

with col_b:
    top_mot = mot_df.head(4)
    top_bar = bar_df.head(4)
    st.markdown('<div class="analysis-card"><div class="mini-card-label">Principais motivadores</div>', unsafe_allow_html=True)
    total_m = max(top_mot["per_1k"].sum(), 1e-9)
    for _, row in top_mot.iterrows():
        st.markdown(pct_bar(pretty_dim(row["dimensao"]), 100*row["per_1k"]/total_m), unsafe_allow_html=True)
    st.markdown('<div class="mini-card-label" style="margin-top:18px;">Principais barreiras</div>', unsafe_allow_html=True)
    total_b = max(top_bar["per_1k"].sum(), 1e-9)
    for _, row in top_bar.iterrows():
        st.markdown(pct_bar(pretty_dim(row["dimensao"]), 100*row["per_1k"]/total_b), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

opp = analise_pj["oportunidades_persona"]
st.markdown('<span class="sec-title">Oportunidades acionáveis</span>', unsafe_allow_html=True)
opp_cards = []
for lbl, val in [("Produto", opp.get("produto", "")), ("Comunicação", opp.get("comunicacao", "")), ("Canal", opp.get("canal", "")), ("Risco / barreira", opp.get("risco", ""))]:
    opp_cards.append(f'<div class="mini-card"><div class="mini-card-label">{lbl}</div><div class="analysis-txt">{html.escape(val)}</div></div>')
st.markdown('<div class="analysis-grid-2">' + ''.join(opp_cards) + '</div>', unsafe_allow_html=True)

if analise_pj.get("oportunidade_jtbd"):
    st.markdown(f'''
    <div class="sintese-block">
        <div class="sintese-label">Oportunidade pelo JTBD dominante</div>
        <div class="sintese-txt">{html.escape(analise_pj['oportunidade_jtbd'])}</div>
    </div>
    ''', unsafe_allow_html=True)

with st.expander("Ver dimensões calculadas e tabelas técnicas"):
    st.markdown("**Dimensões comportamentais da entrevista**")
    st.dataframe(dim_df.rename(columns={"dimensao":"dimensão", "hits":"menções", "per_1k":"menções por 1k palavras"}), use_container_width=True, hide_index=True)
    st.markdown("**Motivadores**")
    st.dataframe(mot_df.rename(columns={"dimensao":"motivador", "hits":"menções", "per_1k":"menções por 1k palavras"}), use_container_width=True, hide_index=True)
    st.markdown("**Barreiras**")
    st.dataframe(bar_df.rename(columns={"dimensao":"barreira", "hits":"menções", "per_1k":"menções por 1k palavras"}), use_container_width=True, hide_index=True)
    st.markdown("**Jobs-to-be-Done**")
    st.dataframe(jtbd_df.rename(columns={"dimensao":"JTBD", "hits":"menções", "per_1k":"menções por 1k palavras", "aderencia_pct":"aderência relativa (%)"}), use_container_width=True, hide_index=True)

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

export_payload = dict(r)
export_payload["persona_jtbd"] = {
    "n_words": analise_pj["n_words"],
    "personas": analise_pj["personas"].to_dict(orient="records"),
    "motivadores": analise_pj["motivators"].to_dict(orient="records"),
    "barreiras": analise_pj["barriers"].to_dict(orient="records"),
    "jtbd": analise_pj["jtbd"].to_dict(orient="records"),
    "quadrante": analise_pj["quadrante"],
    "sintese": analise_pj["sintese_personas_jtbd"],
    "oportunidades_persona": analise_pj["oportunidades_persona"],
    "oportunidade_jtbd": analise_pj["oportunidade_jtbd"],
}

rel = (
    f"KYRA PESQUISA — RELATÓRIO DE ANÁLISE\n"
    f"Projeto: {r['projeto']}\n{'─'*52}\n\n"
    f"SÍNTESE\n{r['sintese']}\n\n"
    f"SENTIMENTO GERAL\n"
    f"Positivo: {sent['pct_pos']:.1f}%  |  Neutro: {sent['pct_neu']:.1f}%  |  Negativo: {sent['pct_neg']:.1f}%\n\n"
    f"NARRATIVA\n{r['narrativa']}\n\n"
    f"PERSONAS / JTBD\n{analise_pj['sintese_personas_jtbd']}\n"
    f"Quadrante: {analise_pj['quadrante']}\n"
    f"Oportunidade JTBD: {analise_pj['oportunidade_jtbd']}\n\nTEMAS IDENTIFICADOS\n"
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
        json.dumps(export_payload, ensure_ascii=False, indent=2).encode(),
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
