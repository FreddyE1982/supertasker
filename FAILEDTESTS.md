============================= test session starts ==============================
platform linux -- Python 3.12.10, pytest-8.4.1, pluggy-1.6.0
rootdir: /workspace/supertasker
configfile: pytest.ini
plugins: anyio-4.9.0
collected 2 items

tests/test_api.py .F                                                     [100%]

=================================== FAILURES ===================================
_______________________________ test_rate_limit ________________________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7f32ef55dcd0>

    @pytest.mark.env(RATE_LIMIT="2")
    def test_rate_limit(monkeypatch):
        r1 = requests.get(f"{API_URL}/appointments")
        r2 = requests.get(f"{API_URL}/appointments")
        r3 = requests.get(f"{API_URL}/appointments")
        assert r1.status_code == 200
>       assert r2.status_code == 200
E       assert 429 == 200
E        +  where 429 = <Response [429]>.status_code

tests/test_api.py:1442: AssertionError
---------------------------- Captured stdout setup -----------------------------
INFO:     127.0.0.1:57422 - "GET /appointments HTTP/1.1" 200 OK
---------------------------- Captured stderr setup -----------------------------
INFO:     Started server process [9440]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
----------------------------- Captured stdout call -----------------------------
INFO:     127.0.0.1:57436 - "GET /appointments HTTP/1.1" 200 OK
INFO:     127.0.0.1:57442 - "GET /appointments HTTP/1.1" 429 Too Many Requests
INFO:     127.0.0.1:57452 - "GET /appointments HTTP/1.1" 429 Too Many Requests
--------------------------- Captured stderr teardown ---------------------------
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [9440]
=========================== short test summary info ============================
FAILED tests/test_api.py::test_rate_limit - assert 429 == 200
========================= 1 failed, 1 passed in 3.55s ==========================
