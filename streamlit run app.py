import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Initialize session state for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("📝 Daily To‑Do List App")
st.write("Manage your daily tasks and download them anytime.")

# Add new task
st.subheader("Add New Task")
task = st.text_input("Task Title")
description = st.text_area("Description")
due_date = st.date_input("Due Date")

if st.button("Add Task"):
    if task:
        st.session_state.tasks.append({
            "Task": task,
            "Description": description,
            "Due Date": str(due_date),
            "Added On": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success("Task added successfully!")
    else:
        st.error("Please enter a task title.")

# Show tasks
st.subheader("Mark Tasks as Completed")
for i, t in enumerate(st.session_state.tasks):
    if st.button(f"Complete: {t['Task']}"):
        st.session_state.tasks[i]["Completed"] = True
        st.success(f"Task '{t['Task']}' marked as completed!")
tasks_df = pd.DataFrame(st.session_state.tasks)

st.subheader("Your To‑Do List")
st.dataframe(tasks_df)

# Download CSV
if not tasks_df.empty:
    csv_buffer = io.StringIO()
    tasks_df.to_csv(csv_buffer, index=False)
    st.download_button("Download To‑Do List (CSV)", csv_buffer.getvalue(), "todo_list.csv", "text/csv")

# Delete all tasks
if st.button("Clear All Tasks"):
    st.session_state.tasks = []
    st.warning("All tasks cleared!")
