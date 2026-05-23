"""
💬 SmartDocs Assistant — RAG App
AI-powered document chat assistant

Zero C-compilation dependencies.
Uses: streamlit, pypdf, google-generativeai, numpy only.
"""

import os, json, math, tempfile
from datetime import datetime
from collections import Counter

import streamlit as st

st.set_page_config(
    page_title="💬 SmartDocs Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #faf5ff 0%, #f0f9ff 50%, #fdf4ff 100%);
}
[data-testid="stSidebar"] {
    background: #1e1b4b !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #e0e7ff !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(165,180,252,0.3) !important;
    color: #e0e7ff !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.8rem !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #6d28d9 !important;
    border-color: #7c3aed !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(165,180,252,0.35) !important;
    color: #e0e7ff !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(165,180,252,0.2) !important; }

.sd-card {
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 14px;
    padding: 14px 8px;
    text-align: center;
    margin-bottom: 4px;
    box-shadow: 0 2px 12px rgba(109,40,217,0.08);
}
.sd-num {
    font-size: 26px; font-weight: 700; color: #6d28d9;
    line-height: 1; font-family: 'Fira Code', monospace;
}
.sd-lbl {
    font-size: 10px; color: #7c3aed; margin-top: 3px;
    font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase;
}

.sd-bubble-out {
    background: linear-gradient(135deg, #6d28d9, #7c3aed);
    color: #fff; padding: 12px 18px;
    border-radius: 20px 20px 4px 20px;
    margin: 8px 0 8px auto; max-width: 72%; width: fit-content;
    font-size: 14px; line-height: 1.65;
    box-shadow: 0 4px 15px rgba(109,40,217,0.25);
}
.sd-bubble-in {
    background: rgba(255,255,255,0.85);
    color: #1e1b4b; padding: 12px 18px;
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 20px 20px 20px 4px;
    margin: 8px auto 8px 0; max-width: 82%;
    font-size: 14px; line-height: 1.65;
    box-shadow: 0 2px 12px rgba(109,40,217,0.07);
}
.sd-bubble-in-ar { direction: rtl; text-align: right; }
.sd-ts {
    font-size: 10px; color: rgba(255,255,255,0.55);
    margin-top: 5px; font-family: 'Fira Code', monospace;
}
.sd-bubble-in .sd-ts { color: #a78bfa; }

.sd-source {
    display: inline-block;
    background: linear-gradient(135deg, #ede9fe, #faf5ff);
    color: #6d28d9; border: 1px solid #c4b5fd;
    border-radius: 20px; padding: 3px 12px;
    font-size: 11px; margin: 3px 4px 3px 0;
    font-family: 'Fira Code', monospace; font-weight: 500;
}
.sd-top-row {
    display: flex; justify-content: space-between;
    font-size: 12px; padding: 5px 0;
    border-bottom: 1px solid rgba(165,180,252,0.2);
    color: #a5b4fc;
}

.stButton > button {
    font-family: 'Sora', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    border-radius: 12px !important; transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6d28d9, #7c3aed) !important;
    color: #fff !important; border: none !important;
    box-shadow: 0 4px 14px rgba(109,40,217,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(109,40,217,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.6) !important;
    border: 1px solid #c4b5fd !important; color: #6d28d9 !important;
}
.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.7) !important;
    border: 1.5px solid #c4b5fd !important;
    border-radius: 12px !important;
    font-family: 'Sora', sans-serif !important;
    color: #1e1b4b !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.5) !important;
    border: 2px dashed #c4b5fd !important;
    border-radius: 14px !important;
}
.stProgress > div > div {
    background: linear-gradient(90deg, #6d28d9, #a78bfa) !important;
}
hr { border-color: rgba(139,92,246,0.2) !important; }
.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "chunks":         [],      # list of {text, page, source}
        "embeddings":     [],      # parallel list of embedding vectors
        "messages":       [],
        "docs_meta":      [],
        "question_count": 0,
        "page_hits":      Counter(),
        "lang":           "en",
        "api_key":        "",
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

# ── Translations ──────────────────────────────────────────────────────────────
LANG = {
    "en": {
        "title":      "💬 SmartDocs Assistant",
        "subtitle":   "RAG-powered chat with your documents — upload any PDF and start asking",
        "upload_lbl": "📄 Upload PDF(s)",
        "processing": "Processing",
        "ask_ph":     "Ask anything about your document…",
        "send":       "Send ↗",
        "no_key":     "⚠️ Enter your Gemini API key in the sidebar first.",
        "no_doc":     "⚠️ Upload at least one PDF first.",
        "thinking":   "🤔 Thinking…",
        "src_hdr":    "📚 Sources",
        "export":     "⬇️ Export conversation (JSON)",
        "stats_q":    "Questions",
        "stats_c":    "Chunks",
        "stats_d":    "Docs",
        "top_pages":  "🔥 Top referenced pages",
        "hint":       "Upload any PDF and start asking questions!",
        "system": (
            "You are a smart document assistant. "
            "Answer using ONLY the provided document context. "
            "Cite page numbers when possible. "
            "If the answer is not in the context say so clearly. "
            "Use markdown for code blocks."
        ),
    },
    "ar": {
        "title":      "💬 مساعد المستندات الذكي",
        "subtitle":   "محادثة ذكية مع مستنداتك — ارفع أي PDF وابدأ الأسئلة",
        "upload_lbl": "📄 ارفع ملفات PDF",
        "processing": "جارٍ المعالجة",
        "ask_ph":     "اسأل أي شيء عن مستنداتك…",
        "send":       "إرسال ↗",
        "no_key":     "⚠️ أدخل مفتاح Gemini API في الشريط الجانبي أولاً.",
        "no_doc":     "⚠️ ارفع ملف PDF واحداً على الأقل أولاً.",
        "thinking":   "🤔 جارٍ التفكير…",
        "src_hdr":    "📚 المصادر",
        "export":     "⬇️ تصدير المحادثة (JSON)",
        "stats_q":    "أسئلة",
        "stats_c":    "مقاطع",
        "stats_d":    "ملفات",
        "top_pages":  "🔥 أكثر الصفحات استخداماً",
        "hint":       "ارفع أي ملف PDF وابدأ بطرح الأسئلة!",
        "system": (
            "أنت مساعد مستندات ذكي. "
            "أجب باستخدام سياق المستند المقدم فقط. "
            "اذكر أرقام الصفحات عند الإمكان. "
            "اكتب إجاباتك باللغة العربية."
        ),
    },
}

def t(k): return LANG[st.session_state.lang].get(k, k)

# ── Pure-Python RAG helpers ───────────────────────────────────────────────────

def pdf_to_chunks(file_bytes: bytes, filename: str) -> list[dict]:
    """Extract text from PDF and split into overlapping chunks."""
    import pypdf, io
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    chunks = []
    chunk_size, overlap = 600, 80

    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue
        # slide a window over the page text
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if len(chunk) > 40:
                chunks.append({
                    "text":   chunk,
                    "page":   page_num,
                    "source": filename,
                })
            start += chunk_size - overlap

    return chunks


def get_embedding(text: str, api_key: str) -> list[float]:
    """Call Gemini embedding API."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def retrieve(query: str, k: int = 4) -> list[tuple[dict, float]]:
    """Embed query, find top-k chunks by cosine similarity."""
    if not st.session_state.chunks:
        return []
    q_emb = get_embedding(query, st.session_state.api_key)
    scored = [
        (chunk, cosine_similarity(q_emb, emb))
        for chunk, emb in zip(st.session_state.chunks, st.session_state.embeddings)
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


def ask_gemini(prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=st.session_state.api_key)
    model  = genai.GenerativeModel("gemini-2.0-flash")
    result = model.generate_content(prompt)
    return result.text


def build_prompt(question: str, results: list[tuple[dict, float]]) -> str:
    context = "\n\n---\n\n".join(
        f"[Source: {r['source']}, page {r['page']}, score {score:.2f}]\n{r['text']}"
        for r, score in results
    )
    return (
        f"{t('system')}\n\n"
        f"DOCUMENT CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\nANSWER:"
    )


def export_json() -> str:
    data = {
        "export_time":  datetime.now().isoformat(),
        "language":     st.session_state.lang,
        "documents":    st.session_state.docs_meta,
        "stats": {
            "questions":    st.session_state.question_count,
            "total_chunks": len(st.session_state.chunks),
            "top_pages":    [
                {"page": k, "hits": v}
                for k, v in st.session_state.page_hits.most_common(10)
            ],
        },
        "conversation": [
            {k: v for k, v in m.items() if k != "sources_raw"}
            for m in st.session_state.messages
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💬 SmartDocs Assistant")

    # Language
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧 English",
                     type="primary" if st.session_state.lang == "en" else "secondary",
                     use_container_width=True):
            st.session_state.lang = "en"; st.rerun()
    with col2:
        if st.button("🇪🇬 العربية",
                     type="primary" if st.session_state.lang == "ar" else "secondary",
                     use_container_width=True):
            st.session_state.lang = "ar"; st.rerun()

    st.divider()

    # API key
    st.markdown("**🔑 Gemini API Key**")
    key_input = st.text_input("key", value=st.session_state.api_key,
                               type="password", placeholder="AIza…",
                               label_visibility="collapsed")
    if key_input != st.session_state.api_key:
        st.session_state.api_key = key_input
    if st.session_state.api_key:
        st.success("✅ Key ready")
    else:
        st.caption("Get key → [aistudio.google.com](https://aistudio.google.com/apikey)")

    st.divider()

    # Upload
    st.markdown(f"**{t('upload_lbl')}**")
    uploaded = st.file_uploader("pdfs", type=["pdf"],
                                 accept_multiple_files=True,
                                 label_visibility="collapsed")

    if uploaded and st.session_state.api_key:
        new_names = sorted(f.name for f in uploaded)
        old_names = sorted(d["name"] for d in st.session_state.docs_meta)
        if new_names != old_names:
            all_chunks, all_embeddings = [], []
            progress = st.progress(0, text=f"{t('processing')}…")
            total = sum(1 for _ in uploaded)  # count
            for i, uf in enumerate(uploaded):
                progress.progress((i) / total, text=f"📄 {uf.name}…")
                file_bytes = uf.read()
                chunks = pdf_to_chunks(file_bytes, uf.name)
                # embed each chunk
                for j, chunk in enumerate(chunks):
                    emb = get_embedding(chunk["text"], st.session_state.api_key)
                    all_chunks.append(chunk)
                    all_embeddings.append(emb)
                progress.progress((i + 1) / total, text=f"✅ {uf.name}")

            st.session_state.chunks     = all_chunks
            st.session_state.embeddings = all_embeddings
            st.session_state.docs_meta  = [{"name": f.name} for f in uploaded]
            progress.empty()
            st.success(f"✅ {len(all_chunks)} chunks indexed!")

    elif uploaded and not st.session_state.api_key:
        st.warning("Enter API key first, then re-upload.")

    # Doc list
    if st.session_state.docs_meta:
        st.markdown("**📂 Indexed docs**")
        for d in st.session_state.docs_meta:
            st.markdown(
                f'<div style="background:#eff6ff;border-radius:6px;padding:5px 9px;'
                f'font-size:12px;margin-bottom:4px;">📄 {d["name"]}</div>',
                unsafe_allow_html=True)

    st.divider()

    # Stats
    st.markdown("**📊 Stats**")
    c1, c2, c3 = st.columns(3)
    for col, num, lbl in [
        (c1, st.session_state.question_count,     t("stats_q")),
        (c2, len(st.session_state.chunks),         t("stats_c")),
        (c3, len(st.session_state.docs_meta),      t("stats_d")),
    ]:
        with col:
            st.markdown(
                f'<div class="sd-card"><div class="sd-num">{num}</div>'
                f'<div class="sd-lbl">{lbl}</div></div>',
                unsafe_allow_html=True)

    if st.session_state.page_hits:
        st.markdown(f"**{t('top_pages')}**")
        for page_key, hits in st.session_state.page_hits.most_common(5):
            st.markdown(
                f'<div class="sd-top-row"><span>📄 {page_key}</span>'
                f'<span style="color:#1a56db;font-weight:600">{hits}×</span></div>',
                unsafe_allow_html=True)

    st.divider()

    if st.session_state.messages:
        st.download_button(
            label=t("export"),
            data=export_json(),
            file_name=f"smartdocs-chat-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )
        if st.button("🗑️ Clear conversation", use_container_width=True):
            st.session_state.messages       = []
            st.session_state.question_count = 0
            st.session_state.page_hits      = Counter()
            st.rerun()


# ── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown(f"## {t('title')}")
st.caption(t("subtitle"))

# Quick buttons
QUICK = {
    "en": ["What is this document about?", "Summarise the key points",
           "What are the main topics?", "List important terms",
           "What conclusions are made?", "Give me a quick overview"],
    "ar": ["عمّ يتحدث هذا المستند؟", "لخّص النقاط الرئيسية",
           "ما المواضيع الرئيسية؟", "اذكر المصطلحات المهمة",
           "ما الاستنتاجات الواردة؟"],
}
triggered = None
qs = QUICK[st.session_state.lang]
cols = st.columns(len(qs))
for col, q in zip(cols, qs):
    with col:
        if st.button(q, use_container_width=True, key=f"q_{q[:18]}"):
            triggered = q

st.divider()

# Chat history
if not st.session_state.messages:
    st.info(f"💡 {t('hint')}")
else:
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("ts", "")
        sources = msg.get("sources", [])

        if role == "user":
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end">'
                f'<div class="sd-bubble-out">{content}'
                f'<div class="sd-ts">{ts}</div></div></div>',
                unsafe_allow_html=True)
        else:
            ar = "sd-bubble-in-ar" if st.session_state.lang == "ar" else ""
            safe = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
            chips = "".join(
                f'<span class="sd-source">📄 {r["source"]} · p.{r["page"]} '
                f'<span style="opacity:.6">({score:.2f})</span></span>'
                for r, score in sources
            )
            src_block = (
                f'<div style="margin-top:8px;font-size:11px;font-weight:600;'
                f'color:#6c757d;text-transform:uppercase;letter-spacing:.05em">'
                f'{t("src_hdr")}</div>{chips}'
            ) if sources else ""
            st.markdown(
                f'<div class="sd-bubble-in {ar}">{safe}'
                f'<div class="sd-ts">{ts}</div>'
                f'{src_block}</div>',
                unsafe_allow_html=True)

# Input
st.markdown("---")
ic, bc = st.columns([9, 1])
with ic:
    user_input = st.text_area("q", placeholder=t("ask_ph"), height=80,
                               label_visibility="collapsed", key="input_area")
with bc:
    st.write("")
    send = st.button(t("send"), type="primary", use_container_width=True)

# Process
question = triggered or (user_input.strip() if send else None)

if question:
    if not st.session_state.api_key:
        st.error(t("no_key")); st.stop()
    if not st.session_state.chunks:
        st.error(t("no_doc")); st.stop()

    ts_now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append(
        {"role": "user", "content": question, "ts": ts_now, "sources": []})
    st.session_state.question_count += 1

    with st.spinner(t("thinking")):
        results = retrieve(question, k=4)

        for chunk, _ in results:
            key = f"{chunk['source']}:p{chunk['page']}"
            st.session_state.page_hits[key] += 1

        prompt = build_prompt(question, results)
        try:
            answer = ask_gemini(prompt)
        except Exception as e:
            answer = f"❌ Gemini error: {e}"

    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer,
        "ts":      datetime.now().strftime("%H:%M"),
        "sources": results,
    })
    st.rerun()
