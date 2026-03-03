# ============================================================
# Student Academic Portal — app.py
# ============================================================

import streamlit as st
import pandas as pd

# ── Config ───────────────────────────────────────────────────
SHEET_URL      = "https://docs.google.com/spreadsheets/d/1MUynpz5LOdHVTsMSK5V4aP8bTCGLHRSy02peJn6XXbk/export?format=csv"
FIXED_BATCH    = "2025-27"
FIXED_COURSE   = "PGDM"
CORE_COLS      = ["Batch", "Course", "Section", "Subject", "Pending_Assignments", "Professor"]
ASSIGNMENT_FIXED_COLS = ["Assignment_No", "Description", "Deadline"]

st.set_page_config(
    page_title="Student Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
<style>
/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {display: none !important;}

html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

/* Hero */
.hero {
    background: linear-gradient(120deg, #0f172a 0%, #1e293b 60%, #0f3460 100%);
    border-radius: 14px;
    padding: 1.8rem 2rem 1.6rem;
    margin-bottom: 1rem;
    color: #fff;
    text-align: center;
}
.hero h1 { font-size: 2rem; font-weight: 800; margin: 0 0 .3rem; letter-spacing: -.5px; }
.hero p  { font-size: .92rem; color: #94a3b8; margin: 0; }

/* Quick link cards */
.ql-grid {
    display: flex;
    flex-wrap: wrap;
    gap: .65rem;
    margin-bottom: 1rem;
}
.ql-card {
    flex: 1 1 140px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: .35rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: .9rem .75rem;
    text-decoration: none !important;
    transition: all .18s ease;
    cursor: pointer;
}
.ql-card:hover {
    background: #2563eb;
    border-color: #93c5fd;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(37,99,235,.25);
}
.ql-card .ql-icon { font-size: 1.4rem; line-height: 1; }
.ql-card .ql-label {
    font-size: .75rem;
    font-weight: 600;
    color: #cbd5e1;
    text-align: center;
    line-height: 1.3;
}

/* Section label */
.section-label {
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: .3rem;
}

/* Divider */
.custom-divider {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1rem 0;
}

/* Disabled section 2 box */
.disabled-box {
    background: #f1f5f9;
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
    padding: .65rem .9rem;
    color: #94a3b8;
    font-size: .83rem;
    text-align: center;
    margin-top: 1.55rem;
}

/* Filter pills */
.filter-pill {
    display: inline-block;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 20px;
    padding: .2rem .65rem;
    font-size: .78rem;
    color: #1e293b;
    margin: .2rem .2rem 0 0;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: .85rem 1rem !important;
}

/* Assignment count badge */
.count-badge {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    background: #0f172a;
    color: #f1f5f9;
    border-radius: 999px;
    padding: .3rem .85rem;
    font-size: .9rem;
    font-weight: 700;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all .18s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,.12);
    user-select: none;
}
.count-badge:hover {
    background: #2563eb;
    border-color: #93c5fd;
    box-shadow: 0 4px 16px rgba(37,99,235,.3);
    transform: translateY(-1px);
}
.count-badge .arrow { font-size: .72rem; opacity: .65; }

/* Assignment detail card */
.assign-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: .8rem 1rem;
    margin-bottom: .55rem;
}
.assign-card .assign-no {
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .07em;
    text-transform: uppercase;
    color: #2563eb;
    margin-bottom: .25rem;
}
.assign-card .assign-desc {
    font-size: .93rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: .35rem;
}
.assign-meta {
    display: flex;
    flex-wrap: wrap;
    gap: .4rem;
    font-size: .78rem;
}
.assign-meta span {
    background: #dbeafe;
    color: #1d4ed8;
    border-radius: 5px;
    padding: .12rem .5rem;
}
.assign-meta .extra-key {
    background: #dcfce7;
    color: #15803d;
}

/* No data */
.no-data {
    text-align: center;
    padding: 2.5rem 1rem;
    color: #94a3b8;
    font-size: .95rem;
}

/* Error box */
.error-box {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: .65rem .9rem;
    color: #991b1b;
    font-size: .87rem;
    margin-bottom: .9rem;
}
</style>
""", unsafe_allow_html=True)


# ── Emoji badge ───────────────────────────────────────────────
def assignment_emoji(count: int) -> str:
    if count == 0: return "🙂"
    if count == 1: return "😩"
    if count == 2: return "😭"
    if count == 3: return "😤"
    return "🤬"


# ── Data loaders ──────────────────────────────────────────────
@st.cache_data(ttl=1)
def load_subjects() -> pd.DataFrame:
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        col_map = {}
        for actual in df.columns:
            for expected in CORE_COLS:
                if actual.lower() == expected.lower() and actual != expected:
                    col_map[actual] = expected
        df.rename(columns=col_map, inplace=True)
        df["Pending_Assignments"] = pd.to_numeric(
            df["Pending_Assignments"], errors="coerce"
        ).fillna(0).astype(int)
        return df
    except Exception as e:
        st.markdown(
            f"<div class='error-box'>⚠️ Could not load subject data.<br><small>{e}</small></div>",
            unsafe_allow_html=True,
        )
        return pd.DataFrame(columns=CORE_COLS)


@st.cache_data(ttl=1)
def load_assignments() -> pd.DataFrame:
    ASSIGNMENT_SHEET_GID = "0"   # ← replace with your Sheet 2 gid
    base = "https://docs.google.com/spreadsheets/d/1MUynpz5LOdHVTsMSK5V4aP8bTCGLHRSy02peJn6XXbk/export?format=csv"
    assign_url = f"{base}&gid={ASSIGNMENT_SHEET_GID}"
    try:
        df = pd.read_csv(assign_url)
        df.columns = df.columns.str.strip()
        known = ["Subject"] + ASSIGNMENT_FIXED_COLS
        col_map = {}
        for actual in df.columns:
            for expected in known:
                if actual.lower() == expected.lower() and actual != expected:
                    col_map[actual] = expected
        df.rename(columns=col_map, inplace=True)
        return df
    except Exception as e:
        st.markdown(
            f"<div class='error-box'>⚠️ Could not load assignment details.<br><small>{e}</small></div>",
            unsafe_allow_html=True,
        )
        return pd.DataFrame(columns=["Subject"] + ASSIGNMENT_FIXED_COLS)


def validate_columns(df: pd.DataFrame, required: list, label: str) -> bool:
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(
            f"**{label} — column mismatch.**\n\n"
            f"Missing: `{'`, `'.join(missing)}`\n\n"
            f"Found: `{'`, `'.join(df.columns.tolist())}`"
        )
        return False
    return True


# ── Session state ─────────────────────────────────────────────
def init_state():
    for k, v in {"page": "landing", "section": None}.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Landing page ──────────────────────────────────────────────
def landing_page(df: pd.DataFrame):
    # Hero banner
    st.markdown("""
    <div class="hero">
        <h1>🎓 Student Academic Portal</h1>
        <p>PGDM 2025–27 &nbsp;·&nbsp; Track assignments, deadlines &amp; workload</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick link cards
    st.markdown("""
    <div class="ql-grid">
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

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Section selector
    st.markdown("<div class='section-label'>Select Your Section</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.selectbox("🗓 Batch", [FIXED_BATCH], disabled=True, key="sel_batch")
    with col2:
        st.selectbox("📘 Course", [FIXED_COURSE], disabled=True, key="sel_course")

    sections = (
        sorted(df[
            (df["Batch"] == FIXED_BATCH) & (df["Course"] == FIXED_COURSE)
        ]["Section"].dropna().unique().tolist())
        if not df.empty else []
    )
    with col3:
        section1 = st.selectbox("🔬 Section 1", ["— Select —"] + sections, key="sel_section1")
    with col4:
        st.markdown("<div class='disabled-box'>🔭 Section 2<br><small>Coming Soon</small></div>",
                    unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    if section1 == "— Select —":
        st.caption("ℹ️ Please select your Section to continue.")

    if st.button("Continue to Subjects →", disabled=(section1 == "— Select —"), type="primary"):
        st.session_state.section = section1
        st.session_state.page    = "subjects"
        st.rerun()


# ── Subjects page ─────────────────────────────────────────────
def subjects_page(df_subjects: pd.DataFrame, df_assignments: pd.DataFrame):
    section = st.session_state.section

    if st.button("← Back", key="back_btn"):
        st.session_state.page = "landing"
        st.rerun()

    st.markdown("## 📚 Subject Dashboard")

    # Filter pills
    pills = "".join(
        f"<span class='filter-pill'>{label}: <strong>{val}</strong></span>"
        for label, val in [("Batch", FIXED_BATCH), ("Course", FIXED_COURSE), ("Section", section)]
    )
    pills += "<span class='filter-pill' style='opacity:.4;'>Section 2: Coming Soon</span>"
    st.markdown(pills, unsafe_allow_html=True)
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Filter data
    filtered = df_subjects[
        (df_subjects["Batch"]   == FIXED_BATCH)  &
        (df_subjects["Course"]  == FIXED_COURSE) &
        (df_subjects["Section"] == section)
    ]

    total_pending  = int(filtered["Pending_Assignments"].sum())
    total_subjects = len(filtered)
    avg = round(total_pending / total_subjects, 1) if total_subjects else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("📌 Total Pending",   total_pending)
    m2.metric("📚 Total Subjects",  total_subjects)
    m3.metric("📈 Avg per Subject", avg)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    st.markdown(f"### Section — {section}")

    if filtered.empty:
        st.markdown(
            "<div class='no-data'>😕 No subjects found for the selected section.</div>",
            unsafe_allow_html=True,
        )
        return

    # Extra dynamic columns in assignment sheet
    known_assign_cols = {"Subject"} | set(ASSIGNMENT_FIXED_COLS)
    extra_cols = [c for c in df_assignments.columns if c not in known_assign_cols] \
                 if not df_assignments.empty else []

    for _, row in filtered.iterrows():
        subject = row["Subject"]
        pending = int(row["Pending_Assignments"])
        prof    = row["Professor"]
        emoji   = assignment_emoji(pending)

        with st.expander(f"{emoji}  {subject}  —  {prof}", expanded=False):
            st.markdown(
                f"""
                <div style='margin-bottom:.6rem;'>
                    <span class='count-badge'>
                        {emoji} {pending} pending assignment{'s' if pending != 1 else ''}
                        <span class='arrow'>▼ click to expand</span>
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(
                f"📂 View {pending} assignment detail{'s' if pending != 1 else ''}",
                expanded=False,
            ):
                subj_assignments = df_assignments[
                    df_assignments["Subject"].str.strip() == subject.strip()
                ] if not df_assignments.empty else pd.DataFrame()

                if subj_assignments.empty:
                    st.caption("No assignment details found for this subject.")
                else:
                    for i, arow in subj_assignments.iterrows():
                        no_val       = arow.get("Assignment_No", i + 1)
                        desc_val     = arow.get("Description", "—")
                        deadline_val = arow.get("Deadline", "—")

                        extra_tags = "".join(
                            f"<span class='extra-key'>{col}: {arow[col]}</span>"
                            for col in extra_cols
                            if pd.notna(arow.get(col)) and str(arow.get(col, "")).strip() != ""
                        )

                        st.markdown(
                            f"""
                            <div class='assign-card'>
                                <div class='assign-no'>Assignment {no_val}</div>
                                <div class='assign-desc'>{desc_val}</div>
                                <div class='assign-meta'>
                                    <span>📅 {deadline_val}</span>
                                    {extra_tags}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    # Section 2 placeholder
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    st.markdown("### 🔭 Section 2 — *Coming Soon*")
    st.markdown(
        "<div class='no-data' style='opacity:.55;'>Section 2 will appear here once enabled.</div>",
        unsafe_allow_html=True,
    )


# ── Router ────────────────────────────────────────────────────
def main():
    init_state()
    df_subjects    = load_subjects()
    df_assignments = load_assignments()

    with st.expander("🛠 Debug: Sheet columns (remove after fixing)", expanded=False):
        st.write("**Sheet 1 — Subjects:**", df_subjects.columns.tolist())
        st.write("**Sheet 2 — Assignments:**", df_assignments.columns.tolist())
        if not df_subjects.empty:    st.dataframe(df_subjects.head(3))
        if not df_assignments.empty: st.dataframe(df_assignments.head(3))

    if not validate_columns(df_subjects, CORE_COLS, "Sheet 1 (Subjects)"):
        st.stop()

    if st.session_state.page == "subjects":
        subjects_page(df_subjects, df_assignments)
    else:
        landing_page(df_subjects)


if __name__ == "__main__":
    main()
