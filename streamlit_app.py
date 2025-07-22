import streamlit as st
import requests
from datetime import datetime, date, timedelta
import calendar
from streamlit_calendar import calendar as st_calendar

API_URL = "http://localhost:8000"

st.title("Calendar App")

if "appointments" not in st.session_state:
    st.session_state["appointments"] = []
if "categories" not in st.session_state:
    st.session_state["categories"] = []
if "calendar_view" not in st.session_state:
    st.session_state["calendar_view"] = "Day"
if "calendar_date" not in st.session_state:
    st.session_state["calendar_date"] = date.today()


def refresh():
    resp = requests.get(f"{API_URL}/appointments")
    if resp.status_code == 200:
        st.session_state["appointments"] = resp.json()


def refresh_categories():
    resp = requests.get(f"{API_URL}/categories")
    if resp.status_code == 200:
        st.session_state["categories"] = resp.json()


refresh()
refresh_categories()


tabs = st.tabs(["Manage Appointments", "Calendar", "Manage Categories"])

with tabs[0]:
    if st.button("Refresh", key="refresh-btn"):
        refresh(); refresh_categories()

    st.header("Create Appointment")
    with st.form("create-form"):
        title = st.text_input("Title", key="create-title")
        description = st.text_input("Description", key="create-description")
        cat_opts = {c["name"]: c["id"] for c in st.session_state["categories"]}
        cat_name = st.selectbox("Category", ["None"] + list(cat_opts.keys()), key="create-cat")
        category_id = cat_opts.get(cat_name)
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
                "category_id": category_id,
            }
            resp = requests.post(f"{API_URL}/appointments", json=data)
            if resp.status_code == 200:
                st.success("Created")
                refresh(); refresh_categories()
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
                cat_opts = {c["name"]: c["id"] for c in st.session_state["categories"]}
                current_name = next((c["name"] for c in st.session_state["categories"] if c["id"] == appt.get("category_id")), "None")
                options = ["None"] + list(cat_opts.keys())
                idx = options.index(current_name) if current_name in options else 0
                cat_name = st.selectbox("Category", options, index=idx, key=f'cat_{appt["id"]}')
                category_id = cat_opts.get(cat_name)
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
                        "category_id": category_id,
                    }
                    resp = requests.put(
                        f'{API_URL}/appointments/{appt["id"]}', json=data
                    )
                    if resp.status_code == 200:
                        st.success("Updated")
                        refresh(); refresh_categories()
                    else:
                        st.error("Error updating")
            if st.button("Delete", key=f'del_{appt["id"]}'):
                resp = requests.delete(f'{API_URL}/appointments/{appt["id"]}')
                if resp.status_code == 200:
                    st.success("Deleted")
                    refresh(); refresh_categories()
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

    view_map = {
        "Day": "timeGridDay",
        "Week": "timeGridWeek",
        "Two Weeks": "twoweek",
        "Month": "dayGridMonth",
    }

    events = []
    cat_lookup = {c["id"]: c for c in st.session_state["categories"]}
    for appt in st.session_state["appointments"]:
        start_dt = datetime.fromisoformat(appt["start_time"])
        end_dt = datetime.fromisoformat(appt["end_time"])
        color = cat_lookup.get(appt.get("category_id"), {}).get("color")
        events.append(
            {
                "id": appt["id"],
                "title": f"{appt['title']} - {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}",
                "start": appt["start_time"],
                "end": appt["end_time"],
                **({"color": color} if color else {}),
            }
        )

    options = {
        "initialDate": st.session_state["calendar_date"].isoformat(),
        "initialView": view_map[view],
        "editable": True,
        "views": {
            "twoweek": {"type": "timeGrid", "duration": {"weeks": 2}, "buttonText": "2 weeks"}
        },
        "height": 650,
    }

    state = st_calendar(events=events, options=options, key="calendar")

    if state.get("eventChange"):
        ev = state["eventChange"]["event"]
        appt_id = int(ev["id"])
        for appt in st.session_state["appointments"]:
            if appt["id"] == appt_id:
                data = appt.copy()
                data["start_time"] = ev["start"]
                data["end_time"] = ev["end"]
                requests.put(f"{API_URL}/appointments/{appt_id}", json=data)
                refresh()
                break

with tabs[2]:
    st.header("Create Category")
    with st.form("cat-form"):
        name = st.text_input("Name", key="cat-name")
        color = st.color_picker("Color", key="cat-color")
        if st.form_submit_button("Create"):
            data = {"name": name, "color": color}
            r = requests.post(f"{API_URL}/categories", json=data)
            if r.status_code == 200:
                st.success("Created")
                refresh_categories()
            else:
                st.error("Error creating category")

    st.header("Categories")
    for cat in st.session_state["categories"]:
        st.markdown(f"<div style='display:flex;align-items:center;'><div style='width:20px;height:20px;background:{cat['color']};margin-right:5px;'></div>{cat['name']}</div>", unsafe_allow_html=True)
