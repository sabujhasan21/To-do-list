import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

st.title("📝 Advanced To-Do Manager")
st.write("Create, edit, complete, and manage your daily tasks with notifications.")

# Initialize session
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# -------- ADD / EDIT TASK --------
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
        else:
            st.error("Task title is required.")

if st.session_state.edit_index is not None:
    task_form(edit=True)
else:
    task_form(edit=False)

# -------- TASK LIST --------
st.subheader("Your Tasks")

# detect overdue
today = date.today()
for t in st.session_state.tasks:
    if t["Status"] != "Completed" and date.fromisoformat(t["End"]) < today:
        t["Status"] = "Overdue"
        st.warning(f"⛔ Task overdue: {t['Task']}")

# sort tasks by date
st.session_state.tasks = sorted(st.session_state.tasks, key=lambda x: x["End"])

# Display tasks
for i, t in enumerate(st.session_state.tasks):
    st.markdown(f"### {t['Task']}")
    st.write(f"📄 {t['Description']}")
    st.write(f"📅 Start: {t['Start']} | End: {t['End']}")
    st.write(f"Status: **{t['Status']}**")

    col1, col2, col3 = st.columns(3)

    if col1.button(f"Edit {i}"):
        st.session_state.edit_index = i

    if col2.button(f"Delete {i}"):
        st.session_state.tasks.pop(i)
        st.experimental_rerun()

    if col3.button(f"Complete {i}"):
        st.session_state.tasks[i]["Status"] = "Completed"
        st.success(f"Task '{t['Task']}' marked completed!")
        st.experimental_rerun()

    st.markdown("---")

# -------- DOWNLOAD --------
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    st.download_button("Download Task List (CSV)", buffer.getvalue(), "tasks.csv", "text/csv")
