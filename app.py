import hashlib
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import streamlit as st


DB_PATH = Path(os.getenv("DB_PATH", "app_secure_responsive.db"))
SUPERVISOR_ACCOUNTS = [
    {
        "username": "admin",
        "password": "SuperSecureAdmin2026",
        "role": "supervisor",
        "full_name": "Master Supervisor",
    },
    {
        "username": "aniket.batwal@sphereglobal.com",
        "password": "Pass@123",
        "role": "supervisor",
        "full_name": "Aniket Batwal",
    },
]


st.set_page_config(
    page_title="Intern Operations & Attendance Tracker",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_responsive_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

            :root {
                --bg: #eef3f8;
                --surface: rgba(255, 255, 255, 0.92);
                --surface-strong: #ffffff;
                --surface-muted: #f7f9fc;
                --border: rgba(15, 23, 42, 0.09);
                --text: #10233c;
                --muted: #5f728a;
                --primary: #0c4a6e;
                --primary-soft: #dff0fb;
                --accent: #0f766e;
                --danger: #b42318;
                --shadow: 0 18px 60px rgba(15, 23, 42, 0.08);
            }

            html, body, [class*="css"] {
                font-family: "Manrope", sans-serif;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(207, 232, 255, 0.8), transparent 28%),
                    radial-gradient(circle at top right, rgba(214, 244, 236, 0.85), transparent 24%),
                    linear-gradient(180deg, #f8fbfe 0%, var(--bg) 100%);
            }

            .block-container {
                padding-top: 0.5rem;
                padding-bottom: 2rem;
                max-width: 1320px;
            }

            #MainMenu, header[data-testid="stHeader"] {
                visibility: hidden;
            }

            [data-testid="collapsedControl"] svg {
                fill: var(--text);
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f223a 0%, #18314f 100%);
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            [data-testid="stSidebar"] * {
                color: #f8fbff;
            }

            [data-testid="stSidebar"] .sidebar-brand {
                padding: 1rem 1rem 0.2rem 1rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                margin-bottom: 1rem;
            }

            [data-testid="stSidebar"] .sidebar-caption {
                color: rgba(237, 245, 255, 0.75);
                font-size: 0.9rem;
            }

            [data-testid="stSidebar"] button[kind="secondary"] {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.18);
                color: #ffffff;
                width: 100%;
            }

            [data-testid="stSidebar"] button[kind="secondary"]:hover {
                border-color: rgba(255, 255, 255, 0.34);
                color: #ffffff;
            }

            .page-hero {
                padding: 1.55rem 1.6rem;
                border-radius: 24px;
                background:
                    linear-gradient(135deg, rgba(12, 74, 110, 0.95), rgba(15, 118, 110, 0.86)),
                    linear-gradient(180deg, #134d73, #0f766e);
                color: #ffffff;
                box-shadow: var(--shadow);
                margin-bottom: 1rem;
                overflow: hidden;
                position: relative;
            }

            .page-hero::after {
                content: "";
                position: absolute;
                inset: auto -50px -60px auto;
                width: 220px;
                height: 220px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.08);
            }

            .hero-kicker {
                text-transform: uppercase;
                letter-spacing: 0.12em;
                font-size: 0.76rem;
                font-weight: 700;
                opacity: 0.82;
                margin-bottom: 0.45rem;
            }

            .hero-title {
                font-size: clamp(1.8rem, 3vw, 2.8rem);
                font-weight: 800;
                margin: 0;
                line-height: 1.08;
            }

            .hero-copy {
                max-width: 760px;
                color: rgba(255, 255, 255, 0.84);
                margin-top: 0.65rem;
                font-size: 1rem;
            }

            .metric-card {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(247, 250, 252, 0.98) 100%);
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 1.15rem 1.2rem;
                box-shadow: 0 10px 32px rgba(15, 23, 42, 0.05);
                min-height: 138px;
            }

            .metric-label {
                color: var(--muted);
                font-size: 0.88rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }

            .metric-value {
                color: var(--text);
                font-size: clamp(1.6rem, 2.4vw, 2.35rem);
                font-weight: 800;
                margin-top: 0.4rem;
                line-height: 1.05;
            }

            .metric-note {
                color: var(--muted);
                margin-top: 0.5rem;
                font-size: 0.92rem;
            }

            .panel {
                background: var(--surface);
                backdrop-filter: blur(18px);
                border: 1px solid var(--border);
                border-radius: 22px;
                box-shadow: 0 14px 40px rgba(15, 23, 42, 0.04);
                padding: 1.15rem;
                margin-bottom: 1rem;
            }

            .panel-title {
                color: var(--text);
                font-size: 1.02rem;
                font-weight: 800;
                margin-bottom: 0.2rem;
            }

            .panel-copy {
                color: var(--muted);
                font-size: 0.92rem;
                margin-bottom: 0.8rem;
            }

            .badge {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.45rem 0.7rem;
                border-radius: 999px;
                background: var(--primary-soft);
                color: var(--primary);
                font-weight: 700;
                font-size: 0.86rem;
            }

            .status-banner {
                border-radius: 20px;
                padding: 1rem 1.1rem;
                background: linear-gradient(180deg, #ffffff, #f7fafc);
                border: 1px solid var(--border);
                margin-bottom: 1rem;
            }

            .status-title {
                color: var(--muted);
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
            }

            .status-value {
                color: var(--text);
                font-size: 1.45rem;
                font-weight: 800;
                margin-top: 0.3rem;
            }

            .login-wrap {
                min-height: calc(100vh - 1rem);
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .login-card {
                width: min(1120px, 100%);
                display: grid;
                grid-template-columns: 1.05fr 0.95fr;
                background: rgba(255, 255, 255, 0.86);
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 28px;
                overflow: hidden;
                box-shadow: 0 24px 80px rgba(15, 23, 42, 0.12);
                backdrop-filter: blur(18px);
            }

            .login-brand {
                padding: 2.2rem;
                background:
                    radial-gradient(circle at top left, rgba(255, 255, 255, 0.22), transparent 34%),
                    linear-gradient(145deg, #0c4a6e 0%, #115e59 100%);
                color: #ffffff;
            }

            .login-brand h1 {
                font-size: clamp(2rem, 3vw, 3rem);
                margin: 0 0 0.8rem 0;
                line-height: 1.05;
            }

            .login-brand p {
                color: rgba(255, 255, 255, 0.84);
                font-size: 1rem;
                max-width: 460px;
            }

            .login-points {
                margin-top: 1.2rem;
                display: grid;
                gap: 0.8rem;
            }

            .login-point {
                padding: 0.8rem 0.95rem;
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.12);
            }

            .login-form {
                padding: 2.1rem;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(249, 251, 253, 0.98));
            }

            .login-form h2 {
                color: var(--text);
                font-size: 1.6rem;
                margin-bottom: 0.4rem;
            }

            .login-form p {
                color: var(--muted);
                margin-bottom: 1rem;
            }

            label, .stTextInput label, .stTextArea label, .stSelectbox label, .stMarkdown, .stCaption {
                color: var(--text);
            }

            div[data-baseweb="input"] input,
            div[data-baseweb="base-input"] input,
            div[data-baseweb="base-input"] textarea,
            textarea {
                color: var(--text) !important;
                -webkit-text-fill-color: var(--text) !important;
                background: #ffffff !important;
            }

            div[data-baseweb="input"] input::placeholder,
            div[data-baseweb="base-input"] input::placeholder,
            div[data-baseweb="base-input"] textarea::placeholder,
            textarea::placeholder {
                color: #7b8da5 !important;
                -webkit-text-fill-color: #7b8da5 !important;
                opacity: 1 !important;
            }

            div[data-baseweb="input"],
            div[data-baseweb="base-input"],
            div[data-baseweb="select"] > div {
                background: #ffffff !important;
                border-color: rgba(15, 23, 42, 0.1) !important;
            }

            div[data-baseweb="select"] * {
                color: var(--text) !important;
            }

            div[data-baseweb="select"] svg,
            div[data-baseweb="input"] svg,
            div[data-baseweb="base-input"] svg {
                fill: #4b5f78 !important;
                color: #4b5f78 !important;
            }

            [data-testid="stForm"] {
                background: transparent;
            }

            [data-testid="stFormSubmitButton"] button,
            .stButton button {
                box-shadow: none !important;
            }

            .clock-button button,
            .stButton button[kind="primary"] {
                min-height: 3rem;
                border-radius: 14px;
                font-weight: 800;
                border: 0;
                background: linear-gradient(135deg, #0c4a6e, #0f766e);
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
                background: rgba(255, 255, 255, 0.6);
                border-radius: 16px;
                padding: 0.35rem;
                border: 1px solid rgba(15, 23, 42, 0.06);
            }

            .stTabs [data-baseweb="tab"] {
                height: 50px;
                border-radius: 12px;
                font-weight: 700;
                color: var(--muted);
            }

            .stTabs [aria-selected="true"] {
                background: #ffffff !important;
                color: var(--text) !important;
                box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
            }

            div[data-testid="stDataFrame"] {
                border-radius: 18px;
                overflow: hidden;
                border: 1px solid rgba(15, 23, 42, 0.08);
            }

            @media (max-width: 980px) {
                .login-card {
                    grid-template-columns: 1fr;
                }
            }

            @media (max-width: 768px) {
                .block-container {
                    padding-top: 0.25rem;
                    padding-left: 0.8rem;
                    padding-right: 0.8rem;
                }

                div[data-testid="column"] {
                    width: 100% !important;
                    flex: 1 1 100% !important;
                }

                .login-brand,
                .login-form,
                .page-hero,
                .panel,
                .metric-card {
                    padding: 1rem;
                    border-radius: 18px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def rows_to_dicts(rows) -> list[dict]:
    return [dict(row) for row in rows]


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assigned_to TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                link TEXT,
                status TEXT NOT NULL
            )
            """
        )

        for account in SUPERVISOR_ACCOUNTS:
            cursor.execute(
                "SELECT id FROM users WHERE username = ?",
                (account["username"],),
            )
            existing = cursor.fetchone()
            account_values = (
                hash_password(account["password"]),
                account["role"],
                account["full_name"],
                account["username"],
            )
            if existing:
                cursor.execute(
                    """
                    UPDATE users
                    SET password = ?, role = ?, full_name = ?
                    WHERE username = ?
                    """,
                    account_values,
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO users (password, role, full_name, username)
                    VALUES (?, ?, ?, ?)
                    """,
                    account_values,
                )
        conn.commit()


def init_session_state() -> None:
    defaults = {
        "authenticated": False,
        "username": "",
        "role": "",
        "full_name": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def login_user(username: str, password: str) -> bool:
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT username, role, full_name
            FROM users
            WHERE username = ? AND password = ?
            """,
            (username.strip(), hash_password(password)),
        )
        user = cursor.fetchone()

    if not user:
        return False

    st.session_state.authenticated = True
    st.session_state.username = user["username"]
    st.session_state.role = user["role"]
    st.session_state.full_name = user["full_name"]
    return True


def logout_user() -> None:
    for key in ("authenticated", "username", "role", "full_name"):
        st.session_state[key] = False if key == "authenticated" else ""
    st.rerun()


def current_date_string() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_intern(username: str, password: str, full_name: str) -> tuple[bool, str]:
    username = username.strip()
    full_name = full_name.strip()

    if not username or not password or not full_name:
        return False, "All fields are required."

    reserved_supervisors = {account["username"].lower() for account in SUPERVISOR_ACCOUNTS}
    if username.lower() in reserved_supervisors:
        return False, "That username is reserved for a supervisor account."

    try:
        with closing(get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, password, role, full_name)
                VALUES (?, ?, ?, ?)
                """,
                (username, hash_password(password), "intern", full_name),
            )
            conn.commit()
        return True, f"Intern account '{username}' created successfully."
    except sqlite3.IntegrityError:
        return False, "That username already exists."


def reset_intern_password(username: str, new_password: str) -> tuple[bool, str]:
    if not username or not new_password:
        return False, "Username and new password are required."

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (username.strip(),))
        user = cursor.fetchone()
        if not user:
            return False, "Intern account not found."
        if user["role"] != "intern":
            return False, "Only intern passwords can be changed here."

        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hash_password(new_password), username.strip()),
        )
        conn.commit()
    return True, f"Password updated for '{username.strip()}'."


