"""
Kyra Pesquisa — Pipeline de análise de transcrições.

Uso no app.py:
    from src.pipeline import run
    resultado = run(texto, nome_arquivo)
"""
import re
import json
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

# ── caminhos ─────────────────────────────────────────────────────────────────
_HERE   = Path(__file__).resolve().parent
_ROOT   = _HERE.parent
_MODELS = _HERE / "models"

_CLUSTER_BASE = _ROOT / "outputs" / "clusterizacao_insights_v2"
_CLUSTER_RUN  = sorted(_CLUSTER_BASE.glob("*"))[-1]
_XAI_DIR      = _ROOT / "outputs" / "xai"

# ── carrega modelos uma vez (ao importar o módulo) ────────────────────────────
_tfidf  = joblib.load(_MODELS / "tfidf.pkl")
_nmf    = joblib.load(_MODELS / "nmf.pkl")
_kmeans = joblib.load(_MODELS / "kmeans.pkl")
_nb     = joblib.load(_MODELS / "taxonomy_nb.pkl")

# ── carrega tabelas de referência ─────────────────────────────────────────────
_nmf_topics = pd.read_csv(_CLUSTER_RUN / "tables" / "nmf_topics.csv")

with open(_XAI_DIR / "evidencias_por_topico.json", encoding="utf-8") as _f:
    _evidencias = {e["topic_id"]: e for e in json.load(_f)}

