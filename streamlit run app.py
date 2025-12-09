import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
import json
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced To-Do Manager", layout="wide")

# ---------------------- LOAD USERS -----------------------
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        # default user for first time
        users = {
            "sabuj2025": {"password": "sabuj"}
        }
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
        return users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# ---------------------- DARK MODE -----------------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode):
    st.session_state.dark_mode = True
    st.markdown("<style>body{background-color:#1E1E1E;color:white;}</style>", unsafe_allow_html=True)
else:
    st.session_state.dark_mode = False

# ---------------------- LOGIN SYSTEM -----------------------
def login_page():
    st.title("🔐 Login Required")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()

username = st.session_state.username

# ---------------------- NAVIGATION BAR -----------------------
st.sidebar.title(f"👤 Logged in as: {username}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.radio("Menu", ["📋 Tasks", "📊 Dashboard", "🧑‍🤝‍🧑 Manage Users", "🔑 Change Password"])

# ---------------------- LOAD TASKS -----------------------
DATA_FILE = f"tasks_{username}.json"

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.tasks, f, indent=4)

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

today = date.today()


# ========================== PAGE 1 → TASK PAGE ==========================
if menu == "📋 Tasks":

    st.title("📝 To-Do Manager")

    st.subheader("Add or Edit Task")

    def task_form(edit=False):
        if edit:
            task_data = st.session_state.tasks[st.session_state.edit_index]
            title = st.text_input("Task Title", task_data["Task"])
            desc = st.text_area("Description", task_data.get("Description", ""))
            start = st.date_input("Start Date", datetime.strptime(task_data["Start"], "%Y-%m-%d").date())
            end = st.date_input("End Date", datetime.strptime(task_data["End"], "%Y-%m-%d").date())
        else:
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

                if edit:
                    st.session_state.tasks[st.session_state.edit_index] = new_task
                    st.session_state.edit_index = None
                    st.success("Task updated!")
                else:
                    st.session_state.tasks.append(new_task)
                    st.success("Task added!")

                save_tasks()
                st.rerun()
            else:
                st.error("Task title required.")

    if st.session_state.edit_index is not None:
        task_form(edit=True)
    else:
        task_form(edit=False)

    st.subheader("Your Tasks")

    for t in st.session_state.tasks:
        if t["Status"] != "Completed" and date.fromisoformat(t["End"]) < today:
            t["Status"] = "Overdue"
    save_tasks()

    for i, t in enumerate(st.session_state.tasks):
        st.markdown(f"### {t['Task']}")
        st.write(f"📄 {t['Description']}")
        st.write(f"📅 {t['Start']} → {t['End']}")
        st.write(f"🔖 Status: **{t['Status']}**")

        c1, c2, c3 = st.columns(3)

        if c1.button(f"Edit {i}"):
            st.session_state.edit_index = i
            st.rerun()

        if c2.button(f"Delete {i}"):
            st.session_state.tasks.pop(i)
            save_tasks()
            st.rerun()

        if c3.button(f"Complete {i}"):
            st.session_state.tasks[i]["Status"] = "Completed"
            save_tasks()
            st.rerun()

        st.markdown("---")

    # CSV Download
    if st.session_state.tasks:
        df = pd.DataFrame(st.session_state.tasks)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        st.download_button("⬇ Download CSV", buffer.getvalue(), "tasks.csv", "text/csv")


# ========================== PAGE 2 → DASHBOARD ==========================
elif menu == "📊 Dashboard":
    st.title("📊 Task Dashboard")

    status_counts = {
        "Completed": sum(t["Status"] == "Completed" for t in st.session_state.tasks),
        "Pending": sum(t["Status"] == "Pending" for t in st.session_state.tasks),
        "Overdue": sum(t["Status"] == "Overdue" for t in st.session_state.tasks),
    }

    labels = list(status_counts.keys())
    values = list(status_counts.values())

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    ax.set_title("Task Status Overview")

    st.pyplot(fig)


# ========================== PAGE 3 → MANAGE USERS ==========================
elif menu == "🧑‍🤝‍🧑 Manage Users":
    st.title("👥 Manage Users (Admin Only)")

    if username != "sabuj2025":
        st.warning("Only admin can manage users.")
        st.stop()

    st.subheader("Add New User")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Add User"):
        if new_user and new_pass:
            users[new_user] = {"password": new_pass}
            save_users(users)
            st.success("User added!")
        else:
            st.error("Please enter username & password")


# ========================== PAGE 4 → PASSWORD CHANGE ==========================
elif menu == "🔑 Change Password":
    st.title("🔑 Change Your Password")

    old = st.text_input("Old Password", type="password")
    new1 = st.text_input("New Password", type="password")
    new2 = st.text_input("Confirm New Password", type="password")

    if st.button("Change Password"):
        if users[username]["password"] != old:
            st.error("Old password incorrect!")
        elif new1 != new2:
            st.error("New passwords do not match!")
        else:
            users[username]["password"] = new1
            save_users(users)
            st.success("Password updated successfully!")
