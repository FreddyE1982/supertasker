import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.title("Calendar App")

if "appointments" not in st.session_state:
    st.session_state["appointments"] = []


def refresh():
    resp = requests.get(f"{API_URL}/appointments")
    if resp.status_code == 200:
        st.session_state["appointments"] = resp.json()


if st.button("Refresh", key="refresh-btn"):
    refresh()

st.header("Create Appointment")
with st.form("create-form"):
    title = st.text_input("Title", key="create-title")
    description = st.text_input("Description", key="create-description")
    start_date = st.date_input("Start Date", key="create-start-date")
    start_time = st.time_input("Start Time", key="create-start-time")
    end_date = st.date_input("End Date", key="create-end-date")
    end_time = st.time_input("End Time", key="create-end-time")
    submitted = st.form_submit_button("Create")
    if submitted:
        start = datetime.combine(start_date, start_time)
        end = datetime.combine(end_date, end_time)
        data = {
            "title": title,
            "description": description,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        }
        resp = requests.post(f"{API_URL}/appointments", json=data)
        if resp.status_code == 200:
            st.success("Created")
            refresh()
        else:
            st.error("Error creating appointment")

st.header("Appointments")
for appt in st.session_state["appointments"]:
    with st.expander(appt["title"]):
        st.write(f"Start: {appt['start_time']}")
        st.write(f"End: {appt['end_time']}")
        st.write(appt.get("description", ""))
        with st.form(f'edit-form-{appt["id"]}'):
            title = st.text_input(
                "Title", value=appt["title"], key=f'title_{appt["id"]}'
            )
            description = st.text_input(
                "Description",
                value=appt.get("description", ""),
                key=f'desc_{appt["id"]}',
            )
            start_date = st.date_input(
                "Start Date",
                value=datetime.fromisoformat(appt["start_time"]).date(),
                key=f'start_date_{appt["id"]}',
            )
            start_time = st.time_input(
                "Start Time",
                value=datetime.fromisoformat(appt["start_time"]).time(),
                key=f'start_time_{appt["id"]}',
            )
            end_date = st.date_input(
                "End Date",
                value=datetime.fromisoformat(appt["end_time"]).date(),
                key=f'end_date_{appt["id"]}',
            )
            end_time = st.time_input(
                "End Time",
                value=datetime.fromisoformat(appt["end_time"]).time(),
                key=f'end_time_{appt["id"]}',
            )
            if st.form_submit_button("Update"):
                start = datetime.combine(start_date, start_time)
                end = datetime.combine(end_date, end_time)
                data = {
                    "title": title,
                    "description": description,
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                }
                resp = requests.put(f'{API_URL}/appointments/{appt["id"]}', json=data)
                if resp.status_code == 200:
                    st.success("Updated")
                    refresh()
                else:
                    st.error("Error updating")
        if st.button("Delete", key=f'del_{appt["id"]}'):
            resp = requests.delete(f'{API_URL}/appointments/{appt["id"]}')
            if resp.status_code == 200:
                st.success("Deleted")
                refresh()
            else:
                st.error("Error deleting")
