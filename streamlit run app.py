import streamlit as st
import pandas as pd
from datetime import date
import json
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced To-Do Manager", layout="wide")

# ------------------ USERS FILE ------------------
USERS_FILE = "users.json"

# Create default users file if not exists
if not os.path.exists(USERS_FILE):
    users = {
        "sabuj2025": {"password": "sabuj", "tasks": []}
    }
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ------------------ LOGIN ------------------
def login_page():
    st.title("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            # Ensure tasks key exists
            if "tasks" not in users[username]:
                users[username]["tasks"] = []
                save_users(users)
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.info("Default → Username: sabuj2025 | Password: sabuj")


def logout_button():
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


# ------------------ DARK MODE ------------------
def dark_mode():
    dark = st.checkbox("🌙 Dark Mode", value=False)
    if dark:
        st.markdown("""
            <style>
            body { background-color: #111 !important; color: white !important; }
            .stButton button { background-color: #444 !important; color: white !important; }
            </style>
        """, unsafe_allow_html=True)


# ------------------ MAIN APP ------------------
def todo_app():
    st.title("📝 Advanced To-Do Manager")
    logout_button()
    dark_mode()
    st.write(f"👤 Logged in as: **{st.session_state.user}**")

    users = load_users()
    username = st.session_state.user

    if username not in users:
        st.error("User not found! Please login again.")
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    if "tasks" not in users[username]:
        users[username]["tasks"] = []
        save_users(users)

    tasks = users[username]["tasks"]

    # ------------------ PASSWORD CHANGE ------------------
    with st.expander("🔒 Change Password"):
        old = st.text_input("Old Password", type="password")
        new = st.text_input("New Password", type="password")
        if st.button("Update Password"):
            if old == users[username]["password"]:
                users[username]["password"] = new
                save_users(users)
                st.success("Password changed!")
            else:
                st.error("Old password incorrect")

    # ------------------ ADD TASK ------------------
    st.subheader("➕ Add New Task")
    title = st.text_input("Task Title")
    desc = st.text_area("Description")
    start = st.date_input("Start Date", date.today())
    end = st.date_input("End Date", date.today())

    if st.button("Save Task"):
        if title:
            new_task = {
                "Task": title,
                "Description": desc,
                "Start": str(start),
                "End": str(end),
                "Status": "Pending"
            }
            tasks.append(new_task)
            users[username]["tasks"] = tasks
            save_users(users)
            st.success("Task added successfully!")
            st.rerun()
        else:
            st.error("Task title required.")

    st.markdown("---")
    st.subheader("📋 Your Tasks")

    # Sort tasks by End date
    tasks = sorted(tasks, key=lambda x: x["End"])
    users[username]["tasks"] = tasks
    save_users(users)

    # ------------------ SHOW TASKS ------------------
    for i, t in enumerate(tasks):
        st.markdown(f"### {t['Task']}")
        st.write(f"📖 {t['Description']}")
        st.write(f"📅 {t['Start']} ➜ {t['End']}")
        st.write(f"Status: **{t['Status']}**")

        c1, c2, c3 = st.columns(3)

        if c1.button(f"Edit {i}"):
            st.session_state.edit_index = i

        if c2.button(f"Delete {i}"):
            tasks.pop(i)
            users[username]["tasks"] = tasks
            save_users(users)
            st.rerun()

        if c3.button(f"Complete {i}"):
            tasks[i]["Status"] = "Completed"
            users[username]["tasks"] = tasks
            save_users(users)
            st.rerun()

        st.markdown("---")

    # ------------------ EDIT TASK ------------------
    if "edit_index" in st.session_state and st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        st.subheader("✏️ Edit Task")

        t = tasks[idx]

        new_title = st.text_input("Task Title", t["Task"])
        new_desc = st.text_area("Description", t["Description"])
        new_start = st.date_input("Start Date", date.fromisoformat(t["Start"]))
        new_end = st.date_input("End Date", date.fromisoformat(t["End"]))

        if st.button("Save Changes"):
            tasks[idx] = {
                "Task": new_title,
                "Description": new_desc,
                "Start": str(new_start),
                "End": str(new_end),
                "Status": t["Status"]
            }
            users[username]["tasks"] = tasks
            save_users(users)

            st.session_state.edit_index = None
            st.success("Task updated!")
            st.rerun()

    st.markdown("---")

    # ------------------ PIE CHART ------------------
    st.subheader("📊 Task Dashboard")
    if len(tasks) == 0:
        st.warning("No tasks available for chart.")
    else:
        df = pd.DataFrame(tasks)
        counts = df["Status"].value_counts()

        if len(counts) > 0:
            fig, ax = plt.subplots()
            ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
            ax.set_title("Task Status Distribution")
            st.pyplot(fig)
        else:
            st.warning("Not enough data for chart.")

    # ------------------ CSV DOWNLOAD ------------------
    if len(tasks) > 0:
        df = pd.DataFrame(tasks)
        st.download_button("⬇ Download CSV", df.to_csv(index=False), "tasks.csv")


# ------------------ RUN APP ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    todo_app()
