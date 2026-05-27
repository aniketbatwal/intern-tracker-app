import calendar
import hashlib
import os
import secrets
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta

import psycopg2
import psycopg2.extras
import psycopg2.errors
import pytz
import streamlit as st
import extra_streamlit_components as stx

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

DATABASE_URL = os.getenv("DATABASE_URL", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "intern-uploads")

SUPERVISOR_ACCOUNTS = [
    {
        "username": "admin",
        "password": "SuperSecureAdmin2026",
        "role": "supervisor",
        "full_name": "Master Supervisor",
        "timezone": "UTC",
    },
    {
        "username": "aniket.batwal@sphereglobal.com",
        "password": "Pass@123",
        "role": "supervisor",
        "full_name": "Aniket Batwal",
        "timezone": "Asia/Kolkata",
    },
]

TIMEZONE_OPTIONS = [
    "UTC",
    "Europe/London",
    "Asia/Kolkata",
    "America/New_York",
    "America/Los_Angeles",
    "Asia/Dubai",
    "Asia/Singapore",
]

st.set_page_config(
    page_title="BA Intern Tracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────── STYLES ────────────────────────────

def inject_styles() -> None:
    st.markdown(
        """<div style="position:fixed;height:0;width:0;overflow:hidden;opacity:0;pointer-events:none;z-index:-1;">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Base ── */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }
        .stApp { background: #F0F4F8 !important; }

        /* ── Remove ALL Streamlit top spacing ── */
        header[data-testid="stHeader"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stToolbar"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
        }
        [data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        [data-testid="stMain"],
        section.main {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            margin-top: 0 !important;
            max-width: 1320px !important;
        }
        #MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
        [data-testid="collapsedControl"] svg { fill: #4B5563 !important; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: #111827 !important;
            border-right: 1px solid rgba(255,255,255,0.04) !important;
        }
        [data-testid="stSidebar"] * { color: #F9FAFB !important; }
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            color: #F9FAFB !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            width: 100% !important;
            box-shadow: none !important;
            height: 38px !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.11) !important;
            box-shadow: none !important;
        }

        /* ── Primary buttons ── */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            background: #2563EB !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            height: 40px !important;
            padding: 0 1.25rem !important;
            letter-spacing: 0 !important;
            transition: background 0.15s ease, box-shadow 0.15s ease !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.08) !important;
        }
        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            background: #1D4ED8 !important;
            box-shadow: 0 4px 14px rgba(37,99,235,0.28) !important;
        }

        /* ── Secondary buttons ── */
        button[kind="secondary"] {
            background: #FFFFFF !important;
            color: #374151 !important;
            border: 1.5px solid #D1D5DB !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        }
        button[kind="secondary"]:hover {
            background: #F9FAFB !important;
            border-color: #9CA3AF !important;
            color: #111827 !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
        }

        /* ── Inputs ── */
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] > div,
        div[data-baseweb="textarea"] > div {
            background: #FFFFFF !important;
            border: 1.5px solid #D1D5DB !important;
            border-radius: 8px !important;
            transition: border-color 0.15s, box-shadow 0.15s !important;
        }
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="base-input"] > div:focus-within {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
        }
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input,
        textarea {
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            font-size: 0.9rem !important;
        }
        div[data-baseweb="input"] input::placeholder,
        textarea::placeholder {
            color: #9CA3AF !important;
            -webkit-text-fill-color: #9CA3AF !important;
            opacity: 1 !important;
        }
        div[data-baseweb="select"] > div {
            background: #FFFFFF !important;
            border: 1.5px solid #D1D5DB !important;
            border-radius: 8px !important;
        }
        div[data-baseweb="select"] * { color: #111827 !important; }
        div[data-baseweb="select"] svg,
        div[data-baseweb="input"] svg { fill: #6B7280 !important; }

        /* ── Labels ── */
        label,
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label {
            color: #374151 !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            background: #E2E8F0 !important;
            border-radius: 10px !important;
            padding: 3px !important;
            gap: 2px !important;
            border: none !important;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 7px !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            color: #6B7280 !important;
            height: 38px !important;
            padding: 0 1.1rem !important;
            background: transparent !important;
        }
        .stTabs [aria-selected="true"] {
            background: #FFFFFF !important;
            color: #111827 !important;
            font-weight: 600 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06) !important;
        }

        /* ── DataFrame ── */
        div[data-testid="stDataFrame"] {
            border-radius: 10px !important;
            overflow: hidden !important;
            border: 1px solid #E5E7EB !important;
        }

        /* ── Form container ── */
        [data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }

        /* ── Alerts ── */
        div[data-testid="stAlert"] { border-radius: 10px !important; }

        /* ── Bordered containers (st.container border=True) ── */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #E5E7EB !important;
            border-radius: 14px !important;
            background: #FFFFFF !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08) !important;
        }

        /* ── Login (LinkedIn-style) ── */
        .ln-brand-row {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 2rem 0 1.25rem;
            gap: 0.5rem;
        }
        .ln-logo-mark {
            width: 52px;
            height: 52px;
            background: #2563EB;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.5px;
        }
        .ln-brand-name {
            font-size: 1rem;
            font-weight: 700;
            color: #374151;
        }
        .ln-card-head {
            padding: 0.25rem 0 0.75rem;
        }
        .ln-heading {
            font-size: 1.55rem;
            font-weight: 800;
            color: #111827;
            letter-spacing: -0.03em;
            margin-bottom: 0.3rem;
            line-height: 1.2;
        }
        .ln-sub {
            font-size: 0.875rem;
            color: #6B7280;
            line-height: 1.5;
        }
        .ln-footer {
            text-align: center;
            font-size: 0.75rem;
            color: #B0B8C4;
            margin-top: 1.25rem;
            padding-bottom: 2rem;
        }

        /* ── Page header ── */
        .page-header {
            margin-bottom: 1.5rem;
            padding-bottom: 1.25rem;
            border-bottom: 1px solid #E5E7EB;
        }
        .page-eyebrow {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #2563EB;
            margin-bottom: 0.3rem;
        }
        .page-title {
            font-size: clamp(1.35rem, 1.8vw, 1.7rem);
            font-weight: 800;
            color: #111827;
            letter-spacing: -0.03em;
            margin: 0 0 0.35rem;
            line-height: 1.2;
        }
        .page-desc {
            font-size: 0.875rem;
            color: #6B7280;
            line-height: 1.55;
            max-width: 640px;
            margin: 0;
        }

        /* ── Stat cards ── */
        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            height: 100%;
            transition: box-shadow 0.2s;
        }
        .stat-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
        .stat-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-bottom: 1rem;
        }
        .dot-blue   { background: #2563EB; }
        .dot-violet { background: #7C3AED; }
        .dot-green  { background: #059669; }
        .dot-amber  { background: #D97706; }
        .stat-value {
            font-size: 2rem;
            font-weight: 800;
            color: #111827;
            letter-spacing: -0.04em;
            line-height: 1;
            margin-bottom: 0.3rem;
        }
        .stat-label {
            font-size: 0.875rem;
            font-weight: 600;
            color: #374151;
        }
        .stat-note {
            font-size: 0.78rem;
            color: #9CA3AF;
            margin-top: 0.15rem;
        }

        /* ── Section header ── */
        .s-head { margin-bottom: 0.75rem; padding-top: 0.25rem; }
        .s-title { font-size: 0.95rem; font-weight: 700; color: #111827; margin-bottom: 0.2rem; }
        .s-desc  { font-size: 0.8rem; color: #9CA3AF; }

        /* ── Clock status ── */
        .clock-status {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.9rem 1rem;
            border-radius: 10px;
            border: 1.5px solid;
            margin-bottom: 0.9rem;
        }
        .cs-in  { background: #ECFDF5; border-color: #6EE7B7; }
        .cs-out { background: #F9FAFB; border-color: #E5E7EB; }
        .cs-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50%       { opacity: 0.35; }
        }
        .cs-dot-in  { background: #10B981; animation: pulse-dot 2s infinite; }
        .cs-dot-out { background: #9CA3AF; }
        .cs-label     { font-size: 0.78rem; font-weight: 500; color: #6B7280; }
        .cs-value-in  { font-size: 0.95rem; font-weight: 700; color: #065F46; }
        .cs-value-out { font-size: 0.95rem; font-weight: 700; color: #374151; }

        /* ── Review items ── */
        .review-item {
            background: #F9FAFB;
            border: 1px solid #F3F4F6;
            border-radius: 12px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.625rem;
        }
        .review-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: #EFF6FF;
            color: #1D4ED8;
            margin-bottom: 0.4rem;
        }
        .review-title { font-size: 0.9rem; font-weight: 600; color: #111827; margin-bottom: 0.15rem; }
        .review-meta  { font-size: 0.78rem; color: #9CA3AF; margin-bottom: 0.4rem; }
        .review-desc  { font-size: 0.85rem; color: #374151; line-height: 1.5; margin-bottom: 0.5rem; }
        .review-link  { font-size: 0.8rem; color: #2563EB; word-break: break-all; }

        /* ── Sidebar ── */
        .sb-brand {
            padding: 1.5rem 1.25rem 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 0.25rem;
        }
        .sb-logo-row { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.4rem; }
        .sb-logo-mark {
            width: 30px; height: 30px;
            background: #2563EB;
            border-radius: 7px;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.72rem; font-weight: 800; color: #FFFFFF;
        }
        .sb-app-name { font-size: 0.9rem; font-weight: 700; color: #F9FAFB; }
        .sb-sub      { font-size: 0.75rem; color: rgba(249,250,251,0.32); }
        .sb-user {
            padding: 0.875rem 1.25rem;
            display: flex; align-items: center; gap: 0.75rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 1rem;
        }
        .sb-avatar {
            width: 32px; height: 32px;
            border-radius: 50%;
            background: #1D4ED8;
            border: 2px solid rgba(255,255,255,0.14);
            display: flex; align-items: center; justify-content: center;
            font-size: 0.72rem; font-weight: 700; color: #FFFFFF;
            flex-shrink: 0;
        }
        .sb-user-name { font-size: 0.86rem; font-weight: 600; color: #F9FAFB; }
        .sb-user-role { font-size: 0.75rem; color: rgba(249,250,251,0.38); text-transform: capitalize; }
        .sb-footer    { padding: 0 1.25rem 1.5rem; }

        /* ── Attendance Calendar ── */
        .cal-wrapper {
            padding: 0.5rem 0;
        }
        .cal-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        .cal-month-label {
            font-size: 1rem;
            font-weight: 700;
            color: #111827;
        }
        .cal-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
        }
        .cal-day-header {
            text-align: center;
            font-size: 0.72rem;
            font-weight: 700;
            color: #9CA3AF;
            padding: 4px 0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .cal-day {
            border-radius: 8px;
            padding: 6px 4px;
            text-align: center;
            font-size: 0.82rem;
            font-weight: 500;
            color: #374151;
            min-height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .cal-day-empty {
            background: transparent;
        }
        .cal-day-present {
            background: #ECFDF5;
            color: #065F46;
            font-weight: 600;
        }
        .cal-day-absent {
            background: #FEF2F2;
            color: #991B1B;
        }
        .cal-day-holiday {
            background: #EFF6FF;
            color: #1D4ED8;
            font-weight: 600;
        }
        .cal-day-weekend {
            background: #F9FAFB;
            color: #9CA3AF;
        }
        .cal-day-future {
            background: #FFFFFF;
            color: #D1D5DB;
        }
        .cal-day-today {
            outline: 2px solid #2563EB;
            outline-offset: -2px;
        }
        .cal-legend {
            display: flex;
            gap: 1rem;
            margin-top: 0.75rem;
            flex-wrap: wrap;
        }
        .cal-legend-item {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.78rem;
            color: #6B7280;
        }
        .cal-legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        .legend-present  { background: #10B981; }
        .legend-absent   { background: #EF4444; }
        .legend-holiday  { background: #3B82F6; }
        .legend-weekend  { background: #D1D5DB; }

        /* ── Holiday list ── */
        .holiday-item {
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 10px;
            padding: 0.6rem 0.9rem;
            margin-bottom: 0.4rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .holiday-title {
            font-size: 0.88rem;
            font-weight: 600;
            color: #1D4ED8;
        }
        .holiday-date {
            font-size: 0.78rem;
            color: #6B7280;
        }

        @media (max-width: 768px) {
            .ln-brand-row { padding: 1rem 0 0.75rem; }
            .block-container,
            [data-testid="stMainBlockContainer"] { padding: 1rem 0.75rem 2rem !important; }
        }
        </style></div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────── ENV CHECK ──────────────────────────

def check_env() -> None:
    if not DATABASE_URL:
        st.error(
            "DATABASE_URL environment variable is not set. "
            "Please configure a PostgreSQL connection string."
        )
        st.stop()


# ─────────────────────────── DATABASE ───────────────────────────

@contextmanager
def get_connection():
    """
    Open a fresh connection per request via Supabase's Transaction Pooler.
    Supabase's pooler (port 6543) already manages warm PostgreSQL connections
    on its side, so each connect() here is just a fast handshake to the pooler.
    Keeping our own local pool caused stale-SSL errors when idle connections
    were silently closed by the cloud provider.
    """
    conn = None
    last_err: Exception | None = None
    for attempt in range(2):
        try:
            conn = psycopg2.connect(
                DATABASE_URL,
                cursor_factory=psycopg2.extras.RealDictCursor,
                connect_timeout=10,
            )
            break
        except Exception as exc:
            last_err = exc
    if conn is None:
        raise last_err  # type: ignore[misc]
    try:
        yield conn
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'UTC'"
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                date TEXT NOT NULL,
                clock_in TEXT,
                clock_out TEXT,
                status TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                assigned_to TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                link TEXT,
                status TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                token TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                filename TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                file_url TEXT NOT NULL,
                uploaded_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS holidays (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                holiday_date TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        for account in SUPERVISOR_ACCOUNTS:
            cursor.execute("SELECT id FROM users WHERE username=%s", (account["username"],))
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "UPDATE users SET password=%s, role=%s, full_name=%s, timezone=%s WHERE username=%s",
                    (
                        hash_password(account["password"]),
                        account["role"],
                        account["full_name"],
                        account["timezone"],
                        account["username"],
                    ),
                )
            else:
                cursor.execute(
                    "INSERT INTO users (username, password, role, full_name, timezone) VALUES (%s, %s, %s, %s, %s)",
                    (
                        account["username"],
                        hash_password(account["password"]),
                        account["role"],
                        account["full_name"],
                        account["timezone"],
                    ),
                )

        conn.commit()


# ─────────────────────────── TIME HELPERS ───────────────────────

def utc_date_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def utc_timestamp_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")


def format_ts_local(ts_str: str, tz_name: str) -> str:
    if not ts_str:
        return ""
    try:
        if ts_str.endswith("+00:00"):
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=timezone.utc)
        else:
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        local_tz = pytz.timezone(tz_name or "UTC")
        local_dt = dt.astimezone(local_tz)
        return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return ts_str


# ─────────────────────────── SESSION / AUTH ─────────────────────

def init_session_state() -> None:
    defaults = {
        "authenticated": False,
        "username": "",
        "role": "",
        "full_name": "",
        "timezone": "UTC",
        "session_token": "",
        "cal_year": datetime.now(timezone.utc).year,
        "cal_month": datetime.now(timezone.utc).month,
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)


def create_session(username: str) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (token, username, expires_at) VALUES (%s, %s, %s)",
            (token, username, expires_at),
        )
        conn.commit()
    return token


def validate_session(token: str):
    if not token:
        return None
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username FROM sessions WHERE token=%s AND expires_at > NOW()",
            (token,),
        )
        row = cursor.fetchone()
    return row["username"] if row else None


def delete_session(token: str) -> None:
    if not token:
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token=%s", (token,))
        conn.commit()


def login_user(username: str, password: str, cm) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, role, full_name, timezone FROM users WHERE username=%s AND password=%s",
            (username.strip(), hash_password(password)),
        )
        user = cursor.fetchone()
    if not user:
        return False
    st.session_state.authenticated = True
    st.session_state.username = user["username"]
    st.session_state.role = user["role"]
    st.session_state.full_name = user["full_name"]
    st.session_state.timezone = user["timezone"] or "UTC"
    token = create_session(user["username"])
    st.session_state.session_token = token
    try:
        cm.set("bt_session", token, expires_at=datetime.now(timezone.utc) + timedelta(days=30))
    except Exception:
        pass
    return True


def restore_session_from_cookie(cm) -> None:
    try:
        token = cm.get("bt_session")
        if not token:
            return
        username = validate_session(token)
        if not username:
            return
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, role, full_name, timezone FROM users WHERE username=%s",
                (username,),
            )
            user = cursor.fetchone()
        if not user:
            return
        st.session_state.authenticated = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]
        st.session_state.full_name = user["full_name"]
        st.session_state.timezone = user["timezone"] or "UTC"
        st.session_state.session_token = token
    except Exception:
        pass


def logout_user(cm) -> None:
    token = st.session_state.get("session_token", "")
    if token:
        delete_session(token)
    try:
        cm.delete("bt_session")
    except Exception:
        pass
    for key in ("authenticated", "username", "role", "full_name", "timezone", "session_token"):
        st.session_state[key] = False if key == "authenticated" else ""
    st.rerun()


# ─────────────────────────── DATA: USERS ────────────────────────

def create_intern(username: str, password: str, full_name: str, tz: str = "UTC") -> tuple[bool, str]:
    username = username.strip()
    full_name = full_name.strip()
    if not username or not password or not full_name:
        return False, "All fields are required."
    reserved = {a["username"].lower() for a in SUPERVISOR_ACCOUNTS}
    if username.lower() in reserved:
        return False, "That username is reserved for a supervisor account."
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role, full_name, timezone) VALUES (%s, %s, %s, %s, %s)",
                (username, hash_password(password), "intern", full_name, tz),
            )
            conn.commit()
        return True, f"Intern account '{username}' created successfully."
    except psycopg2.errors.UniqueViolation:
        return False, "That username already exists."


def reset_intern_password(username: str, new_password: str) -> tuple[bool, str]:
    if not username or not new_password:
        return False, "Username and new password are required."
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=%s", (username.strip(),))
        user = cursor.fetchone()
        if not user:
            return False, "Intern account not found."
        if user["role"] != "intern":
            return False, "Only intern passwords can be changed here."
        cursor.execute(
            "UPDATE users SET password=%s WHERE username=%s",
            (hash_password(new_password), username.strip()),
        )
        conn.commit()
    return True, f"Password updated for '{username.strip()}'."


def list_interns() -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, full_name, timezone FROM users WHERE role='intern' ORDER BY full_name"
        )
        return list(cursor.fetchall())


def get_intern_timezone(username: str) -> str:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT timezone FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
    return row["timezone"] if row and row["timezone"] else "UTC"


# ─────────────────────────── DATA: ATTENDANCE ───────────────────

def get_open_attendance_record(username: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM attendance WHERE username=%s AND clock_out IS NULL ORDER BY id DESC LIMIT 1",
            (username,),
        )
        return cursor.fetchone()


def clock_in(username: str) -> tuple[bool, str]:
    if get_open_attendance_record(username):
        return False, "You are already clocked in."
    now_ts = utc_timestamp_string()
    now_date = utc_date_string()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attendance (username, date, clock_in, clock_out, status) VALUES (%s, %s, %s, %s, %s)",
            (username, now_date, now_ts, None, "Clocked In"),
        )
        conn.commit()
    return True, "Clock-in recorded successfully."


def clock_out(username: str) -> tuple[bool, str]:
    open_record = get_open_attendance_record(username)
    if not open_record:
        return False, "No active clock-in found."
    ci_str = open_record["clock_in"]
    try:
        if ci_str.endswith("+00:00"):
            clock_in_dt = datetime.strptime(ci_str, "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=timezone.utc)
        else:
            clock_in_dt = datetime.strptime(ci_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        clock_in_dt = datetime.now(timezone.utc)
    clock_out_ts = utc_timestamp_string()
    clock_out_dt = datetime.now(timezone.utc)
    elapsed = clock_out_dt - clock_in_dt
    total_seconds = int(elapsed.total_seconds())
    hours, remainder = divmod(max(total_seconds, 0), 3600)
    minutes, _ = divmod(remainder, 60)
    status = f"Completed ({hours}h {minutes}m)"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE attendance SET clock_out=%s, status=%s WHERE id=%s",
            (clock_out_ts, status, open_record["id"]),
        )
        conn.commit()
    return True, f"Clock-out recorded. Session: {hours}h {minutes}m."


def get_today_attendance() -> list[dict]:
    today = utc_date_string()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, date, clock_in, clock_out, status FROM attendance WHERE date=%s ORDER BY clock_in DESC",
            (today,),
        )
        return list(cursor.fetchall())


def get_user_attendance_history(username: str) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, clock_in, clock_out, status FROM attendance WHERE username=%s ORDER BY date DESC, id DESC",
            (username,),
        )
        return list(cursor.fetchall())


def get_all_attendance_dates(username: str) -> set:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date FROM attendance WHERE username=%s AND clock_in IS NOT NULL",
            (username,),
        )
        rows = cursor.fetchall()
    return {row["date"] for row in rows}


# ─────────────────────────── DATA: TASKS ────────────────────────

def create_task(assigned_to: str, title: str, description: str) -> tuple[bool, str]:
    if not assigned_to or not title.strip():
        return False, "Assigned intern and task title are required."
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (assigned_to, title, description, link, status) VALUES (%s, %s, %s, %s, %s)",
            (assigned_to, title.strip(), description.strip(), "", "Assigned"),
        )
        conn.commit()
    return True, f"Task '{title.strip()}' dispatched to {assigned_to}."


def submit_task_link(task_id: int, username: str, link: str) -> tuple[bool, str]:
    link = link.strip()
    if not link:
        return False, "Please enter a valid artifact URL."
    if not (link.startswith("http://") or link.startswith("https://")):
        return False, "Artifact URL must start with http:// or https://"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET link=%s, status=%s WHERE id=%s AND assigned_to=%s",
            (link, "Pending Review", task_id, username),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Task not found or not assigned to you."
    return True, "Assignment link submitted successfully."


def review_task(task_id: int, new_status: str, reviewer_username: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=%s", (reviewer_username,))
        user = cursor.fetchone()
        if not user or user["role"] != "supervisor":
            return
        cursor.execute("UPDATE tasks SET status=%s WHERE id=%s", (new_status, task_id))
        conn.commit()


def get_tasks_for_user(username: str) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, link, status FROM tasks WHERE assigned_to=%s ORDER BY id DESC",
            (username,),
        )
        return list(cursor.fetchall())


def get_pending_reviews() -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, assigned_to, title, description, link, status FROM tasks WHERE status='Pending Review' ORDER BY id DESC"
        )
        return list(cursor.fetchall())


def get_supervisor_metrics() -> dict:
    today_logs = get_today_attendance()
    pending_reviews = get_pending_reviews()
    interns = list_interns()
    active_clocked_in = sum(1 for r in today_logs if r["clock_out"] is None)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM tasks WHERE status='Assigned'")
        row = cursor.fetchone()
        assigned_tasks = row["count"] if row else 0
    return {
        "intern_count": len(interns),
        "today_logs": len(today_logs),
        "active_clocked_in": active_clocked_in,
        "pending_reviews": len(pending_reviews),
        "assigned_tasks": assigned_tasks,
    }


# ─────────────────────────── DATA: HOLIDAYS ─────────────────────

def add_holiday(title: str, holiday_date: str, created_by: str) -> tuple[bool, str]:
    if not title.strip() or not holiday_date:
        return False, "Title and date are required."
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO holidays (title, holiday_date, created_by, created_at) VALUES (%s, %s, %s, %s)",
            (title.strip(), str(holiday_date), created_by, utc_timestamp_string()),
        )
        conn.commit()
    return True, f"Holiday '{title.strip()}' added."


def delete_holiday(holiday_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM holidays WHERE id=%s", (holiday_id,))
        conn.commit()


def get_upcoming_holidays() -> list[dict]:
    today = utc_date_string()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, holiday_date, created_by FROM holidays WHERE holiday_date >= %s ORDER BY holiday_date ASC",
            (today,),
        )
        return list(cursor.fetchall())


def get_all_holidays() -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, holiday_date, created_by, created_at FROM holidays ORDER BY holiday_date DESC"
        )
        return list(cursor.fetchall())


# ─────────────────────────── DATA: UPLOADS ──────────────────────

@st.cache_resource
def get_supabase_client():
    if not SUPABASE_AVAILABLE:
        return None
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception:
        return None


def upload_file_to_storage(uploaded_file, username: str) -> tuple[bool, str, str]:
    supabase = get_supabase_client()
    if supabase is None:
        return False, "Supabase storage is not configured.", ""
    try:
        file_bytes = uploaded_file.read()
        storage_path = f"{username}/{utc_date_string()}_{uploaded_file.name}"
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            storage_path,
            file_bytes,
            {"content-type": uploaded_file.type or "application/octet-stream"},
        )
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO uploads (username, filename, storage_path, file_url, uploaded_at) VALUES (%s, %s, %s, %s, %s)",
                (username, uploaded_file.name, storage_path, public_url, utc_timestamp_string()),
            )
            conn.commit()
        return True, f"'{uploaded_file.name}' uploaded successfully.", public_url
    except Exception as e:
        return False, f"Upload failed: {e}", ""


def get_uploads_for_user(username: str) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, filename, file_url, uploaded_at FROM uploads WHERE username=%s ORDER BY id DESC",
            (username,),
        )
        return list(cursor.fetchall())


def get_all_uploads() -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, filename, file_url, uploaded_at FROM uploads ORDER BY id DESC"
        )
        return list(cursor.fetchall())


# ─────────────────────────── UI PRIMITIVES ──────────────────────

def render_login(cm) -> None:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown(
            """
            <div class="ln-brand-row">
                <div class="ln-logo-mark">BA</div>
                <div class="ln-brand-name">Intern Tracker</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.markdown(
                """
                <div class="ln-card-head">
                    <div class="ln-heading">Sign in</div>
                    <div class="ln-sub">Access your operations workspace.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Email or username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign in", use_container_width=True)
        if submitted:
            if login_user(username, password, cm):
                st.success("Signed in. Loading your workspace…")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
        st.markdown(
            '<p class="ln-footer">© 2025 Sphere Global &middot; BA Intern Tracker</p>',
            unsafe_allow_html=True,
        )


def render_sidebar(cm) -> None:
    with st.sidebar:
        name = st.session_state.full_name
        initials = "".join(p[0].upper() for p in name.split()[:2])
        role = st.session_state.role.capitalize()
        st.markdown(
            f"""
            <div class="sb-brand">
                <div class="sb-logo-row">
                    <div class="sb-logo-mark">BA</div>
                    <div class="sb-app-name">Intern Tracker</div>
                </div>
                <div class="sb-sub">Operations &amp; Attendance Portal</div>
            </div>
            <div class="sb-user">
                <div class="sb-avatar">{initials}</div>
                <div>
                    <div class="sb-user-name">{name}</div>
                    <div class="sb-user-role">{role}</div>
                </div>
            </div>
            <div class="sb-footer">
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign out", use_container_width=True):
            logout_user(cm)
        st.markdown("</div>", unsafe_allow_html=True)


def render_page_header(eyebrow: str, title: str, desc: str) -> None:
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-eyebrow">{eyebrow}</div>
            <h1 class="page-title">{title}</h1>
            <p class="page-desc">{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(stats: list[dict]) -> None:
    cols = st.columns(len(stats))
    for col, s in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-dot {s['dot']}"></div>
                    <div class="stat-value">{s['value']}</div>
                    <div class="stat-label">{s['label']}</div>
                    <div class="stat-note">{s['note']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_section_header(title: str, desc: str) -> None:
    st.markdown(
        f'<div class="s-head"><div class="s-title">{title}</div><div class="s-desc">{desc}</div></div>',
        unsafe_allow_html=True,
    )


def render_clock_status(is_clocked_in: bool) -> None:
    if is_clocked_in:
        st.markdown(
            """
            <div class="clock-status cs-in">
                <div class="cs-dot cs-dot-in"></div>
                <div>
                    <div class="cs-label">Current Status</div>
                    <div class="cs-value-in">Clocked In</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="clock-status cs-out">
                <div class="cs-dot cs-dot-out"></div>
                <div>
                    <div class="cs-label">Current Status</div>
                    <div class="cs-value-out">Not Clocked In</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_attendance_calendar(username: str) -> None:
    year = st.session_state.cal_year
    month = st.session_state.cal_month

    present_dates = get_all_attendance_dates(username)
    all_holidays = get_all_holidays()
    holiday_dates = {h["holiday_date"] for h in all_holidays}

    today_utc = datetime.now(timezone.utc).date()
    today_str = today_utc.strftime("%Y-%m-%d")

    month_name = datetime(year, month, 1).strftime("%B %Y")

    nav_left, nav_mid, nav_right = st.columns([1, 4, 1])
    with nav_left:
        if st.button("◀", key="cal_prev"):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with nav_mid:
        st.markdown(
            f'<div style="text-align:center;font-size:1rem;font-weight:700;color:#111827;padding:0.4rem 0;">{month_name}</div>',
            unsafe_allow_html=True,
        )
    with nav_right:
        if st.button("▶", key="cal_next"):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    # Build calendar HTML
    cal = calendar.monthcalendar(year, month)
    day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    header_html = "".join(
        f'<div class="cal-day cal-day-header">{d}</div>' for d in day_headers
    )

    days_html = ""
    for week in cal:
        for day_num in week:
            if day_num == 0:
                days_html += '<div class="cal-day cal-day-empty"></div>'
                continue
            date_str = f"{year:04d}-{month:02d}-{day_num:02d}"
            weekday = datetime(year, month, day_num).weekday()
            is_weekend = weekday >= 5
            is_today = date_str == today_str
            is_future = date_str > today_str
            is_holiday = date_str in holiday_dates
            is_present = date_str in present_dates
            is_past_weekday = not is_weekend and not is_future and date_str != today_str

            extra_class = ""
            if is_holiday:
                extra_class = "cal-day-holiday"
            elif is_weekend:
                extra_class = "cal-day-weekend"
            elif is_future:
                extra_class = "cal-day-future"
            elif is_present:
                extra_class = "cal-day-present"
            elif is_past_weekday:
                extra_class = "cal-day-absent"

            today_class = " cal-day-today" if is_today else ""
            days_html += f'<div class="cal-day {extra_class}{today_class}">{day_num}</div>'

    calendar_html = f"""
    <div class="cal-wrapper">
        <div class="cal-grid">
            {header_html}
            {days_html}
        </div>
        <div class="cal-legend">
            <div class="cal-legend-item">
                <div class="cal-legend-dot legend-present"></div>Present
            </div>
            <div class="cal-legend-item">
                <div class="cal-legend-dot legend-absent"></div>Absent
            </div>
            <div class="cal-legend-item">
                <div class="cal-legend-dot legend-holiday"></div>Holiday
            </div>
            <div class="cal-legend-item">
                <div class="cal-legend-dot legend-weekend"></div>Weekend
            </div>
        </div>
    </div>
    """
    st.markdown(calendar_html, unsafe_allow_html=True)


# ─────────────────────────── DASHBOARDS ─────────────────────────

def render_supervisor_dashboard() -> None:
    metrics = get_supervisor_metrics()
    render_page_header(
        "Supervisor Workspace",
        "Team operations at a glance.",
        "Review who is clocked in, dispatch work, and manage intern access from a single control centre.",
    )
    render_stat_cards([
        {"dot": "dot-blue",   "value": metrics["today_logs"],       "label": "Attendance Logs",  "note": "Recorded today"},
        {"dot": "dot-violet", "value": metrics["assigned_tasks"],    "label": "Active Tasks",     "note": "Assigned to interns"},
        {"dot": "dot-green",  "value": metrics["active_clocked_in"], "label": "Clocked In",       "note": "Currently working"},
        {"dot": "dot-amber",  "value": metrics["pending_reviews"],   "label": "Pending Reviews",  "note": "Awaiting your action"},
    ])

    st.write("")
    ops_tab, access_tab, files_tab = st.tabs(["Team Operations", "User Access", "Files & Holidays"])

    with ops_tab:
        left_col, right_col = st.columns((1.2, 1), gap="medium")

        with left_col:
            with st.container(border=True):
                render_section_header(
                    "Today's Attendance Feed",
                    "Live attendance events — see who is active right now.",
                )
                rows = get_today_attendance()
                if rows:
                    st.dataframe(rows, use_container_width=True, hide_index=True)
                else:
                    st.info("No attendance records logged today.")

        with right_col:
            with st.container(border=True):
                render_section_header(
                    "Dispatch New Task",
                    "Assign a piece of work to a specific intern.",
                )
                interns = list_interns()
                if interns:
                    intern_options = {
                        f"{i['full_name']} ({i['username']})": i["username"] for i in interns
                    }
                    with st.form("dispatch_task_form", clear_on_submit=True):
                        selected_label = st.selectbox("Assign to", list(intern_options.keys()))
                        task_title = st.text_input("Task title")
                        task_description = st.text_area("Instructions", height=120)
                        if st.form_submit_button("Dispatch Task", use_container_width=True):
                            ok, msg = create_task(intern_options[selected_label], task_title, task_description)
                            (st.success if ok else st.error)(msg)
                            if ok:
                                st.rerun()
                else:
                    st.warning("Create at least one intern account before dispatching tasks.")

        st.write("")
        with st.container(border=True):
            render_section_header(
                "Pending Reviews",
                "Approve submitted artifacts or return them for revision.",
            )
            pending = get_pending_reviews()
            reviewer = st.session_state.username
            if pending:
                for task in pending:
                    st.markdown(
                        f"""
                        <div class="review-item">
                            <div class="review-badge">Submission #{task['id']}</div>
                            <div class="review-title">{task['title']}</div>
                            <div class="review-meta">Assigned to {task['assigned_to']}</div>
                            <div class="review-desc">{task['description'] or 'No description provided.'}</div>
                            <div class="review-link">{task['link']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"Approve #{task['id']}", key=f"approve_{task['id']}", use_container_width=True):
                            review_task(task["id"], "Approved", reviewer)
                            st.success(f"Task #{task['id']} approved.")
                            st.rerun()
                    with c2:
                        if st.button(f"Request Revision #{task['id']}", key=f"revise_{task['id']}", use_container_width=True, type="secondary"):
                            review_task(task["id"], "Revision Needed", reviewer)
                            st.warning(f"Task #{task['id']} returned for revision.")
                            st.rerun()
            else:
                st.info("No pending submissions right now.")

    with access_tab:
        left_col, right_col = st.columns(2, gap="medium")

        with left_col:
            with st.container(border=True):
                render_section_header(
                    "Create Intern Account",
                    "Provision new intern credentials from this panel.",
                )
                with st.form("create_intern_form", clear_on_submit=True):
                    new_username  = st.text_input("Username")
                    new_password  = st.text_input("Password", type="password")
                    new_full_name = st.text_input("Full name")
                    new_timezone  = st.selectbox("Timezone", TIMEZONE_OPTIONS, index=0)
                    if st.form_submit_button("Create Account", use_container_width=True):
                        ok, msg = create_intern(new_username, new_password, new_full_name, new_timezone)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()

        with right_col:
            with st.container(border=True):
                render_section_header(
                    "Reset Intern Password",
                    "Overwrite a password if an intern loses access.",
                )
                interns = list_interns()
                if interns:
                    reset_options = [i["username"] for i in interns]
                    with st.form("reset_password_form", clear_on_submit=True):
                        reset_username = st.selectbox("Intern", reset_options)
                        new_pw = st.text_input("New password", type="password")
                        if st.form_submit_button("Reset Password", use_container_width=True):
                            ok, msg = reset_intern_password(reset_username, new_pw)
                            (st.success if ok else st.error)(msg)
                else:
                    st.info("No intern accounts exist yet.")

        st.write("")
        with st.container(border=True):
            render_section_header(
                "Intern Directory",
                "All active intern accounts managed by supervisors.",
            )
            interns = list_interns()
            if interns:
                st.dataframe(interns, use_container_width=True, hide_index=True)
            else:
                st.info("No intern accounts have been created yet.")

    with files_tab:
        left_col, right_col = st.columns(2, gap="medium")

        with left_col:
            with st.container(border=True):
                render_section_header(
                    "Manage Holidays",
                    "Add or remove holidays visible to all interns.",
                )
                with st.form("add_holiday_form", clear_on_submit=True):
                    h_title = st.text_input("Holiday name")
                    h_date  = st.date_input("Date")
                    if st.form_submit_button("Add Holiday", use_container_width=True):
                        ok, msg = add_holiday(h_title, str(h_date), st.session_state.username)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()

                st.write("")
                all_holidays = get_all_holidays()
                if all_holidays:
                    for h in all_holidays:
                        col_info, col_btn = st.columns([4, 1])
                        with col_info:
                            st.markdown(
                                f"""
                                <div class="holiday-item">
                                    <div>
                                        <div class="holiday-title">{h['title']}</div>
                                        <div class="holiday-date">{h['holiday_date']}</div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        with col_btn:
                            if st.button("Delete", key=f"del_holiday_{h['id']}", type="secondary"):
                                delete_holiday(h["id"])
                                st.rerun()
                else:
                    st.info("No holidays have been added yet.")

        with right_col:
            with st.container(border=True):
                render_section_header(
                    "Intern File Uploads",
                    "All files submitted by interns.",
                )
                uploads = get_all_uploads()
                if uploads:
                    st.dataframe(uploads, use_container_width=True, hide_index=True)
                else:
                    st.info("No files have been uploaded yet.")


def render_intern_dashboard() -> None:
    username = st.session_state.username
    full_name = st.session_state.full_name
    intern_tz = st.session_state.get("timezone", "UTC")
    open_record = get_open_attendance_record(username)
    tasks = get_tasks_for_user(username)
    approved_tasks = [t for t in tasks if t["status"] == "Approved"]
    pending_tasks  = [t for t in tasks if t["status"] in {"Assigned", "Revision Needed"}]

    render_page_header(
        "Intern Workspace",
        f"Welcome, {full_name}.",
        "Clock your workday, submit assignment artifacts, and track your approvals.",
    )
    render_stat_cards([
        {
            "dot": "dot-green" if open_record else "dot-blue",
            "value": "In" if open_record else "Out",
            "label": "Clock Status",
            "note": utc_date_string(),
        },
        {"dot": "dot-amber",  "value": len(pending_tasks),  "label": "Pending Tasks",  "note": "Assigned or needs revision"},
        {"dot": "dot-violet", "value": len(approved_tasks), "label": "Approved Items", "note": "Reviewed by supervisor"},
    ])

    st.write("")
    left_col, right_col = st.columns(2, gap="medium")

    with left_col:
        with st.container(border=True):
            render_section_header(
                "Attendance",
                "Start or end your session with an accurate timestamp.",
            )
            render_clock_status(bool(open_record))
            if open_record:
                if st.button("Clock Out", type="primary", use_container_width=True):
                    ok, msg = clock_out(username)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()
            else:
                if st.button("Clock In", type="primary", use_container_width=True):
                    ok, msg = clock_in(username)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()

        with st.container(border=True):
            render_section_header(
                "Attendance History",
                "Your recent sessions and completion status.",
            )
            history = get_user_attendance_history(username)
            if history:
                formatted = []
                for row in history:
                    formatted.append({
                        "date": row["date"],
                        "clock_in": format_ts_local(row["clock_in"], intern_tz),
                        "clock_out": format_ts_local(row["clock_out"], intern_tz) if row["clock_out"] else "",
                        "status": row["status"],
                    })
                st.dataframe(formatted, use_container_width=True, hide_index=True)
            else:
                st.info("No attendance history yet.")

    with right_col:
        with st.container(border=True):
            render_section_header(
                "Submit Assignment",
                "Attach the artifact URL for a task so your supervisor can review it.",
            )
            submittable = [t for t in tasks if t["status"] in {"Assigned", "Revision Needed"}]
            if submittable:
                task_options = {
                    f"#{t['id']} — {t['title']} ({t['status']})": t["id"] for t in submittable
                }
                with st.form("submit_artifact_form", clear_on_submit=True):
                    selected_task = st.selectbox("Task", list(task_options.keys()))
                    artifact_link = st.text_input("Artifact URL")
                    if st.form_submit_button("Submit for Review", use_container_width=True):
                        ok, msg = submit_task_link(task_options[selected_task], username, artifact_link)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()
            else:
                st.info("No tasks currently available for submission.")

        with st.container(border=True):
            render_section_header(
                "Upload Files",
                "Upload documents or assets for your supervisor.",
            )
            uploaded_files = st.file_uploader(
                "Upload files",
                type=["pdf", "docx", "doc", "pptx", "ppt", "png", "jpg", "jpeg", "gif", "webp"],
                accept_multiple_files=True,
                key="intern_file_uploader",
            )
            if st.button("Upload", key="upload_files_btn", use_container_width=True):
                if uploaded_files:
                    for uf in uploaded_files:
                        ok, msg, _ = upload_file_to_storage(uf, username)
                        (st.success if ok else st.error)(msg)
                    st.rerun()
                else:
                    st.warning("Please select at least one file.")

            st.write("")
            user_uploads = get_uploads_for_user(username)
            if user_uploads:
                render_section_header("Your Uploaded Files", "")
                for up in user_uploads:
                    ts_local = format_ts_local(up["uploaded_at"], intern_tz)
                    st.markdown(
                        f'📄 <a href="{up["file_url"]}" target="_blank">{up["filename"]}</a> '
                        f'<span style="font-size:0.78rem;color:#9CA3AF;">— {ts_local}</span>',
                        unsafe_allow_html=True,
                    )

        with st.container(border=True):
            render_section_header(
                "Approved Submissions",
                "Items reviewed and approved by your supervisor.",
            )
            if approved_tasks:
                st.dataframe(approved_tasks, use_container_width=True, hide_index=True)
            else:
                st.info("Approved items will appear here after supervisor review.")

    # Full-width row: Calendar + Upcoming Holidays
    st.write("")
    cal_col, holidays_col = st.columns([3, 1], gap="medium")

    with cal_col:
        with st.container(border=True):
            render_section_header(
                "Attendance Calendar",
                "Your monthly attendance at a glance.",
            )
            render_attendance_calendar(username)

    with holidays_col:
        with st.container(border=True):
            render_section_header(
                "Upcoming Holidays",
                "Scheduled holidays for your team.",
            )
            upcoming = get_upcoming_holidays()
            if upcoming:
                for h in upcoming:
                    st.markdown(
                        f"""
                        <div class="holiday-item">
                            <div>
                                <div class="holiday-title">{h['title']}</div>
                                <div class="holiday-date">{h['holiday_date']}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No upcoming holidays scheduled.")


# ─────────────────────────── MAIN ───────────────────────────────

@st.cache_resource
def _init_db_once():
    """Run DB migrations exactly once per server process, not on every rerun."""
    init_db()
    return True


def main() -> None:
    # Instantiate CookieManager once per session — recreating it every rerun
    # forces an extra round-trip that doubles perceived load time.
    if "cm" not in st.session_state:
        st.session_state.cm = stx.CookieManager(key="ba_tracker_cm")
    cm = st.session_state.cm
    inject_styles()
    check_env()
    _init_db_once()
    init_session_state()

    if not st.session_state.authenticated:
        restore_session_from_cookie(cm)

    if not st.session_state.authenticated:
        render_login(cm)
        return

    render_sidebar(cm)

    if st.session_state.role == "supervisor":
        render_supervisor_dashboard()
    else:
        render_intern_dashboard()


if __name__ == "__main__":
    main()
