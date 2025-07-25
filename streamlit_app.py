import streamlit as st
import requests
from datetime import datetime, date, time as dtime, timedelta
import calendar
import os
from streamlit_calendar import calendar as st_calendar

API_URL = "http://localhost:8000"

st.title("Calendar App")

if "appointments" not in st.session_state:
    st.session_state["appointments"] = []
if "categories" not in st.session_state:
    st.session_state["categories"] = []
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
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


def refresh_tasks():
    resp = requests.get(f"{API_URL}/tasks")
    if resp.status_code == 200:
        tasks = resp.json()
        for t in tasks:
            sresp = requests.get(f"{API_URL}/tasks/{t['id']}/subtasks")
            t["subtasks"] = sresp.json() if sresp.status_code == 200 else []
            fresp = requests.get(f"{API_URL}/tasks/{t['id']}/focus_sessions")
            t["focus_sessions"] = fresp.json() if fresp.status_code == 200 else []
        st.session_state["tasks"] = tasks


refresh()
refresh_categories()
refresh_tasks()


tabs = st.tabs(
    [
        "Manage Appointments",
        "Manage Tasks",
        "Calendar",
        "Manage Categories",
    ]
)

with tabs[0]:
    if st.button("Refresh", key="refresh-btn"):
        refresh()
        refresh_categories()

    st.header("Create Appointment")
    with st.form("create-form"):
        title = st.text_input("Title", key="create-title")
        description = st.text_input("Description", key="create-description")
        cat_opts = {c["name"]: c["id"] for c in st.session_state["categories"]}
        cat_name = st.selectbox(
            "Category", ["None"] + list(cat_opts.keys()), key="create-cat"
        )
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
                refresh()
                refresh_categories()
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
                current_name = next(
                    (
                        c["name"]
                        for c in st.session_state["categories"]
                        if c["id"] == appt.get("category_id")
                    ),
                    "None",
                )
                options = ["None"] + list(cat_opts.keys())
                idx = options.index(current_name) if current_name in options else 0
                cat_name = st.selectbox(
                    "Category", options, index=idx, key=f'cat_{appt["id"]}'
                )
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
                        refresh()
                        refresh_categories()
                    else:
                        st.error("Error updating")
            if st.button("Delete", key=f'del_{appt["id"]}'):
                resp = requests.delete(f'{API_URL}/appointments/{appt["id"]}')
                if resp.status_code == 200:
                    st.success("Deleted")
                    refresh()
                    refresh_categories()
                else:
                    st.error("Error deleting")

