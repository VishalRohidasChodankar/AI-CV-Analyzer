import streamlit as st
import pdfplumber
import pandas as pd
import re
from typing import Optional, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process as fuzz_process, fuzz

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI CV Screening Tool",
    page_icon="📄",
    layout="wide",
)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
STOPWORDS = {
    "a", "the", "is", "are", "we", "you", "for", "with", "and", "or",
    "to", "of", "in", "that", "have", "this", "be", "on", "it", "as",
    "at", "by", "from", "an", "will", "must", "should", "can", "our",
    "your", "not", "but", "if", "its", "was", "has", "had", "do",
    "did", "been", "they", "their", "them", "who", "which", "what",
    "how", "when", "where", "all", "any", "both", "each", "more",
    "also", "into", "than", "then", "these", "those", "just", "about",
}

EXPERIENCE_KEYWORDS = {"years", "experience", "worked", "managed", "led"}
EDUCATION_KEYWORDS  = {"bachelor", "master", "degree", "university", "college", "bsc", "msc", "mba"}

RANK_BG     = {1: "#FFFBE6", 2: "#EBF4FF", 3: "#EBF4FF"}
RANK_BORDER = {1: "2px solid #FFD700", 2: "2px solid #4A90D9", 3: "2px solid #4A90D9"}

INITIALS_COLORS = ["#E74C3C", "#2ECC71", "#3498DB", "#9B59B6",
                   "#F39C12", "#1ABC9C", "#E67E22", "#34495E"]

# ─────────────────────────────────────────────
# TEXT HELPERS
# ─────────────────────────────────────────────

def extract_candidate_name(filename: str) -> str:
    name = filename.replace(".pdf", "").replace(".PDF", "")
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r'\b(cv|resume|curriculum|vitae)\b', '', name, flags=re.IGNORECASE).strip()
    return name.title() if name else filename


def extract_text_from_pdf(uploaded_file) -> Optional[str]:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
        raw = " ".join(pages_text)
        cleaned = raw.lower()
        cleaned = re.sub(r'[^a-z0-9\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    except Exception:
        return None


def extract_jd_keywords(jd_text: str) -> List[str]:
    text = jd_text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    words = text.split()
    seen, unique = set(), []
    for w in words:
        if len(w) >= 3 and w not in STOPWORDS and w not in seen:
            seen.add(w)
            unique.append(w)
    return unique


# ─────────────────────────────────────────────
# ALGORITHM 1 — TF-IDF + COSINE SIMILARITY
# Processes all CVs at once (vectorized, fast at scale)
# ─────────────────────────────────────────────

def compute_tfidf_scores(jd_text: str, cv_texts: List[str]) -> List[float]:
    """
    Returns cosine similarity (0–100) between the JD and each CV.
    Uses bigrams (1,2) so phrases like "machine learning" are captured.
    """
    corpus = [jd_text] + cv_texts
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),   # single words + two-word phrases
        min_df=1,
        sublinear_tf=True,    # log-scale term frequency to reduce dominance of repeated words
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    jd_vector  = tfidf_matrix[0]
    cv_vectors = tfidf_matrix[1:]
    scores = cosine_similarity(jd_vector, cv_vectors)[0]
    return [round(float(s) * 100, 1) for s in scores]


# ─────────────────────────────────────────────
# ALGORITHM 2 — FUZZY MATCHING
# Catches word variations: "managed" ≈ "managing", "develop" ≈ "developer"
# ─────────────────────────────────────────────

def fuzzy_match_keywords(
    jd_keywords: List[str],
    cv_text: str,
    threshold: int = 82,
) -> Tuple[List[str], List[Tuple[str, str]], List[str]]:
    """
    For each JD keyword:
      - exact match  → green bucket
      - fuzzy match  → orange bucket  (jd_kw, matched_cv_word)
      - no match     → red bucket
    Returns (exact_matches, fuzzy_matches, missing)
    """
    cv_words = list(set(cv_text.split()))
    exact, fuzzy, missing = [], [], []

    for kw in jd_keywords:
        if kw in cv_text:
            exact.append(kw)
            continue
        result = fuzz_process.extractOne(
            kw, cv_words,
            scorer=fuzz.ratio,
            score_cutoff=threshold,
        )
        if result:
            fuzzy.append((kw, result[0]))   # (jd keyword, similar word found in CV)
        else:
            missing.append(kw)

    return exact, fuzzy, missing


