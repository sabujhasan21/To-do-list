import streamlit as st
import pandas as pd
from datetime import date, datetime
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


# ------------------ LOGIN PAGE ------------------
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


# ------------------ WORK-STYLE BACKGROUND ------------------
def set_background():
    st.markdown(
        """
        <style>
        body { background-color: #f5f5f5; color: #111; }
        .stButton>button { background-color: #1976D2; color: white; }
        .stTextInput>div>input, .stTextArea>div>textarea, .stDateInput>div>input {
            background-color: white; color: #111;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ------------------ DARK MODE ------------------
def dark_mode_toggle():
    dark = st.sidebar.checkbox("🌙 Dark Mode", value=False)
    if dark:
        st.markdown(
            """
            <style>
            body { background-color: #111 !important; color: white !important; }
            .stButton>button { background-color: #444 !important; color: white !important; }
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


# ------------------ DISPLAY TASKS TABLE ------------------
def display_tasks_table(tasks):
    if len(tasks) == 0:
        st.warning("No tasks found.")
        return

    # Table Header
    header_cols = st.columns([2, 3, 2, 2, 1, 1, 1, 2])
    headers = ["Task", "Description", "Start", "End", "Status", "Priority", "Assigned By", "Actions"]
    for col, h in zip(header_cols, headers):
        col.markdown(f"**{h}**")

    st.markdown("---")

    users = load_users()
    username = st.session_state.user

    # Display Rows
    for i, t in enumerate(tasks):
        row_cols = st.columns([2, 3, 2, 2, 1, 1, 1, 2])
        row_cols[0].write(t["Task"])
        row_cols[1].write(t["Description"])
        row_cols[2].write(t["Start"])
        row_cols[3].write(t["End"])

        # Status color
        status_color = {"Pending": "orange", "Running": "blue", "Completed": "green", "Overdue": "red"}.get(t["Status"], "black")
        row_cols[4].markdown(f"<span style='color:{status_color};'><b>{t['Status']}</b></span>", unsafe_allow_html=True)

        # Priority color
        priority_color = {"High": "red", "Medium": "orange", "Low": "green"}.get(t["Priority"], "black")
        row_cols[5].markdown(f"<span style='color:{priority_color};'><b>{t['Priority']}</b></span>", unsafe_allow_html=True)

        row_cols[6].write(t.get("AssignedBy", ""))

        # Action Buttons
        action_col = row_cols[7]
        c1, c2, c3, c4 = action_col.columns(4)
        if c1.button("✏️", key=f"edit{i}"):
            st.session_state.edit_index = i
        if c2.button("🗑️", key=f"del{i}"):
            tasks.pop(i)
            users[username]["tasks"] = tasks
            save_users(users)
            st.rerun()
        if c3.button("✅", key=f"comp{i}"):
            tasks[i]["Status"] = "Completed"
            users[username]["tasks"] = tasks
            save_users(users)
            st.rerun()
        if c4.button("🏃", key=f"run{i}"):
            tasks[i]["Status"] = "Running"
            users[username]["tasks"] = tasks
            save_users(users)
            st.rerun()

    # Edit Modal
    if "edit_index" in st.session_state and st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        t = tasks[idx]
        st.subheader("✏️ Edit Task")
        new_title = st.text_input("Task Title", t["Task"])
        new_desc = st.text_area("Description", t["Description"])
        new_start = st.date_input("Start Date", date.fromisoformat(t["Start"]))
        new_end = st.date_input("End Date", date.fromisoformat(t["End"]))
        new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(t.get("Priority", "Low")))
        new_assigned_by = st.text_input("Assigned By", t.get("AssignedBy", ""))

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


# ------------------ TASKS PAGE ------------------
def tasks_page():
    set_background()
    st.title("📝 Your Tasks")
    users = load_users()
    username = st.session_state.user
    tasks = users[username]["tasks"]

    # ---------------- Add Task Form ----------------
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

    # ---------------- Year + Month Filter ----------------
    st.subheader("Filter Tasks by Year and Month")
    years = sorted(list({date.fromisoformat(t["Start"]).year for t in tasks}), reverse=True)
    if not years:
        st.warning("No tasks available.")
        return
    selected_year = st.selectbox("Select Year", years)
    months = sorted(list({date.fromisoformat(t["Start"]).month for t in tasks if date.fromisoformat(t["Start"]).year == selected_year}))
    selected_month = st.selectbox("Select Month", months, format_func=lambda x: date(1900, x, 1).strftime("%B"))

    filtered_tasks = [t for t in tasks if date.fromisoformat(t["Start"]).year == selected_year and date.fromisoformat(t["Start"]).month == selected_month]

    # ---------------- Yearly Chart ----------------
    st.subheader("📊 Tasks Created per Year")
    yearly_counts = {}
    for t in tasks:
        y = date.fromisoformat(t["Start"]).year
        yearly_counts[y] = yearly_counts.get(y, 0) + 1
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(yearly_counts.keys(), yearly_counts.values(), color="skyblue")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Tasks")
    ax.set_title("Tasks Created per Year")
    st.pyplot(fig)

    # Drill-down: monthly chart
    st.subheader(f"📅 Tasks per Month in {selected_year}")
    monthly_counts = {m: 0 for m in range(1, 13)}
    for t in tasks:
        if date.fromisoformat(t["Start"]).year == selected_year:
            m = date.fromisoformat(t["Start"]).month
            monthly_counts[m] += 1
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    ax2.bar([date(1900, m, 1).strftime("%b") for m in monthly_counts.keys()], monthly_counts.values(), color="orange")
    ax2.set_title(f"Tasks per Month in {selected_year}")
    st.pyplot(fig2)

    # Display filtered tasks in table
    display_tasks_table(filtered_tasks)


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


# ------------------ DASHBOARD ------------------
def dashboard_page():
    set_background()
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
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
            ax.set_title("Task Status Distribution")
            st.pyplot(fig)
        else:
            st.warning("Not enough data for chart.")


# ------------------ CSV DOWNLOAD ------------------
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
