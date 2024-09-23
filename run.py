#!/usr/bin/python3
import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV") or "default")

if __name__ == "__main__":
    app.run(port=5000)
