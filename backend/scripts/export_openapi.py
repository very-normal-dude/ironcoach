"""Writes the API contract (docs/openapi.json) from the real code.

Run from the backend/ folder (virtual environment active):
    python scripts/export_openapi.py

Re-run it and commit the result every time you change an endpoint or a schema.
"""
import json
import sys
from pathlib import Path

# make "import app" work when running this file directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402

out = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {out}")
