import os
import subprocess
import sys
import time
from datetime import date
from datetime import time as dtime
from datetime import timedelta

import requests
from streamlit.testing.v1 import AppTest

API_URL = "http://localhost:8000"
TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)


def wait_for_api(url: str, timeout: float = 5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url).status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False


def start_server():
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app"])
    assert wait_for_api(f"{API_URL}/appointments")
    return proc


def stop_server(proc):
    proc.terminate()
    proc.wait()
    if os.path.exists("appointments.db"):
        os.remove("appointments.db")


def test_full_gui_interaction():
    proc = start_server()
    try:
        at = AppTest.from_file("streamlit_app.py").run()

        # create category
        cat_tab = next(t for t in at.tabs if t.label == "Manage Categories")
        at = cat_tab.text_input(key="cat-name").input("Work").run()
        at = cat_tab.color_picker(key="cat-color").set_value("#ff0000").run()
        at = cat_tab.number_input(key="cat-start").set_value(9).run()
        at = cat_tab.number_input(key="cat-end").set_value(17).run()
        at = cat_tab.text_input(key="cat-energy").input(",".join(["1"] * 24)).run()
        at = cat_tab.button(key="FormSubmitter:cat-form-Create").click().run()
        assert "Created" in [s.value for s in at.success]

        # create appointment
        at = at.text_input(key="create-title").input("Meeting").run()
        at = at.text_input(key="create-description").input("Discuss project").run()
        at = at.date_input(key="create-start-date").set_value(TODAY).run()
        at = at.time_input(key="create-start-time").set_value(dtime(10, 0)).run()
        at = at.date_input(key="create-end-date").set_value(TODAY).run()
        at = at.time_input(key="create-end-time").set_value(dtime(11, 0)).run()
        at = at.button[1].click().run()
        assert "Created" in [s.value for s in at.success]
        at = at.button(key="refresh-btn").click().run()
        assert any(e.label == "Meeting" for e in at.expander)

        # plan task
        at = at.tabs[1].text_input(key="plan-title").input("Planned").run()
        at = at.tabs[1].text_input(key="plan-desc").input("Auto").run()
        at = at.tabs[1].number_input(key="plan-diff").set_value(3).run()
        at = at.tabs[1].number_input(key="plan-priority").set_value(3).run()
        at = at.tabs[1].number_input(key="plan-dur").set_value(50).run()
        at = at.tabs[1].date_input(key="plan-due").set_value(TOMORROW).run()
        at = at.tabs[1].number_input(key="plan-he-start").set_value(8).run()
        at = at.tabs[1].number_input(key="plan-he-end").set_value(11).run()
        at = at.tabs[1].number_input(key="plan-fatigue").set_value(0.5).run()
        at = at.tabs[1].text_input(key="plan-curve").input(",".join(["1"] * 24)).run()
        at = at.tabs[1].number_input(key="plan-buffer").set_value(5).run()
        at = at.tabs[1].checkbox(key="plan-int-buffer").check().run()
        at = at.tabs[1].number_input(key="plan-spaced").set_value(1.0).run()
        at = at.tabs[1].button(key="FormSubmitter:plan-form-Plan").click().run()
        assert "Planned" in [s.value for s in at.success]
        at = at.tabs[1].button(key="refresh-tasks").click().run()
        assert any("Planned" in e.label for e in at.expander)

        # create task
        at = at.tabs[1].text_input(key="task-title").input("Task 1").run()
        at = at.tabs[1].text_input(key="task-desc").input("Do something").run()
        at = at.tabs[1].date_input(key="task-due-date").set_value(TOMORROW).run()
        at = at.tabs[1].date_input(key="task-start-date").set_value(TOMORROW).run()
        at = at.tabs[1].time_input(key="task-start-time").set_value(dtime(9, 0)).run()
        at = at.tabs[1].date_input(key="task-end-date").set_value(TOMORROW).run()
        at = at.tabs[1].time_input(key="task-end-time").set_value(dtime(10, 0)).run()
        at = at.tabs[1].number_input(key="task-perceived").set_value(2).run()
        at = at.tabs[1].number_input(key="task-estimated").set_value(3).run()
        at = at.tabs[1].number_input(key="task-priority").set_value(3).run()
        at = (
            at.tabs[1].button(key="FormSubmitter:task-create-form-Create").click().run()
        )
        assert "Created" in [s.value for s in at.success]
        at = at.tabs[1].button(key="refresh-tasks").click().run()
        assert any(e.label == "Task 1" for e in at.expander)

        # create subtask
        at = at.text_input(key="new_sub_1").input("Step 1").run()
        at = at.button(key="FormSubmitter:subtask-create-1-Add Subtask").click().run()
        assert "Created" in [s.value for s in at.success]
        at = at.tabs[1].button(key="refresh-tasks").click().run()

        # create focus session
        at = at.number_input(key="fs_dur_1").set_value(30).run()
        at = at.button(key="fs_start_1").click().run()
        assert "Created" in [s.value for s in at.success]
        at = at.tabs[1].button(key="refresh-tasks").click().run()

        # update focus session
        at = at.date_input(key="fs_end_date_1_1").set_value(TOMORROW).run()
        at = at.time_input(key="fs_end_time_1_1").set_value(dtime(10, 30)).run()
        at = at.checkbox(key="fs_comp_1_1").check().run()
        at = at.button(key="FormSubmitter:fs-edit-1-1-Update").click().run()
        assert "Updated" in [s.value for s in at.success]
        at = at.tabs[1].button(key="refresh-tasks").click().run()

        # delete focus session
        at = at.button(key="fsdel_1_1").click().run()
        assert "Deleted" in [s.value for s in at.success]
        at = at.tabs[1].button(key="refresh-tasks").click().run()

        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        at = cal_tab.date_input(key="calendar-date").set_value(TODAY).run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        at = cal_tab.selectbox[0].set_value("Day").run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert TODAY.isoformat() in cal_tab.markdown[0].value
        assert any("Meeting" in md.value for md in cal_tab.markdown)
        at = cal_tab.button(key="cal-next").click().run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert (TODAY + timedelta(days=1)).isoformat() in cal_tab.markdown[0].value
        at = cal_tab.button(key="cal-prev").click().run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert TODAY.isoformat() in cal_tab.markdown[0].value

        at = cal_tab.selectbox[0].set_value("Week").run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert TODAY.isoformat() in cal_tab.markdown[0].value
        at = cal_tab.button(key="cal-next").click().run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert (TODAY + timedelta(days=7)).isoformat() in cal_tab.markdown[0].value
        at = cal_tab.button(key="cal-prev").click().run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert TODAY.isoformat() in cal_tab.markdown[0].value

        at = cal_tab.selectbox[0].set_value("Two Weeks").run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert TODAY.isoformat() in cal_tab.markdown[0].value
        at = cal_tab.button(key="cal-next").click().run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert (TODAY + timedelta(days=14)).isoformat() in cal_tab.markdown[0].value
        at = cal_tab.button(key="cal-prev").click().run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert TODAY.isoformat() in cal_tab.markdown[0].value

        at = cal_tab.selectbox[0].set_value("Month").run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert TODAY.isoformat() in cal_tab.markdown[0].value
        at = cal_tab.button(key="cal-next").click().run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert (TODAY + timedelta(days=31)).isoformat() in cal_tab.markdown[0].value
        at = cal_tab.button(key="cal-prev").click().run()
        cal_tab = next(t for t in at.tabs if t.label == "Calendar")
        assert TODAY.isoformat() in cal_tab.markdown[0].value
        # update appointment
        at = at.text_input(key="title_1").set_value("Updated Meeting").run()
        at = at.text_input(key="desc_1").set_value("Updated notes").run()
        at = at.date_input(key="start_date_1").set_value(TOMORROW).run()
        at = at.time_input(key="start_time_1").set_value(dtime(9, 0)).run()
        at = at.date_input(key="end_date_1").set_value(TOMORROW).run()
        at = at.time_input(key="end_time_1").set_value(dtime(10, 0)).run()
        at = at.tabs[0].button(key="FormSubmitter:edit-form-1-Update").click().run()
        assert "Updated" in [s.value for s in at.success]
        at = at.button(key="refresh-btn").click().run()
        assert any(e.label == "Updated Meeting" for e in at.expander)

        # update task
        at = at.text_input(key="task_title_1").set_value("Updated Task").run()
        at = at.text_input(key="task_description_1").set_value("More work").run()
        at = at.date_input(key="sdate_1").set_value(TOMORROW + timedelta(days=1)).run()
        at = at.time_input(key="stime_1").set_value(dtime(10, 0)).run()
        at = at.date_input(key="edate_1").set_value(TOMORROW + timedelta(days=1)).run()
        at = at.time_input(key="etime_1").set_value(dtime(11, 0)).run()
        at = at.number_input(key="pdiff_1").set_value(3).run()
        at = at.number_input(key="ediff_1").set_value(4).run()
        at = at.number_input(key="prio_1").set_value(4).run()
        at = at.checkbox(key="wo_1").check().run()
        at = at.tabs[1].button(key="FormSubmitter:task-edit-1-Update").click().run()
        assert "Updated" in [s.value for s in at.success]
        at = at.tabs[1].button(key="refresh-tasks").click().run()
        assert any(e.label == "Updated Task" for e in at.expander)

        # delete appointment
        at = at.tabs[0].button[3].click().run()
        assert "Deleted" in [s.value for s in at.success]
        at = at.button(key="refresh-btn").click().run()
        assert not any("Meeting" in e.label for e in at.expander)

    finally:
        stop_server(proc)
