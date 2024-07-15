# remotepty

Very very basic client-side pty library written in Python. Similar to xterm.js (not really), but instead, a real terminal is used. Few adjustments are needed for the three functions below, these are used to build websocket messages. It's not guaranteed that it will work out of box (works for me), but at least it can be a starting point for you.

```sh
pip install websockets
```

```py
import remotepty

url = "wss://...."

def msg_payload(m):
    return f'...'

def ping_payload():
    return '...'

def resize_payload(cols, rows):
    return f'...'

remotepty.attach_remote_pty_url(
    ws_url=url,
    input_payload_func=msg_payload,
    ping_payload_func=ping_payload,
    resize_payload_func=resize_payload,
)
```