# ── helpers ───────────────────────────────────────────────────────────────────
def _clean(texto: str) -> str:
    texto = re.sub(r"Speaker \d+\s*[-–]\s*\d{2}:\d{2}", " ", texto)
    texto = re.sub(r"\d{2}:\d{2}(:\d{2})?", " ", texto)
    texto = re.sub(r"\b(mp3|m4a|wav|pdf)\b", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"https?://\S+", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def _chunks(texto: str, target: int = 250, min_words: int = 60) -> list:
    words = texto.split()
    result, i = [], 0
    while i < len(words):
        chunk = words[i: i + target]
        if len(chunk) >= min_words:
            result.append(" ".join(chunk))
        i += target
    return result or [texto]

def _norm(w: str) -> str:
    s = unicodedata.normalize("NFKD", w.lower())
    return "".join(c for c in s if not unicodedata.combining(c))

# ── léxico completo do nb06 ───────────────────────────────────────────────────
_TERMOS_POS = {
    "ótimo","ótima","ótimos","ótimas","excelente","excelentes","excepcional",
    "incrível","incríveis","maravilhoso","maravilhosa","maravilhosos","maravilhosas",
    "fantástico","fantástica","perfeito","perfeita","perfeitos","perfeitas",
    "top","show","demais","legal","bacana","bom","boa","bons","boas",
    "positivo","positiva","melhor","melhores",
    "adoro","adorei","amo","amei","gosto","gostei","gosta","gostamos",
    "adotei","adotaria","prefiro","preferi","preferiria","curto","curti","curtiu",
    "aprecio","apreciei","recomendo","recomendaria","recomendei","recomenda",
    "indicaria","indico","indiquei","indica",
    "satisfeito","satisfeita","satisfação","contente","feliz",
    "animado","animada","empolgado","empolgada",
    "qualidade","eficiente","eficaz","funciona","funcionou","resolve","resolveu",
    "prático","prática","práticos","práticas","fácil","simples","conveniente","acessível",
    "vale","valeu","confiança","confiável","seguro","segura","segurança",
    "agradável","bonito","bonita","lindo","linda","elegante",
    "inovador","inovadora","único","única","superou","surpreendeu","surpreendente",
    "benefício","vantagem","gostoso","delicioso","aprovado","aprovada",
    "otimo","otima","incrivel","marvilhoso","agradavel","pratico","facil","confiavel",
    "hidrata","suave","macio","leve","rapido","rapida",
}

_TERMOS_NEG = {
    "péssimo","péssima","péssimos","péssimas","horrível","horríveis",
    "terrível","terríveis","ruim","ruins","fraco","fraca","fracos","fracas",
    "negativo","negativa","decepcionante","frustrante","insatisfatório","insatisfatória",
    "pior","piores","detesto","detestei","odeio","odiei","detestava","odiava",
    "insatisfeito","insatisfeita","insatisfação","frustrado","frustrada","frustração",
    "decepcionado","decepcionada","decepção","arrependimento","arrependida","arrependido",
    "desapontado","desapontada","desapontamento",
    "problema","problemas","defeito","defeitos","falha","falhas",
    "erro","erros","travou","quebrou","estragou","danificou","danifica",
    "reclamar","reclamei","reclamação","reclamações","reclamo",
    "vergonhoso","vergonhosa","absurdo","absurda","inaceitável","inadmissível",
    "enganoso","enganosa","difícil","difíceis","caro","cara","caros","caras",
    "pessimo","pessima","horrivel","terrivel","nao recomendo","nao gosto",
    "ressecou","irritou","ardeu","oleoso","pegajoso","nojento","alergia",
}

_NEGACOES = {
    "não","nao","nunca","jamais","nem","nenhum","nenhuma","tampouco",
    "sequer","sem","contra","impossível","incapaz",
}

def _sentiment_lexico(texto: str) -> dict:
    """Léxico ampliado do nb06 com detecção de negação em janela de 3 palavras."""
    t = texto.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    palavras = t.split()

    n_pos, n_neg = 0, 0
    JANELA = 3

    # multi-word primeiro
    for termo, pol in [(tm, +1) for tm in _TERMOS_POS if " " in tm] + \
                      [(tm, -1) for tm in _TERMOS_NEG if " " in tm]:
        if termo in t:
            idx = t.find(termo)
            prefixo = t[:idx].split()
            negado = any(w in _NEGACOES for w in prefixo[-JANELA:])
            pol_ef = -pol if negado else pol
            if pol_ef > 0: n_pos += 1
            else: n_neg += 1

    # palavras individuais
    for i, palavra in enumerate(palavras):
        pw = _norm(palavra)
        if pw in {_norm(x) for x in _TERMOS_POS}:
            pol = +1
        elif pw in {_norm(x) for x in _TERMOS_NEG}:
            pol = -1
        else:
            continue
        contexto = palavras[max(0, i-JANELA):i]
        negado = any(_norm(w) in {_norm(n) for n in _NEGACOES} for w in contexto)
        pol_ef = -pol if negado else pol
        if pol_ef > 0: n_pos += 1
        else: n_neg += 1

    score = n_pos - n_neg
    total = n_pos + n_neg
    confianca = round(abs(score) / total, 3) if total > 0 else 0.0

    if score > 0:
        return {"sentimento": "POS", "score": confianca, "fonte": "lexico"}
    elif score < 0:
        return {"sentimento": "NEG", "score": confianca, "fonte": "lexico"}
    return {"sentimento": "NEU", "score": 0.0, "fonte": "lexico"}

# ── carrega BERT uma vez ao importar ─────────────────────────────────────────
_bert_pipe = None

def _get_bert():
    global _bert_pipe
    if _bert_pipe is None:
        try:
            from transformers import pipeline as hf_pipeline
            _bert_pipe = hf_pipeline(
                "text-classification",
                model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
                truncation=True, max_length=512, top_k=None,
            )
        except Exception:
            pass
    return _bert_pipe

def _sentiment_bert(chunk: str) -> dict:
    """DistilBERT com threshold de 0.60."""
    pipe = _get_bert()
    if pipe is None:
        return None
    try:
        scores = pipe(chunk[:512])[0]
        sm = {x["label"]: x["score"] for x in scores}
        pos, neg = sm.get("positive", 0), sm.get("negative", 0)
        THRESHOLD = 0.60
        if pos >= THRESHOLD:
            return {"sentimento": "POS", "score": round(pos, 4), "fonte": "bert"}
        elif neg >= THRESHOLD:
            return {"sentimento": "NEG", "score": round(neg, 4), "fonte": "bert"}
        return {"sentimento": "NEU", "score": round(sm.get("neutral", 0), 4), "fonte": "bert"}
    except Exception:
        return None

def _sentiment_combinado(chunks: list) -> list:
    """
    Combina BERT + léxico para maior precisão em textos de pesquisa qualitativa.

    Regras de combinação:
    - BERT e léxico concordam → usa esse resultado com alta confiança
    - BERT diz NEU (baixa confiança) e léxico tem opinião → usa léxico
    - BERT tem opinião forte (>= 0.60) e léxico diz NEU → usa BERT
    - BERT e léxico discordam → classifica como NEU (texto ambíguo)
    """
    results = []
    for c in chunks:
        lex = _sentiment_lexico(c)
        bert = _sentiment_bert(c)

        if bert is None:
            # BERT falhou — usa léxico
            results.append(lex)
            continue

        b_sent = bert["sentimento"]
        l_sent = lex["sentimento"]

        if b_sent == l_sent:
            # concordam → resultado confiável
            results.append({"sentimento": b_sent, "score": bert["score"]})
        elif b_sent == "NEU" and l_sent != "NEU":
            # BERT incerto, léxico tem opinião → usa léxico
            results.append(lex)
        elif l_sent == "NEU" and b_sent != "NEU":
            # léxico neutro, BERT tem opinião forte → usa BERT
            results.append(bert)
        else:
            # discordam → NEU (texto ambíguo, não força classificação)
            results.append({"sentimento": "NEU", "score": 0.0})

    return results

def _pii_ok(texto: str) -> bool:
    patterns = [
        r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
        r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b",
        r"(?:\+?55\s*)?\(?\d{2}\)?\s*\d{4,5}-?\d{4}",
    ]
    return not any(re.search(p, texto) for p in patterns)

# ── função principal ──────────────────────────────────────────────────────────
def run(texto_bruto: str, nome: str = "projeto") -> dict:
    """
    Recebe o texto completo de uma transcrição.
    Retorna dicionário no formato que o app.py espera.
    """
    nome_limpo = Path(nome).stem

    # 1. limpeza + chunking
    texto  = _clean(texto_bruto)
    chunks = _chunks(texto)
    n_chunks = len(chunks)

    if n_chunks == 0:
        return {"erro": "Texto muito curto ou vazio após limpeza."}

    # 2. vetoriza com TF-IDF treinado
    X = _tfidf.transform(chunks)

    # 3. tópicos NMF — cada chunk → tópico dominante
    W          = _nmf.transform(X)
    topico_ids = W.argmax(axis=1)

    # 4. sentimento combinado BERT + léxico
    sent_results = _sentiment_combinado(chunks)
    sentimentos  = [s["sentimento"] for s in sent_results]

    # 5. métricas gerais
    n_speakers = len(set(re.findall(r"Speaker\s*(\d+)", texto_bruto)))
    if n_speakers == 0:
        n_speakers = min(10, max(2, len(chunks) // 5))
    n_participantes = max(1, n_speakers - 1)
    duracao_min     = max(1, round(len(texto.split()) / 130))

    n_pos = sentimentos.count("POS")
    n_neg = sentimentos.count("NEG")
    n_neu = sentimentos.count("NEU")
    pct_pos = round(n_pos / n_chunks * 100, 1)
    pct_neg = round(n_neg / n_chunks * 100, 1)
    pct_neu = round(n_neu / n_chunks * 100, 1)
    dominante = max(
        {"POS": pct_pos, "NEG": pct_neg, "NEU": pct_neu},
        key=lambda k: {"POS": pct_pos, "NEG": pct_neg, "NEU": pct_neu}[k]
    )

    # 6. agrega por tópico NMF
    temas_out = []
    for t_num in range(_nmf.n_components):
        idx = np.where(topico_ids == t_num)[0]
        if len(idx) == 0:
            continue
        pct = round(len(idx) / n_chunks * 100, 1)
        if pct < 3.0:
            continue

        t_id  = f"nmf_{t_num:02d}"
        t_row = _nmf_topics[_nmf_topics["topic_id"] == t_id]
        label  = t_row["auto_label_short"].iloc[0] if len(t_row) > 0 else t_id
        termos = [t.strip() for t in t_row["top_terms"].iloc[0].split(";")][:6] \
                 if len(t_row) > 0 else []

        s_tema = [sentimentos[i] for i in idx]
        s_pos  = round(s_tema.count("POS") / len(s_tema) * 100, 1)
        s_neg  = round(s_tema.count("NEG") / len(s_tema) * 100, 1)
        s_neu  = round(s_tema.count("NEU") / len(s_tema) * 100, 1)

        # seleciona trechos alinhados com o sentimento dominante do tema
        sent_dominante_tema = max(
            {"POS": s_pos, "NEG": s_neg, "NEU": s_neu},
            key=lambda k: {"POS": s_pos, "NEG": s_neg, "NEU": s_neu}[k]
        )

        # filtra chunks deste tópico que têm o sentimento dominante
        idx_sent_alinhado = [i for i in idx if sentimentos[i] == sent_dominante_tema]

        if len(idx_sent_alinhado) >= 2:
            # ordena por score NMF dentro dos chunks com sentimento correto
            scores_alinhados = W[idx_sent_alinhado, t_num]
            top3_idx = [idx_sent_alinhado[j]
                        for j in np.argsort(scores_alinhados)[::-1][:3]]
        else:
            # fallback: usa os de maior score NMF independente do sentimento
            top3_idx = list(idx[np.argsort(W[idx, t_num])[::-1][:3]])

        trechos = [chunks[i][:400] for i in top3_idx]

        if not trechos and t_num in _evidencias:
            trechos = [e["trecho"][:400] for e in _evidencias[t_num]["evidencias"][:3]]

        lift = round(pct / (100.0 / _nmf.n_components), 2)

        temas_out.append({
            "label":   label,
            "pct":     pct,
            "lift":    lift,
            "termos":  termos,
            "s_pos":   s_pos,
            "s_neu":   s_neu,
            "s_neg":   s_neg,
            "trechos": trechos,
        })

    temas_out = sorted(temas_out, key=lambda x: x["pct"], reverse=True)[:8]

    # 7. síntese por template
    tema_top  = temas_out[0]["label"] if temas_out else "n/d"
    tema_neg  = max(temas_out, key=lambda x: x["s_neg"])["label"] if temas_out else "n/d"
    sent_desc = {"POS": "positivo", "NEG": "negativo", "NEU": "neutro"}.get(dominante, "neutro")

    narrativa = (
        f"As entrevistas revelam um discurso predominantemente {sent_desc} "
        f"({pct_neu:.1f}% neutro, {pct_pos:.1f}% positivo, {pct_neg:.1f}% negativo). "
        f"O tema mais recorrente é '{tema_top}'. "
        f"O tema com maior carga negativa é '{tema_neg}'."
    )
    sintese = (
        f"O projeto é dominado pelo tema '{tema_top}', com sentimento {sent_desc} "
        f"e maior criticidade concentrada em '{tema_neg}'."
    )

    return {
        "projeto":         nome_limpo,
        "n_chunks":        n_chunks,
        "n_participantes": n_participantes,
        "duracao_min":     duracao_min,
        "sentimento": {
            "dominante": dominante,
            "pct_pos":   pct_pos,
            "pct_neu":   pct_neu,
            "pct_neg":   pct_neg,
        },
        "temas":     temas_out,
        "narrativa": narrativa,
        "sintese":   sintese,
        "pii_ok":    _pii_ok(texto_bruto),
    }
