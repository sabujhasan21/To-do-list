import streamlit as st
import pandas as pd
from datetime import date
import json
import os

st.set_page_config(page_title="Daily To-Do List", layout="wide")

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


# ------------------ BACKGROUND & CSS ------------------
def set_background():
    st.markdown(
        """
        <style>
        body { background-color: #f5f5f5; color: #111; }
        .stSidebar { background-color: #e6e6e6; }
        .task-card {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 2px 2px 5px #ccc;
        }
        .task-title { font-size:20px; font-weight:bold; }
        .task-desc { font-size:14px; color:#333; }
        .task-info { font-size:13px; color:#555; }
        .task-buttons button {
            border-radius:5px;
            padding:5px 8px;
            margin-right:5px;
            border:none;
            cursor:pointer;
            transition:0.3s;
        }
        .edit-btn { background-color:#1976D2; color:white;}
        .edit-btn:hover { background-color:#0D47A1;}
        .delete-btn { background-color:#D32F2F; color:white;}
        .delete-btn:hover { background-color:#B71C1C;}
        .complete-btn { background-color:#388E3C; color:white;}
        .complete-btn:hover { background-color:#1B5E20;}
        .running-btn { background-color:#FBC02D; color:white;}
        .running-btn:hover { background-color:#F57F17;}
        </style>
        """, unsafe_allow_html=True
    )


def dark_mode_toggle():
    dark = st.sidebar.checkbox("🌙 Dark Mode", value=False)
    if dark:
        st.markdown(
            """
            <style>
            body { background-color: #111 !important; color: white !important; }
            .task-card { background-color: #222 !important; color:white; box-shadow:2px2px5px #000;}
            .stSidebar { background-color: #333 !important; color: white !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )


# ------------------ LOGOUT ------------------
def logout_button():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


# ------------------ DISPLAY TASK CARDS ------------------
def display_tasks_cards(tasks):
    if len(tasks) == 0:
        st.warning("No tasks found.")
        return

    users = load_users()
    username = st.session_state.user

    for i, t in enumerate(tasks):
        priority_color = {"High": "red", "Medium": "orange", "Low": "green"}.get(t.get("Priority", "Low"), "black")
        status_color = {"Pending": "orange", "Running": "blue", "Completed": "green", "Overdue": "red"}.get(t.get("Status", "Pending"), "black")

        st.markdown(
            f"""
            <div class="task-card">
                <div class="task-title">{t['Task']}</div>
                <div class="task-desc">{t['Description']}</div>
                <div class="task-info">
                    Start: {t['Start']} | End: {t['End']} | 
                    Status: <span style='color:{status_color}'>{t['Status']}</span> |
                    Priority: <span style='color:{priority_color}'>{t['Priority']}</span> |
                    Assigned By: {t.get('AssignedBy','')}
                </div>
                <div class="task-buttons">
                    <button class="edit-btn" onclick="window.location.reload();">✏️ Edit</button>
                    <button class="delete-btn" onclick="window.location.reload();">🗑️ Delete</button>
                    <button class="complete-btn" onclick="window.location.reload();">✅ Complete</button>
                    <button class="running-btn" onclick="window.location.reload();">🏃 Running</button>
                </div>
            </div>
            """, unsafe_allow_html=True
        )


# ------------------ TASKS PAGE ------------------
def tasks_page():
    set_background()
    st.title("📝 Daily To-Do List")
    users = load_users()
    username = st.session_state.user
    tasks = users[username]["tasks"]

    st.subheader("➕ Add New Task")
    with st.form("add_task_form"):
        title = st.text_input("Task Title")
        desc = st.text_area("Description")
        start = st.date_input("Start Date", date.today())
        end = st.date_input("End Date", date.today())
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        assigned_by = st.text_input("Assigned By", "")
        submitted = st.form_submit_button("Save Task")
        if submitted:
            if title:
                new_task = {
                    "Task": title,
                    "Description": desc,
                    "Start": str(start),
                    "End": str(end),
                    "Status": "Pending",
                    "Priority": priority,
                    "AssignedBy": assigned_by
                }
                tasks.insert(0, new_task)
                users[username]["tasks"] = tasks
                save_users(users)
                st.success("Task added successfully!")
                st.rerun()
            else:
                st.error("Task title required.")

    st.markdown("---")

    # Filter by Year + Month
    st.subheader("Filter Tasks by Year and Month")
    years = sorted(list({date.fromisoformat(t["Start"]).year for t in tasks}), reverse=True)
    if years:
        selected_year = st.selectbox("Year", years)
        months = sorted(list({date.fromisoformat(t["Start"]).month for t in tasks if date.fromisoformat(t["Start"]).year == selected_year}))
        selected_month = st.selectbox("Month", months, format_func=lambda x: date(1900, x, 1).strftime("%B"))
        filtered_tasks = [t for t in tasks if date.fromisoformat(t["Start"]).year == selected_year and date.fromisoformat(t["Start"]).month == selected_month]
        display_tasks_cards(filtered_tasks)
    else:
        st.warning("No tasks yet.")


# ------------------ CSV PAGE ------------------
def csv_page():
    set_background()
    st.title("⬇ Download Tasks as CSV")
    users = load_users()
    username = st.session_state.user
    tasks = users[username]["tasks"]

    if len(tasks) == 0:
        st.warning("No tasks to download.")
        return

    st.subheader("Select Date Range")
    start_date = st.date_input("Start Date", date.today())
    end_date = st.date_input("End Date", date.today())

    filtered_tasks = [t for t in tasks if start_date <= date.fromisoformat(t["Start"]) <= end_date]

    if len(filtered_tasks) == 0:
        st.warning("No tasks in this date range.")
        return

    df = pd.DataFrame(filtered_tasks)
    csv_data = df.to_csv(index=False)
    st.download_button("Download CSV", csv_data, f"tasks_{start_date}_to_{end_date}.csv")


# ------------------ PASSWORD PAGE ------------------
def password_page():
    set_background()
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


# ------------------ RUN APP ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    dark_mode_toggle()
    logout_button()
    menu = st.sidebar.radio("Pages", ["Tasks", "CSV Download", "Password Change"])
    if menu == "Tasks":
        tasks_page()
    elif menu == "CSV Download":
        csv_page()
    elif menu == "Password Change":
        password_page()
