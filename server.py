import sys
import uuid
import typing as t
import pwd
import os
import werkzeug.debug
from werkzeug.serving import run_simple
from app import app
import multiprocessing

def initialize():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        user = pwd.getpwuid(os.getuid())[0]
        modname = getattr(app, "__module__", t.cast(object, app).__class__.__module__)
        mod = sys.modules.get(modname)
        app_name = getattr(app, "__name__", type(app).__name__)
        mod_file_loc = getattr(mod, '__file__', None)
        mac_addr = str (uuid.getnode ())
        machine_id = werkzeug.debug.get_machine_id()

        print("User: %s\nModule: %s\nModule Name: %s\nApp Location: %s\nMac Address: %s\nWerkzeug Machine ID: %s\n"
            % (user, modname, app_name, mod_file_loc, mac_addr, machine_id))

def start_server():
    run_simple('0.0.0.0', 7777, app, use_reloader=True, use_debugger=True, use_evalex=True)

if __name__ == '__main__':
    proc = multiprocessing.Process(target=start_server)
    proc.start()
    initialize()