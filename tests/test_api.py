import subprocess
import time
import requests
import os

import pytest

API_URL = 'http://localhost:8000'

@pytest.fixture(scope='session', autouse=True)
def start_server():
    proc = subprocess.Popen(['uvicorn', 'app.main:app'])
    time.sleep(1)
    yield
    proc.terminate()
    proc.wait()
    if os.path.exists('appointments.db'):
        os.remove('appointments.db')


def test_create_list_update_delete():
    cat = {'name': 'Work', 'color': '#ff0000'}
    r = requests.post(f'{API_URL}/categories', json=cat)
    assert r.status_code == 200
    category = r.json()

    data = {
        'title': 'Meeting',
        'description': 'Discuss project',
        'start_time': '2024-01-01T10:00:00',
        'end_time': '2024-01-01T11:00:00',
        'category_id': category['id']
    }
    r = requests.post(f'{API_URL}/appointments', json=data)
    assert r.status_code == 200
    appt = r.json()
    assert appt['title'] == data['title']
    assert appt['category_id'] == category['id']

    r = requests.get(f'{API_URL}/appointments')
    assert r.status_code == 200
    assert len(r.json()) == 1

    update = data.copy()
    update['title'] = 'Updated Meeting'
    update['category_id'] = category['id']
    r = requests.put(f'{API_URL}/appointments/{appt["id"]}', json=update)
    assert r.status_code == 200
    assert r.json()['title'] == 'Updated Meeting'
    assert r.json()['category_id'] == category['id']

    r = requests.delete(f'{API_URL}/appointments/{appt["id"]}')
    assert r.status_code == 200
    r = requests.get(f'{API_URL}/appointments')
    assert r.status_code == 200
    assert r.json() == []