with tabs[1]:
    if st.button("Refresh Tasks", key="refresh-tasks"):
        refresh_tasks()

    st.subheader("Plan Task Automatically")
    with st.form("plan-form"):
        p_title = st.text_input("Title", key="plan-title")
        p_desc = st.text_input("Description", key="plan-desc")
        p_diff = st.number_input(
            "Estimated Difficulty", min_value=1, max_value=5, step=1, key="plan-diff"
        )
        p_priority = st.number_input(
            "Priority", value=3, min_value=1, max_value=5, step=1, key="plan-priority"
        )
        p_duration = st.number_input(
            "Estimated Duration Minutes", min_value=1, step=1, key="plan-dur"
        )
        p_due = st.date_input("Due Date", key="plan-due")
        cat_opts = {c["name"]: c["id"] for c in st.session_state["categories"]}
        cat_name = st.selectbox(
            "Category", ["None"] + list(cat_opts.keys()), key="plan-cat"
        )
        p_category_id = cat_opts.get(cat_name)
        he_start = st.number_input(
            "High Energy Start Hour",
            min_value=0,
            max_value=23,
            value=int(os.getenv("HIGH_ENERGY_START_HOUR", "9")),
            step=1,
            key="plan-he-start",
        )
        he_end = st.number_input(
            "High Energy End Hour",
            min_value=0,
            max_value=23,
            value=int(os.getenv("HIGH_ENERGY_END_HOUR", "12")),
            step=1,
            key="plan-he-end",
        )
        p_fatigue = st.number_input(
            "Fatigue Break Factor",
            min_value=0.0,
            value=float(os.getenv("FATIGUE_BREAK_FACTOR", "0")),
            step=0.1,
            key="plan-fatigue",
        )
        p_curve = st.text_input(
            "Energy Curve (24 comma numbers)",
            value=os.getenv("ENERGY_CURVE", ""),
            key="plan-curve",
        )
        p_day_weight = st.number_input(
            "Energy Day Order Weight",
            min_value=0.0,
            value=float(os.getenv("ENERGY_DAY_ORDER_WEIGHT", "0")),
            step=0.1,
            key="plan-day-weight",
        )
        p_cat_prod = st.number_input(
            "Category Productivity Weight",
            min_value=0.0,
            value=float(os.getenv("CATEGORY_PRODUCTIVITY_WEIGHT", "0")),
            step=0.1,
            key="plan-cat-prod",
        )
        p_buffer = st.number_input(
            "Transition Buffer Minutes",
            min_value=0,
            value=int(os.getenv("TRANSITION_BUFFER_MINUTES", "0")),
            step=1,
            key="plan-buffer",
        )
        p_int_buffer = st.checkbox(
            "Intelligent Transition Buffer",
            value=os.getenv("INTELLIGENT_TRANSITION_BUFFER", "0")
            in ["1", "true", "True"],
            key="plan-int-buffer",
        )
        p_spaced = st.number_input(
            "Spaced Repetition Factor",
            min_value=1.0,
            value=float(os.getenv("SPACED_REPETITION_FACTOR", "1")),
            step=0.1,
            key="plan-spaced",
        )
        if st.form_submit_button("Plan"):
            data = {
                "title": p_title,
                "description": p_desc,
                "estimated_difficulty": int(p_diff),
                "estimated_duration_minutes": int(p_duration),
                "due_date": p_due.isoformat(),
                "priority": int(p_priority),
                "high_energy_start_hour": int(he_start),
                "high_energy_end_hour": int(he_end),
                "fatigue_break_factor": float(p_fatigue),
                "energy_curve": [int(x) for x in p_curve.split(",") if x.strip()],
                "energy_day_order_weight": float(p_day_weight),
                "transition_buffer_minutes": int(p_buffer),
                "intelligent_transition_buffer": bool(p_int_buffer),
                "category_productivity_weight": float(p_cat_prod),
                "spaced_repetition_factor": float(p_spaced),
                "category_id": p_category_id,
            }
            r = requests.post(f"{API_URL}/tasks/plan", json=data)
            if r.status_code == 200:
                st.success("Planned")
                refresh_tasks()
            else:
                st.error("Error planning task")

    st.header("Create Task")
    with st.form("task-create-form"):
        t_title = st.text_input("Title", key="task-title")
        t_description = st.text_input("Description", key="task-desc")
        due_date = st.date_input("Due Date", key="task-due-date")
        start_date = st.date_input("Start Date", key="task-start-date")
        start_time = st.time_input("Start Time", key="task-start-time")
        end_date = st.date_input("End Date", key="task-end-date")
        end_time = st.time_input("End Time", key="task-end-time")
        cat_opts = {c["name"]: c["id"] for c in st.session_state["categories"]}
        t_cat = st.selectbox(
            "Category", ["None"] + list(cat_opts.keys()), key="task-cat"
        )
        t_cat_id = cat_opts.get(t_cat)
        perceived = st.number_input(
            "Perceived Difficulty", value=0, step=1, key="task-perceived"
        )
        estimated = st.number_input(
            "Estimated Difficulty", value=0, step=1, key="task-estimated"
        )
        priority = st.number_input(
            "Priority", value=3, min_value=1, max_value=5, step=1, key="task-priority"
        )
        worked_on = st.checkbox("Worked On", value=False, key="task-worked")
        paused = st.checkbox("Paused", value=False, key="task-paused")
        submitted = st.form_submit_button("Create")
        if submitted:
            data = {
                "title": t_title,
                "description": t_description,
                "due_date": due_date.isoformat(),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "perceived_difficulty": int(perceived),
                "estimated_difficulty": int(estimated),
                "priority": int(priority),
                "worked_on": worked_on,
                "paused": paused,
                "category_id": t_cat_id,
            }
            r = requests.post(f"{API_URL}/tasks", json=data)
            if r.status_code == 200:
                st.success("Created")
                refresh_tasks()
            else:
                st.error("Error creating task")

    st.header("Tasks")
    for task in st.session_state["tasks"]:
        with st.expander(task["title"]):
            st.write(f"Due: {task['due_date']} | Priority: {task.get('priority', 3)}")

            edit_tab, sub_tab, fs_tab = st.tabs(["Edit", "Subtasks", "Focus Sessions"])

            with edit_tab:
                with st.form(f'task-edit-{task["id"]}'):
                    title = st.text_input(
                        "Title", value=task["title"], key=f'task_title_{task["id"]}'
                    )
                    description = st.text_input(
                        "Description",
                        value=task.get("description", ""),
                        key=f'task_description_{task["id"]}',
                    )
                    due = st.date_input(
                        "Due Date",
                        value=date.fromisoformat(task["due_date"]),
                        key=f'due_{task["id"]}',
                    )
                    sdate = st.date_input(
                        "Start Date",
                        value=date.fromisoformat(
                            task.get("start_date", task["due_date"])
                        ),
                        key=f'sdate_{task["id"]}',
                    )
                    stime = st.time_input(
                        "Start Time",
                        value=dtime.fromisoformat(task.get("start_time", "00:00:00")),
                        key=f'stime_{task["id"]}',
                    )
                    edate = st.date_input(
                        "End Date",
                        value=date.fromisoformat(
                            task.get("end_date", task["due_date"])
                        ),
                        key=f'edate_{task["id"]}',
                    )
                    etime = st.time_input(
                        "End Time",
                        value=dtime.fromisoformat(task.get("end_time", "00:00:00")),
                        key=f'etime_{task["id"]}',
                    )
                    cat_opts = {
                        c["name"]: c["id"] for c in st.session_state["categories"]
                    }
                    current_name = next(
                        (
                            c["name"]
                            for c in st.session_state["categories"]
                            if c["id"] == task.get("category_id")
                        ),
                        "None",
                    )
                    options = ["None"] + list(cat_opts.keys())
                    idx = options.index(current_name) if current_name in options else 0
                    category_name = st.selectbox(
                        "Category", options, index=idx, key=f'task_cat_{task["id"]}'
                    )
                    category_id = cat_opts.get(category_name)
                    pdiff = st.number_input(
                        "Perceived Difficulty",
                        value=task.get("perceived_difficulty", 0) or 0,
                        key=f'pdiff_{task["id"]}',
                        step=1,
                    )
                    ediff = st.number_input(
                        "Estimated Difficulty",
                        value=task.get("estimated_difficulty", 0) or 0,
                        key=f'ediff_{task["id"]}',
                        step=1,
                    )
                    prio = st.number_input(
                        "Priority",
                        value=task.get("priority", 3) or 3,
                        min_value=1,
                        max_value=5,
                        step=1,
                        key=f'prio_{task["id"]}',
                    )
                    wo = st.checkbox(
                        "Worked On",
                        value=task.get("worked_on", False),
                        key=f'wo_{task["id"]}',
                    )
                    pa = st.checkbox(
                        "Paused",
                        value=task.get("paused", False),
                        key=f'pa_{task["id"]}',
                    )
                    if st.form_submit_button("Update"):
                        data = {
                            "title": title,
                            "description": description,
                            "due_date": due.isoformat(),
                            "start_date": sdate.isoformat(),
                            "end_date": edate.isoformat(),
                            "start_time": stime.isoformat(),
                            "end_time": etime.isoformat(),
                            "perceived_difficulty": int(pdiff),
                            "estimated_difficulty": int(ediff),
                            "priority": int(prio),
                            "worked_on": wo,
                            "paused": pa,
                            "category_id": category_id,
                        }
                        resp = requests.put(f"{API_URL}/tasks/{task['id']}", json=data)
                        if resp.status_code == 200:
                            st.success("Updated")
                            refresh_tasks()
                        else:
                            st.error("Error updating task")
            with sub_tab:
                for sub in task.get("subtasks", []):
                    with st.form(f'subtask-edit-{task["id"]}-{sub["id"]}'):
                        stitle = st.text_input(
                            "Title",
                            value=sub["title"],
                            key=f'subtitle_{task["id"]}_{sub["id"]}',
                        )
                        scomp = st.checkbox(
                            "Completed",
                            value=sub.get("completed", False),
                            key=f'subcomp_{task["id"]}_{sub["id"]}',
                        )
                        if st.form_submit_button("Update"):
                            data = {"title": stitle, "completed": scomp}
                            r = requests.put(
                                f"{API_URL}/tasks/{task['id']}/subtasks/{sub['id']}",
                                json=data,
                            )
                            if r.status_code == 200:
                                st.success("Updated")
                                refresh_tasks()
                            else:
                                st.error("Error updating subtask")
                    if st.button("Delete", key=f'subdel_{task["id"]}_{sub["id"]}'):
                        r = requests.delete(
                            f"{API_URL}/tasks/{task['id']}/subtasks/{sub['id']}"
                        )
                        if r.status_code == 200:
                            st.success("Deleted")
                            refresh_tasks()
                        else:
                            st.error("Error deleting subtask")
                with st.form(f'subtask-create-{task["id"]}'):
                    new_sub = st.text_input("Title", key=f'new_sub_{task["id"]}')
                    if st.form_submit_button("Add Subtask"):
                        data = {"title": new_sub, "completed": False}
                        r = requests.post(
                            f"{API_URL}/tasks/{task['id']}/subtasks", json=data
                        )
                        if r.status_code == 200:
                            st.success("Created")
                            refresh_tasks()
                        else:
                            st.error("Error creating subtask")

            with fs_tab:
                for fs in task.get("focus_sessions", []):
                    with st.form(f'fs-edit-{task["id"]}-{fs["id"]}'):
                        end_dt = datetime.fromisoformat(fs["end_time"])
                        end_date = st.date_input(
                            "End Date",
                            value=end_dt.date(),
                            key=f'fs_end_date_{task["id"]}_{fs["id"]}',
                        )
                        end_time = st.time_input(
                            "End Time",
                            value=end_dt.time(),
                            key=f'fs_end_time_{task["id"]}_{fs["id"]}',
                        )
                        completed = st.checkbox(
                            "Completed",
                            value=fs.get("completed", False),
                            key=f'fs_comp_{task["id"]}_{fs["id"]}',
                        )
                        if st.form_submit_button("Update"):
                            data = {
                                "end_time": datetime.combine(
                                    end_date, end_time
                                ).isoformat(),
                                "completed": completed,
                            }
                            r = requests.put(
                                f"{API_URL}/tasks/{task['id']}/focus_sessions/{fs['id']}",
                                json=data,
                            )
                            if r.status_code == 200:
                                st.success("Updated")
                                refresh_tasks()
                            else:
                                st.error("Error updating session")
                    if st.button(
                        "Delete",
                        key=f'fsdel_{task["id"]}_{fs["id"]}',
                    ):
                        r = requests.delete(
                            f"{API_URL}/tasks/{task['id']}/focus_sessions/{fs['id']}"
                        )
                        if r.status_code == 200:
                            st.success("Deleted")
                            refresh_tasks()
                        else:
                            st.error("Error deleting session")
                duration = st.number_input(
                    "Duration Minutes",
                    value=25,
                    step=1,
                    key=f'fs_dur_{task["id"]}',
                )
                if st.button("Start Session", key=f'fs_start_{task["id"]}'):
                    data = {"duration_minutes": int(duration)}
                    r = requests.post(
                        f"{API_URL}/tasks/{task['id']}/focus_sessions",
                        json=data,
                    )
                    if r.status_code == 200:
                        st.success("Created")
                        refresh_tasks()
                    else:
                        st.error("Error creating session")
            if st.button("Delete", key=f'task_del_{task["id"]}'):
                resp = requests.delete(f"{API_URL}/tasks/{task['id']}")
                if resp.status_code == 200:
                    st.success("Deleted")
                    refresh_tasks()
                else:
                    st.error("Error deleting task")

