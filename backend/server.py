import os
from backend.api import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n========================================================")
    print(f"  NEXUS | Green AI Energy Optimization Backend Server")
    print(f"  Running on: http://localhost:{port}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
