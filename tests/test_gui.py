import subprocess
import time
import os
from datetime import date, time as dtime
import requests
from streamlit.testing.v1 import AppTest

API_URL = "http://localhost:8000"


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
    proc = subprocess.Popen(["uvicorn", "app.main:app"])
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

        # create appointment
        at = at.text_input(key="create-title").input("Meeting").run()
        at = at.text_input(key="create-description").input("Discuss project").run()
        at = at.date_input(key="create-start-date").set_value(date(2024, 1, 1)).run()
        at = at.time_input(key="create-start-time").set_value(dtime(10, 0)).run()
        at = at.date_input(key="create-end-date").set_value(date(2024, 1, 1)).run()
        at = at.time_input(key="create-end-time").set_value(dtime(11, 0)).run()
        at = at.button[1].click().run()
        assert "Created" in [s.value for s in at.success]
        at = at.button(key="refresh-btn").click().run()
        assert any(e.label == "Meeting" for e in at.expander)

        # calendar views
        at = at.tabs[1].date_input(key="calendar-date").set_value(date(2024, 1, 1)).run()
        at = at.tabs[1].selectbox[0].set_value("Day").run()
        assert "2024-01-01" in at.tabs[1].markdown[0].value
        assert any("Meeting" in md.value for md in at.tabs[1].markdown)
        at = at.tabs[1].button[1].click().run()
        assert "2024-01-02" in at.tabs[1].markdown[0].value
        at = at.tabs[1].button[0].click().run()
        assert "2024-01-01" in at.tabs[1].markdown[0].value

        at = at.tabs[1].selectbox[0].set_value("Week").run()
        assert "2024-01-01" in at.tabs[1].markdown[0].value
        at = at.tabs[1].button[1].click().run()
        assert "2024-01-08" in at.tabs[1].markdown[0].value
        at = at.tabs[1].button[0].click().run()

        at = at.tabs[1].selectbox[0].set_value("Two Weeks").run()
        assert "2024-01-01" in at.tabs[1].markdown[0].value
        at = at.tabs[1].button[1].click().run()
        assert "2024-01-15" in at.tabs[1].markdown[0].value
        at = at.tabs[1].button[0].click().run()

        at = at.tabs[1].selectbox[0].set_value("Month").run()
        assert "2024-01-01" in at.tabs[1].markdown[0].value
        at = at.tabs[1].button[1].click().run()
        assert "2024-02-01" in at.tabs[1].markdown[0].value
        at = at.tabs[1].button[0].click().run()

        # update appointment
        at = at.text_input(key="title_1").set_value("Updated Meeting").run()
        at = at.text_input(key="desc_1").set_value("Updated notes").run()
        at = at.date_input(key="start_date_1").set_value(date(2024, 1, 2)).run()
        at = at.time_input(key="start_time_1").set_value(dtime(9, 0)).run()
        at = at.date_input(key="end_date_1").set_value(date(2024, 1, 2)).run()
        at = at.time_input(key="end_time_1").set_value(dtime(10, 0)).run()
        at = at.tabs[0].button[2].click().run()
        assert "Updated" in [s.value for s in at.success]
        at = at.button(key="refresh-btn").click().run()
        assert any(e.label == "Updated Meeting" for e in at.expander)

        # delete appointment
        at = at.tabs[0].button[3].click().run()
        assert "Deleted" in [s.value for s in at.success]
        at = at.button(key="refresh-btn").click().run()
        assert len(at.expander) == 0
    finally:
        stop_server(proc)
