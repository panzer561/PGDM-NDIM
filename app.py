# ============================================================
# Student Academic Portal — app.py
# ============================================================

import streamlit as st
import pandas as pd

# ── Config ───────────────────────────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MUynpz5LOdHVTsMSK5V4aP8bTCGLHRSy02peJn6XXbk/export?format=csv"

# Core columns the app always expects
CORE_COLS = ["Batch", "Course", "Section", "Subject", "Pending_Assignments", "Professor"]

# Assignment-level columns (each assignment is a row linked by Subject)
ASSIGNMENT_FIXED_COLS = ["Assignment_No", "Description", "Deadline"]
# Any column beyond the above is treated as dynamic/extra

st.set_page_config(
    page_title="Student Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
<style>
/* Hide Streamlit top right menu */
#MainMenu {visibility: hidden;}
/* Hide footer */
footer {visibility: hidden;}
/* Hide header */
header {visibility: hidden;}
/* Hide deploy button & GitHub link */
[data-testid="stToolbar"] {display: none !important;}

html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px;
    padding: 3rem 2.5rem 2.5rem;
    margin-bottom: 2rem;
    color: #fff;
    text-align: center;
}
.hero h1 { font-size: 2.8rem; font-weight: 800; margin: 0 0 .5rem; letter-spacing: -1px; }
.hero p  { font-size: 1.1rem; color: #a8b2d8; margin: 0; }

.usp-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
.usp-card {
    background: #f8f9ff;
    border: 1px solid #e0e4f5;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
}
.usp-card .icon { font-size: 1.8rem; }
.usp-card p { margin: .4rem 0 0; font-size: .88rem; color: #444; font-weight: 500; }

.section-label {
    font-size: .75rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #7b8ab8;
    margin-bottom: .3rem;
}

.filter-pill {
    display: inline-block;
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    border-radius: 20px;
    padding: .25rem .75rem;
    font-size: .8rem;
    color: #3730a3;
    margin: .2rem .2rem 0 0;
}

[data-testid="metric-container"] {
    background: #f0f4ff;
    border: 1px solid #d4dcfa;
    border-radius: 12px;
    padding: 1rem 1.2rem !important;
}

.custom-divider {
    border: none;
    border-top: 2px solid #e8ecf5;
    margin: 1.5rem 0;
}

/* Clickable assignment count badge */
.count-badge {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    background: #1e293b;
    color: #fff;
    border-radius: 999px;
    padding: .35rem .9rem;
    font-size: .95rem;
    font-weight: 700;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all .18s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,.15);
    user-select: none;
}
.count-badge:hover {
    background: #3730a3;
    border-color: #818cf8;
    box-shadow: 0 4px 16px rgba(99,102,241,.35);
    transform: translateY(-1px);
}
.count-badge .arrow { font-size: .75rem; opacity: .7; }

/* Assignment detail card */
.assign-card {
    background: #f8faff;
    border: 1px solid #e0e7ff;
    border-left: 4px solid #6366f1;
    border-radius: 10px;
    padding: .9rem 1.1rem;
    margin-bottom: .65rem;
}
.assign-card .assign-no {
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .07em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: .3rem;
}
.assign-card .assign-desc {
    font-size: .97rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: .4rem;
}
.assign-meta {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem;
    font-size: .8rem;
    color: #64748b;
}
.assign-meta span {
    background: #e0e7ff;
    color: #3730a3;
    border-radius: 6px;
    padding: .15rem .55rem;
}
.assign-meta .extra-key {
    background: #f0fdf4;
    color: #166534;
}

.disabled-box {
    background: #f3f4f6;
    border: 1px dashed #d1d5db;
    border-radius: 8px;
    padding: .75rem 1rem;
    color: #9ca3af;
    font-size: .88rem;
    text-align: center;
    margin-top: 1.6rem;
}

.no-data {
    text-align: center;
    padding: 3rem 1rem;
    color: #9ca3af;
    font-size: 1rem;
}

.error-box {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: .75rem 1rem;
    color: #991b1b;
    font-size: .9rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ── Emoji badge logic ─────────────────────────────────────────
def assignment_emoji(count: int) -> str:
    if count == 0:   return "🙂"
    if count == 1:   return "😩"
    if count == 2:   return "😭"
    if count == 3:   return "😤"
    return "🤬"      # 4+


# ── Data loaders ─────────────────────────────────────────────
@st.cache_data(ttl=1)
def load_subjects() -> pd.DataFrame:
    """
    Sheet 1 (gid=0): Subject-level data.
    Columns: Batch, Course, Section, Subject, Pending_Assignments, Professor
    """
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


@st.cache_data(ttl=300)
def load_assignments() -> pd.DataFrame:
    """
    Sheet 2 (gid=1): Assignment-level data.
    Fixed columns : Subject, Assignment_No, Description, Deadline
    Extra columns : anything else (Comments, Marks, Links…) — shown dynamically
    URL uses gid=1 for the second sheet tab.
    """
    assign_url = SHEET_URL.replace("export?format=csv", "export?format=csv&gid=1")
    try:
        df = pd.read_csv(assign_url)
        df.columns = df.columns.str.strip()
        # Normalise case for known columns
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


# ── Session state init ────────────────────────────────────────
def init_state():
    defaults = {"page": "landing", "batch": None, "course": None, "section": None}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Timetable page ────────────────────────────────────────────
def show_timetable_page():
    st.markdown("## 📅 Weekly Timetable")
    st.info("Placeholder — connect your institution's schedule or upload a timetable CSV.")
    slots  = ["9:00–10:00", "10:00–11:00", "11:00–12:00", "12:00–1:00", "2:00–3:00", "3:00–4:00"]
    sample = {
        "Monday":    ["Machine Learning", "—", "Deep Learning",   "Break", "Statistics",  "Lab"],
        "Tuesday":   ["Python",           "Cloud Arch.", "—",     "Break", "DevOps",      "—"],
        "Wednesday": ["Networking",       "—", "Linux Admin",     "Break", "—",           "Machine Learning"],
        "Thursday":  ["Deep Learning",    "Statistics", "—",      "Break", "Python",      "Lab"],
        "Friday":    ["—",               "Cloud Arch.", "DevOps", "Break", "Linux Admin", "—"],
    }
    st.dataframe(pd.DataFrame(sample, index=slots), use_container_width=True)
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    if st.button("← Back to Portal", key="tt_back"):
        st.session_state.page = "landing"
        st.rerun()


# ── Landing page ──────────────────────────────────────────────
def landing_page(df: pd.DataFrame):
    st.markdown("""
    <div class="hero">
        <h1>🎓 Student Academic Portal</h1>
        <p>Your one-stop dashboard to track assignments, deadlines &amp; workload</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="usp-grid">
        <div class="usp-card"><div class="icon">📋</div><p>Track Assignments</p></div>
        <div class="usp-card"><div class="icon">⏰</div><p>Monitor Deadlines</p></div>
        <div class="usp-card"><div class="icon">📊</div><p>Subject-wise Workload</p></div>
        <div class="usp-card"><div class="icon">⚡</div><p>Clean &amp; Fast Interface</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    _, tt_col = st.columns([6, 1])
    with tt_col:
        if st.button("📅 View Timetable", use_container_width=True):
            st.session_state.page = "timetable"
            st.rerun()

    st.markdown("<div class='section-label'>Select Your Profile</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    batches = sorted(df["Batch"].dropna().unique().tolist()) if not df.empty else []
    with col1:
        batch = st.selectbox("🗓 Batch", ["— Select —"] + batches, key="sel_batch")

    courses = (
        sorted(df[df["Batch"] == batch]["Course"].dropna().unique().tolist())
        if batch != "— Select —" else []
    )
    with col2:
        course = st.selectbox("📘 Course", ["— Select —"] + courses,
                              key="sel_course", disabled=(batch == "— Select —"))

    sections = (
        sorted(df[(df["Batch"] == batch) & (df["Course"] == course)]["Section"].dropna().unique().tolist())
        if (batch != "— Select —" and course != "— Select —") else []
    )
    with col3:
        section1 = st.selectbox("🔬 Section 1", ["— Select —"] + sections,
                                key="sel_section1", disabled=(course == "— Select —"))

    with col4:
        st.markdown("<div class='disabled-box'>🔭 Section 2<br><small>Coming Soon</small></div>",
                    unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    all_selected = all(v != "— Select —" for v in [batch, course, section1])
    if not all_selected:
        st.caption("ℹ️ Please select Batch, Course, and Section 1 to continue.")

    if st.button("Continue to Subjects →", disabled=not all_selected, type="primary"):
        st.session_state.batch   = batch
        st.session_state.course  = course
        st.session_state.section = section1
        st.session_state.page    = "subjects"
        st.rerun()


# ── Subjects / Dashboard page ─────────────────────────────────
def subjects_page(df_subjects: pd.DataFrame, df_assignments: pd.DataFrame):
    batch   = st.session_state.batch
    course  = st.session_state.course
    section = st.session_state.section

    if st.button("← Back", key="back_btn"):
        st.session_state.page = "landing"
        st.rerun()

    st.markdown("## 📚 Subject Dashboard")

    pills_html = "".join(
        f"<span class='filter-pill'>{label}: <strong>{val}</strong></span>"
        for label, val in [("Batch", batch), ("Course", course), ("Section 1", section)]
    )
    pills_html += "<span class='filter-pill' style='opacity:.45;'>Section 2: Coming Soon</span>"
    st.markdown(pills_html, unsafe_allow_html=True)
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    filtered = df_subjects[
        (df_subjects["Batch"]   == batch)  &
        (df_subjects["Course"]  == course) &
        (df_subjects["Section"] == section)
    ]

    total_pending  = int(filtered["Pending_Assignments"].sum())
    total_subjects = len(filtered)
    avg = round(total_pending / total_subjects, 1) if total_subjects else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("📌 Total Pending",  total_pending)
    m2.metric("📚 Total Subjects", total_subjects)
    m3.metric("📈 Avg per Subject", avg)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    st.markdown(f"### 🗂 Section 1 — {section}")

    if filtered.empty:
        st.markdown(
            "<div class='no-data'>😕 No subjects found for the selected filters.</div>",
            unsafe_allow_html=True,
        )
        return

    # Determine extra (dynamic) columns in the assignment sheet
    known_assign_cols = {"Subject"} | set(ASSIGNMENT_FIXED_COLS)
    extra_cols = [c for c in df_assignments.columns if c not in known_assign_cols] \
                 if not df_assignments.empty else []

    for _, row in filtered.iterrows():
        subject = row["Subject"]
        pending = int(row["Pending_Assignments"])
        emoji   = assignment_emoji(pending)
        prof    = row["Professor"]

        # ── Level 1 expander: subject row ─────────────────────
        expander_label = f"{emoji}  {subject}  —  👨‍🏫 {prof}"
        with st.expander(expander_label, expanded=False):

            # Clickable-looking count badge + hint text
            st.markdown(
                f"""
                <div style='margin-bottom:.6rem;'>
                    <span class='count-badge'>
                        {emoji} {pending} pending assignment{'s' if pending != 1 else ''}
                        <span class='arrow'>▼ click to expand</span>
                    </span>
                    &nbsp;<span style='font-size:.8rem;color:#94a3b8;'>
                        ↓ expand below for details
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── Level 2 expander: assignment details ───────────
            assign_key = f"assign_{subject}_{batch}_{section}"
            with st.expander(
                f"📂 View {pending} assignment detail{'s' if pending != 1 else ''}",
                expanded=False,
                # unique key via label — Streamlit uses label+parent as key
            ):
                subj_assignments = df_assignments[
                    df_assignments["Subject"].str.strip() == subject.strip()
                ] if not df_assignments.empty else pd.DataFrame()

                if subj_assignments.empty:
                    st.caption("No assignment details found in Sheet 2 for this subject.")
                else:
                    for i, arow in subj_assignments.iterrows():
                        # Build meta tags (fixed fields)
                        deadline_val = arow.get("Deadline", "—")
                        desc_val     = arow.get("Description", "—")
                        no_val       = arow.get("Assignment_No", i + 1)

                        # Dynamic extra columns
                        extra_tags = "".join(
                            f"<span class='extra-key'>{col}: {arow[col]}</span>"
                            for col in extra_cols
                            if pd.notna(arow.get(col, None)) and str(arow.get(col, "")).strip() != ""
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
        "<div class='no-data' style='opacity:.6;'>Section 2 is not yet available.</div>",
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

    page = st.session_state.page
    if page == "timetable":
        show_timetable_page()
    elif page == "subjects":
        subjects_page(df_subjects, df_assignments)
    else:
        landing_page(df_subjects)


if __name__ == "__main__":
    main()