def list_interns() -> list[dict]:
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT username, full_name
            FROM users
            WHERE role = 'intern'
            ORDER BY full_name COLLATE NOCASE, username COLLATE NOCASE
            """
        )
        return rows_to_dicts(cursor.fetchall())


def get_open_attendance_record(username: str):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM attendance
            WHERE username = ? AND date = ? AND clock_out IS NULL
            ORDER BY id DESC
            LIMIT 1
            """,
            (username, current_date_string()),
        )
        return cursor.fetchone()


def clock_in(username: str) -> tuple[bool, str]:
    if get_open_attendance_record(username):
        return False, "You are already clocked in for today."

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attendance (username, date, clock_in, clock_out, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, current_date_string(), current_timestamp(), None, "Clocked In"),
        )
        conn.commit()
    return True, "Clock-in recorded successfully."


def clock_out(username: str) -> tuple[bool, str]:
    open_record = get_open_attendance_record(username)
    if not open_record:
        return False, "No active clock-in found for today."

    clock_in_dt = datetime.strptime(open_record["clock_in"], "%Y-%m-%d %H:%M:%S")
    clock_out_ts = current_timestamp()
    clock_out_dt = datetime.strptime(clock_out_ts, "%Y-%m-%d %H:%M:%S")
    elapsed = clock_out_dt - clock_in_dt
    total_seconds = int(elapsed.total_seconds())
    hours, remainder = divmod(max(total_seconds, 0), 3600)
    minutes, _ = divmod(remainder, 60)
    status = f"Completed ({hours}h {minutes}m)"

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE attendance
            SET clock_out = ?, status = ?
            WHERE id = ?
            """,
            (clock_out_ts, status, open_record["id"]),
        )
        conn.commit()
    return True, f"Clock-out recorded. Session duration: {hours}h {minutes}m."


def get_today_attendance() -> list[dict]:
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT username, date, clock_in, clock_out, status
            FROM attendance
            WHERE date = ?
            ORDER BY clock_in DESC
            """,
            (current_date_string(),),
        )
        return rows_to_dicts(cursor.fetchall())


