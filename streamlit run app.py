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
# Initialize Streamlit Session
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# -----------------------------
# Login Page
# -----------------------------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.write("If new user → It will auto-create your account.")

# -----------------------------
# Create new user if not exists
# -----------------------------
def create_user(username):
    users[username] = {
        "password": "",
        "tasks": [],
        "completed": []
    }
    save_data(users)

# -----------------------------
# App Sidebar
# -----------------------------
def app_sidebar():
    st.sidebar.title("📌 DAILY TO DO LIST")

    choice = st.sidebar.radio(
        "Menu",
        ["➕ Add Task", "📄 Your Tasks", "✅ Completed Tasks"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    return choice

# -----------------------------
# Add Task Page
# -----------------------------
def add_task_page():
    st.title("➕ Add New Task")

    task_title = st.text_input("Task Title")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])

    if st.button("Add Task"):
        if task_title.strip() == "":
            st.error("Task cannot be empty")
            return

        username = st.session_state.username
        new_task = {
            "title": task_title,
            "priority": priority,
            "status": "Running",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        users[username]["tasks"].insert(0, new_task)
        save_data(users)
        st.success("Task added successfully!")
        st.rerun()

# -----------------------------
# Display Task Table
# -----------------------------
def display_task_table(task_list):
    if len(task_list) == 0:
        st.info("No tasks found.")
        return

    for i, task in enumerate(task_list):
        col1, col2, col3, col4 = st.columns([4, 2, 1, 1])

        with col1:
            st.write(f"**{task['title']}**")
            st.caption(f"Priority: {task['priority']} • Created: {task['created']}")

        with col2:
            st.write(task["status"])

        # RUNNING TASKS ONLY
        if task["status"] != "Completed":
            with col3:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.session_state.show_edit = True
                    st.rerun()

            with col4:
                if st.button("❌", key=f"delete_{i}"):
                    username = st.session_state.username
                    users[username]["tasks"].pop(i)
                    save_data(users)
                    st.rerun()

        # COMPLETE BUTTON UNDER TABLE
        c1, c2, _ = st.columns([1, 1, 4])
        if task["status"] != "Completed":
            if c1.button("✔ Complete", key=f"complete_{i}"):
                username = st.session_state.username
                task["status"] = "Completed"
                users[username]["completed"].append(task)
                users[username]["tasks"].pop(i)
                save_data(users)
                st.rerun()

        st.markdown("---")

# -----------------------------
# Edit Task Window
# -----------------------------
def edit_task_window():
    username = st.session_state.username
    i = st.session_state.edit_index

    task = users[username]["tasks"][i]

    st.subheader("✏ Edit Task")

    new_title = st.text_input("Task Name", value=task["title"])
    new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High","Medium","Low"].index(task["priority"]))

    if st.button("Save"):
        task["title"] = new_title
        task["priority"] = new_priority
        save_data(users)
        st.session_state.show_edit = False
        st.rerun()

    if st.button("Cancel"):
        st.session_state.show_edit = False
        st.rerun()

# -----------------------------
# Tasks Page
# -----------------------------
def task_list_page():
    st.title("📄 Your Tasks")

    username = st.session_state.username

    if "tasks" not in users[username]:
        users[username]["tasks"] = []
        save_data(users)

    tasks = users[username]["tasks"]

    if "show_edit" in st.session_state and st.session_state.show_edit:
        edit_task_window()
    else:
        display_task_table(tasks)

# -----------------------------
# Completed Tasks Page
# -----------------------------
def completed_page():
    st.title("✅ Completed Tasks (Permanent Log)")

    username = st.session_state.username

    completed = users[username].get("completed", [])

    if len(completed) == 0:
        st.info("No completed tasks yet.")
        return

    for task in completed:
        st.success(f"✔ {task['title']} — {task['created']}")
        st.caption(f"Priority: {task['priority']}")
        st.markdown("---")

# -----------------------------
# MAIN APP
# -----------------------------
if st.session_state.logged_in:
    username = st.session_state.username
    if username not in users:
        create_user(username)

    menu = app_sidebar()

    if menu == "➕ Add Task":
        add_task_page()

    elif menu == "📄 Your Tasks":
        task_list_page()

    elif menu == "✅ Completed Tasks":
        completed_page()

else:
    login_page()
