import os
import subprocess

port = os.environ.get("PORT", "8501")
subprocess.run([
    "streamlit", "run", "dashboard.py",
    "--server.port", port,
    "--server.address", "0.0.0.0",
    "--server.headless", "true"
])