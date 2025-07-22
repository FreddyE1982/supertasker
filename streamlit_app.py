import streamlit as st
import requests
from datetime import datetime, date, timedelta
import calendar

API_URL = "http://localhost:8000"

st.title("Calendar App")

if "appointments" not in st.session_state:
    st.session_state["appointments"] = []
if "calendar_view" not in st.session_state:
    st.session_state["calendar_view"] = "Day"
if "calendar_date" not in st.session_state:
    st.session_state["calendar_date"] = date.today()


def refresh():
    resp = requests.get(f"{API_URL}/appointments")
    if resp.status_code == 200:
        st.session_state["appointments"] = resp.json()


tabs = st.tabs(["Manage Appointments", "Calendar"])

with tabs[0]:
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
                    resp = requests.put(
                        f'{API_URL}/appointments/{appt["id"]}', json=data
                    )
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

with tabs[1]:
    view = st.selectbox(
        "View", ["Day", "Week", "Two Weeks", "Month"],
        index=["Day", "Week", "Two Weeks", "Month"].index(st.session_state["calendar_view"]),
        key="view-select"
    )
    st.session_state["calendar_view"] = view

    cal_date = st.date_input(
        "Current Date",
        value=st.session_state["calendar_date"],
        key="calendar-date",
    )
    st.session_state["calendar_date"] = cal_date

    def add_months(d: date, months: int) -> date:
        year = d.year + (d.month - 1 + months) // 12
        month = (d.month - 1 + months) % 12 + 1
        day = min(d.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def shift(step: int):
        if view == "Day":
            st.session_state["calendar_date"] += timedelta(days=step)
        elif view == "Week":
            st.session_state["calendar_date"] += timedelta(days=7 * step)
        elif view == "Two Weeks":
            st.session_state["calendar_date"] += timedelta(days=14 * step)
        else:
            st.session_state["calendar_date"] = add_months(
                st.session_state["calendar_date"], step
            )

    col1, col2 = st.columns(2)
    if col1.button("Previous", key="cal-prev"):
        shift(-1)
    if col2.button("Next", key="cal-next"):
        shift(1)

    def get_range(d: date, mode: str):
        if mode == "Day":
            start = end = d
        elif mode == "Week":
            start = d
            end = d + timedelta(days=6)
        elif mode == "Two Weeks":
            start = d
            end = d + timedelta(days=13)
        else:
            start = d.replace(day=1)
            last = calendar.monthrange(d.year, d.month)[1]
            end = date(d.year, d.month, last)
        return start, end

    start, end = get_range(st.session_state["calendar_date"], view)
    st.write(f"Showing {start} to {end}")
    for appt in st.session_state["appointments"]:
        st_start = datetime.fromisoformat(appt["start_time"]).date()
        if start <= st_start <= end:
            st.write(f"{appt['title']}: {appt['start_time']} - {appt['end_time']}")
