import time
import sys
import threading
import curses
from websockets.sync.client import connect, ClientConnection
from websockets.exceptions import ConnectionClosedError

def resize(stdscr, ws, resize_payload_func):
    cols, rows= stdscr.getmaxyx()
    payload = resize_payload_func(rows, cols)
    ws_send(ws, payload)

def write_stdout(m):
    sys.stdout.write(m)
    sys.stdout.flush()

class Pinger():
    def __init__(self, ws, frequency=4, ping_payload_func=None):
        self.frequency = frequency
        self.ws = ws
        self.ping_payload_func = ping_payload_func
        self.stopped = False

    def start(self):
        threading.Thread(target=self.run).start()

    def run(self):
        while not self.stopped:
            time.sleep(self.frequency)
            try:
                ws_ping(self.ws, self.ping_payload_func)
            except ConnectionClosedError:
                return

    def stop(self):
        self.stopped = True

def ws_ping(ws: ClientConnection, ping_payload_func):
    ws.send(ping_payload_func())

def ws_input(ws, inp: str, input_payload_func):
    payload = input_payload_func(inp)
    return ws_send(ws, payload)

def ws_spawn_pinger(ws, freqency=4, ping_payload_func=None) -> Pinger:
    return Pinger(ws=ws, frequency=freqency, ping_payload_func=ping_payload_func)

def ws_send(ws, payload):
    ws.send(payload)

def attach_remote_pty_url(ws_url: str, input_payload_func, ping_frequency=4, ping_payload_func=None, resize_payload_func=None):
    with connect(ws_url) as ws:
        attach_remote_pty(ws, input_payload_func, ping_frequency, ping_payload_func, resize_payload_func)

def attach_remote_pty(ws: ClientConnection, input_payload_func, ping_frequency=4, ping_payload_func=None, resize_payload_func=None):

    # https://docs.python.org/3/howto/curses.html
    stdscr = curses.initscr()

    try:
        stdscr.timeout(1)
        stdscr.scrollok(1)
        stdscr.keypad(True)
        curses.cbreak()
        curses.noecho()

        try:
            curses.start_color()
        except:
            pass

        if resize_payload_func: resize(stdscr, ws, resize_payload_func)
        if ping_payload_func: ws_spawn_pinger(ws, freqency=ping_frequency, ping_payload_func=ping_payload_func).start()

        def recv_loop():
            while True:
                try:
                    m = ws.recv(timeout=None)
                    write_stdout(m)
                except ConnectionClosedError as e:
                    return
                except Exception as e:
                    write_stdout(f"Error - {e}, type: {type(e)}")
                    return
        threading.Thread(target=recv_loop, args=()).start()

        while True:
            try:
                chn = stdscr.getch()
                if chn < 0: continue
                ch = chr(chn)
                if ch == "\n": ch = "\\r"
                elif ch == "\t": ch = "\\t"
                elif chn == curses.KEY_UP: ch = "\\u001b[A"
                elif chn == curses.KEY_LEFT: ch = "\\u001b[D"
                elif chn == curses.KEY_RIGHT: ch = "\\u001b[C"
                elif chn == curses.KEY_DOWN: ch = "\\u001b[B"
                elif chn == curses.KEY_EXIT or chn == 27: ch = "\\u001b"
                elif chn == curses.KEY_BACKSPACE: ch = ""
                elif chn > 255:
                    write_stdout(f"chn: {chn}, ch: {ch}")
                    continue
                elif curses.keyname(chn) == b"^B": ch = "\\u0002"
                elif curses.keyname(chn) == b"^F": ch = "\\u0006"
                elif curses.keyname(chn) == b"^R": ch = "\\u0012"

                # write_stdout(f"key chn: {chn}, ch: {ch}, {curses.keyname(chn)}")

                ws_input(ws, ch, input_payload_func)
            except KeyboardInterrupt:
                try:
                    ws_input(ws, "\\u0003", input_payload_func)
                except ConnectionClosedError:
                    write_stdout(f"Connection closed")
                    return
                continue
            except ConnectionClosedError as e:
                write_stdout(f"Connection closed")
                return
            except Exception as e:
                write_stdout(f"Fatal: {e}, type: {type(e)}")
                return
    finally:
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()