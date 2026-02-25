"""
Cloud startup script for AWS App Runner.
Adds /app/deps to sys.path so packages installed with --target survive
the multi-stage Docker COPY, then starts uvicorn.
"""
import sys
import os

# Ensure packages installed to /app/deps are importable
deps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deps")
if os.path.isdir(deps_dir):
    sys.path.insert(0, deps_dir)

# Also ensure the app directory itself is in the path (for src.* imports)
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"[start.py] Starting uvicorn on port {port}")
    print(f"[start.py] sys.path = {sys.path[:5]}")
    print(f"[start.py] deps_dir exists: {os.path.isdir(deps_dir)}")
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, log_level="info")
