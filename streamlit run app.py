import streamlit as st
import json
import os
from datetime import datetime

# -----------------------------
# JSON File Handling
# -----------------------------
DATA_FILE = "users.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

users = load_data()

# -----------------------------
# Fix Missing Keys (KEYERROR FIX)
# -----------------------------
def ensure_user_structure(username):
    if username not in users:
        users[username] = {}

    if "password" not in users[username]:
        users[username]["password"] = ""

    if "tasks" not in users[username]:
        users[username]["tasks"] = []

    if "completed" not in users[username]:
        users[username]["completed"] = []

    save_data(users)

# -----------------------------
# Streamlit Session
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# -----------------------------
# Login Page
# -----------------------------
def login_page():
    st.title("Daily To Do List")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            ensure_user_structure(username)
            st.rerun()
        else:
            st.error("Invalid username or password")

# -----------------------------
# Sidebar
# -----------------------------
def menu_sidebar():
    st.sidebar.title("Menu")

    choice = st.sidebar.radio(
        "Select",
        ["Add Task", "Your Tasks", "Completed Tasks"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    return choice

# -----------------------------
# Add Task Page
# -----------------------------
def add_task():
    st.title("Add New Task")

    task = st.text_input("Task Name")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])

    if st.button("Add"):
        if task.strip() == "":
            st.error("Task cannot be empty")
            return

        username = st.session_state.username

        new_task = {
            "title": task,
            "priority": priority,
            "status": "Running",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        users[username]["tasks"].insert(0, new_task)
        save_data(users)
        st.success("Task Added!")
        st.rerun()

# -----------------------------
# Task Display Table
# -----------------------------
def show_tasks():
    st.title("Your Tasks")

    username = st.session_state.username
    tasks = users[username]["tasks"]

    if st.session_state.edit_mode:
        edit_task()
        return

    if len(tasks) == 0:
        st.info("No tasks added yet.")
        return

    for i, task in enumerate(tasks):
        col1, col2, col3, col4, col5 = st.columns([4, 2, 1, 1, 1])

        with col1:
            st.write(f"**{task['title']}**")
            st.caption(f"{task['priority']} | {task['created']}")

        with col2:
            st.write(task["status"])

        with col3:
            if st.button("✏", key=f"edit{i}"):
                st.session_state.edit_mode = True
                st.session_state.edit_index = i
                st.rerun()

        with col4:
            if st.button("❌", key=f"del{i}"):
                users[username]["tasks"].pop(i)
                save_data(users)
                st.rerun()

        with col5:
            if st.button("✔", key=f"comp{i}"):
                task["status"] = "Completed"
                users[username]["completed"].append(task)
                users[username]["tasks"].pop(i)
                save_data(users)
                st.rerun()

        st.markdown("---")

# -----------------------------
# Edit Task Page
# -----------------------------
def edit_task():
    username = st.session_state.username
    i = st.session_state.edit_index
    task = users[username]["tasks"][i]

    st.title("Edit Task")

    new_title = st.text_input("Task Name", value=task["title"])
    new_priority = st.selectbox(
        "Priority",
        ["High", "Medium", "Low"],
        index=["High", "Medium", "Low"].index(task["priority"])
    )

    if st.button("Save"):
        task["title"] = new_title
        task["priority"] = new_priority
        save_data(users)
        st.session_state.edit_mode = False
        st.rerun()

    if st.button("Cancel"):
        st.session_state.edit_mode = False
        st.rerun()

# -----------------------------
# Completed Tasks Page
# -----------------------------
def completed_tasks():
    st.title("Completed Tasks")

    username = st.session_state.username
    completed = users[username]["completed"]

    if len(completed) == 0:
        st.info("No completed tasks.")
        return

    for task in completed:
        st.success(f"✔ {task['title']} ({task['priority']}) — {task['created']}")
        st.markdown("---")

# -----------------------------
# MAIN APP
# -----------------------------
if st.session_state.logged_in:
    ensure_user_structure(st.session_state.username)

    page = menu_sidebar()

    if page == "Add Task":
        add_task()
    elif page == "Your Tasks":
        show_tasks()
    elif page == "Completed Tasks":
        completed_tasks()
else:
    login_page()