with tabs[2]:
    view = st.selectbox(
        "View",
        ["Day", "Week", "Two Weeks", "Month"],
        index=["Day", "Week", "Two Weeks", "Month"].index(
            st.session_state["calendar_view"]
        ),
        key="view-select",
    )
    st.session_state["calendar_view"] = view

    cal_date = st.date_input(
        "Current Date",
        value=st.session_state["calendar_date"],
        key="calendar-date",
    )
    st.session_state["calendar_date"] = cal_date
    st.markdown(st.session_state["calendar_date"].isoformat())

    def add_months(d: date, months: int) -> date:
        year = d.year + (d.month - 1 + months) // 12
        month = (d.month - 1 + months) % 12 + 1
        day = min(d.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def shift(step: int):
        if st.session_state["calendar_view"] == "Day":
            st.session_state["calendar_date"] += timedelta(days=step)
        elif st.session_state["calendar_view"] == "Week":
            st.session_state["calendar_date"] += timedelta(days=7 * step)
        elif st.session_state["calendar_view"] == "Two Weeks":
            st.session_state["calendar_date"] += timedelta(days=14 * step)
        else:
            st.session_state["calendar_date"] = add_months(
                st.session_state["calendar_date"], step
            )
        st.session_state["calendar-date"] = st.session_state["calendar_date"]

    col1, col2 = st.columns(2)
    col1.button("Previous", key="cal-prev", on_click=shift, args=(-1,))
    col2.button("Next", key="cal-next", on_click=shift, args=(1,))

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

    for task in st.session_state["tasks"]:
        if task.get("start_date") and task.get("start_time"):
            sdt = datetime.combine(
                date.fromisoformat(task["start_date"]),
                dtime.fromisoformat(task["start_time"]),
            )
        else:
            sdt = datetime.combine(date.fromisoformat(task["due_date"]), dtime(0, 0))
        if task.get("end_date") and task.get("end_time"):
            edt = datetime.combine(
                date.fromisoformat(task["end_date"]),
                dtime.fromisoformat(task["end_time"]),
            )
        else:
            edt = sdt
        color = cat_lookup.get(task.get("category_id"), {}).get("color")
        events.append(
            {
                "id": f"t{task['id']}",
                "title": f"Task: {task['title']}",
                "start": sdt.isoformat(),
                "end": edt.isoformat(),
                **({"color": color} if color else {}),
            }
        )
        for fs in task.get("focus_sessions", []):
            events.append(
                {
                    "id": f"fs{fs['id']}",
                    "title": f"Focus: {task['title']}",
                    "start": fs["start_time"],
                    "end": fs["end_time"],
                    "color": "#888888",
                }
            )

    options = {
        "initialDate": st.session_state["calendar_date"].isoformat(),
        "initialView": view_map[view],
        "editable": True,
        "views": {
            "twoweek": {
                "type": "timeGrid",
                "duration": {"weeks": 2},
                "buttonText": "2 weeks",
            }
        },
        "height": 650,
    }

    state = st_calendar(events=events, options=options, key="calendar")

    st.markdown("### Events")
    for ev in events:
        st.markdown(f"- {ev['title']}")

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

with tabs[3]:
    st.header("Create Category")
    with st.form("cat-form"):
        name = st.text_input("Name", key="cat-name")
        color = st.color_picker("Color", key="cat-color")
        start_hour = st.number_input(
            "Preferred Start Hour",
            min_value=0,
            max_value=23,
            step=1,
            key="cat-start",
        )
        end_hour = st.number_input(
            "Preferred End Hour",
            min_value=0,
            max_value=23,
            step=1,
            key="cat-end",
        )
        curve = st.text_input(
            "Energy Curve (24 comma numbers)",
            key="cat-energy",
        )
        if st.form_submit_button("Create"):
            data = {
                "name": name,
                "color": color,
                "preferred_start_hour": int(start_hour),
                "preferred_end_hour": int(end_hour),
                "energy_curve": [int(x) for x in curve.split(",") if x.strip()],
            }
            r = requests.post(f"{API_URL}/categories", json=data)
            if r.status_code == 200:
                st.success("Created")
                refresh_categories()
            else:
                st.error("Error creating category")

    st.header("Categories")
    for cat in st.session_state["categories"]:
        info = f"{cat['name']}"
        if (
            cat.get("preferred_start_hour") is not None
            and cat.get("preferred_end_hour") is not None
        ):
            info += f" ({cat['preferred_start_hour']}-{cat['preferred_end_hour']})"
        if cat.get("energy_curve"):
            info += " [curve]"
        st.markdown(
            f"<div style='display:flex;align-items:center;'><div style='width:20px;height:20px;background:{cat['color']};margin-right:5px;'></div>{info}</div>",
            unsafe_allow_html=True,
        )
