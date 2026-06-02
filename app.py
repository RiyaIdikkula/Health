import streamlit as st
import sqlite3
import pandas as pd
import re
import requests
import json
from datetime import date

DB_NAME = "patients.db"

st.set_page_config(
    page_title="MediScan — Health Prediction",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

.stApp {
    background: #0a0f1e;
    color: #e2e8f0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #0a1628 100%);
    border-right: 1px solid rgba(56, 189, 248, 0.15);
}

[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 0.9rem;
    padding: 10px 16px;
    border-radius: 10px;
    transition: all 0.2s;
    cursor: pointer;
    display: block;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(56, 189, 248, 0.08);
    color: #38bdf8 !important;
}

/* ── Page Title ── */
.page-header {
    background: linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(99,102,241,0.08) 100%);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}

.page-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, transparent 70%);
    border-radius: 50%;
}

.page-header h1 {
    font-size: 1.9rem;
    font-weight: 700;
    color: #f0f9ff;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
}

.page-header p {
    color: #64748b;
    font-size: 0.9rem;
    margin: 0;
}

/* ── Metric Cards ── */
.metric-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 14px;
    padding: 24px;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(56,189,248,0.4);
}

.metric-card .value {
    font-size: 2.4rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #38bdf8, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 8px;
}

.metric-card .label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #475569;
    font-weight: 600;
}

.metric-card .icon {
    font-size: 1.8rem;
    margin-bottom: 10px;
    display: block;
}

/* ── Form Styling ── */
.stTextInput input, .stNumberInput input {
    background: #0f172a !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Sora', sans-serif !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s !important;
}

.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
}

.stTextInput label, .stNumberInput label, .stDateInput label, .stSelectbox label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    margin-bottom: 4px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 12px 28px !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(14,165,233,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(14,165,233,0.4) !important;
    background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
}

/* ── Alerts ── */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 12px !important;
    font-family: 'Sora', sans-serif !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border: 1px solid rgba(56,189,248,0.15) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #0f172a !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Form container ── */
.form-card {
    background: linear-gradient(135deg, #0f172a 0%, #1a2035 100%);
    border: 1px solid rgba(56,189,248,0.12);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
}

.section-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #38bdf8;
    font-weight: 600;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(56,189,248,0.15);
}

/* ── Patient info card ── */
.patient-info-card {
    background: rgba(56,189,248,0.06);
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.patient-info-card span {
    color: #94a3b8;
    font-size: 0.85rem;
}

.patient-info-card strong {
    color: #e2e8f0;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    text-align: center;
    padding: 20px 10px 28px;
    border-bottom: 1px solid rgba(56,189,248,0.1);
    margin-bottom: 20px;
}

.sidebar-brand h2 {
    font-size: 1.3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 8px 0 2px;
    letter-spacing: -0.3px;
}

.sidebar-brand p {
    font-size: 0.72rem;
    color: #334155;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── AI remark box ── */
.ai-remark {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(56,189,248,0.08));
    border: 1px solid rgba(99,102,241,0.3);
    border-left: 4px solid #6366f1;
    border-radius: 12px;
    padding: 18px 20px;
    margin-top: 16px;
}

.ai-remark .ai-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #818cf8;
    font-weight: 700;
    margin-bottom: 6px;
}