def get_user_attendance_history(username: str) -> list[dict]:
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT date, clock_in, clock_out, status
            FROM attendance
            WHERE username = ?
            ORDER BY date DESC, id DESC
            """,
            (username,),
        )
        return rows_to_dicts(cursor.fetchall())


def create_task(assigned_to: str, title: str, description: str) -> tuple[bool, str]:
    if not assigned_to or not title.strip():
        return False, "Assigned intern and task title are required."

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (assigned_to, title, description, link, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (assigned_to, title.strip(), description.strip(), "", "Assigned"),
        )
        conn.commit()
    return True, f"Task '{title.strip()}' dispatched to {assigned_to}."


def submit_task_link(task_id: int, username: str, link: str) -> tuple[bool, str]:
    if not link.strip():
        return False, "Please enter a valid artifact URL."

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tasks
            SET link = ?, status = ?
            WHERE id = ? AND assigned_to = ?
            """,
            (link.strip(), "Pending Review", task_id, username),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Task not found or not assigned to you."
    return True, "Assignment link submitted successfully."


def review_task(task_id: int, new_status: str) -> None:
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()


def get_tasks_for_user(username: str) -> list[dict]:
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, description, link, status
            FROM tasks
            WHERE assigned_to = ?
            ORDER BY id DESC
            """,
            (username,),
        )
        return rows_to_dicts(cursor.fetchall())


def get_pending_reviews() -> list[dict]:
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, assigned_to, title, description, link, status
            FROM tasks
            WHERE status = 'Pending Review'
            ORDER BY id DESC
            """
        )
        return rows_to_dicts(cursor.fetchall())


