import streamlit as st
import pandas as pd
from datetime import date
import json
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced To-Do Manager", layout="wide")

USERS_FILE = "users.json"

# ------------------ USERS FILE ------------------
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
            if "tasks" not in users[username]:
                users[username]["tasks"] = []
                save_users(users)
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.info("Default → Username: sabuj2025 | Password: sabuj")


# ------------------ DARK MODE ------------------
def dark_mode_toggle():
    dark = st.sidebar.checkbox("🌙 Dark Mode", value=False)
    if dark:
        st.markdown("""
            <style>
            body { background-color: #111 !important; color: white !important; }
            .stButton button { background-color: #444 !important; color: white !important; }
            </style>
        """, unsafe_allow_html=True)


# ------------------ LOGOUT ------------------
def logout_button():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


# ------------------ TASKS PAGE ------------------
def tasks_page():
    st.title("📝 Tasks")
    users = load_users()
    username = st.session_state.user
    tasks = users[username]["tasks"]

    # Add Task
    st.subheader("➕ Add New Task")
    title = st.text_input("Task Title")
    desc = st.text_area("Description")
    start = st.date_input("Start Date", date.today())
    end = st.date_input("End Date", date.today())
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    assigned_by = st.text_input("Assigned By", "")

    if st.button("Save Task"):
        if title:
            tasks.append({
                "Task": title,
                "Description": desc,
                "Start": str(start),
                "End": str(end),
                "Status": "Pending",
                "Priority": priority,
                "AssignedBy": assigned_by
            })
            users[username]["tasks"] = tasks
            save_users(users)
            st.success("Task added successfully!")
            st.rerun()
        else:
            st.error("Task title required.")

    st.markdown("---")
    st.subheader("📋 Your Tasks")

    # Sort tasks
    tasks = sorted(tasks, key=lambda x: x["End"])
    users[username]["tasks"] = tasks
    save_users(users)

    # Show Tasks
    for i, t in enumerate(tasks):
        # Priority color
        color = {"High": "red", "Medium": "orange", "Low": "green"}.get(t.get("Priority", "Low"), "blue")
        st.markdown(f"### {t['Task']}  <span style='color:{color}'>({t.get('Priority','Low')})</span>", unsafe_allow_html=True)
        st.write(f"📖 {t['Description']}")
        st.write(f"📅 {t['Start']} ➜ {t['End']}")
        st.write(f"Status: **{t['Status']}** | Assigned By: {t.get('AssignedBy','')}")

        # Buttons Right side
        c1, c2, c3, c4 = st.columns([1,1,1,1])
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
        if c4.button(f"Running {i}"):
            tasks[i]["Status"] = "Running"
            users[username]["tasks"] = tasks
            save_users(users)
            st.rerun()

        st.markdown("---")

    # Edit Task
    if "edit_index" in st.session_state and st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        t = tasks[idx]
        st.subheader("✏️ Edit Task")
        new_title = st.text_input("Task Title", t["Task"])
        new_desc = st.text_area("Description", t["Description"])
        new_start = st.date_input("Start Date", date.fromisoformat(t["Start"]))
        new_end = st.date_input("End Date", date.fromisoformat(t["End"]))
        new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High","Medium","Low"].index(t.get("Priority","Low")))
        new_assigned_by = st.text_input("Assigned By", t.get("AssignedBy",""))

        if st.button("Save Changes"):
            tasks[idx] = {
                "Task": new_title,
                "Description": new_desc,
                "Start": str(new_start),
                "End": str(new_end),
                "Status": t["Status"],
                "Priority": new_priority,
                "AssignedBy": new_assigned_by
            }
            users[username]["tasks"] = tasks
            save_users(users)
            st.session_state.edit_index = None
            st.success("Task updated!")
            st.rerun()


# ------------------ PASSWORD PAGE ------------------
def password_page():
    st.title("🔑 Change Password")
    users = load_users()
    username = st.session_state.user

    old = st.text_input("Old Password", type="password")
    new = st.text_input("New Password", type="password")
    confirm = st.text_input("Confirm New Password", type="password")

    if st.button("Update Password"):
        if users[username]["password"] != old:
            st.error("Old password incorrect!")
        elif new != confirm:
            st.error("Passwords do not match!")
        else:
            users[username]["password"] = new
            save_users(users)
            st.success("Password updated successfully!")


# ------------------ DASHBOARD ------------------
def dashboard_page():
    st.title("📊 Task Dashboard")
    users = load_users()
    username = st.session_state.user
    tasks = users[username]["tasks"]

    if len(tasks) == 0:
        st.warning("No tasks available for chart.")
    else:
        df = pd.DataFrame(tasks)
        counts = df["Status"].value_counts()
        if len(counts) > 0:
            fig, ax = plt.subplots(figsize=(4,4))
            ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
            ax.set_title("Task Status Distribution")
            st.pyplot(fig)
        else:
            st.warning("Not enough data for chart.")


# ------------------ CSV PAGE ------------------
def csv_page():
    st.title("⬇ Download Tasks as CSV")
    users = load_users()
    username = st.session_state.user
    tasks = users[username]["tasks"]
    if len(tasks) > 0:
        df = pd.DataFrame(tasks)
        st.download_button("Download CSV", df.to_csv(index=False), "tasks.csv")
    else:
        st.warning("No tasks to download.")


# ------------------ RUN APP ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    dark_mode_toggle()
    logout_button()
    menu = st.sidebar.radio("Pages", ["Tasks", "Dashboard", "Password Change", "CSV Download"])
    if menu == "Tasks":
        tasks_page()
    elif menu == "Dashboard":
        dashboard_page()
    elif menu == "Password Change":
        password_page()
    elif menu == "CSV Download":
        csv_page()
