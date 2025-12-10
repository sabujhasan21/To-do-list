import streamlit as st
import pandas as pd
from datetime import date
import json
import os

st.set_page_config(page_title="Daily To-Do List", layout="wide")

USERS_FILE = "users.json"

# ------------------ INIT USERS FILE ------------------
DEFAULT_STRUCTURE = {
    "password": "",
    "tasks": [],
    "completed": []
}

if not os.path.exists(USERS_FILE):
    users = {"sabuj2025": {"password": "sabuj", "tasks": [], "completed": []}}
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def load_users():
    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    # FIX: Ensures all needed keys exist for every user
    changed = False
    for u, data in users.items():
        for key in ["password", "tasks", "completed"]:
            if key not in data:
                users[u][key] = DEFAULT_STRUCTURE[key]
                changed = True
    if changed:
        save_users(users)

    return users


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ------------------ LOGIN PAGE ------------------
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
            st.error("❌ Invalid username or password")


# ------------------ UI STYLE ------------------
def page_style():
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )


# ------------------ ADD TASK ------------------
def add_task_page():
    users = load_users()
    username = st.session_state.user

    # SAFETY FIX: Ensure structure exists
    if "tasks" not in users[username]:
        users[username]["tasks"] = []
    save_users(users)

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
                st.rerun()


# ------------------ ACTIVE TASK LIST ------------------
def task_list_page():
    users = load_users()
    username = st.session_state.user

    # FIX: Always ensure keys e
