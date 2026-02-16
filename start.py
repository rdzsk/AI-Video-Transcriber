import subprocess
import time
import webview
import os
import signal

PORT = "3000"

server = subprocess.Popen(
    ["python3", "-m", "http.server", PORT],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(0.7)

try:
    webview.create_window("AI", f"http://127.0.0.1:{PORT}/static/index.html", width=1000, height=800)
    webview.start(gui="qtk")
finally:
    server.send_signal(signal.SIGTERM)