def get_supervisor_metrics() -> dict:
    today_logs = get_today_attendance()
    pending_reviews = get_pending_reviews()
    interns = list_interns()
    active_clocked_in = sum(1 for row in today_logs if row["clock_out"] is None)

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM tasks WHERE status = 'Assigned'")
        assigned_tasks = cursor.fetchone()["count"]

    return {
        "intern_count": len(interns),
        "today_logs": len(today_logs),
        "active_clocked_in": active_clocked_in,
        "pending_reviews": len(pending_reviews),
        "assigned_tasks": assigned_tasks,
    }


def render_page_hero(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <section class="page-hero">
            <div class="hero-kicker">{kicker}</div>
            <h1 class="hero-title">{title}</h1>
            <div class="hero-copy">{copy}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: list[dict]) -> None:
    columns = st.columns(len(metrics))
    for column, metric in zip(columns, metrics):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{metric['label']}</div>
                    <div class="metric-value">{metric['value']}</div>
                    <div class="metric-note">{metric['note']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_panel_header(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="panel-title">{title}</div>
        <div class="panel-copy">{copy}</div>
        """,
        unsafe_allow_html=True,
    )


def render_login() -> None:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    left, center, right = st.columns([0.03, 1, 0.03])
    with center:
        st.markdown(
            """
            <section class="login-card">
                <div class="login-brand">
                    <div class="hero-kicker">Secure Workforce Portal</div>
                    <h1>Intern operations designed for real teams.</h1>
                    <p>
                        Track attendance, route assignments, and control account access through a
                        supervisor-first workflow that stays clean on desktop and mobile.
                    </p>
                    <div class="login-points">
                        <div class="login-point"><strong>Role-gated access</strong><br/>Supervisor-only user management and password resets.</div>
                        <div class="login-point"><strong>Attendance precision</strong><br/>Reliable clock events and daily operational visibility.</div>
                        <div class="login-point"><strong>Submission reviews</strong><br/>Approve work artifacts or request revision from one dashboard.</div>
                    </div>
                </div>
                <div class="login-form">
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<h2>Sign in to continue</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p>Use your assigned supervisor or intern credentials to access the portal.</p>",
            unsafe_allow_html=True,
        )
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Access Dashboard", use_container_width=True)

        if submitted:
            if login_user(username, password):
                st.success("Login successful. Loading your workspace...")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.markdown("</div></section>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div style="font-size:1.15rem;font-weight:800;">Intern Tracker</div>
                <div class="sidebar-caption">Operations, attendance, and review workflow</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(f"**{st.session_state.full_name}**")
        st.caption(f"Access role: {st.session_state.role}")
        if st.button("Logout", type="secondary", use_container_width=True):
            logout_user()


def render_supervisor_dashboard() -> None:
    metrics = get_supervisor_metrics()
    render_page_hero(
        "Supervisor Workspace",
        "Team operations at a glance.",
        "Review who is clocked in, dispatch work, and manage intern access from a single secure control center.",
    )

    render_metric_cards(
        [
            {
                "label": "Attendance Summary",
                "value": metrics["today_logs"],
                "note": "logs recorded for today's activity",
            },
            {
                "label": "Active Tasks",
                "value": metrics["assigned_tasks"],
                "note": "tasks currently assigned to interns",
            },
            {
                "label": "Live Clock Status",
                "value": metrics["active_clocked_in"],
                "note": "interns presently clocked in",
            },
            {
                "label": "Pending Reviews",
                "value": metrics["pending_reviews"],
                "note": "submissions awaiting supervisor action",
            },
        ]
    )

    operations_tab, access_tab = st.tabs(
        ["Team Operations & Live Metrics", "User Access Management Control"]
    )

    with operations_tab:
        left, right = st.columns((1.2, 1))

        with left:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_panel_header(
                    "Today's Attendance Feed",
                    "Monitor daily attendance events and see who is still active in real time.",
                )
                attendance_rows = get_today_attendance()
                if attendance_rows:
                    st.dataframe(attendance_rows, use_container_width=True, hide_index=True)
                else:
                    st.info("No attendance records have been logged today.")
                st.markdown("</div>", unsafe_allow_html=True)

        with right:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_panel_header(
                    "Dispatch New Task",
                    "Assign a clear piece of work to a specific intern with title and instructions.",
                )
                interns = list_interns()
                if interns:
                    intern_options = {
                        f"{intern['full_name']} ({intern['username']})": intern["username"]
                        for intern in interns
                    }
                    with st.form("dispatch_task_form", clear_on_submit=True):
                        selected_label = st.selectbox("Assign To", list(intern_options.keys()))
                        task_title = st.text_input("Task Title")
                        task_description = st.text_area("Task Description", height=170)
                        create_task_submit = st.form_submit_button(
                            "Dispatch Task",
                            use_container_width=True,
                        )
                    if create_task_submit:
                        success, message = create_task(
                            intern_options[selected_label],
                            task_title,
                            task_description,
                        )
                        (st.success if success else st.error)(message)
                        if success:
                            st.rerun()
                else:
                    st.warning("Create at least one intern account before dispatching tasks.")
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_panel_header(
            "Pending Task Reviews",
            "Approve submitted artifacts or return them for revision with one click.",
        )
        pending_reviews = get_pending_reviews()
        if pending_reviews:
            for task in pending_reviews:
                with st.container(border=True):
                    top_left, top_right = st.columns((1.5, 1))
                    with top_left:
                        st.markdown(f"**{task['title']}**")
                        st.caption(f"Assigned to: {task['assigned_to']}")
                        st.write(task["description"] or "No description provided.")
                    with top_right:
                        st.markdown(
                            f"<div class='badge'>Submission #{task['id']}</div>",
                            unsafe_allow_html=True,
                        )
                        st.write(f"Artifact URL: {task['link']}")

                    action_col1, action_col2 = st.columns(2)
                    with action_col1:
                        if st.button(
                            f"Approve #{task['id']}",
                            key=f"approve_{task['id']}",
                            use_container_width=True,
                        ):
                            review_task(task["id"], "Approved")
                            st.success(f"Task #{task['id']} approved.")
                            st.rerun()
                    with action_col2:
                        if st.button(
                            f"Revision Needed #{task['id']}",
                            key=f"revise_{task['id']}",
                            use_container_width=True,
                        ):
                            review_task(task["id"], "Revision Needed")
                            st.warning(f"Task #{task['id']} marked for revision.")
                            st.rerun()
        else:
            st.info("No pending task submissions right now.")
        st.markdown("</div>", unsafe_allow_html=True)

    with access_tab:
        left, right = st.columns(2)
        with left:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            render_panel_header(
                "Create New Intern",
                "Provision intern credentials directly from the supervisor control panel.",
            )
            with st.form("create_intern_form", clear_on_submit=True):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_full_name = st.text_input("Full Name")
                create_intern_submit = st.form_submit_button(
                    "Create Intern",
                    use_container_width=True,
                )
            if create_intern_submit:
                success, message = create_intern(new_username, new_password, new_full_name)
                (st.success if success else st.error)(message)
                if success:
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            render_panel_header(
                "Reset Intern Password",
                "Overwrite an intern password if they lose access. Interns cannot reset their own passwords.",
            )
            interns = list_interns()
            if interns:
                reset_options = [intern["username"] for intern in interns]
                with st.form("reset_password_form", clear_on_submit=True):
                    reset_username = st.selectbox("Intern Username", reset_options)
                    replacement_password = st.text_input("New Password", type="password")
                    reset_submit = st.form_submit_button(
                        "Overwrite Password",
                        use_container_width=True,
                    )
                if reset_submit:
                    success, message = reset_intern_password(
                        reset_username,
                        replacement_password,
                    )
                    (st.success if success else st.error)(message)
            else:
                st.info("No intern accounts are available to reset yet.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_panel_header(
            "Intern Directory",
            "Current active intern accounts managed by supervisor-level users.",
        )
        interns = list_interns()
        if interns:
            st.dataframe(interns, use_container_width=True, hide_index=True)
        else:
            st.info("No intern accounts have been created yet.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_intern_dashboard() -> None:
    username = st.session_state.username
    full_name = st.session_state.full_name
    open_record = get_open_attendance_record(username)
    tasks = get_tasks_for_user(username)
    approved_tasks = [task for task in tasks if task["status"] == "Approved"]
    pending_items = [
        task for task in tasks if task["status"] in {"Assigned", "Revision Needed"}
    ]

    render_page_hero(
        "Intern Workspace",
        f"Welcome, {full_name}.",
        "Clock your workday, submit artifacts for review, and keep a simple history of your approved assignments.",
    )

    render_metric_cards(
        [
            {
                "label": "Clock Status",
                "value": "Clocked In" if open_record else "Clocked Out",
                "note": current_date_string(),
            },
            {
                "label": "Pending Tasks",
                "value": len(pending_items),
                "note": "assigned or returned for revision",
            },
            {
                "label": "Approved Items",
                "value": len(approved_tasks),
                "note": "submissions approved by a supervisor",
            },
        ]
    )

    left, right = st.columns((1, 1))

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_panel_header(
            "Attendance Status",
            "Use the primary action below to start or end your day with an accurate timestamp.",
        )
        st.markdown(
            f"""
            <div class="status-banner">
                <div class="status-title">Current State</div>
                <div class="status-value">{'Clocked In' if open_record else 'Ready to Clock In'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="clock-button">', unsafe_allow_html=True)
        if open_record:
            if st.button("Clock Out", type="primary", use_container_width=True):
                success, message = clock_out(username)
                (st.success if success else st.error)(message)
                if success:
                    st.rerun()
        else:
            if st.button("Clock In", type="primary", use_container_width=True):
                success, message = clock_in(username)
                (st.success if success else st.error)(message)
                if success:
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_panel_header(
            "Attendance History",
            "Review your recent attendance sessions and their completion status.",
        )
        history = get_user_attendance_history(username)
        if history:
            st.dataframe(history, use_container_width=True, hide_index=True)
        else:
            st.info("No attendance history available yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_panel_header(
            "Submit Assignment Artifact",
            "Attach the URL for the work you completed so it can be reviewed by your supervisor.",
        )
        submittable_tasks = [
            task for task in tasks if task["status"] in {"Assigned", "Revision Needed"}
        ]
        if submittable_tasks:
            task_options = {
                f"#{task['id']} - {task['title']} ({task['status']})": task["id"]
                for task in submittable_tasks
            }
            with st.form("submit_artifact_form", clear_on_submit=True):
                selected_task = st.selectbox("Task", list(task_options.keys()))
                artifact_link = st.text_input("Assignment Artifact URL")
                submit_artifact = st.form_submit_button(
                    "Submit Link",
                    use_container_width=True,
                )
            if submit_artifact:
                success, message = submit_task_link(
                    task_options[selected_task],
                    username,
                    artifact_link,
                )
                (st.success if success else st.error)(message)
                if success:
                    st.rerun()
        else:
            st.info("No tasks are currently available for submission.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_panel_header(
            "Approved Submission History",
            "Your approved items stay visible here for easy reference.",
        )
        if approved_tasks:
            st.dataframe(approved_tasks, use_container_width=True, hide_index=True)
        else:
            st.info("Approved items will appear here after supervisor review.")
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    inject_responsive_styles()
    init_db()
    init_session_state()

    if not st.session_state.authenticated:
        render_login()
        return

    render_sidebar()

    if st.session_state.role == "supervisor":
        render_supervisor_dashboard()
    else:
        render_intern_dashboard()


if __name__ == "__main__":
    main()
