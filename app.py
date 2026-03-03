# ============================================================
# Student Academic Portal — app.py  |  Netflix-style UI
# ============================================================

import streamlit as st
import pandas as pd

# ── Config ───────────────────────────────────────────────────
SHEET_URL             = "https://docs.google.com/spreadsheets/d/1MUynpz5LOdHVTsMSK5V4aP8bTCGLHRSy02peJn6XXbk/export?format=csv"
FIXED_BATCH           = "2025-27"
FIXED_COURSE          = "PGDM"
CORE_COLS             = ["Batch", "Course", "Section", "Subject", "Pending_Assignments", "Professor"]
ASSIGNMENT_FIXED_COLS = ["Assignment_No", "Description", "Deadline"]

st.set_page_config(
    page_title="NDIM Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ─────────────────────────────────────────── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"]   { visibility: hidden; display: none !important; }

html, body, [class*="css"] {
    font-family: 'Netflix Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background-color: #141414;
    color: #e5e5e5;
}

/* Force dark background everywhere */
.stApp, [data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] {
    background-color: #141414 !important;
}

/* ── Top navbar ───────────────────────────────────────────── */
.nf-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: .75rem 2rem;
    background: linear-gradient(180deg,#000 0%,transparent 100%);
    margin-bottom: .5rem;
}
.nf-nav .logo {
    font-size: 1.9rem;
    font-weight: 900;
    color: #e50914;
    letter-spacing: -1px;
    text-transform: uppercase;
}
.nf-nav .tagline {
    font-size: .78rem;
    color: #888;
    letter-spacing: .05em;
    text-transform: uppercase;
}

/* ── Hero billboard ───────────────────────────────────────── */
.nf-hero {
    position: relative;
    background: linear-gradient(105deg,#0a0a0a 30%,#1a0a0a 70%,#2d0000 100%);
    border-radius: 8px;
    padding: 3rem 3rem 2.5rem;
    margin-bottom: 2rem;
    overflow: hidden;
}
.nf-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 80% 50%, rgba(229,9,20,.18) 0%, transparent 65%);
    pointer-events: none;
}
.nf-hero .badge {
    display: inline-block;
    background: #e50914;
    color: #fff;
    font-size: .65rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
    padding: .2rem .6rem;
    border-radius: 3px;
    margin-bottom: .75rem;
}
.nf-hero h1 {
    font-size: 3rem;
    font-weight: 900;
    color: #fff;
    margin: 0 0 .5rem;
    line-height: 1.1;
    text-shadow: 2px 2px 8px rgba(0,0,0,.8);
}
.nf-hero p {
    font-size: 1rem;
    color: #b3b3b3;
    margin: 0 0 1.5rem;
    max-width: 480px;
}
.nf-hero-meta {
    display: flex;
    gap: 1.2rem;
    font-size: .82rem;
    color: #888;
    margin-top: .5rem;
}
.nf-hero-meta span { color: #e5e5e5; font-weight: 600; }

/* ── Row section label ────────────────────────────────────── */
.nf-row-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e5e5e5;
    margin: 1.5rem 0 .75rem;
    letter-spacing: .01em;
}
.nf-row-title em {
    font-size: .78rem;
    font-style: normal;
    color: #46d369;
    font-weight: 600;
    margin-left: .5rem;
}

