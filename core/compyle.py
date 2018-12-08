from io import StringIO
import sys
import traceback
from contextlib import contextmanager
from core.http import Http

@contextmanager
def stdout_io(stdout=None):

    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

def compyle(code, env):
    
    with stdout_io() as s:
        try:
            code = code.decode('utf-8')
            http = Http(env)

            exec(code, locals())
            data = s.getvalue()

            return (bytes(data, 'utf-8'), http.custom_headers, http.httperror)

        except Exception as e:

            data = '<pre><span onclick="document.getElementById(\'tbe\').style.display = \'block\';this.style.display = \'none\'" style="text-decoration:underline;cursor:pointer;"><b>Exception: </b>' + str(e) + '</span> <div id="tbe" class="hidden">'+str(traceback.format_exc())+'</div>' + '</pre>'

            return (bytes(data, 'utf-8'), {}, 0)