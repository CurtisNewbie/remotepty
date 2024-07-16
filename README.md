# remotepty

Very basic client-side pty library written in Python. It was originally written to communicate with the remote server terminal using websocket. The default emulated terminal was implemented using xterm.js that runs in a browser, but I prefer a real terminal to a web browser, I just wrote one for myself.

Few adjustments are needed for the three functions below, these are used to build websocket messages. It's not guaranteed to work out of box, but at least it can be a starting point for you.

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