# ============================================================
# Student Academic Portal — app.py
# ============================================================

import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Student Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

/* Hide default Streamlit chrome */
#MainMenu, footer { visibility: hidden; }

/* Hero banner */
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

/* USP cards */
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

/* Section headings */
.section-label {
    font-size: .75rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #7b8ab8;
    margin-bottom: .3rem;
}

/* Timetable button */
.tt-wrapper { text-align: right; margin-top: .5rem; }

/* Filter summary pill */
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

/* Dashboard metric card override */
[data-testid="metric-container"] {
    background: #f0f4ff;
    border: 1px solid #d4dcfa;
    border-radius: 12px;
    padding: 1rem 1.2rem !important;
}

/* Divider */
.custom-divider {
    border: none;
    border-top: 2px solid #e8ecf5;
    margin: 1.5rem 0;
}

/* Warning banner */
.warn-box {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: .75rem 1rem;
    color: #92400e;
    font-size: .9rem;
    margin-bottom: 1rem;
}

/* No-data message */
.no-data {
    text-align: center;
    padding: 3rem 1rem;
    color: #9ca3af;
    font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ── Data loader ──────────────────────────────────────────────
# ── Data loader (Google Sheets) ──────────────────────────────
sheet_url = "https://docs.google.com/spreadsheets/d/1MUynpz5LOdHVTsMSK5V4aP8bTCGLHRSy02peJn6XXbk/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(sheet_url)

        # Clean column names (remove spaces)
        df.columns = df.columns.str.strip()

        # Ensure required columns exist
        required_cols = [
            "Batch",
            "Course",
            "Specialization",
            "Subject",
            "Pending_Assignments",
            "Deadline",
            "Professor",
        ]

        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            st.error(f"Missing columns in Google Sheet: {missing}")
            st.stop()

        # Convert types safely
        df["Pending_Assignments"] = pd.to_numeric(
            df["Pending_Assignments"], errors="coerce"
        ).fillna(0)

        df["Deadline"] = pd.to_datetime(df["Deadline"], errors="coerce")

        # Convert Batch to string (important!)
        df["Batch"] = df["Batch"].astype(str)

        return df

    except Exception as e:
        st.error("Failed to load data from Google Sheet.")
        st.write(e)
        st.stop()

# ── Session state init ────────────────────────────────────────
def init_state():
    defaults = {
        "page":        "landing",
        "batch":       None,
        "course":      None,
        "spec1":       None,
        "spec2":       None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── Timetable modal (dialog simulation) ──────────────────────
def show_timetable_page():
    """Render a simple timetable overlay."""
    st.markdown("## 📅 Weekly Timetable")
    st.info("This is a placeholder timetable. Connect your institution's schedule API or upload a timetable CSV to populate this section.")

    days   = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots  = ["9:00–10:00", "10:00–11:00", "11:00–12:00", "12:00–1:00", "2:00–3:00", "3:00–4:00"]
    sample = {
        "Monday":    ["Machine Learning", "—", "Deep Learning", "Break", "Statistics", "Lab"],
        "Tuesday":   ["Python for AI", "Cloud Arch.", "—", "Break", "DevOps", "—"],
        "Wednesday": ["Networking", "—", "Linux Admin", "Break", "—", "Machine Learning"],
        "Thursday":  ["Deep Learning", "Statistics", "—", "Break", "Python for AI", "Lab"],
        "Friday":    ["—", "Cloud Arch.", "DevOps", "Break", "Linux Admin", "—"],
    }

    tt_df = pd.DataFrame(sample, index=slots)
    st.dataframe(tt_df, use_container_width=True)
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
        <p>Your one-stop dashboard to track assignments, deadlines & workload</p>
    </div>
    """, unsafe_allow_html=True)

    # USP cards
    st.markdown("""
    <div class="usp-grid">
        <div class="usp-card"><div class="icon">📋</div><p>Track Assignments</p></div>
        <div class="usp-card"><div class="icon">⏰</div><p>Monitor Deadlines</p></div>
        <div class="usp-card"><div class="icon">📊</div><p>Subject-wise Workload</p></div>
        <div class="usp-card"><div class="icon">⚡</div><p>Clean & Fast Interface</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Timetable button (top-right area) ─────────────────────
    _, tt_col = st.columns([6, 1])
    with tt_col:
        if st.button("📅 View Timetable", use_container_width=True):
            st.session_state.page = "timetable"
            st.rerun()

    # ── Dropdowns ─────────────────────────────────────────────
    st.markdown("<div class='section-label'>Select Your Profile</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    batches = sorted(df["Batch"].unique().tolist())
    with col1:
        batch = st.selectbox("🗓 Batch", ["— Select —"] + batches, key="sel_batch")

    # Cascade: course depends on batch
    if batch != "— Select —":
        courses = sorted(df[df["Batch"] == batch]["Course"].unique().tolist())
    else:
        courses = []

    with col2:
        course = st.selectbox(
            "📘 Course",
            ["— Select —"] + courses,
            key="sel_course",
            disabled=(batch == "— Select —"),
        )

    # Cascade: specialization depends on batch + course
    if batch != "— Select —" and course != "— Select —":
        specs = sorted(
            df[(df["Batch"] == batch) & (df["Course"] == course)]["Specialization"].unique().tolist()
        )
    else:
        specs = []

    with col3:
        spec1 = st.selectbox(
            "🔬 Specialization 1",
            ["— Select —"] + specs,
            key="sel_spec1",
            disabled=(course == "— Select —"),
        )

    with col4:
        spec2 = st.selectbox(
            "🔭 Specialization 2",
            ["— Select —"] + specs,
            key="sel_spec2",
            disabled=(spec1 == "— Select —"),
        )

    # Duplicate specialization warning
    if (
        spec1 != "— Select —"
        and spec2 != "— Select —"
        and spec1 == spec2
    ):
        st.markdown(
            "<div class='warn-box'>⚠️ Specialization 1 and Specialization 2 are the same. Please choose different specializations.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Continue button — disabled unless all fields are selected
    all_selected = all(
        v != "— Select —" for v in [batch, course, spec1, spec2]
    ) and spec1 != spec2

    if not all_selected:
        st.caption("ℹ️ Please complete all selections (with different specializations) to continue.")

    if st.button(
        "Continue to Subjects →",
        disabled=not all_selected,
        type="primary",
        use_container_width=False,
    ):
        st.session_state.batch  = batch
        st.session_state.course = course
        st.session_state.spec1  = spec1
        st.session_state.spec2  = spec2
        st.session_state.page   = "subjects"
        st.rerun()


# ── Subjects / Dashboard page ─────────────────────────────────
def subjects_page(df: pd.DataFrame):
    batch  = st.session_state.batch
    course = st.session_state.course
    spec1  = st.session_state.spec1
    spec2  = st.session_state.spec2

    # Back button
    if st.button("← Back", key="back_btn"):
        st.session_state.page = "landing"
        st.rerun()

    # Page title
    st.markdown("## 📚 Subject Dashboard")

    # Filter pills
    pills_html = "".join(
        f"<span class='filter-pill'>{label}: <strong>{val}</strong></span>"
        for label, val in [("Batch", batch), ("Course", course),
                           ("Spec 1", spec1), ("Spec 2", spec2)]
    )
    st.markdown(pills_html, unsafe_allow_html=True)
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Filter data
    base = df[(df["Batch"] == batch) & (df["Course"] == course)]
    df1  = base[base["Specialization"] == spec1]
    df2  = base[base["Specialization"] == spec2]

    total1    = int(df1["Pending_Assignments"].sum())
    total2    = int(df2["Pending_Assignments"].sum())
    combined  = total1 + total2

    # ── Dashboard metrics ─────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric(f"📌 Pending — {spec1}", total1, help="Total pending assignments in Specialization 1")
    m2.metric(f"📌 Pending — {spec2}", total2, help="Total pending assignments in Specialization 2")
    m3.metric("🔢 Combined Total", combined, help="Sum of both specializations")

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Subject expanders ─────────────────────────────────────
    def render_subjects(data: pd.DataFrame, spec_label: str):
        st.markdown(f"### 🗂 {spec_label}")
        if data.empty:
            st.markdown(
                "<div class='no-data'>😕 No subjects found for the selected filters.</div>",
                unsafe_allow_html=True,
            )
            return

        for _, row in data.iterrows():
            pending = int(row["Pending_Assignments"])
            badge   = "🔴" if pending >= 3 else ("🟡" if pending == 2 else "🟢")
            label   = f"{badge} {row['Subject']}  —  {pending} assignment{'s' if pending != 1 else ''} pending"

            with st.expander(label, expanded=False):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**📋 Pending**\n\n{pending}")
                c2.markdown(f"**📅 Deadline**\n\n{row['Deadline']}")
                c3.markdown(f"**👨‍🏫 Professor**\n\n{row['Professor']}")

    render_subjects(df1, spec1)
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    render_subjects(df2, spec2)


# ── App router ────────────────────────────────────────────────
def main():
    init_state()
    df = load_data()

    page = st.session_state.page

    if page == "timetable":
        show_timetable_page()
    elif page == "subjects":
        subjects_page(df)
    else:
        landing_page(df)


if __name__ == "__main__":
    main()
