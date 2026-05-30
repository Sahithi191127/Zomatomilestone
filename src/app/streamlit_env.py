"""Apply Streamlit secrets to os.environ before Settings loads (Cloud + local secrets.toml)."""

from __future__ import annotations

import os


def apply_streamlit_secrets() -> None:
    """
    Map top-level Streamlit secrets to environment variables for pydantic-settings.

    Streamlit Community Cloud also injects secrets as env vars; this covers local
    `.streamlit/secrets.toml` when keys are not already set.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    try:
        secrets = st.secrets
    except Exception:
        return

    for key, value in secrets.items():
        if key.startswith("_"):
            continue
        env_key = str(key).upper()
        if isinstance(value, str):
            os.environ.setdefault(env_key, value)
        elif isinstance(value, (int, float, bool)):
            os.environ.setdefault(env_key, str(value))
