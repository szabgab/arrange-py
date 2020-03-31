#!/usr/bin/env python3
import subprocess
import os
import sys
import time

wfile = os.environ["HOME"]+"/.windowlist"
arg = sys.argv[1]

def get(command):
    return subprocess.check_output(["/bin/bash", "-c", command]).decode("utf-8")

def check_window(w_id):
    w_type = get("xprop -id "+w_id)
    if " _NET_WM_WINDOW_TYPE_NORMAL" in w_type:
        return True
    else:
        return False

def get_res():
    # get resolution and the workspace correction (vector)
    xr = subprocess.check_output(["xrandr"]).decode("utf-8").split()
    pos = xr.index("current")
    res = [int(xr[pos+1]), int(xr[pos+3].replace(",", "") )]
    vp_data = subprocess.check_output(["wmctrl", "-d"]).decode("utf-8").split()
    curr_vpdata = [int(n) for n in vp_data[5].split(",")]
    return [res, curr_vpdata]

app = lambda pid: subprocess.check_output(["ps", "-p",  pid, "-o", "comm="]).decode("utf-8").strip()

def read_windows():
    res = get_res()
    w_list =  [l.split() for l in get("wmctrl -lpG").splitlines()]
    relevant = [[w[2],[int(n) for n in w[3:7]]] for w in w_list if check_window(w[0]) == True]
    for i, r in enumerate(relevant):      
        relevant[i] = app(r[0])+" "+str((" ").join([str(n) for n in r[1]]))
    with open(wfile, "wt") as out:
        for l in relevant:
            out.write(l+"\n")

def open_appwindow(app, x, y, w, h):
    ws1 = get("wmctrl -lp"); t = 0
    # fix command for certain apps that open in new tab by default
    if app == "gedit":
        option = " --new-window"
    else:
        option = ""
    # fix command if process name and command to run are different
    if "gnome-terminal" in app:
        app = "gnome-terminal"
    elif "chrome" in app:
        app = "/usr/bin/google-chrome-stable"


    subprocess.Popen(["/bin/bash", "-c", app+option])
    # fix exception for Chrome (command = google-chrome-stable, but processname = chrome)
    app = "chrome" if "chrome" in app else app
    while t < 30:      
        ws2 = [w.split()[0:3] for w in get("wmctrl -lp").splitlines() if not w in ws1]
        procs = [[(p, w[0]) for p in get("ps -e ww").splitlines() \
                  if app in p and w[2] in p] for w in ws2]
        if len(procs) > 0:
            time.sleep(0.5)
            w_id = procs[0][0][1]
            cmd1 = "wmctrl -ir "+w_id+" -b remove,maximized_horz"
            cmd2 = "wmctrl -ir "+w_id+" -b remove,maximized_vert"
            cmd3 = "wmctrl -ir "+procs[0][0][1]+" -e 0,"+x+","+y+","+w+","+h
            for cmd in [cmd1, cmd2, cmd3]:   
                subprocess.call(["/bin/bash", "-c", cmd])
            break
        time.sleep(0.5)
        t = t+1

def run_remembered():
    res = get_res()[1]
    try:
        lines = [l.split() for l in open(wfile).read().splitlines()]
        for l in lines:          
            l[1] = str(int(l[1]) - res[0]); l[2] = str(int(l[2]) - res[1] - 24)
            open_appwindow(l[0], l[1], l[2], l[3], l[4])   
    except FileNotFoundError:
        pass

if arg == "-run":
    run_remembered()
elif arg == "-read":
    read_windows()

