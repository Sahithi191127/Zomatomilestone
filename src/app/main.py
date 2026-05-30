"""Streamlit presentation layer — TastePilot (reference: images/code.html)."""

from __future__ import annotations

import sys
from pathlib import Path
from time import perf_counter, sleep

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx

from app.streamlit_env import apply_streamlit_secrets

apply_streamlit_secrets()

from app.config import settings
from app.dependencies import get_recommendation_use_case, get_repository
from app.exceptions import PreferenceValidationError
from app.ui import components as ui

MOOD_OPTIONS: list[tuple[str, str]] = [
    ("Choose an occasion (optional)", ""),
    ("Date Night", "date_night"),
    ("Family Dinner", "family_dinner"),
    ("Quick Lunch", "quick_lunch"),
    ("Friends Hangout", "friends_hangout"),
    ("Work Meeting", "work_meeting"),
    ("Solo Dining", "solo_dining"),
    ("Celebration", "celebration_birthday"),
    ("Fine Dining", "fine_dining"),
    ("Cafe / Chill", "cafe_chill"),
]
MOOD_LABELS = [label for label, _ in MOOD_OPTIONS]
MOOD_VALUE_BY_LABEL = {label: value for label, value in MOOD_OPTIONS}

BUDGET_UI = [("BUDGET", "low"), ("MEDIUM", "medium"), ("PREMIUM", "high")]
RESULT_COUNTS = list(range(1, 11)) + [15, 20]
CUISINE_PLACEHOLDER = "Search or select cuisines…"
MAX_ADDITIONAL_CHARS = min(120, settings.max_additional_preferences_length)

PHASE_HOME = "home"
PHASE_LOADING = "loading"
PHASE_RESULTS = "results"
PHASE_EMPTY = "empty"
PHASE_ERROR = "error"
PHASE_DATA = "data_unavailable"


