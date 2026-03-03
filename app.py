# ============================================================
# Student Academic Portal — app.py
# ============================================================

import streamlit as st
import pandas as pd

# ── Config ───────────────────────────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MUynpz5LOdHVTsMSK5V4aP8bTCGLHRSy02peJn6XXbk/export?format=csv"

st.set_page_config(
    page_title="Student Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
#MainMenu, footer { visibility: hidden; }

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


# ── Data loader ──────────────────────────────────────────────
REQUIRED_COLS = ["Batch", "Course", "Section", "Subject", "Pending_Assignments", "Deadline", "Professor"]

@st.cache_data(ttl=60)
def load_data() -> pd.DataFrame:
    """Fetch live data from Google Sheets (CSV export URL)."""
    try:
        df = pd.read_csv(SHEET_URL)
        # Normalize: strip whitespace + unify case for matching
        df.columns = df.columns.str.strip()
        # Build a case-insensitive rename map to expected column names
        col_map = {c: c for c in df.columns}  # identity by default
        for actual in df.columns:
            for expected in REQUIRED_COLS:
                if actual.lower() == expected.lower() and actual != expected:
                    col_map[actual] = expected
        df.rename(columns=col_map, inplace=True)
        df["Pending_Assignments"] = pd.to_numeric(
            df["Pending_Assignments"], errors="coerce"
        ).fillna(0).astype(int)
        return df
    except Exception as e:
        st.markdown(
            f"<div class='error-box'>⚠️ Could not load data from Google Sheets.<br>"
            f"<small>{e}</small><br>"
            f"Make sure the sheet is shared as <strong>'Anyone with the link can view'</strong>.</div>",
            unsafe_allow_html=True,
        )
        return pd.DataFrame(columns=REQUIRED_COLS)


def validate_columns(df: pd.DataFrame) -> bool:
    """Check all required columns exist and show a clear error if not."""
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        st.error(
            f"**Column mismatch detected.**\n\n"
            f"Missing columns: `{'`, `'.join(missing)}`\n\n"
            f"Columns found in your sheet: `{'`, `'.join(df.columns.tolist())}`\n\n"
            f"Expected exactly: `{'`, `'.join(REQUIRED_COLS)}`\n\n"
            f"Fix the header row in your Google Sheet and try again."
        )
        return False
    return True


# ── Session state init ────────────────────────────────────────
def init_state():
    defaults = {
        "page":    "landing",
        "batch":   None,
        "course":  None,
        "section": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Timetable page ────────────────────────────────────────────
def show_timetable_page():
    st.markdown("## 📅 Weekly Timetable")
    st.info("Placeholder — connect your institution's schedule or upload a timetable CSV to populate this section.")

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
    # Hero
    st.markdown("""
    <div class="hero">
        <h1>🎓 Student Academic Portal</h1>
        <p>Your one-stop dashboard to track assignments, deadlines &amp; workload</p>
    </div>
    """, unsafe_allow_html=True)

    # USP cards
    st.markdown("""
    <div class="usp-grid">
        <div class="usp-card"><div class="icon">📋</div><p>Track Assignments</p></div>
        <div class="usp-card"><div class="icon">⏰</div><p>Monitor Deadlines</p></div>
        <div class="usp-card"><div class="icon">📊</div><p>Subject-wise Workload</p></div>
        <div class="usp-card"><div class="icon">⚡</div><p>Clean &amp; Fast Interface</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Timetable button — top right
    _, tt_col = st.columns([6, 1])
    with tt_col:
        if st.button("📅 View Timetable", use_container_width=True):
            st.session_state.page = "timetable"
            st.rerun()

    # ── Dropdowns ─────────────────────────────────────────────
    st.markdown("<div class='section-label'>Select Your Profile</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # Batch
    batches = sorted(df["Batch"].dropna().unique().tolist()) if not df.empty else []
    with col1:
        batch = st.selectbox("🗓 Batch", ["— Select —"] + batches, key="sel_batch")

    # Course — cascades from Batch
    courses = (
        sorted(df[df["Batch"] == batch]["Course"].dropna().unique().tolist())
        if batch != "— Select —" else []
    )
    with col2:
        course = st.selectbox(
            "📘 Course",
            ["— Select —"] + courses,
            key="sel_course",
            disabled=(batch == "— Select —"),
        )

    # Section 1 — cascades from Batch + Course
    sections = (
        sorted(df[(df["Batch"] == batch) & (df["Course"] == course)]["Section"].dropna().unique().tolist())
        if (batch != "— Select —" and course != "— Select —") else []
    )
    with col3:
        section1 = st.selectbox(
            "🔬 Section 1",
            ["— Select —"] + sections,
            key="sel_section1",
            disabled=(course == "— Select —"),
        )

    # Section 2 — permanently disabled placeholder
    with col4:
        st.markdown("<div class='disabled-box'>🔭 Section 2<br><small>Coming Soon</small></div>",
                    unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Continue — enabled only when all three active dropdowns are filled
    all_selected = all(v != "— Select —" for v in [batch, course, section1])

    if not all_selected:
        st.caption("ℹ️ Please select Batch, Course, and Section 1 to continue.")

    if st.button(
        "Continue to Subjects →",
        disabled=not all_selected,
        type="primary",
    ):
        st.session_state.batch   = batch
        st.session_state.course  = course
        st.session_state.section = section1
        st.session_state.page    = "subjects"
        st.rerun()


# ── Subjects / Dashboard page ─────────────────────────────────
def subjects_page(df: pd.DataFrame):
    batch   = st.session_state.batch
    course  = st.session_state.course
    section = st.session_state.section

    if st.button("← Back", key="back_btn"):
        st.session_state.page = "landing"
        st.rerun()

    st.markdown("## 📚 Subject Dashboard")

    # Active filter pills
    pills_html = "".join(
        f"<span class='filter-pill'>{label}: <strong>{val}</strong></span>"
        for label, val in [("Batch", batch), ("Course", course), ("Section 1", section)]
    )
    pills_html += "<span class='filter-pill' style='opacity:.45;'>Section 2: Coming Soon</span>"
    st.markdown(pills_html, unsafe_allow_html=True)
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Filter
    filtered = df[
        (df["Batch"] == batch) &
        (df["Course"] == course) &
        (df["Section"] == section)
    ]

    total_pending = int(filtered["Pending_Assignments"].sum())
    total_subjects = len(filtered)

    # ── Metrics ───────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("📌 Total Pending", total_pending,  help="Sum of all pending assignments")
    m2.metric("📚 Total Subjects", total_subjects, help="Number of subjects this section")
    avg = round(total_pending / total_subjects, 1) if total_subjects else 0
    m3.metric("📈 Avg per Subject", avg,           help="Average pending per subject")

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Subject expanders ─────────────────────────────────────
    st.markdown(f"### 🗂 Section 1 — {section}")

    if filtered.empty:
        st.markdown(
            "<div class='no-data'>😕 No subjects found for the selected filters.<br>"
            "<small>Check that your Google Sheet has matching data.</small></div>",
            unsafe_allow_html=True,
        )
        return

    for _, row in filtered.iterrows():
        pending = int(row["Pending_Assignments"])
        badge   = "🔴" if pending >= 3 else ("🟡" if pending == 2 else "🟢")
        label   = f"{badge} {row['Subject']}  —  {pending} assignment{'s' if pending != 1 else ''} pending"

        with st.expander(label, expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**📋 Pending Assignments**\n\n{pending}")
            c2.markdown(f"**📅 Deadline**\n\n{row['Deadline']}")
            c3.markdown(f"**👨‍🏫 Professor**\n\n{row['Professor']}")

    # Section 2 placeholder
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    st.markdown("### 🔭 Section 2 — *Coming Soon*")
    st.markdown(
        "<div class='no-data' style='opacity:.6;'>Section 2 is not yet available.<br>"
        "<small>It will appear here once enabled.</small></div>",
        unsafe_allow_html=True,
    )


# ── Router ────────────────────────────────────────────────────
def main():
    init_state()
    df = load_data()

    # Always show column debug info in an expander for easy diagnosis
    with st.expander("🛠 Debug: Sheet columns (remove after fixing)", expanded=False):
        st.write("Columns detected:", df.columns.tolist())
        st.write("Row count:", len(df))
        if not df.empty:
            st.dataframe(df.head(3))

    if not validate_columns(df):
        st.stop()

    page = st.session_state.page
    if page == "timetable":
        show_timetable_page()
    elif page == "subjects":
        subjects_page(df)
    else:
        landing_page(df)


if __name__ == "__main__":
    main()