# ─────────────────────────────────────────────
# COMBINED SCORER
# ─────────────────────────────────────────────

def score_cv(
    cv_text: str,
    jd_keywords: List[str],
    tfidf_score: float,
    skills_w: float,
    exp_w: float,
    edu_w: float,
    fuzzy_threshold: int,
) -> dict:
    """
    Skill score  = 70% TF-IDF cosine similarity  +  30% fuzzy keyword coverage
    Exp score    = presence of experience-related words
    Edu score    = presence of education-related words
    Final score  = weighted sum of the three components
    """
    cv_words = set(cv_text.split())

    # Fuzzy keyword breakdown
    exact, fuzzy, missing = fuzzy_match_keywords(jd_keywords, cv_text, fuzzy_threshold)

    # Fuzzy coverage ratio (exact + fuzzy hits / total keywords)
    total_hits    = len(exact) + len(fuzzy)
    fuzzy_coverage = (total_hits / len(jd_keywords) * 100) if jd_keywords else 0

    # Combined skill score
    skill_score = round((tfidf_score * 0.70) + (fuzzy_coverage * 0.30), 1)

    # Experience score
    exp_score = 80 if any(kw in cv_words for kw in EXPERIENCE_KEYWORDS) else 30

    # Education score
    edu_score = 80 if any(kw in cv_words for kw in EDUCATION_KEYWORDS) else 20

    # Weighted final
    final = (skill_score * skills_w) + (exp_score * exp_w) + (edu_score * edu_w)

    return {
        "skill_score":    skill_score,
        "tfidf_score":    tfidf_score,
        "fuzzy_coverage": round(fuzzy_coverage, 1),
        "exp_score":      exp_score,
        "edu_score":      edu_score,
        "final_score":    round(final, 1),
        "exact":          exact,
        "fuzzy":          fuzzy,
        "missing":        missing,
    }


# ─────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────

def get_initials(name: str) -> str:
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if len(name) >= 2 else name.upper()


def render_badge(word: str, color: str, title: str = "") -> str:
    # Use &quot; to escape inner quotes so the title attribute stays valid HTML
    safe_title = title.replace('"', "&quot;").replace("'", "&#39;")
    tip = f'title="{safe_title}"' if safe_title else ""
    return (
        f'<span {tip} style="background:{color};color:white;padding:3px 9px;'
        f'border-radius:12px;font-size:12px;margin:2px;display:inline-block;cursor:default;">'
        f'{word}</span>'
    )


