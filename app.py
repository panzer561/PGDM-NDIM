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


@st.cache_data(ttl=1)
def load_assignments() -> pd.DataFrame:
    """
    Sheet 2: Assignment-level data.
    Fixed columns : Subject, Assignment_No, Description, Deadline
    Extra columns : anything else (Comments, Marks, Links…) — shown dynamically

    To find your gid:
      1. Open your Google Sheet
      2. Click the second tab at the bottom
      3. Look at the URL: ...#gid=XXXXXXXXX
      4. Paste that number in ASSIGNMENT_SHEET_GID below
    """
    ASSIGNMENT_SHEET_GID = "0"   # ← REPLACE with your actual Sheet 2 gid

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


# ── Session state init ────────────────────────────────────────
def init_state():
    defaults = {"page": "landing", "batch": None, "course": None, "section": None}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Timetable page ────────────────────────────────────────────
def show_timetable_page():
    if st.button("← Back to Portal", key="tt_back"):
        st.session_state.page = "landing"
        st.rerun()

    st.markdown("## 📅 Timetable — Semester II (PGDM 2025–2027)")
    st.caption("Wednesday 04 Mar 2026 is a **Holiday — Holi** 🎨")
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Full timetable data ───────────────────────────────────
    # Structure: { day: { section: { slot: (subject, professor, room) } } }
    TT = {
        "Monday (02 Mar)": {
            # --- Major-2 sections ---
            "AIML-A": {
                "9:40–10:55":  ("Data Engineering Using SQLite", "Dr. Rinku Dixit", "WB 5401"),
                "11:05–12:20": ("Machine Learning using Python", "Dr. Shailee Choudhary", "WB 5401"),
            },
            "AIML-B": {
                "9:40–10:55":  ("Machine Learning using Python", "Dr. Shailee Choudhary", "WB 5402"),
                "11:05–12:20": ("ML using Knime & Alteryx + FC Session", "Dr. Nabeela Hasan", "WB 5402"),
            },
            "AIML-C": {
                "9:40–10:55":  ("ML using Knime & Alteryx", "Dr. Nabeela Hasan", "WB 5403"),
                "11:05–12:20": ("Data Engineering Using SQLite + FC Session", "Dr. Rinku Dixit", "WB 5403"),
            },
            "MF": {
                "9:40–10:55":  ("Sales & Distribution Management", "Dr. Prabal Chakraborty", "KB 301"),
                "11:05–12:20": ("Sales & Distribution Management", "Dr. Prabal Chakraborty", "KB 301"),
            },
            "MG": {
                "9:40–10:55":  ("Sales & Distribution Management", "Dr. Gajendra Sharma", "KB 302"),
                "11:05–12:20": ("Sales & Distribution Management", "Dr. Gajendra Sharma", "KB 302"),
            },
            "FE": {
                "9:40–10:55":  ("SAPM", "Dr. Rajbeer Kaur", "WB 5405"),
                "11:05–12:20": ("Mergers and Acquisitions", "Dr. Geetika Batra", "WB 5405"),
            },
            "DM": {
                "9:40–10:55":  ("PPC Campaigns", "Prof. Kunal Jha", "KB 102"),
                "11:05–12:20": ("PPC Campaigns", "Prof. Kunal Jha", "KB 102"),
            },
            "HR2": {
                "9:40–10:55":  ("Performance Management System", "Prof. Parveen Kaur", "WB 5501"),
                "11:05–12:20": ("Talent Acquisition", "Dr. Aaqib Danish", "WB 5501"),
            },
            "FAIM": {
                "9:40–10:55":  ("Alternative Assets & Private Equity", "Dr. Geetika Batra", "WB 5502"),
                "11:05–12:20": ("Financial Planning", "Dr. Sharif / Dr. Somnath", "WB 5502"),
            },
            "OPR-A": {
                "9:40–10:55":  ("Operations Research & Application", "Dr. MKP Naik", "KB 303"),
                "11:05–12:20": ("Logistics & SCM", "Prof. Arun Kumar", "KB 303"),
            },
            "OPR-B": {
                "9:40–10:55":  ("Logistics & SCM", "Prof. Arun Kumar", "KB 6500"),
                "11:05–12:20": ("Operations Research & Application + FC Session", "Dr. MKP Naik", "KB 6500"),
            },
            # --- Major-1 sections ---
            "MA": {
                "12:30–1:45": ("Sales & Distribution Management", "Prof. Veena Kumar / Dr. Samriti Mahajan", "WB 5401"),
                "2:20–3:35":  ("Power BI", "Dr. Raj Kumar Garg", "WB 5401 (Lab)"),
                "3:45–5:00":  ("CSD-2", "Dr. Jyoti Kukreja / Angad Munshi", "WB 5401"),
            },
            "MB": {
                "12:30–1:45": ("Financial Management", "Dr. Pushpa Negi", "WB 5402"),
                "2:20–3:35":  ("Strategic Brand Communication (IMC)", "Dr. Komal Khatter", "WB 5402"),
                "3:45–5:00":  ("Economic Environment of Business", "Dr. Charu Tayal", "WB 5402"),
            },
            "MC": {
                "12:30–1:45": ("Research Methodology", "Dr. S S Khullar", "WB 5403"),
                "2:20–3:35":  ("Sales & Distribution Management", "Prof. Veena Kumar", "WB 5403"),
                "3:45–5:00":  ("HRM", "Dr. Tanveer Shah", "WB 5403"),
            },
            "MD": {
                "12:30–1:45": ("HRM AI Integration Module", "Dr. Antarpreet Singh / Dr. Aaqib Danish", "WB 5501"),
                "2:20–3:35":  ("CSD-2", "Dr. Jyoti Kukreja / Dr. Samriti Mahajan", "WB 5501"),
                "3:45–5:00":  ("Research Methodology", "Dr. Elizabeth Jacob", "WB 5501"),
            },
            "ME": {
                "12:30–1:45": ("Financial Management", "Dr. Nidhi Mathur", "WB 5502"),
                "2:20–3:35":  ("Strategic International Business Operations", "Dr. S P Sharma", "WB 5502"),
                "3:45–5:00":  ("Strategic Brand Communication (IMC)", "Dr. Chaitali / Dr. Mohd. Azhar", "WB 5502"),
            },
            "FA": {
                "12:30–1:45": ("Research Methodology", "Prof. Sayanti Banerjee", "KB 301"),
                "2:20–3:35":  ("HRM", "Dr. Sunaina Sardana", "KB 301"),
                "3:45–5:00":  ("SAPM", "Dr. Som Nath Paul", "KB 301"),
            },
            "FB": {
                "12:30–1:45": ("Corporate Finance", "Dr. Silky Vigg", "KB 302"),
                "2:20–3:35":  ("CSD-2 + Guest Session", "Dr. Parul Malik", "KB 302"),
                "3:45–5:00":  ("Research Methodology", "Prof. Sayanti Banerjee", "KB 302"),
            },
            "FC": {
                "12:30–1:45": ("HRM", "Dr. Rashmi Chauhan", "KB 303"),
                "2:20–3:35":  ("SAPM", "Dr. Som Nath Paul", "KB 303"),
                "3:45–5:00":  ("Corporate Finance", "Dr. Nidhi Mathur", "KB 303"),
            },
            "FD": {
                "12:30–1:45": ("Principle of Banking", "Prof. Rachna Kathuria", "KB 6500"),
                "2:20–3:35":  ("HRM AI Integration Module", "Dr. Antarpreet Singh / Dr. Tanveer Shah", "KB 6500"),
                "3:45–5:00":  ("Power BI", "Prof. Praveen Malik", "KB 6500"),
            },
            "HR": {
                "12:30–1:45": ("Power BI", "Dr. Raj Kumar Garg", "WB 5405 (Lab)"),
                "2:20–3:35":  ("Research Methodology", "Dr. S S Khullar / Dr. Elizabeth", "WB 5405"),
                "3:45–5:00":  ("Financial Management", "Dr. Saib Fakhar / Dr. Silky Vigg", "WB 5405"),
            },
        },
        "Tuesday (03 Mar)": {
            "MA": {
                "9:40–10:40":  ("Digital Marketing Social Media", "Prof. Sonal Gulati", "WB 5401"),
                "10:50–11:50": ("Strategic Brand Communication (IMC)", "Dr. Ritu Talwar", "WB 5401"),
                "12:00–1:00":  ("HRM", "Dr. Monica Verma", "WB 5401"),
                "1:40–2:40":   ("Business Intelligence using Emerging Technology", "Dr. Kamal Kundra", "WB 5401"),
                "2:50–3:50":   ("Financial Management", "Dr. Rajbeer Kaur", "WB 5401"),
            },
            "MB": {
                "9:40–10:40":  ("Aptitude", "Prof. Atul Rawat", "WB 5402"),
                "10:50–11:50": ("Strategic Brand Communication (IMC)", "Dr. Komal Khatter", "WB 5402"),
                "12:00–1:00":  ("CSD-2", "Dr. Mahima Gulati", "WB 5402"),
                "1:40–2:40":   ("Research Methodology", "Dr. Elizabeth Jacob", "WB 5402"),
                "2:50–3:50":   ("Sales & Distribution Management", "Dr. Swati Bhatnagar", "WB 5402"),
            },
            "MC": {
                "9:40–10:40":  ("Strategic Brand Communication (IMC)", "Dr. Ritu Talwar", "WB 5403"),
                "10:50–11:50": ("Power BI", "Dr. Raj Kumar Garg", "WB 5403 (Lab)"),
                "12:00–1:00":  ("Strategic International Business Operations", "Dr. S P Sharma", "WB 5403"),
                "1:40–2:40":   ("Aptitude", "Prof. Atul Rawat", "WB 5403"),
                "2:50–3:50":   ("Financial Management", "Dr. Kavita Berwal / Dr. Pushpa Negi", "WB 5403"),
            },
            "MD": {
                "9:40–10:40":  ("Strategic Brand Communication (IMC)", "Prof. Abha Grover / Dr. Sarita Nagvanshi", "WB 5501"),
                "10:50–11:50": ("Economic Environment of Business", "Dr. Shagun Arora", "WB 5501"),
                "12:00–1:00":  ("Economic Environment of Business", "Dr. Shagun Arora", "WB 5501"),
                "1:40–2:40":   ("Power BI", "Prof. Praveen Malik", "WB 5501 (Lab)"),
                "2:50–3:50":   ("Aptitude", "Prof. Atul Rawat", "WB 5501"),
            },
            "ME": {
                "9:40–10:40":  ("CSD-2", "Dr. Mahima Gulati", "WB 5502"),
                "10:50–11:50": ("Sales & Distribution Management", "Dr. Gajendra Sharma", "WB 5502"),
                "12:00–1:00":  ("Strategic Brand Communication (IMC)", "Dr. Chaitali / Dr. Mohd. Azhar", "WB 5502"),
                "1:40–2:40":   ("Digital Marketing Social Media", "Prof. Kunal Jha", "WB 5502 (Lab)"),
                "2:50–3:50":   ("Economic Environment of Business", "Prof. Karan Khati", "WB 5502"),
            },
            "FA": {
                "9:40–10:40":  ("Economic Environment of Business", "Prof. Karan Khati", "KB 301"),
                "10:50–11:50": ("Power BI", "Dr. Arpana Chaturvedi", "KB 301 (Lab)"),
                "12:00–1:00":  ("Principle of Insurance", "Prof. Dinesh Gupta", "KB 301"),
                "1:40–2:40":   ("CSD-2", "Dr. Parul Malik", "KB 301"),
                "2:50–3:50":   ("Research Methodology", "Prof. Sayanti Banerjee", "KB 301"),
            },
            "FB": {
                "9:40–10:40":  ("Strategic International Business Operations", "Dr. Sangeeta Yadav", "KB 302"),
                "10:50–11:50": ("Principle of Insurance", "Prof. Dinesh Gupta", "KB 302"),
                "12:00–1:00":  ("HRM", "Dr. Sunaina Sardana", "KB 302"),
                "1:40–2:40":   ("Research Methodology", "Prof. Sayanti Banerjee", "KB 302"),
                "2:50–3:50":   ("Power BI", "Dr. Arpana Chaturvedi", "KB 302 (Lab)"),
            },
            "FC": {
                "9:40–10:40":  ("Principle of Insurance", "Prof. Dinesh Gupta", "KB 303"),
                "10:50–11:50": ("SAPM", "Dr. Som Nath Paul", "KB 303"),
                "12:00–1:00":  ("FMS", "Dr. Agnihotri", "KB 303"),
                "1:40–2:40":   ("HRM AI Integration Module", "Dr. Antarpreet Singh / Dr. Rashmi Chauhan", "KB 303"),
                "2:50–3:50":   ("Business Intelligence using Emerging Technology", "Dr. Kamal Kundra", "KB 303"),
            },
            "FD": {
                "9:40–10:40":  ("Economic Environment of Business", "Dr. Shagun Arora", "KB 6500"),
                "10:50–11:50": ("FMS", "Dr. Agnihotri", "KB 6500"),
                "12:00–1:00":  ("Corporate Finance", "Dr. Silky Vigg", "KB 6500"),
                "1:40–2:40":   ("SAPM", "Dr. Haseen / Dr. Som Nath Paul", "KB 6500"),
                "2:50–3:50":   ("Power BI", "Prof. Praveen Malik", "KB 6500 (Lab)"),
            },
            "HR": {
                "9:40–10:40":  ("Research Methodology", "Dr. S S Khullar / Dr. Elizabeth", "WB 5405"),
                "10:50–11:50": ("HRM", "Dr. Monica Verma", "WB 5405"),
                "12:00–1:00":  ("Psychometrics & Competency Mapping", "Dr. Radha Sharma", "WB 5405"),
                "1:40–2:40":   ("CSD-2", "Prof. Nikhil Singh", "WB 5405"),
                "2:50–3:50":   ("Economic Environment of Business", "Dr. Zeeshan", "WB 5405"),
            },
        },
        "Wednesday (04 Mar)": {
            "ALL SECTIONS": {
                "Full Day": ("🎨 HOLIDAY — HOLI", "—", "—"),
            },
        },
        "Thursday (05 Mar)": {
            "MA": {
                "9:40–10:55":  ("Power BI", "Dr. Raj Kumar Garg", "WB 5401 (Lab)"),
                "11:05–12:20": ("Strategic Brand Communication (IMC)", "Dr. Ritu Talwar", "WB 5401"),
                "12:30–1:45":  ("Sales & Distribution Management", "Prof. Veena Kumar / Dr. Samriti Mahajan", "WB 5401"),
                "2:20–3:35":   ("Aptitude", "Prof. Atul Rawat", "WB 5401"),
                "3:45–5:00":   ("CSD-2", "Dr. Jyoti Kukreja / Angad Munshi", "WB 5401"),
            },
            "MB": {
                "9:40–10:55":  ("HRM", "Dr. Tanveer Shah", "WB 5402"),
                "11:05–12:20": ("Digital Marketing Social Media", "Prof. Kunal Jha", "WB 5402"),
                "12:30–1:45":  ("Financial Management", "Dr. Pushpa Negi", "WB 5402"),
                "2:20–3:35":   ("Power BI", "Dr. Raj Kumar Garg", "WB 5402 (Lab)"),
                "3:45–5:00":   ("CSD-2", "Dr. Mahima Gulati", "WB 5402"),
            },
            "MC": {
                "9:40–10:55":  ("Strategic Brand Communication (IMC)", "Dr. Ritu Talwar", "WB 5403"),
                "11:05–12:20": ("Sales & Distribution Management", "Prof. Veena Kumar", "WB 5403"),
                "12:30–1:45":  ("CSD-2", "Dr. Jyoti Kukreja / Angad Munshi", "WB 5403"),
                "2:20–3:35":   ("Business Intelligence using Emerging Technology", "Dr. Kamal Kundra", "WB 5403 (Lab)"),
                "3:45–5:00":   ("Financial Management", "Dr. Kavita Berwal / Dr. Pushpa Negi", "WB 5403"),
            },
            "MD": {
                "9:40–10:55":  ("Strategic Brand Communication (IMC)", "Prof. Abha Grover / Dr. Sarita Nagvanshi", "WB 5501"),
                "11:05–12:20": ("Strategic International Business Operations", "Dr. S P Sharma", "WB 5501"),
                "12:30–1:45":  ("Power BI", "Prof. Praveen Malik", "WB 5501 (Lab)"),
                "2:20–3:35":   ("Financial Management", "Dr. Sharif Mohd. / Dr. Nidhi Mathur", "WB 5501"),
                "3:45–5:00":   ("Digital Marketing Social Media", "Prof. Kunal Jha", "WB 5501"),
            },
            "ME": {
                "9:40–10:55":  ("Aptitude", "Prof. Atul Rawat", "WB 5502"),
                "11:05–12:20": ("Power BI", "Prof. Praveen Malik", "WB 5502 (Lab)"),
                "12:30–1:45":  ("HRM AI Integration Module", "Dr. Antarpreet Singh / Dr. Aaqib Danish", "WB 5502"),
                "2:20–3:35":   ("Research Methodology", "Dr. Anuj Nain", "WB 5502"),
                "3:45–5:00":   ("Business Intelligence using Emerging Technology", "Dr. Kamal Kundra", "WB 5502"),
            },
            "FA": {
                "9:40–10:55":  ("Strategic International Business Operations", "Dr. Sangeeta Yadav (9:50–10:50)", "KB 301"),
                "11:05–12:20": ("Corporate Finance", "Dr. Pushpa Negi", "KB 301"),
                "12:30–1:45":  ("Power BI", "Dr. Arpana Chaturvedi", "KB 301 (Lab)"),
                "2:20–3:35":   ("Corporate Finance", "Dr. Pushpa Negi", "KB 301"),
                "3:45–5:00":   ("CSD-2", "Dr. Parul Malik", "KB 301"),
            },
            "FB": {
                "9:40–10:55":  ("SAPM", "Dr. Som Nath Paul", "KB 302"),
                "11:05–12:20": ("Power BI", "Dr. Arpana Chaturvedi", "KB 302 (Lab)"),
                "12:30–1:45":  ("Aptitude", "Prof. Atul Rawat", "KB 302 (Lab)"),
                "2:20–3:35":   ("CSD-2", "Dr. Parul Malik", "KB 302"),
                "3:45–5:00":   ("—", "—", "—"),
            },
            "FC": {
                "9:40–10:55":  ("Research Methodology", "Dr. Mohd. Azhar / Dr. Anuj Nain", "KB 303"),
                "11:05–12:20": ("Economic Environment of Business", "Dr. Zeeshan", "KB 303"),
                "12:30–1:45":  ("FMS", "Dr. Agnihotri", "KB 303"),
                "2:20–3:35":   ("Power BI", "Dr. Arpana Chaturvedi", "KB 303 (Lab)"),
                "3:45–5:00":   ("Aptitude", "Prof. Atul Rawat", "KB 303"),
            },
            "FD": {
                "9:40–10:55":  ("Economic Environment of Business", "Dr. Shagun Arora", "KB 6500"),
                "11:05–12:20": ("FMS", "Dr. Agnihotri", "KB 6500"),
                "12:30–1:45":  ("Research Methodology", "Dr. Mohd. Azhar / Dr. Anuj Nain", "KB 6500"),
                "2:20–3:35":   ("SAPM", "Dr. Haseen / Dr. Som Nath Paul", "KB 6500"),
                "3:45–5:00":   ("Principle of Insurance", "CA Navin Saraf", "KB 6500"),
            },
            "HR": {
                "9:40–10:55":  ("Performance Management System", "Prof. Parveen Kaur", "WB 5405"),
                "11:05–12:20": ("Aptitude", "Prof. Atul Rawat", "WB 5405"),
                "12:30–1:45":  ("Talent Acquisition", "Dr. Teena Singh (12:30–2:30)", "WB 5405"),
                "2:20–3:35":   ("—", "—", "—"),
                "3:45–5:00":   ("Psychometrics & Competency Mapping", "Dr. Radha Sharma", "WB 5405"),
            },
        },
        "Friday (06 Mar)": {
            "MA": {
                "9:40–10:50":  ("Financial Management", "Dr. Rajbeer Kaur", "WB 5401"),
                "2:00–3:10":   ("HRM", "Dr. Monica Verma", "WB 5401"),
                "3:20–4:30":   ("Economic Environment of Business", "Dr. Charu Tayal", "WB 5401"),
            },
            "MB": {
                "9:40–10:50":  ("Research Methodology", "Dr. Elizabeth Jacob", "WB 5402"),
                "2:00–3:10":   ("HRM AI Integration Module", "Dr. Antarpreet Singh / Dr. Tanveer Shah", "WB 5402"),
                "3:20–4:30":   ("Sales & Distribution Management", "Dr. Swati Bhatnagar", "WB 5402"),
            },
            "MC": {
                "9:40–10:50":  ("Business to Business Marketing", "Prof. Angad Munshi", "WB 5403"),
                "2:00–3:10":   ("CSD-2", "Dr. Jyoti Kukreja / Angad Munshi", "WB 5403"),
                "3:20–4:30":   ("Digital Marketing Social Media", "Prof. Kunal Jha", "WB 5403"),
            },
            "MD": {
                "9:40–10:50":  ("Financial Management", "Dr. Sharif Mohd. / Dr. Nidhi Mathur", "WB 5501"),
                "2:00–3:10":   ("Sales & Distribution Management", "Dr. Swati Bhatnagar", "WB 5501"),
                "3:20–4:30":   ("Research Methodology", "Dr. Elizabeth Jacob", "WB 5501"),
            },
            "ME": {
                "9:40–10:50":  ("Economic Environment of Business", "Prof. Karan Khati", "WB 5502"),
                "2:00–3:10":   ("CSD-2", "Dr. Mahima Gulati", "WB 5502"),
                "3:20–4:30":   ("Sales & Distribution Management", "Dr. Gajendra Sharma", "WB 5502"),
            },
            "FA": {
                "9:40–10:50":  ("Mergers and Acquisitions", "Prof. Manav Vigg", "KB 301"),
                "2:00–3:10":   ("HRM", "Dr. Sunaina Sardana", "KB 301"),
                "3:20–4:30":   ("Economic Environment of Business", "Prof. Karan Khati", "KB 301"),
            },
            "FB": {
                "9:40–10:50":  ("Corporate Finance", "Dr. Silky Vigg", "KB 302"),
                "2:00–3:10":   ("Economic Environment of Business", "Prof. Karan Khati", "KB 302"),
                "3:20–4:30":   ("SAPM", "Dr. Som Nath Paul", "KB 302"),
            },
            "FC": {
                "9:40–10:50":  ("CSD-2", "Dr. Parul Malik", "KB 303"),
                "2:00–3:10":   ("Mergers and Acquisitions", "Prof. Manav Vigg", "KB 303"),
                "3:20–4:30":   ("Corporate Finance", "Dr. Nidhi Mathur", "KB 303"),
            },
            "FD": {
                "9:40–10:50":  ("Mergers and Acquisitions", "Dr. Geetika Batra", "KB 6500"),
                "2:00–3:10":   ("Corporate Finance", "Dr. Silky Vigg", "KB 6500"),
                "3:20–4:30":   ("CSD-2", "Dr. Mahima Gulati / Prof. Manav Vigg", "KB 6500"),
            },
            "HR": {
                "9:40–10:50":  ("Performance Management System", "Prof. Parveen Kaur", "WB 5405"),
                "2:00–3:10":   ("CSD-2", "Prof. Nikhil Singh", "WB 5405"),
                "3:20–4:30":   ("HRM", "Dr. Monica Verma", "WB 5405"),
            },
            # Major-2 Friday
            "AIML-A": {
                "11:00–12:10": ("Machine Learning using Python", "Dr. Shailee Choudhary", "WB 5401"),
                "12:20–1:30":  ("ML using Knime & Alteryx", "Dr. Nabeela Hasan", "WB 5401"),
            },
            "AIML-B": {
                "11:00–12:10": ("ML using Knime & Alteryx", "Dr. Nabeela Hasan", "WB 5402"),
                "12:20–1:30":  ("Data Engineering Using SQLite", "Dr. Rinku Dixit", "WB 5402"),
            },
            "AIML-C": {
                "11:00–12:10": ("Data Engineering Using SQLite", "Dr. Rinku Dixit", "WB 5403"),
                "12:20–1:30":  ("Machine Learning using Python", "Dr. Shailee Choudhary", "WB 5403"),
            },
            "MF": {
                "11:00–12:10": ("Strategic Brand Communication (IMC)", "Prof. Abha Grover", "KB 301"),
                "12:20–1:30":  ("Sales & Distribution Management", "Dr. Prabal Chakraborty", "KB 301"),
            },
            "MG": {
                "11:00–12:10": ("Sales & Distribution Management", "Dr. Gajendra Sharma", "KB 302"),
                "12:20–1:30":  ("Strategic Brand Communication (IMC)", "Prof. Abha Grover / Prof. Sarita Nagvanshi", "KB 302"),
            },
            "FE": {
                "11:00–12:10": ("SAPM", "Dr. Rajbeer Kaur", "WB 5405"),
                "12:20–1:30":  ("Principles of Banking", "Dr. Kavita Berwal / Prof. Rachna Kathuria", "WB 5405"),
            },
            "DM": {
                "11:00–12:10": ("Digital Marketing Analytics", "Prof. Sonal Gulati", "KB 102"),
                "12:20–1:30":  ("Strategic Social Media Marketing", "Prof. Sonal Gulati", "KB 102"),
            },
            "HR2": {
                "11:00–12:10": ("Performance Management System", "Prof. Parveen Kaur", "WB 5501"),
                "12:20–1:30":  ("Talent Acquisition", "Dr. Aaqib Danish", "WB 5501"),
            },
            "FAIM": {
                "11:00–12:10": ("Alternative Assets & Private Equity", "Dr. Geetika Batra", "WB 5502"),
                "12:20–1:30":  ("Foundation of Financial Data Science", "Dr. Pushpa Negi", "WB 5502"),
            },
            "OPR-A": {
                "11:00–12:10": ("Operations Research & Application", "Dr. MKP Naik", "KB 303"),
                "12:20–1:30":  ("Management of Service Operations", "Dr. Uday Sankar", "KB 303"),
            },
            "OPR-B": {
                "11:00–12:10": ("Management of Service Operations", "Dr. Uday Sankar", "KB 6500"),
                "12:20–1:30":  ("Operations Research & Application", "Dr. MKP Naik", "KB 6500"),
            },
        },
        "Saturday (07 Mar)": {
            "FE": {
                "9:40–10:55": ("FMS", "Dr. Haseen / Dr. Chand Tandon", "WB 5405"),
            },
            "MA": {
                "11:05–12:20": ("Basics of Project Management", "Dr. Ashish Yadav (2:20–4:20)", "WB 5501"),
                "12:30–1:45":  ("Basics of Project Management (contd.)", "Dr. Ashish Yadav", "WB 5501"),
                "2:20–3:35":   ("Research Methodology", "Dr. S S Khullar", "WB 5501"),
            },
            "MB": {
                "11:05–12:20": ("Digital Marketing Social Media", "Prof. Kunal Jha", "WB 5502"),
                "12:30–1:45":  ("Economic Environment of Business", "Dr. Charu Tayal", "WB 5502"),
                "2:20–3:35":   ("HRM", "Dr. Tanveer Shah", "WB 5502"),
            },
            "MC": {
                "11:05–12:20": ("Economic Environment of Business", "Dr. Zeeshan", "WB 5503"),
                "12:30–1:45":  ("Economic Environment of Business", "Dr. Zeeshan", "WB 5503"),
            },
            "MD": {
                "12:30–1:45":  ("CSD-2", "Dr. Jyoti Kukreja / Dr. Samriti Mahajan", "WB 5505"),
            },
            "ME": {
                "11:05–12:20": ("Research Methodology", "Dr. Anuj Nain", "WB 5601"),
                "12:30–1:45":  ("Digital Marketing Social Media", "Prof. Kunal Jha", "WB 5601"),
            },
            "FA": {
                "11:05–12:20": ("Aptitude", "Prof. Atul Rawat", "WB 5401"),
                "12:30–1:45":  ("—", "—", "—"),
            },
            "FB": {
                "11:05–12:20": ("Basics of Project Management", "Dr. MKP Naik (11:05–12:05)", "WB 5402"),
                "12:30–1:45":  ("Basics of Project Management (contd.)", "Dr. MKP Naik", "WB 5402"),
                "2:20–3:35":   ("Basics of Project Management", "Dr. Uday Sankar (2:20–4:20)", "WB 5402"),
            },
            "FC": {
                "11:05–12:20": ("Research Methodology", "Dr. Mohd. Azhar / Dr. Anuj Nain", "WB 5403"),
                "12:30–1:45":  ("Research Methodology", "Dr. Mohd. Azhar / Dr. Anuj Nain", "WB 5403"),
            },
            "FD": {
                "11:05–12:20": ("Economic Environment of Business", "Dr. Zeeshan", "WB 5405"),
                "12:30–1:45":  ("Aptitude", "Prof. Atul Rawat", "WB 5405"),
            },
        },
    }

    # ── Section selector ──────────────────────────────────────
    all_sections = sorted({
        sec
        for day_data in TT.values()
        for sec in day_data.keys()
        if sec != "ALL SECTIONS"
    })

    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        selected_section = st.selectbox("🔍 Filter by Section", ["All Sections"] + all_sections)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    days_order = ["Monday (02 Mar)", "Tuesday (03 Mar)", "Wednesday (04 Mar)",
                  "Thursday (05 Mar)", "Friday (06 Mar)", "Saturday (07 Mar)"]

    day_emoji = {
        "Monday (02 Mar)":    "📅",
        "Tuesday (03 Mar)":   "📅",
        "Wednesday (04 Mar)": "🎨",
        "Thursday (05 Mar)":  "📅",
        "Friday (06 Mar)":    "📅",
        "Saturday (07 Mar)":  "📅",
    }

    for day in days_order:
        day_data = TT.get(day, {})
        st.markdown(f"### {day_emoji[day]} {day}")

        if "ALL SECTIONS" in day_data:
            st.info("🎨 Holiday — Holi. No classes scheduled.")
            st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
            continue

        # Filter sections
        sections_to_show = (
            {k: v for k, v in day_data.items() if k == selected_section}
            if selected_section != "All Sections"
            else day_data
        )

        if not sections_to_show:
            st.caption(f"No data for **{selected_section}** on this day.")
            st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
            continue

        for section, slots in sections_to_show.items():
            with st.expander(f"📌 Section **{section}**", expanded=(selected_section != "All Sections")):
                rows = []
                for slot, (subj, prof, room) in slots.items():
                    rows.append({"Time Slot": slot, "Subject": subj, "Professor": prof, "Room": room})
                df_tt = pd.DataFrame(rows)
                st.dataframe(df_tt, use_container_width=True, hide_index=True)

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)


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