/* ── Quick link cards ─────────────────────────────────────── */
.ql-row {
    display: flex;
    gap: .6rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.ql-card {
    flex: 1 1 160px;
    background: #1f1f1f;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 1.1rem 1rem;
    text-decoration: none !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: .45rem;
    transition: all .2s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.ql-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: #e50914;
    transform: scaleX(0);
    transition: transform .2s ease;
}
.ql-card:hover {
    background: #2a2a2a;
    border-color: #444;
    transform: scale(1.04);
    box-shadow: 0 8px 30px rgba(0,0,0,.6);
}
.ql-card:hover::after { transform: scaleX(1); }
.ql-card .ql-icon { font-size: 1.6rem; }
.ql-card .ql-label {
    font-size: .75rem;
    font-weight: 600;
    color: #b3b3b3;
    text-align: center;
    line-height: 1.4;
}

/* ── Section selector area ────────────────────────────────── */
.nf-select-wrap {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 1.4rem 1.6rem 1.2rem;
    margin-bottom: 1.5rem;
}

/* Override Streamlit select/dropdown colours */
[data-testid="stSelectbox"] label {
    color: #888 !important;
    font-size: .72rem !important;
    text-transform: uppercase;
    letter-spacing: .07em;
}
[data-testid="stSelectbox"] > div > div {
    background: #2a2a2a !important;
    border: 1px solid #3a3a3a !important;
    color: #e5e5e5 !important;
    border-radius: 5px !important;
}

/* Continue button */
[data-testid="stButton"] > button[kind="primary"] {
    background: #e50914 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 5px !important;
    font-weight: 700 !important;
    font-size: .95rem !important;
    padding: .55rem 2rem !important;
    letter-spacing: .03em;
    transition: background .15s ease, transform .12s ease !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #f40612 !important;
    transform: scale(1.03) !important;
}
[data-testid="stButton"] > button:not([kind="primary"]) {
    background: rgba(255,255,255,.1) !important;
    color: #fff !important;
    border: 1px solid #555 !important;
    border-radius: 5px !important;
    font-weight: 600 !important;
}
[data-testid="stButton"] > button:not([kind="primary"]):hover {
    background: rgba(255,255,255,.18) !important;
}

/* Disabled section 2 */
.disabled-box {
    background: #1a1a1a;
    border: 1px dashed #333;
    border-radius: 5px;
    padding: .62rem .9rem;
    color: #555;
    font-size: .82rem;
    text-align: center;
    margin-top: 1.55rem;
}

/* ── Subject cards (expanders styled) ────────────────────── */
[data-testid="stExpander"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    margin-bottom: .5rem !important;
}
[data-testid="stExpander"]:hover {
    border-color: #444 !important;
    background: #1f1f1f !important;
}
[data-testid="stExpander"] summary {
    color: #e5e5e5 !important;
    font-weight: 600 !important;
    font-size: .95rem !important;
}

/* ── Metric cards ─────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
    color: #888 !important;
    font-size: .78rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #fff !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
}

/* ── Filter pills ─────────────────────────────────────────── */
.filter-pill {
    display: inline-block;
    background: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: .2rem .65rem;
    font-size: .75rem;
    color: #b3b3b3;
    margin: .2rem .2rem 0 0;
}
.filter-pill strong { color: #e5e5e5; }

/* ── Assignment count badge ───────────────────────────────── */
.count-badge {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    background: #e50914;
    color: #fff;
    border-radius: 4px;
    padding: .3rem .9rem;
    font-size: .88rem;
    font-weight: 700;
    cursor: pointer;
    border: none;
    transition: all .15s ease;
    user-select: none;
}
.count-badge:hover {
    background: #f40612;
    transform: scale(1.04);
    box-shadow: 0 4px 16px rgba(229,9,20,.4);
}
.count-badge .arrow { font-size: .7rem; opacity: .8; }

/* ── Assignment detail card ───────────────────────────────── */
.assign-card {
    background: #242424;
    border: 1px solid #333;
    border-left: 4px solid #e50914;
    border-radius: 6px;
    padding: .85rem 1rem;
    margin-bottom: .5rem;
}
.assign-card .assign-no {
    font-size: .65rem;
    font-weight: 800;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #e50914;
    margin-bottom: .2rem;
}
.assign-card .assign-desc {
    font-size: .92rem;
    font-weight: 600;
    color: #e5e5e5;
    margin-bottom: .35rem;
}
.assign-meta {
    display: flex;
    flex-wrap: wrap;
    gap: .4rem;
    font-size: .76rem;
}
.assign-meta span {
    background: #333;
    color: #b3b3b3;
    border-radius: 4px;
    padding: .12rem .5rem;
}
.assign-meta .extra-key {
    background: #1a3a1a;
    color: #46d369;
}

/* ── Divider ──────────────────────────────────────────────── */
.nf-divider {
    border: none;
    border-top: 1px solid #2a2a2a;
    margin: 1.2rem 0;
}

/* ── No data ──────────────────────────────────────────────── */
.no-data {
    text-align: center;
    padding: 2.5rem 1rem;
    color: #555;
    font-size: .95rem;
}

/* ── Error ────────────────────────────────────────────────── */
.error-box {
    background: #2d0a0a;
    border-left: 4px solid #e50914;
    border-radius: 6px;
    padding: .65rem .9rem;
    color: #ffb3b3;
    font-size: .87rem;
    margin-bottom: .9rem;
}

/* Caption / info text */
.stCaption, [data-testid="stCaptionContainer"] p { color: #555 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────
def assignment_emoji(count: int) -> str:
    if count == 0: return "🙂"
    if count == 1: return "😩"
    if count == 2: return "😭"
    if count == 3: return "😤"
    return "🤬"

def divider():
    st.markdown("<hr class='nf-divider'>", unsafe_allow_html=True)


# ── Data loaders ──────────────────────────────────────────────
@st.cache_data(ttl=1)
def load_subjects() -> pd.DataFrame:
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        col_map = {}
        for a in df.columns:
            for e in CORE_COLS:
                if a.lower() == e.lower() and a != e:
                    col_map[a] = e
        df.rename(columns=col_map, inplace=True)
        df["Pending_Assignments"] = pd.to_numeric(
            df["Pending_Assignments"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as ex:
        st.markdown(f"<div class='error-box'>⚠️ Could not load subject data.<br><small>{ex}</small></div>",
                    unsafe_allow_html=True)
        return pd.DataFrame(columns=CORE_COLS)


@st.cache_data(ttl=1)
def load_assignments() -> pd.DataFrame:
    ASSIGNMENT_SHEET_GID = "423288098"   # ← replace with your Sheet 2 gid
    base = "https://docs.google.com/spreadsheets/d/1MUynpz5LOdHVTsMSK5V4aP8bTCGLHRSy02peJn6XXbk/export?format=csv"
    try:
        df = pd.read_csv(f"{base}&gid={ASSIGNMENT_SHEET_GID}")
        df.columns = df.columns.str.strip()
        known = ["Subject"] + ASSIGNMENT_FIXED_COLS
        col_map = {}
        for a in df.columns:
            for e in known:
                if a.lower() == e.lower() and a != e:
                    col_map[a] = e
        df.rename(columns=col_map, inplace=True)
        return df
    except Exception as ex:
        st.markdown(f"<div class='error-box'>⚠️ Could not load assignment details.<br><small>{ex}</small></div>",
                    unsafe_allow_html=True)
        return pd.DataFrame(columns=["Subject"] + ASSIGNMENT_FIXED_COLS)


def validate_columns(df, required, label):
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"**{label} — column mismatch.**\n\nMissing: `{'`, `'.join(missing)}`\n\nFound: `{'`, `'.join(df.columns.tolist())}`")
        return False
    return True


# ── Session state ─────────────────────────────────────────────
def init_state():
    for k, v in {"page": "landing", "section": None}.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Landing page ──────────────────────────────────────────────
def landing_page(df: pd.DataFrame):
    # Navbar
    st.markdown("""
    <div class="nf-nav">
        <div class="logo">NDIM</div>
        <div class="tagline">Academic Portal &nbsp;·&nbsp; PGDM 2025–27</div>
    </div>
    """, unsafe_allow_html=True)

    # Hero billboard
    total_subjects = len(df) if not df.empty else 0
    st.markdown(f"""
    <div class="nf-hero">
        <div class="badge">Now Streaming</div>
        <h1>Your Academic<br>Dashboard</h1>
        <p>Track every assignment, deadline, and subject — all in one place.</p>
        <div class="nf-hero-meta">
            <div>Batch &nbsp;<span>{FIXED_BATCH}</span></div>
            <div>Course &nbsp;<span>{FIXED_COURSE}</span></div>
            <div>Subjects &nbsp;<span>{total_subjects}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick links row
    st.markdown('<div class="nf-row-title">📌 Quick Access <em>Resources</em></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="ql-row">
        <a class="ql-card" href="https://drive.google.com/drive/folders/1zTkxiZukKfBA3vpe0wS-iYFnqNrXME05?usp=sharing" target="_blank">
            <span class="ql-icon">📂</span>
            <span class="ql-label">Previous Year<br>Question Papers</span>
        </a>
        <a class="ql-card" href="https://drive.google.com/file/d/1vs5ISXnOEeLodg1nrBQLLaSphDTuCLMv/view" target="_blank">
            <span class="ql-icon">📅</span>
            <span class="ql-label">Exam Date<br>Sheet</span>
        </a>
        <a class="ql-card" href="https://docs.google.com/spreadsheets/u/0/d/14eg5WGhT3t2EFMQLph1k2HQClay-Sw0Z/htmlview#gid=1318678321" target="_blank">
            <span class="ql-icon">🗓️</span>
            <span class="ql-label">Time<br>Table</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

    divider()

    # Section selector
    st.markdown('<div class="nf-row-title">🎬 Select Your Section</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.selectbox("Batch", [FIXED_BATCH], disabled=True, key="sel_batch")
    with col2:
        st.selectbox("Course", [FIXED_COURSE], disabled=True, key="sel_course")

    sections = (
        sorted(df[
            (df["Batch"] == FIXED_BATCH) & (df["Course"] == FIXED_COURSE)
        ]["Section"].dropna().unique().tolist())
        if not df.empty else []
    )
    with col3:
        section1 = st.selectbox("Section 1", ["— Select —"] + sections, key="sel_section1")
    with col4:
        st.markdown("<div class='disabled-box'>Section 2<br><small>Coming Soon</small></div>",
                    unsafe_allow_html=True)

    if section1 == "— Select —":
        st.caption("Select your section to continue.")
    else:
        if st.button("▶  Continue to Dashboard", type="primary"):
            st.session_state.section = section1
            st.session_state.page    = "subjects"
            st.rerun()


# ── Subjects page ─────────────────────────────────────────────
def subjects_page(df_subjects: pd.DataFrame, df_assignments: pd.DataFrame):
    section = st.session_state.section

    # Navbar with back
    col_logo, col_back = st.columns([8, 1])
    with col_logo:
        st.markdown("""
        <div style='padding:.6rem 0;'>
            <span style='font-size:1.6rem;font-weight:900;color:#e50914;letter-spacing:-1px;'>NDIM</span>
            <span style='font-size:.78rem;color:#555;margin-left:.75rem;text-transform:uppercase;letter-spacing:.05em;'>Academic Portal</span>
        </div>
        """, unsafe_allow_html=True)
    with col_back:
        if st.button("← Back"):
            st.session_state.page = "landing"
            st.rerun()

    divider()

    # Filter pills
    pills = "".join(
        f"<span class='filter-pill'>{label}: <strong>{val}</strong></span>"
        for label, val in [("Batch", FIXED_BATCH), ("Course", FIXED_COURSE), ("Section", section)]
    )
    pills += "<span class='filter-pill' style='opacity:.35;'>Section 2: Coming Soon</span>"
    st.markdown(pills, unsafe_allow_html=True)

    divider()

    # Filter
    filtered = df_subjects[
        (df_subjects["Batch"]   == FIXED_BATCH)  &
        (df_subjects["Course"]  == FIXED_COURSE) &
        (df_subjects["Section"] == section)
    ]

    total_pending  = int(filtered["Pending_Assignments"].sum())
    total_subjects = len(filtered)
    avg = round(total_pending / total_subjects, 1) if total_subjects else 0

    # Metrics
    st.markdown('<div class="nf-row-title">📊 Overview</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Pending",   total_pending)
    m2.metric("Total Subjects",  total_subjects)
    m3.metric("Avg per Subject", avg)

    divider()

    # Subjects
    st.markdown(f'<div class="nf-row-title">📚 Subjects <em>Section {section}</em></div>',
                unsafe_allow_html=True)

    if filtered.empty:
        st.markdown("<div class='no-data'>No subjects found for this section.</div>",
                    unsafe_allow_html=True)
        return

    known_assign_cols = {"Subject"} | set(ASSIGNMENT_FIXED_COLS)
    extra_cols = [c for c in df_assignments.columns if c not in known_assign_cols] \
                 if not df_assignments.empty else []

    for _, row in filtered.iterrows():
        subject = row["Subject"]
        pending = int(row["Pending_Assignments"])
        prof    = row["Professor"]
        emoji   = assignment_emoji(pending)

        with st.expander(f"{emoji}  {subject}  —  {prof}", expanded=False):
            st.markdown(f"""
            <div style='margin-bottom:.7rem;'>
                <span class='count-badge'>
                    {emoji} {pending} pending assignment{'s' if pending != 1 else ''}
                    <span class='arrow'>&nbsp;▼</span>
                </span>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"📂 View details ({pending} assignment{'s' if pending != 1 else ''})",
                             expanded=False):
                subj_df = df_assignments[
                    df_assignments["Subject"].str.strip() == subject.strip()
                ] if not df_assignments.empty else pd.DataFrame()

                if subj_df.empty:
                    st.caption("No assignment details found for this subject.")
                else:
                    for i, arow in subj_df.iterrows():
                        no_val       = arow.get("Assignment_No", i + 1)
                        desc_val     = arow.get("Description", "—")
                        deadline_val = arow.get("Deadline", "—")
                        extra_tags   = "".join(
                            f"<span class='extra-key'>{col}: {arow[col]}</span>"
                            for col in extra_cols
                            if pd.notna(arow.get(col)) and str(arow.get(col, "")).strip()
                        )
                        st.markdown(f"""
                        <div class='assign-card'>
                            <div class='assign-no'>Assignment {no_val}</div>
                            <div class='assign-desc'>{desc_val}</div>
                            <div class='assign-meta'>
                                <span>📅 {deadline_val}</span>
                                {extra_tags}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    divider()
    st.markdown('<div class="nf-row-title" style="opacity:.4;">🔭 Section 2 — Coming Soon</div>',
                unsafe_allow_html=True)
    st.markdown("<div class='no-data'>Section 2 will appear here once enabled.</div>",
                unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────
def main():
    init_state()
    df_subjects    = load_subjects()
    df_assignments = load_assignments()

    with st.expander("🛠 Debug — remove after fixing", expanded=False):
        st.write("Sheet 1 cols:", df_subjects.columns.tolist())
        st.write("Sheet 2 cols:", df_assignments.columns.tolist())
        if not df_subjects.empty:    st.dataframe(df_subjects.head(3))
        if not df_assignments.empty: st.dataframe(df_assignments.head(3))

    if not validate_columns(df_subjects, CORE_COLS, "Sheet 1"):
        st.stop()

    if st.session_state.page == "subjects":
        subjects_page(df_subjects, df_assignments)
    else:
        landing_page(df_subjects)


if __name__ == "__main__":
    main()
