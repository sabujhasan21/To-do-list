import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
import json
import os

st.title("📝 Advanced To-Do Manager (With Login + Auto Save)")

# ------------------- LOGIN SYSTEM -------------------
def login_page():
    st.subheader("🔐 Please Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # UPDATED LOGIN HERE
        if username == "sabuj2025" and password == "sabuj":
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()   # stop app unless logged in


# ------------------- DATA SAVE / LOAD -------------------
DATA_FILE = "tasks.json"

# load tasks from file
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# save tasks to file
def save_tasks():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.tasks, f, indent=4)

# initialize session from file
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None


# ------------------- ADD / EDIT TASK -------------------
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
                st.success("Task updated successfully!")
            else:
                st.session_state.tasks.append(new_task)
                st.success("Task added successfully!")

            save_tasks()  # save immediately after any change
            st.experimental_rerun()

        else:
            st.error("Task title is required.")

if st.session_state.edit_index is not None:
    task_form(edit=True)
else:
    task_form(edit=False)


# ------------------- TASK LIST -------------------
st.subheader("Your Tasks")

today = date.today()

# detect overdue
for t in st.session_state.tasks:
    if t["Status"] != "Completed" and date.fromisoformat(t["End"]) < today:
        t["Status"] = "Overdue"

save_tasks()  # save after status updates

# sort tasks
st.session_state.tasks = sorted(st.session_state.tasks, key=lambda x: x["End"])

# display tasks
for i, t in enumerate(st.session_state.tasks):
    st.markdown(f"### {t['Task']}")
    st.write(f"📄 {t['Description']}")
    st.write(f"📅 Start: {t['Start']} | End: {t['End']}")
    st.write(f"Status: **{t['Status']}**")

    col1, col2, col3 = st.columns(3)

    if col1.button(f"Edit {i}"):
        st.session_state.edit_index = i
        st.experimental_rerun()

    if col2.button(f"Delete {i}"):
        st.session_state.tasks.pop(i)
        save_tasks()
        st.experimental_rerun()

    if col3.button(f"Complete {i}"):
        st.session_state.tasks[i]["Status"] = "Completed"
        save_tasks()
        st.success(f"Task '{t['Task']}' marked completed!")
        st.experimental_rerun()

    st.markdown("---")


# ------------------- DOWNLOAD CSV -------------------
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    st.download_button("Download Task List (CSV)", buffer.getvalue(),
                       "tasks.csv", "text/csv")