def render_candidate_card(rank: int, name: str, scores: dict, index: int):
    border   = RANK_BORDER.get(rank, "1px solid #DDDDDD")
    bg       = RANK_BG.get(rank, "#FAFAFA")
    av_color = INITIALS_COLORS[index % len(INITIALS_COLORS)]
    initials = get_initials(name)
    score    = scores["final_score"]

    top_badge = ""
    if rank == 1:
        top_badge = (
            '<span style="background:#FFD700;color:#333;padding:3px 10px;'
            'border-radius:12px;font-size:12px;font-weight:bold;margin-left:10px;">'
            '🏆 Top Candidate</span>'
        )

    score_color = "#27AE60" if score >= 65 else ("#E67E22" if score >= 40 else "#E74C3C")

    # Badge HTML — three tiers
    exact_html = " ".join(
        render_badge(kw, "#27AE60", "Exact match") for kw in scores["exact"][:20]
    )
    fuzzy_html = " ".join(
        render_badge(f'{kw} ({cv_w})', "#E67E22", f'JD keyword: {kw} | matched: {cv_w}')
        for kw, cv_w in scores["fuzzy"][:15]
    )
    missing_html = " ".join(
        render_badge(kw, "#E74C3C", "Not found") for kw in scores["missing"][:20]
    )

    # Single-line HTML — Streamlit's markdown parser breaks nested divs on newlines
    card_html = (
        f'<div style="border:{border};background:{bg};border-radius:12px;padding:20px;margin-bottom:8px;">'
        f'<div style="display:flex;align-items:center;">'
        f'<div style="background:{av_color};color:white;border-radius:50%;width:48px;height:48px;'
        f'display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:bold;flex-shrink:0;">'
        f'{initials}</div>'
        f'<div style="margin-left:14px;flex:1;">'
        f'<span style="font-size:18px;font-weight:bold;">#{rank} {name}</span>{top_badge}</div>'
        f'<div style="font-size:30px;font-weight:bold;color:{score_color};">{score}%</div>'
        f'</div></div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    st.progress(int(min(score, 100)))

    # Sub-score metrics — 5 columns
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Final Score",       f"{scores['final_score']}%")
    c2.metric("Skill Match",       f"{scores['skill_score']}%")
    c3.metric("TF-IDF Similarity", f"{scores['tfidf_score']}%")
    c4.metric("Experience",        f"{scores['exp_score']}%")
    c5.metric("Education",         f"{scores['edu_score']}%")

    # Keyword badges
    if scores["exact"]:
        st.markdown("**✅ Exact Matches:**")
        st.markdown(exact_html, unsafe_allow_html=True)

    if scores["fuzzy"]:
        st.markdown("**🟠 Fuzzy Matches** *(similar words found)*:")
        st.markdown(fuzzy_html, unsafe_allow_html=True)

    if scores["missing"]:
        st.markdown("**❌ Missing Keywords:**")
        st.markdown(missing_html, unsafe_allow_html=True)

    st.markdown("---")


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("📋 CV Screener")
    st.caption("TF-IDF + Cosine Similarity + Fuzzy Matching")
    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload CV Files (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more candidate CVs in PDF format.",
    )

    jd_text = st.text_area(
        "Paste Job Description",
        height=200,
        placeholder="Paste the full job description here...",
    )

    st.markdown("---")
    st.subheader("⚖️ Scoring Weights")
    st.caption("Must total 100%")

    skills_pct = st.slider("Skills Weight (%)",     0, 100, 50, step=5)
    exp_pct    = st.slider("Experience Weight (%)", 0, 100, 30, step=5)
    edu_pct    = st.slider("Education Weight (%)",  0, 100, 20, step=5)

    total = skills_pct + exp_pct + edu_pct
    if total != 100:
        st.error(f"Weights sum to {total}% — must equal 100%")
    else:
        st.success("✅ Weights total: 100%")

    st.markdown("---")
    st.subheader("🔤 Fuzzy Match Settings")
    fuzzy_threshold = st.slider(
        "Fuzzy Similarity Threshold (%)",
        min_value=60, max_value=95, value=82, step=1,
        help="How similar a word must be to count as a match. Higher = stricter.",
    )
    st.caption(f"e.g. at {fuzzy_threshold}%: 'managed' ≈ 'managing' ✅")

    st.markdown("---")
    screen_btn = st.button("🔍 Screen Candidates", use_container_width=True, type="primary")


# ─────────────────────────────────────────────
# MAIN PANEL
# ─────────────────────────────────────────────
st.title("🤖 AI CV Screening Tool")
st.markdown(
    "Powered by **TF-IDF + Cosine Similarity** for smart scoring "
    "and **Fuzzy Matching** to catch word variations."
)

if screen_btn:

    # ── Validation ──────────────────────────────
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one CV.")
        st.stop()
    if not jd_text.strip():
        st.warning("⚠️ Please paste a job description.")
        st.stop()
    if total != 100:
        st.error("❌ Scoring weights must add up to 100%. Adjust the sliders.")
        st.stop()

    skills_w = skills_pct / 100
    exp_w    = exp_pct    / 100
    edu_w    = edu_pct    / 100

    # ── Extract JD keywords ──────────────────────
    jd_keywords = extract_jd_keywords(jd_text)
    if not jd_keywords:
        st.error("❌ Could not extract keywords from the job description.")
        st.stop()

    # ── Read all PDFs ────────────────────────────
    cv_texts, cv_names, skipped = [], [], []
    with st.spinner("Reading CVs..."):
        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            if text is None:
                skipped.append(file.name)
            else:
                cv_texts.append(text)
                cv_names.append(extract_candidate_name(file.name))

    for fname in skipped:
        st.warning(f"⚠️ Could not read **{fname}** — skipped.")

    if not cv_texts:
        st.error("❌ No CVs could be processed.")
        st.stop()

    # ── TF-IDF (all CVs at once) ─────────────────
    with st.spinner("Running TF-IDF + Cosine Similarity across all CVs..."):
        jd_clean   = jd_text.lower()
        jd_clean   = re.sub(r'[^a-z0-9\s]', ' ', jd_clean)
        tfidf_scores = compute_tfidf_scores(jd_clean, cv_texts)

    # ── Fuzzy + Final Scoring ────────────────────
    results = []
    with st.spinner("Running Fuzzy Matching and calculating final scores..."):
        for i, (name, cv_text, tfidf_s) in enumerate(zip(cv_names, cv_texts, tfidf_scores)):
            scores = score_cv(cv_text, jd_keywords, tfidf_s, skills_w, exp_w, edu_w, fuzzy_threshold)
            results.append({"name": name, **scores})

    # ── Sort ─────────────────────────────────────
    df = pd.DataFrame(results).sort_values("final_score", ascending=False).reset_index(drop=True)

    # ── Summary Metrics ──────────────────────────
    st.markdown("### 📊 Summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📁 CVs Scanned",          len(df))
    m2.metric("🔑 JD Keywords",           len(jd_keywords))
    m3.metric("🏆 Top Score",             f"{df.iloc[0]['final_score']}%")
    avg_fuzzy = round(df["fuzzy_coverage"].mean(), 1)
    m4.metric("🟠 Avg Fuzzy Coverage",    f"{avg_fuzzy}%")

    st.markdown("---")

    # ── Algorithm Info ───────────────────────────
    with st.expander("ℹ️ How scoring works"):
        st.markdown("""
**Skill Score** = 70% × TF-IDF Cosine Similarity + 30% × Fuzzy Keyword Coverage

| Component | What it does |
|---|---|
| **TF-IDF** | Weights rare/important JD words higher; uses bigrams (e.g. "machine learning") |
| **Cosine Similarity** | Measures overall text direction match between JD and CV (0–100%) |
| **Fuzzy Matching** | Catches word variants: *managed → managing*, *develop → developer* |

**Final Score** = (Skill × skills_weight) + (Experience × exp_weight) + (Education × edu_weight)
        """)

    # ── JD Keywords ─────────────────────────────
    with st.expander("🔍 View Extracted JD Keywords"):
        kw_html = " ".join(render_badge(kw, "#2C3E50") for kw in jd_keywords)
        st.markdown(kw_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── Legend ───────────────────────────────────
    st.markdown(
        "**Badge Legend:** "
        '<span style="background:#27AE60;color:white;padding:2px 8px;border-radius:10px;font-size:12px;">Exact match</span> &nbsp;'
        '<span style="background:#E67E22;color:white;padding:2px 8px;border-radius:10px;font-size:12px;">Fuzzy match</span> &nbsp;'
        '<span style="background:#E74C3C;color:white;padding:2px 8px;border-radius:10px;font-size:12px;">Missing</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Candidate Cards ──────────────────────────
    st.markdown("### 🏅 Ranked Candidates")
    for i, row in df.iterrows():
        render_candidate_card(rank=i + 1, name=row["name"], scores=row.to_dict(), index=i)

    # ── Export CSV ───────────────────────────────
    st.markdown("### 📥 Export Results")
    export_df = df[["name", "final_score", "skill_score", "tfidf_score",
                    "fuzzy_coverage", "exp_score", "edu_score"]].copy()
    export_df.columns = [
        "Candidate", "Final Score (%)", "Skill Score (%)",
        "TF-IDF Score (%)", "Fuzzy Coverage (%)", "Experience Score (%)", "Education Score (%)",
    ]
    export_df.insert(0, "Rank", range(1, len(export_df) + 1))
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Rankings as CSV",
        data=csv,
        file_name="cv_screening_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

else:
    # ── Landing State ─────────────────────────────
    st.info("👈 Upload CVs and paste a job description in the sidebar, then click **Screen Candidates**.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### 📤 Step 1")
        st.markdown("Upload PDF CVs in the sidebar.")
    with col2:
        st.markdown("#### 📝 Step 2")
        st.markdown("Paste the full job description.")
    with col3:
        st.markdown("#### ⚖️ Step 3")
        st.markdown("Set scoring weights and fuzzy threshold.")
    with col4:
        st.markdown("#### 🔍 Step 4")
        st.markdown("Click **Screen Candidates** to rank.")
