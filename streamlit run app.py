import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Daily To Do List", layout="centered")

# ===================== File Handler =====================
DATA_FILE = "users.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===================== Notification System =====================
def notify(message, color="#4CAF50"):
    notification_html = f"""
    <div style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: {color};
        padding: 18px 30px;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        box-shadow: 0px 0px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: fadeInOut 1.8s ease-in-out;
    ">
        {message}
    </div>

    <style>
    @keyframes fadeInOut {
        0% {{opacity: 0;}}
        15% {{opacity: 1;}}
        85% {{opacity: 1;}}
        100% {{opacity: 0;}}
    }}
    </style>
    """
    st.markdown(notification_html, unsafe_allow_html=True)

# ===================== Login System =====================
users = load_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

def login_page():
    st.markdown("<h1 style='text-align:center;'>Daily To Do List</h1>", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            notify("Login Successful")
        else:
            notify("Invalid username or password", "#E53935")

    st.write("---")

    st.subheader("Create New Account")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Create Account", use_container_width=True):
        if new_user in users:
            notify("User already exists!", "#E53935")
        else:
            users[new_user] = {"password": new_pass, "tasks": [], "completed": []}
            save_data(users)
            notify("Account Created Successfully")

# ===================== Task Functions =====================
def add_task_ui():
    st.subheader("Create New Task")

    title = st.text_input("Task Title")
    details = st.text_area("Task Details")

    if st.button("Save Task", use_container_width=True):
        if title.strip() == "":
            notify("Title cannot be empty", "#E53935")
        else:
            users[st.session_state.username]["tasks"].append({
                "title": title,
                "details": details,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            save_data(users)
            notify("Task Saved Successfully")

def task_list_ui():
    st.subheader("Your Tasks")

    tasks = users[st.session_state.username]["tasks"]

    if len(tasks) == 0:
        st.info("No tasks available.")
        return

    for idx, t in enumerate(tasks):

        with st.container():
            st.markdown("""
            <div style="
                padding: 15px;
                border-radius: 12px;
                background: white;
                box-shadow: 0 0 8px rgba(0,0,0,0.15);
                margin-bottom: 12px;">
            """, unsafe_allow_html=True)

            st.markdown(f"### {t['title']}")
            st.write(t["details"])
            st.caption(f"Created: {t['time']}")

            col1, col2, col3 = st.columns(3)

            if col1.button("Complete", key=f"comp{idx}"):
                users[st.session_state.username]["completed"].append(t)
                users[st.session_state.username]["tasks"].pop(idx)
                save_data(users)
                notify("Task Completed")
                st.rerun()

            if col2.button("Edit", key=f"edit{idx}"):
                st.session_state.editing = idx
                st.rerun()

            if col3.button("Delete", key=f"del{idx}"):
                users[st.session_state.username]["tasks"].pop(idx)
                save_data(users)
                notify("Task Deleted", "#E53935")
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

def edit_task_ui():
    idx = st.session_state.editing
    task = users[st.session_state.username]["tasks"][idx]

    st.subheader("Edit Task")

    title = st.text_input("Task Title", value=task["title"])
    details = st.text_area("Task Details", value=task["details"])

    if st.button("Save Changes", use_container_width=True):
        users[st.session_state.username]["tasks"][idx]["title"] = title
        users[st.session_state.username]["tasks"][idx]["details"] = details
        save_data(users)
        notify("Task Updated")
        del st.session_state["editing"]
        st.rerun()

def completed_ui():
    st.subheader("Completed Tasks")
    completed = users[st.session_state.username]["completed"]

    if len(completed) == 0:
        st.info("No completed tasks yet.")
        return

    for t in completed:
        with st.container():
            st.markdown("""
                <div style="padding: 15px; border-radius: 12px;
                background: #E3F7E1; box-shadow: 0 0 6px rgba(0,0,0,0.1);
                margin-bottom: 12px;">
            """, unsafe_allow_html=True)

            st.markdown(f"### ✅ {t['title']}")
            st.write(t["details"])
            st.caption(f"Completed: {t['time']}")

            st.markdown("</div>", unsafe_allow_html=True)

# ===================== Main App =====================
if not st.session_state.logged_in:
    login_page()
else:
    menu = st.sidebar.radio("Menu", ["Create Task", "Task List", "Completed Tasks"])

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        notify("Logged Out", "#E53935")
        st.rerun()

    if menu == "Create Task":
        add_task_ui()

    elif menu == "Task List":
        if "editing" in st.session_state:
            edit_task_ui()
        else:
            task_list_ui()

    elif menu == "Completed Tasks":
        completed_ui()
