# remotepty

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