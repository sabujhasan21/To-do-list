import streamlit as st
import pandas as pd
from datetime import date
import json
import os

st.set_page_config(page_title="Daily To-Do List", layout="wide")

USERS_FILE = "users.json"

DEFAULT_STRUCTURE = {"password": "", "tasks": [], "completed": []}

# ---------------- INIT USERS FILE ----------------
if not os.path.exists(USERS_FILE):
    users = {"sabuj2025": {"password": "sabuj", "tasks": [], "completed": []}}
    json.dump(users, open(USERS_FILE, "w"), indent=4)


def load_users():
    users = json.load(open(USERS_FILE, "r"))
    changed = False

    for u in users:
        for k in DEFAULT_STRUCTURE:
            if k not in users[u]:
                users[u][k] = DEFAULT_STRUCTURE[k]
                changed = True

    if changed:
        save_users(users)

    return users


def save_users(users):
    json.dump(users, open(USERS_FILE, "w"), indent=4)


# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if user in users and users[user]["password"] == pwd:
            st.session_state.logged = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("❌ Wrong username or password")


# ---------------- UI STYLE (after login only) ----------------
def load_style():
    st.markdown("""
        <style>
        .task-card {
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 4px 10px #d1d1d1;
            margin-bottom: 15px;
        }
        .task-title { font-size: 20px; font-weight: bold; }
        .task-info { font-size: 14px; margin-top: 8px; }

        .stButton > button {
            border-radius: 8px;
            padding: 6px 14px;
            transition: 0.2s;
            border: 1px solid #cccccc;
        }
        .stButton > button:hover {
            transform: scale(0.97);
            background: #efefef;
        }
        </style>
    """, unsafe_allow_html=True)


# ---------------- ADD TASK ----------------
def add_task_page():
    users = load_users()
    username = st.session_state.user
    tasks = users[username]["tasks"]

    st.subheader("➕ Add New Task")

    with st.form("addf"):
        title = st.text_input("Task Title")
        desc = st.text_area("Description")
        start = st.date_input("Start Date", date.today())
        end = st.date_input("End Date", date.today())
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        assigned = st.text_input("Assigned By")

        if st.form_submit_button("Save"):
            if not title:
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
                st.rerun()


# ---------------- ACTIVE TASKS ----------------
def task_list_page():
    users = load_users()
    username = st.session_state.user
    tasks = users[username]["tasks"]
    completed = users[username]["completed"]

    st.subheader("📝 Active Tasks")

    if not tasks:
        st.info("No Active Tasks")
        return

    for i, t in enumerate(tasks):
        pcolor = {"High": "red", "Medium": "orange", "Low": "green"}[t["Priority"]]
        scolor = "blue" if t["Status"] == "Running" else "orange"

        st.markdown(f"""
            <div class="task-card">
                <div class="task-title">{t['Task']}</div>
                <div class="task-info">
                    {t['Description']}<br>
                    Start: {t['Start']} | End: {t['End']}<br>
                    <b>Status:</b> <span style='color:{scolor}'>{t['Status']}</span> |
                    <b>Priority:</b> <span style='color:{pcolor}'>{t['Priority']}</span> |
                    <b>Assigned By:</b> {t['AssignedBy']}
                </div>
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)

        if c1.button("✏️ Edit", key=f"e{i}"):
            st.session_state.edit = i

        if c2.button("🗑 Delete", key=f"d{i}"):
            tasks.pop(i)
            save_users(users)
            st.rerun()

        if c3.button("✔ Complete", key=f"c{i}"):
            completed.insert(0, t)
            tasks.pop(i)
            save_users(users)
            st.rerun()

        if c4.button("🏃 Running", key=f"r{i}"):
            tasks[i]["Status"] = "Running"
            save_users(users)
            st.rerun()

    # ----------- EDIT MODE -----------
    if "edit" in st.session_state:
        idx = st.session_state.edit
        t = tasks[idx]

        st.subheader("✏️ Edit Task")

        with st.form("editf"):
            nt = st.text_input("Title", t["Task"])
            nd = st.text_area("Description", t["Description"])
            ns = st.date_input("Start", date.fromisoformat(t["Start"]))
            ne = st.date_input("End", date.fromisoformat(t["End"]))
            np = st.selectbox("Priority", ["High", "Medium", "Low"],
                              index=["High", "Medium", "Low"].index(t["Priority"]))
            na = st.text_input("Assigned By", t["AssignedBy"])

            if st.form_submit_button("Save Changes"):
                tasks[idx] = {
                    "Task": nt,
                    "Description": nd,
                    "Start": str(ns),
                    "End": str(ne),
                    "Status": t["Status"],
                    "Priority": np,
                    "AssignedBy": na,
                }
                save_users(users)
                st.session_state.edit = None
                st.success("Updated!")
                st.rerun()


# ---------------- COMPLETED TASKS ----------------
def completed_page():
    users = load_users()
    username = st.session_state.user
    completed = users[username]["completed"]

    st.subheader("✅ Completed Tasks")

    if not completed:
        st.info("No Completed Tasks")
        return

    for t in completed:
        st.markdown(f"""
            <div class="task-card">
                <div class="task-title">{t['Task']}</div>
                <div class="task-info">
                    {t['Description']}<br>
                    <b>Status:</b> <span style='color:green'>Completed</span>
                </div>
            </div>
        """, unsafe_allow_html=True)


# ---------------- CSV EXPORT ----------------
def csv_page():
    users = load_users()
    username = st.session_state.user
    all_tasks = users[username]["tasks"] + users[username]["completed"]

    st.subheader("⬇ Export CSV")

    if not all_tasks:
        st.info("No tasks available")
        return

    df = pd.DataFrame(all_tasks)
    st.download_button("Download CSV", df.to_csv(index=False), "tasks.csv")


# ---------------- PASSWORD CHANGE ----------------
def password_page():
    users = load_users()
    username = st.session_state.user

    st.subheader("🔑 Change Password")

    old = st.text_input("Old Password", type="password")
    new = st.text_input("New Password", type="password")
    c = st.text_input("Confirm Password", type="password")

    if st.button("Update"):
        if users[username]["password"] != old:
            st.error("Wrong old password")
        elif new != c:
            st.error("Password mismatch")
        else:
            users[username]["password"] = new
            save_users(users)
            st.success("Password Updated!")


# ---------------- MAIN APP ----------------
if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    login_page()

else:
    load_style()

    st.sidebar.title("📌 Menu")
    page = st.sidebar.radio("", ["Add Task", "Active Tasks", "Completed Tasks", "CSV Export", "Password Change", "Logout"])

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
        st.rerun()
