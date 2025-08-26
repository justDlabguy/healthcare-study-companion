import os
from pathlib import Path

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
print(f"Created uploads directory at: {UPLOAD_DIR.absolute()}")
