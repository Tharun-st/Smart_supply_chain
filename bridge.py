"""
Intelligent Supply Chain Management System
Persistent Python WSGI/Flask Fast IPC Bridge

Enables sub-millisecond execution of the Flask application, custom data structures,
and algorithmic operations via standard I/O communication without requiring elevated
socket listening permissions on restricted Windows systems.
"""

import sys
import json
import os

# Preserve the true stdout stream for Node.js IPC JSON messaging
ipc_stdout = sys.stdout
# Redirect standard sys.stdout to sys.stderr so any print() statements (e.g. database logs) do not corrupt the IPC protocol
sys.stdout = sys.stderr

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def run_bridge():
    client = app.test_client()
    sys.stderr.write("[Python Bridge] Initialized Flask client with live DSA services.\n")
    sys.stderr.flush()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            req = json.loads(line)
            method = req.get("method", "GET").upper()
            path = req.get("path", "/")
            body = req.get("body")
            headers = req.get("headers", {})

            # Prepare request data
            kwargs = {
                "method": method,
                "path": path,
                "headers": headers
            }
            if body:
                if isinstance(body, dict) or isinstance(body, list):
                    kwargs["json"] = body
                else:
                    kwargs["data"] = body

            # Execute request through Flask application pipeline
            response = client.open(**kwargs)

            # Response formatting
            content_type = response.headers.get("Content-Type", "text/html; charset=utf-8")
            resp_payload = {
                "status": response.status_code,
                "content_type": content_type,
                "body": response.get_data(as_text=True)
            }

            ipc_stdout.write(json.dumps(resp_payload) + "\n")
            ipc_stdout.flush()

        except Exception as e:
            err_payload = {
                "status": 500,
                "content_type": "application/json",
                "body": json.dumps({"status": "error", "message": str(e)})
            }
            ipc_stdout.write(json.dumps(err_payload) + "\n")
            ipc_stdout.flush()

if __name__ == "__main__":
    run_bridge()
