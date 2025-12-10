import streamlit as st
import pandas as pd
from datetime import date
import json
import os

st.set_page_config(page_title="Daily To-Do List", layout="wide")

USERS_FILE = "users.json"

# ------------------ INIT USERS FILE ------------------
if not os.path.exists(USERS_FILE):
    users = {"sabuj2025": {"password": "sabuj", "tasks": [], "completed": []}}
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# --------------- FIX MISSING KEYS (NO MORE KEYERROR) -----------
def ensure_user(username):
    users = load_users()

    if username not in users:
        users[username] = {"password": "", "tasks": [], "completed": []}

    if "tasks" not in users[username]:
        users[username]["tasks"] = []

    if "completed" not in users[username]:
        users[username]["completed"] = []

    if "password" not in users[username]:
        users[username]["password"] = ""

    save_users(users)
    return users


# ------------------ LOGIN PAGE ------------------
def login_page():
    st.title("🔐 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()

        # Fix key
        if user in users:
            ensure_user(user)

        if user in users and users[user]["password"] == pwd:
            st.session_state.logged = True
            st.session_state.user = user
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")


# ------------------ UI STYLE ------------------
def page_style():
    st.markdown("""
        <style>
        .task-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 3px 6px #ccc;
            margin-bottom: 12px;
        }
        .task-title { font-size: 20px; font-weight: bold; }
        .task-info { font-size: 13px; color: #444; margin-top: 6px; }
        .stButton>button {
            border-radius: 5px;
            padding: 6px 12px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            opacity: 0.85;
            transform: scale(0.97);
        }
        </style>
    """, unsafe_allow_html=True)


# ------------------ ADD TASK ------------------
def add_task_page():
    users = ensure_user(st.session_state.user)
    username = st.session_state.user
    tasks = users[username]["tasks"]

    st.subheader("➕ Add New Task")

    with st.form("add_form"):
        title = st.text_input("Task Title")
        desc = st.text_area("Description")
        start = st.date_input("Start", date.today())
        end = st.date_input("End", date.today())
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        assigned = st.text_input("Assigned By")

        saved = st.form_submit_button("Save Task")

        if saved:
            if title == "":
                st.error("Title required!")
            else:
                tasks.insert(0, {
                    "Task": title,
                    "Description": desc,
                    "Start": str(start),
                    "End": str(end),
                    "Status": "Pending",
                    "Priority": priority,
                    "AssignedBy": assigned
                })
                users[username]["tasks"] = tasks
                save_users(users)
                st.success("Task Added!")


# ------------------ DISPLAY TASKS ------------------
def task_list_page():
    users = ensure_user(st.session_state.user)
    username = st.session_state.user
    tasks = users[username]["tasks"]
    completed = users[username]["completed"]

    st.subheader("📝 Your Active Tasks (Pending + Running)")

    if len(tasks) == 0:
        st.info("No Active Tasks")
        return

    for i, t in enumerate(tasks):
        priority_color = {"High": "red", "Medium": "orange", "Low": "green"}[t["Priority"]]
        status_color = "blue" if t["Status"] == "Running" else "orange"

        st.markdown(
            f"""
            <div class='task-card'>
                <div class='task-title'>{t['Task']}</div>
                <div class='task-info'>
                    {t['Description']}<br>
                    Start: {t['Start']} | End: {t['End']}<br>
                    <b>Status:</b> <span style='color:{status_color}'>{t['Status']}</span> |
                    <b>Priority:</b> <span style='color:{priority_color}'>{t['Priority']}</span> |
                    <b>Assigned By:</b> {t['AssignedBy']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)

        # EDIT
        if c1.button("✏️ Edit", key=f"e{i}"):
            st.session_state.edit_id = i

        # DELETE
        if c2.button("🗑 Delete", key=f"d{i}"):
            tasks.pop(i)
            users[username]["tasks"] = tasks
            save_users(users)
            st.success("Task deleted!")
            st.experimental_rerun()

        # COMPLETE
        if c3.button("✔ Complete", key=f"c{i}"):
            completed.insert(0, t)
            tasks.pop(i)
            users[username]["tasks"] = tasks
            users[username]["completed"] = completed
            save_users(users)
            st.success("Task moved to Completed!")
            st.experimental_rerun()

        # RUNNING
        if c4.button("🏃 Running", key=f"r{i}"):
            tasks[i]["Status"] = "Running"
            users[username]["tasks"] = tasks
            save_users(users)
            st.experimental_rerun()

    # EDIT FORM
    if "edit_id" in st.session_state and st.session_state.edit_id is not None:
        idx = st.session_state.edit_id
        t = tasks[idx]

        st.subheader("✏️ Edit Task")
        with st.form("edit_form"):
            nt = st.text_input("Title", t["Task"])
            nd = st.text_area("Description", t["Description"])
            ns = st.date_input("Start", date.fromisoformat(t["Start"]))
            ne = st.date_input("End", date.fromisoformat(t["End"]))
            np = st.selectbox("Priority", ["High", "Medium", "Low"],
                              index=["High", "Medium", "Low"].index(t["Priority"]))
            na = st.text_input("Assigned By", t["AssignedBy"])

            sv = st.form_submit_button("Save Changes")

            if sv:
                tasks[idx] = {
                    "Task": nt,
                    "Description": nd,
                    "Start": str(ns),
                    "End": str(ne),
                    "Status": t["Status"],
                    "Priority": np,
                    "AssignedBy": na
                }
                users[username]["tasks"] = tasks
                save_users(users)
                st.success("Task updated!")
                st.session_state.edit_id = None
                st.experimental_rerun()


# ------------------ COMPLETED TASKS PAGE ------------------
def completed_page():
    users = ensure_user(st.session_state.user)
    username = st.session_state.user
    completed = users[username]["completed"]

    st.subheader("✅ Completed Tasks (Permanent Record)")

    if len(completed) == 0:
        st.info("No Completed Tasks Yet")
        return

    for t in completed:
        st.markdown(
            f"""
            <div class='task-card'>
                <div class='task-title'>{t['Task']}</div>
                <div class='task-info'>
                    {t['Description']}<br>
                    Start: {t['Start']} | End: {t['End']}<br>
                    <b>Status:</b> <span style='color:green'>Completed</span> |
                    <b>Priority:</b> {t['Priority']} |
                    <b>Assigned By:</b> {t['AssignedBy']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ------------------ CSV EXPORT ------------------
def csv_page():
    users = ensure_user(st.session_state.user)
    username = st.session_state.user
    tasks = users[username]["tasks"] + users[username]["completed"]

    st.subheader("⬇ Export Tasks to CSV")

    if len(tasks) == 0:
        st.warning("No tasks available")
        return

    start = st.date_input("Start Date", date.today())
    end = st.date_input("End Date", date.today())

    filtered = [
        t for t in tasks
        if start <= date.fromisoformat(t["Start"]) <= end
    ]

    if len(filtered) == 0:
        st.info("No tasks found in this date range")
        return

    df = pd.DataFrame(filtered)
    st.download_button("Download CSV", df.to_csv(index=False), "tasks.csv")


# ------------------ PASSWORD ------------------
def password_page():
    users = ensure_user(st.session_state.user)
    username = st.session_state.user

    st.subheader("🔑 Change Password")

    old = st.text_input("Old Password", type="password")
    new = st.text_input("New Password", type="password")
    c = st.text_input("Confirm New Password", type="password")

    if st.button("Update"):
        if users[username]["password"] != old:
            st.error("Old password incorrect")
        elif new != c:
            st.error("Passwords do not match")
        else:
            users[username]["password"] = new
            save_users(users)
            st.success("Password updated!")


# ------------------ MAIN APP ------------------
if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    login_page()
else:
    page_style()

    st.sidebar.title("📌 Menu")
    page = st.sidebar.radio(
        "",
        ["Add Task", "Active Tasks", "Completed Tasks", "CSV Export", "Password Change", "Logout"]
    )

    if page == "Add Task":
        add_task_page()

    elif page == "Active Tasks":
        task_list_page()

    elif page == "Completed Tasks":
        completed_page()

    elif page == "CSV Export":
        csv_page()

    elif page == "Password Change":
        password_page()

    elif page == "Logout":
        st.session_state.logged = False
        st.experimental_rerun()
