#!/usr/bin/env python3
"""Export FastAPI OpenAPI schema to JSON file."""
import json
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def export_openapi(output_path: str = "openapi.json") -> None:
    """Export the OpenAPI schema to a JSON file."""
    schema = app.openapi()
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Exported OpenAPI schema to {output_path}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "openapi.json"
    export_openapi(output)