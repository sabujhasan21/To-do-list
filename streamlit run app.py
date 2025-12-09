import streamlit as st
import pandas as pd
import json
from datetime import date
import matplotlib.pyplot as plt
import os


# ----------------------------- USER DATABASE -----------------------------
USER_DB = "users.json"

# Create users.json file if not exists
if not os.path.exists(USER_DB):
    users = {
        "sabuj2025": {
            "password": "sabuj",
            "tasks": []
        }
    }
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)


def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)


def save_users(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------- LOGIN SYSTEM -----------------------------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()

        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

    st.info("Default user → **Username:** sabuj2025 | **Password:** sabuj")


def logout_button():
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.experimental_rerun()


# ----------------------------- DARK MODE -----------------------------
def dark_mode():
    dark = st.checkbox("🌙 Dark Mode", value=False)
    if dark:
        st.markdown("""
            <style>
            body { background-color: #111 !important; color: white !important; }
            .stButton button { background-color: #444 !important; color: white !important; }
            </style>
        """, unsafe_allow_html=True)


# ----------------------------- MAIN TODO APP -----------------------------
def todo_app():
    st.title("📝 Advanced To-Do Manager")
    logout_button()
    dark_mode()

    st.write(f"👤 Logged in as: **{st.session_state.user}**")

    users = load_users()
    tasks = users[st.session_state.user]["tasks"]

    # --------------------- PASSWORD CHANGE ---------------------
    with st.expander("🔒 Change Password"):
        old = st.text_input("Old Password", type="password")
        new = st.text_input("New Password", type="password")
        if st.button("Update Password"):
            if old == users[st.session_state.user]["password"]:
                users[st.session_state.user]["password"] = new
                save_users(users)
                st.success("Password changed!")
            else:
                st.error("Old password incorrect")

    # --------------------- ADD TASK ---------------------
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
            users[st.session_state.user]["tasks"] = tasks
            save_users(users)
            st.success("Task added successfully!")
        else:
            st.error("Task title required.")

    st.markdown("---")
    st.subheader("📋 Your Tasks")

    # Sort tasks
    tasks = sorted(tasks, key=lambda x: x["End"])

    # Save back sorted
    users[st.session_state.user]["tasks"] = tasks
    save_users(users)

    # Display tasks
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
            users[st.session_state.user]["tasks"] = tasks
            save_users(users)
            st.experimental_rerun()

        if c3.button(f"Complete {i}"):
            tasks[i]["Status"] = "Completed"
            users[st.session_state.user]["tasks"] = tasks
            save_users(users)
            st.experimental_rerun()

        st.markdown("---")

    # --------------------- EDIT TASK ---------------------
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
            users[st.session_state.user]["tasks"] = tasks
            save_users(users)

            st.session_state.edit_index = None
            st.success("Task updated!")
            st.experimental_rerun()

    st.markdown("---")

    # --------------------- PIE CHART DASHBOARD ---------------------
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

    # --------------------- DOWNLOAD CSV ---------------------
    if len(tasks) > 0:
        df = pd.DataFrame(tasks)
        st.download_button("⬇ Download CSV", df.to_csv(index=False), "tasks.csv")


# ----------------------------- APP RUN -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    todo_app()
