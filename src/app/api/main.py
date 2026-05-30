"""Run API with: python -m app.api.main (from PYTHONPATH=src)."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    reload = os.environ.get("API_RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run(
        "app.api.app:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        reload_dirs=["src"] if reload else None,
    )


if __name__ == "__main__":
    main()
