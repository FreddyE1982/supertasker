import streamlit as st
import requests
from datetime import datetime

API_URL = 'http://localhost:8000'

st.title('Calendar App')

if 'appointments' not in st.session_state:
    st.session_state['appointments'] = []

def refresh():
    resp = requests.get(f'{API_URL}/appointments')
    if resp.status_code == 200:
        st.session_state['appointments'] = resp.json()

if st.button('Refresh'):
    refresh()

st.header('Create Appointment')
with st.form('create'):
    title = st.text_input('Title')
    description = st.text_input('Description')
    start = st.datetime_input('Start Time')
    end = st.datetime_input('End Time')
    submitted = st.form_submit_button('Create')
    if submitted:
        data = {
            'title': title,
            'description': description,
            'start_time': start.isoformat(),
            'end_time': end.isoformat()
        }
        resp = requests.post(f'{API_URL}/appointments', json=data)
        if resp.status_code == 200:
            st.success('Created')
            refresh()
        else:
            st.error('Error creating appointment')

st.header('Appointments')
for appt in st.session_state['appointments']:
    with st.expander(appt['title']):
        st.write(f"Start: {appt['start_time']}")
        st.write(f"End: {appt['end_time']}")
        st.write(appt.get('description', ''))
        with st.form(f'edit_{appt["id"]}'):
            title = st.text_input('Title', value=appt['title'])
            description = st.text_input('Description', value=appt.get('description', ''))
            start = st.datetime_input('Start Time', value=datetime.fromisoformat(appt['start_time']))
            end = st.datetime_input('End Time', value=datetime.fromisoformat(appt['end_time']))
            if st.form_submit_button('Update'):
                data = {
                    'title': title,
                    'description': description,
                    'start_time': start.isoformat(),
                    'end_time': end.isoformat()
                }
                resp = requests.put(f'{API_URL}/appointments/{appt["id"]}', json=data)
                if resp.status_code == 200:
                    st.success('Updated')
                    refresh()
                else:
                    st.error('Error updating')
        if st.button('Delete', key=f'del_{appt["id"]}'):
            resp = requests.delete(f'{API_URL}/appointments/{appt["id"]}')
            if resp.status_code == 200:
                st.success('Deleted')
                refresh()
            else:
                st.error('Error deleting')