def _init_session() -> None:
    defaults = {
        "tp_phase": PHASE_HOME,
        "tp_payload": None,
        "tp_response": None,
        "tp_elapsed_ms": 0,
        "tp_error": "",
        "tp_error_type": "",
        "_tp_form_enhancer_loaded": False,
        "tp_form_min_rating": 2.9,
        "tp_form_budget_idx": 1,
        "tp_form_top_k": 5,
        "tp_form_mood_idx": 0,
        "tp_form_cuisine_key": "Italian",
        "tp_form_location": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _format_label(value: str) -> str:
    return " ".join(
        word.capitalize() for word in value.replace("_", " ").replace("-", " ").split()
    )


@st.cache_resource(show_spinner=False)
def _cached_repository():
    return get_repository()


def _safe_cities() -> list[str]:
    try:
        return _cached_repository().get_cities()
    except Exception:
        return []


def _safe_cuisines() -> list[str]:
    try:
        return _cached_repository().get_cuisines()
    except Exception:
        return []


def _default_index(options: list[str], preferred: str) -> int:
    if preferred in options:
        return options.index(preferred)
    return 0


def _cuisine_options(cuisines: list[str]) -> tuple[list[str], dict[str, str]]:
    """Display labels (capitalized) mapped to repository values."""
    display_to_raw: dict[str, str] = {}
    labels: list[str] = []
    for raw in cuisines:
        label = _format_label(raw)
        display_to_raw[label] = raw
        labels.append(label)
    return labels, display_to_raw


def _default_cuisine_label(cuisine_labels: list[str]) -> str:
    """Prefer Italian / first cuisine — not the placeholder (avoids blocked submits)."""
    preferred = st.session_state.tp_form_cuisine_key
    if preferred in cuisine_labels and preferred != CUISINE_PLACEHOLDER:
        return preferred
    for candidate in ("Italian", "North Indian", "Chinese"):
        if candidate in cuisine_labels:
            return candidate
    return cuisine_labels[0] if cuisine_labels else CUISINE_PLACEHOLDER


def _resolve_cuisine(cuisines: list[str], cuisine_query: str) -> str:
    query = cuisine_query.strip().lower()
    if not query:
        return "italian" if "italian" in cuisines else cuisines[0]
    for item in cuisines:
        if query in item.lower() or item.lower() in query:
            return item
    return query


LOADING_MIN_SECONDS = 4.5


def _clear_loading_session() -> None:
    for key in ("tp_loading_started", "tp_loading_api_done"):
        st.session_state.pop(key, None)


def _reset_to_home() -> None:
    st.session_state.tp_phase = PHASE_HOME
    st.session_state.tp_payload = None
    st.session_state.tp_response = None
    st.session_state.tp_error = ""
    st.session_state.tp_error_type = ""
    _clear_loading_session()


def _handle_loading_phase() -> None:
    """Dedicated loading state: overlay only, staged UX, then results."""
    if "tp_loading_started" not in st.session_state:
        st.session_state.tp_loading_started = perf_counter()

    ui.render_loading_screen()

    if not st.session_state.get("tp_loading_api_done"):
        _run_recommendation()
        st.session_state.tp_loading_api_done = True

    if st.session_state.tp_phase == PHASE_ERROR:
        _clear_loading_session()
        st.rerun()
        return

    if st.session_state.tp_phase in (PHASE_RESULTS, PHASE_EMPTY):
        elapsed = perf_counter() - float(st.session_state.tp_loading_started)
        remaining = LOADING_MIN_SECONDS - elapsed
        if remaining > 0:
            sleep(remaining)

    _clear_loading_session()
    st.rerun()


def _render_data_unavailable() -> None:
    ui.render_premium_alert(
        "info",
        "Restaurant data unavailable",
        "We could not load the restaurant catalog. Check your data path and try again.",
        show_retry=True,
    )
    if st.button("Retry loading data", type="primary", use_container_width=True):
        _cached_repository.clear()
        st.session_state.tp_phase = PHASE_HOME
        st.rerun()


def _render_budget_and_results_row() -> tuple[str, int]:
    """Budget uses horizontal radio (theme primary #b7122a for selection)."""
    budget_options = [label for label, _ in BUDGET_UI]
    budget_idx = int(st.session_state.tp_form_budget_idx)
    if budget_idx < 0 or budget_idx >= len(budget_options):
        budget_idx = 1

    row2a, row2b = st.columns(2, gap="large")
    with row2a:
        budget_label = st.radio(
            "BUDGET RANGE",
            options=budget_options,
            index=budget_idx,
            horizontal=True,
            width="stretch",
            key="tp_budget_radio",
        )
    with row2b:
        st.selectbox(
            "Number of results",
            options=RESULT_COUNTS,
            index=RESULT_COUNTS.index(int(st.session_state.tp_form_top_k)),
            key="tp_top_k_select",
        )

    top_k = int(st.session_state.tp_top_k_select)
    st.session_state.tp_form_budget_idx = budget_options.index(budget_label)
    st.session_state.tp_form_top_k = top_k
    return dict(BUDGET_UI)[budget_label], top_k


def _render_preferences_form(cities: list[str], cuisines: list[str]) -> bool:
    cuisine_labels, cuisine_map = _cuisine_options(cuisines) if cuisines else ([], {})

    with st.container(border=True, key="tp_preferences_form"):
        submitted = _render_preferences_fields(cities, cuisines, cuisine_labels, cuisine_map)
    return submitted


def _render_preferences_fields(
    cities: list[str],
    cuisines: list[str],
    cuisine_labels: list[str],
    cuisine_map: dict[str, str],
) -> bool:
    row1a, row1b = st.columns(2, gap="large")
    with row1a:
        if cities:
            default_city = st.session_state.tp_form_location or (
                "Bellandur" if "Bellandur" in cities else cities[0]
            )
            location = st.selectbox(
                "Area",
                options=cities,
                index=_default_index(cities, default_city),
                key="tp_area_select",
            )
        else:
            location = st.text_input("Area", value="Btm", key="tp_area_text")

    with row1b:
        min_rating = st.slider(
            "Minimum rating",
            min_value=0.0,
            max_value=5.0,
            value=float(st.session_state.tp_form_min_rating),
            step=0.1,
            key="tp_min_rating_slider",
        )
        st.markdown(
            f'<div class="rating-value">{min_rating:.1f} <span class="tp-rating-star">★</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="tp-form-row-gap"></div>', unsafe_allow_html=True)
    budget, top_k = _render_budget_and_results_row()
    st.markdown('<div class="tp-form-row-gap"></div>', unsafe_allow_html=True)

    if cuisines:
        default_cuisine = _default_cuisine_label(cuisine_labels)
        cuisine_display = st.selectbox(
            "Preferred cuisines",
            options=cuisine_labels,
            index=_default_index(cuisine_labels, default_cuisine),
            help="Search or select cuisines…",
            key="tp_cuisine_select",
        )
        cuisine = cuisine_map.get(cuisine_display, "")
    else:
        cuisine = st.text_input(
            "Preferred cuisines",
            value="Italian",
            placeholder="Search or select cuisines…",
            key="tp_cuisine_text",
        )
        cuisine_display = cuisine

    additional = st.text_area(
        "Additional preferences",
        value="",
        placeholder="Describe your perfect dining experience…",
        height=72,
        max_chars=MAX_ADDITIONAL_CHARS,
        key="tp_additional_prefs",
    )

    st.markdown('<div class="tp-form-row-gap"></div>', unsafe_allow_html=True)
    mood_label = st.selectbox(
        "Mood / occasion",
        options=MOOD_LABELS,
        index=int(st.session_state.tp_form_mood_idx),
        help="Choose an occasion (optional)",
        key="tp_mood_select",
    )
    mood = MOOD_VALUE_BY_LABEL.get(mood_label) or None

    st.markdown('<div class="tp-form-row-gap tp-form-row-gap-lg"></div>', unsafe_allow_html=True)
    submitted = st.button(
        "✨ Get AI Recommendations",
        type="primary",
        use_container_width=True,
        key="tp_submit_recommendations",
    )

    if not submitted:
        return False

    if cuisines and not cuisine:
        cuisine = _resolve_cuisine(cuisines, "italian")

    if isinstance(cuisine, str) and cuisines and cuisine:
        cuisine = _resolve_cuisine(cuisines, cuisine)
    elif isinstance(cuisine, str) and not cuisines:
        cuisine = cuisine.strip().lower()

    st.session_state.tp_form_min_rating = min_rating
    st.session_state.tp_form_mood_idx = MOOD_LABELS.index(mood_label)
    if cuisines:
        st.session_state.tp_form_cuisine_key = cuisine_display
    st.session_state.tp_form_location = location

    st.session_state.tp_payload = {
        "location": location,
        "budget": budget,
        "cuisine": cuisine,
        "min_rating": float(min_rating),
        "top_k": top_k,
        "mood": mood,
        "additional_preferences": additional.strip() or None,
    }
    st.session_state.tp_phase = PHASE_LOADING
    return True


def _apply_empty_chip(chip: str | None) -> None:
    if chip == "lower_rating":
        st.session_state.tp_form_min_rating = max(0.0, float(st.session_state.tp_form_min_rating) - 0.5)
    elif chip == "expand_budget":
        budget_options = [label for label, _ in BUDGET_UI]
        st.session_state.tp_form_budget_idx = min(2, int(st.session_state.tp_form_budget_idx) + 1)
        st.session_state.tp_budget_radio = budget_options[st.session_state.tp_form_budget_idx]
    elif chip in ("nearby_areas", "broaden_cuisine", "adjust_filters"):
        pass
    _reset_to_home()
    st.rerun()


def _run_recommendation() -> None:
    payload = st.session_state.tp_payload
    if not payload:
        _reset_to_home()
        return

    use_case = get_recommendation_use_case(strict_location=True)
    started = perf_counter()
    try:
        response = use_case.execute(payload)
    except PreferenceValidationError as exc:
        detail = exc.message
        if exc.suggestions:
            detail += f" Did you mean: {', '.join(_format_label(s) for s in exc.suggestions[:5])}?"
        st.session_state.tp_phase = PHASE_ERROR
        st.session_state.tp_error_type = "validation"
        st.session_state.tp_error = detail
        return
    except Exception:  # pragma: no cover
        st.session_state.tp_phase = PHASE_ERROR
        st.session_state.tp_error_type = "system"
        st.session_state.tp_error = "Something went wrong. Please try again."
        return

    st.session_state.tp_elapsed_ms = int((perf_counter() - started) * 1000)
    st.session_state.tp_response = response
    if not response.recommendations:
        st.session_state.tp_phase = PHASE_EMPTY
    else:
        st.session_state.tp_phase = PHASE_RESULTS


def render() -> None:
    st.set_page_config(page_title="TastePilot", page_icon="🍽️", layout="centered")
    _init_session()

    try:
        _render_app()
    except Exception as exc:  # pragma: no cover
        ui.inject_theme()
        st.error("The app hit an unexpected error. Details below.")
        st.exception(exc)
        if st.button("Reload home", type="primary"):
            _reset_to_home()
            st.rerun()


def _render_app() -> None:
    ui.inject_theme()
    phase = st.session_state.tp_phase

    if phase == PHASE_LOADING:
        _handle_loading_phase()
        return

    ui.render_nav()

    cities = _safe_cities()
    cuisines = _safe_cuisines()

    if not cities and not cuisines and phase == PHASE_HOME:
        ui.render_hero()
        _render_data_unavailable()
        ui.render_footer()
        return

    if phase == PHASE_ERROR:
        ui.render_hero()
        err_type = st.session_state.tp_error_type
        if err_type == "validation":
            ui.render_premium_alert(
                "error",
                "Check your preferences",
                st.session_state.tp_error,
            )
        else:
            retry = ui.render_premium_alert(
                "error",
                "Something went wrong",
                st.session_state.tp_error or "Something went wrong. Please try again.",
                show_retry=True,
            )
            if retry:
                _clear_loading_session()
                st.session_state.tp_phase = PHASE_LOADING
                st.rerun()
        if st.button("Adjust filters", use_container_width=True):
            _reset_to_home()
            st.rerun()
        ui.render_footer()
        return

    if phase == PHASE_EMPTY:
        chip = ui.render_empty_state()
        if chip:
            _apply_empty_chip(chip)
        ui.render_footer()
        return

    if phase == PHASE_RESULTS:
        response = st.session_state.tp_response
        if response is None:
            _reset_to_home()
            st.rerun()
        mood = None
        if st.session_state.tp_payload:
            mood = st.session_state.tp_payload.get("mood")
        ui.render_results_header(
            response.summary,
            fallback=response.meta.fallback_used,
        )
        ui.render_results_grid(response, mood=mood)
        payload = st.session_state.tp_payload or {}
        cuisine_label = st.session_state.get("tp_form_cuisine_key") or ""
        if not cuisine_label and payload.get("cuisine"):
            cuisine_label = " ".join(
                w.capitalize() for w in str(payload["cuisine"]).replace("_", " ").split()
            )
        ui.render_match_details(
            location=str(payload.get("location") or ""),
            cuisine=cuisine_label,
            budget=str(payload.get("budget") or "medium"),
            min_rating=float(payload.get("min_rating") or 0.0),
        )
        adjust, again = ui.render_results_actions()
        if adjust or again:
            _reset_to_home()
            st.rerun()
        ui.render_footer()
        return

    ui.render_hero()
    submitted = _render_preferences_form(cities, cuisines)
    if submitted:
        st.rerun()
    ui.render_footer()


def _launch_streamlit() -> None:
    from streamlit.web import cli as stcli

    script = str(Path(__file__).resolve())
    sys.argv = ["streamlit", "run", script, *sys.argv[1:]]
    raise SystemExit(stcli.main())


if get_script_run_ctx() is not None:
    render()
elif __name__ == "__main__":
    _launch_streamlit()