.ai-remark .ai-text {
    color: #c7d2fe;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* ── Delete danger zone ── */
.danger-zone {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 12px;
    padding: 18px 20px;
    margin-top: 12px;
}

.stButton.danger > button {
    background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
    box-shadow: 0 4px 15px rgba(220,38,38,0.25) !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #38bdf8 !important;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── DB Functions ─────────────────────────────────────────────────────────────
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_table():
    conn = get_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT,
        dob TEXT,
        email TEXT,
        glucose REAL,
        haemoglobin REAL,
        cholesterol REAL,
        remarks TEXT
    )
    """)
    conn.commit()
    conn.close()

def validate_email(email):
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def generate_prediction(glucose, haemoglobin, cholesterol):
    prompt = f"""
    Patient Vitals:
    - Glucose: {glucose}
    - Haemoglobin: {haemoglobin}
    - Cholesterol: {cholesterol}

    You are a health risk prediction model. Based on the input values for Glucose, Haemoglobin, and Cholesterol, predict the most likely health risk category.

    Output requirements:
    * Return only the predicted health risk and a short single-sentence remark.
    * Do not include explanations, reasoning, confidence scores, labels, formatting, bullet points, or introductory text.
    * Keep the remark brief and medically relevant.
    * If the values appear normal, indicate low or minimal health risk.
    * If the values suggest abnormalities, indicate the most likely health concern.

    Example output:
    Moderate Diabetes Risk - Elevated glucose levels suggest a potential risk of impaired blood sugar control.
    """
    try:
        url = "http://localhost:11434/api/generate"
        payload = {"model": "phi3", "prompt": prompt, "stream": False}
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()

        lines = [l.strip() for l in response.text.strip().splitlines() if l.strip()]
        full_response = ""
        for line in lines:
            try:
                chunk = json.loads(line)
                if "response" in chunk:
                    full_response += chunk["response"]
                if chunk.get("done"):
                    break
            except json.JSONDecodeError:
                continue
        return full_response.strip() or "No prediction returned."
    except requests.exceptions.ConnectionError:
        return "Prediction Failed - Could not connect to local Ollama server."
    except requests.exceptions.Timeout:
        return "Prediction Failed - Ollama server timed out."
    except Exception as e:
        return f"Prediction Failed - {str(e)}"


# ─── Init ─────────────────────────────────────────────────────────────────────
create_table()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size:2.2rem">🩺</div>
        <h2>MediScan</h2>
        <p>Health Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Navigation",
        ["📊  Dashboard", "➕  Add Patient", "📋  View Patients", "✏️  Update Patient", "🗑️  Delete Patient"],
        label_visibility="collapsed"
    )


# ─── Pages ────────────────────────────────────────────────────────────────────

# ── Dashboard ──
if "Dashboard" in menu:
    st.markdown("""
    <div class="page-header">
        <h1>📊 Health Overview</h1>
        <p>Real-time patient statistics and risk summary</p>
    </div>
    """, unsafe_allow_html=True)

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()

    total = len(df)
    high_risk = len(df[df["remarks"].str.contains("risk", case=False, na=False)]) if total else 0
    normal = total - high_risk

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="icon">👥</span>
            <div class="value">{total}</div>
            <div class="label">Total Patients</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <span class="icon">⚠️</span>
            <div class="value">{high_risk}</div>
            <div class="label">At Risk</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <span class="icon">✅</span>
            <div class="value">{normal}</div>
            <div class="label">Normal</div>
        </div>
        """, unsafe_allow_html=True)

    if not df.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Recent Records</div>', unsafe_allow_html=True)
        st.dataframe(
            df.tail(5)[["id", "fullname", "dob", "glucose", "haemoglobin", "cholesterol", "remarks"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color: #334155;">
            <div style="font-size:3rem">🏥</div>
            <p style="font-size:1rem; margin-top:12px;">No patients yet. Add your first patient to get started.</p>
        </div>
        """, unsafe_allow_html=True)


# ── Add Patient ──
elif "Add" in menu:
    st.markdown("""
    <div class="page-header">
        <h1>➕ Add New Patient</h1>
        <p>Enter patient details and generate an AI health prediction</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("patient_form"):
        st.markdown('<div class="section-label">Personal Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            fullname = st.text_input("Full Name", placeholder="e.g. Arjun Menon")
        with col2:
            email = st.text_input("Email Address", placeholder="arjun@example.com")

        dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">📈 Vitals & Lab Values</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            glucose = st.number_input("Glucose (mg/dL)", min_value=0.0, step=0.1,
                                      help="Normal fasting: 70–100 mg/dL")
        with col2:
            haemoglobin = st.number_input("Haemoglobin (g/dL)", min_value=0.0, step=0.1,
                                          help="Normal: Men 13.5–17.5, Women 12–15.5 g/dL")
        with col3:
            cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=0.0, step=0.1,
                                          help="Desirable: < 200 mg/dL")

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🔬 Generate Prediction & Save", use_container_width=True)

        if submit:
            if not fullname.strip():
                st.error("⚠️ Please enter the patient's full name.")
            elif not validate_email(email):
                st.error("⚠️ Please enter a valid email address.")
            elif dob > date.today():
                st.error("⚠️ Date of birth cannot be in the future.")
            else:
                with st.spinner("🤖 Analysing vitals ..."):
                    remarks = generate_prediction(glucose, haemoglobin, cholesterol)

                conn = get_connection()
                conn.execute(
                    "INSERT INTO patients (fullname, dob, email, glucose, haemoglobin, cholesterol, remarks) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (fullname, str(dob), email, glucose, haemoglobin, cholesterol, remarks)
                )
                conn.commit()
                conn.close()

                st.success(f"✅ Patient **{fullname}** saved successfully!")
                st.markdown(f"""
                <div class="ai-remark">
                    <div class="ai-label">🤖 AI Remarks </div>
                    <div class="ai-text">{remarks}</div>
                </div>
                """, unsafe_allow_html=True)


# ── View Patients ──
elif "View" in menu:
    st.markdown("""
    <div class="page-header">
        <h1>📋 Patient Records</h1>
        <p>Browse, search, and export all patient data</p>
    </div>
    """, unsafe_allow_html=True)

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()

    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍  Search by name", placeholder="Type a patient name...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if not df.empty:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export CSV", csv, "patients.csv", "text/csv", use_container_width=True)

    if search:
        df = df[df["fullname"].str.contains(search, case=False, na=False)]

    if df.empty:
        st.markdown("""
        <div style="text-align:center; padding: 50px; color: #334155;">
            <div style="font-size:2.5rem">🔍</div>
            <p style="margin-top:10px;">No matching patients found.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color:#475569; font-size:0.82rem; margin-bottom:10px;">Showing <strong style="color:#38bdf8;">{len(df)}</strong> patient(s)</p>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Update Patient ──
elif "Update" in menu:
    st.markdown("""
    <div class="page-header">
        <h1>✏️ Update Patient</h1>
        <p>Edit patient details and regenerate health prediction</p>
    </div>
    """, unsafe_allow_html=True)

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients", conn)

    if df.empty:
        st.warning("No patients available to update.")
    else:
        patient_options = {f"ID {row['id']} — {row['fullname']}": row['id'] for _, row in df.iterrows()}
        selected_label = st.selectbox("Select Patient", list(patient_options.keys()))
        pid = patient_options[selected_label]
        patient = df[df["id"] == pid].iloc[0]

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Edit Details</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fullname = st.text_input("Full Name", value=patient["fullname"])
        with col2:
            email = st.text_input("Email", value=patient["email"])

        col1, col2, col3 = st.columns(3)
        with col1:
            glucose = st.number_input("Glucose (mg/dL)", value=float(patient["glucose"]), step=0.1)
        with col2:
            haemoglobin = st.number_input("Haemoglobin (g/dL)", value=float(patient["haemoglobin"]), step=0.1)
        with col3:
            cholesterol = st.number_input("Cholesterol (mg/dL)", value=float(patient["cholesterol"]), step=0.1)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Changes & Re-predict", use_container_width=True):
            with st.spinner(" "):
                remarks = generate_prediction(glucose, haemoglobin, cholesterol)

            conn.execute(
                "UPDATE patients SET fullname=?, email=?, glucose=?, haemoglobin=?, cholesterol=?, remarks=? WHERE id=?",
                (fullname, email, glucose, haemoglobin, cholesterol, remarks, int(pid))
            )
            conn.commit()
            st.success(f"✅ Patient **{fullname}** updated successfully!")
            st.markdown(f"""
            <div class="ai-remark">
                <div class="ai-label">🤖 Updated AI Prediction</div>
                <div class="ai-text">{remarks}</div>
            </div>
            """, unsafe_allow_html=True)
            st.rerun()

    conn.close()


# ── Delete Patient ──
elif "Delete" in menu:
    st.markdown("""
    <div class="page-header">
        <h1>🗑️ Delete Patient</h1>
        <p>Permanently remove a patient record from the system</p>
    </div>
    """, unsafe_allow_html=True)

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients", conn)

    if df.empty:
        st.warning("No patients available to delete.")
    else:
        patient_options = {f"ID {row['id']} — {row['fullname']}": row['id'] for _, row in df.iterrows()}
        selected_label = st.selectbox("Select Patient to Delete", list(patient_options.keys()))
        pid = patient_options[selected_label]
        patient = df[df["id"] == pid].iloc[0]

        # Patient preview card
        st.markdown(f"""
        <div class="patient-info-card">
            <div><span>👤 Name</span><br><strong>{patient['fullname']}</strong></div>
            <div><span>📧 Email</span><br><strong>{patient['email']}</strong></div>
            <div><span>🎂 DOB</span><br><strong>{patient['dob']}</strong></div>
            <div><span>🩸 Glucose</span><br><strong>{patient['glucose']} mg/dL</strong></div>
            <div><span>🔬 Haemoglobin</span><br><strong>{patient['haemoglobin']} g/dL</strong></div>
            <div><span>💊 Cholesterol</span><br><strong>{patient['cholesterol']} mg/dL</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="danger-zone">
            <p style="color:#fca5a5; font-size:0.85rem; margin:0 0 12px;">
                ⚠️ This action is <strong>permanent</strong> and cannot be undone.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🗑️ Delete {patient['fullname']}", use_container_width=True):
            conn.execute("DELETE FROM patients WHERE id=?", (int(pid),))
            conn.commit()
            st.success(f"✅ Patient **{patient['fullname']}** (ID {pid}) has been deleted.")
            st.rerun()

    conn.close()