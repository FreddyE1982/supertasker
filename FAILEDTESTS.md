E                                                                        [100%]
==================================== ERRORS ====================================
____________________ ERROR at setup of test_register_login _____________________

    @pytest.fixture
    def server():
        if os.path.exists("appointments.db"):
            os.remove("appointments.db")
        env = os.environ.copy()
        env["DISABLE_AUTH"] = "0"
        env["RATE_LIMIT"] = "1000"
        proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app"], env=env)
>       assert wait_for_api(f"{API_URL}/openapi.json")
E       AssertionError: assert False
E        +  where False = wait_for_api('http://localhost:8000/openapi.json')

tests/test_auth.py:31: AssertionError
---------------------------- Captured stderr setup -----------------------------
Traceback (most recent call last):
  File "/root/.pyenv/versions/3.12.10/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1963, in _exec_single_context
    self.dialect.do_execute(
  File "/root/.pyenv/versions/3.12.10/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 943, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: disk I/O error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/root/.pyenv/versions/3.12.10/lib/python3.12/site-packages/uvicorn/__main__.py", line 4, in <module>
    uvicorn.main()
  File "/root/.pyenv/versions/3.12.10/lib/python3.12/site-packages/click/core.py", line 1442, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.12.10/lib/python3.12/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.12.10/lib/python3.12/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
