"""Reusable TastePilot UI blocks (matches reference mockups)."""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from app.models.recommendation import RecommendationResponse
from app.ui.assets import EMPTY_ILLUSTRATION_PATH, LOADING_RING_PATH, LOGO_PATH, logo_src

THEME_CSS = Path(__file__).resolve().parent.parent / "static" / "theme.css"
FORM_FIELDS_CSS = Path(__file__).resolve().parent.parent / "static" / "form_fields.css"
FOOTER_AREAS = ["Koramangala", "Indiranagar", "HSR Layout", "Whitefield"]

LOGO_WIDTH_NAV = 160  # matches images/code.html reference header
LOGO_WIDTH_FOOTER = 120
LOGO_HEIGHT_LOADING = 48

MOOD_MATCH_FOOTER: dict[str, str] = {
    "date_night": "Great match for date night",
    "family_dinner": "Great match for family dining",
    "quick_lunch": "Great match for a quick lunch",
    "friends_hangout": "Great match for friends hangout",
    "work_meeting": "Great match for work meetings",
    "solo_dining": "Great match for solo dining",
    "celebration_birthday": "Great match for celebrations",
    "fine_dining": "Great match for fine dining",
    "cafe_chill": "Great match for a relaxed cafe vibe",
}


def inject_theme() -> None:
    """Inject theme.css + form_fields.css (single form card + bordered inputs)."""
    css = THEME_CSS.read_text(encoding="utf-8")
    fields_css = FORM_FIELDS_CSS.read_text(encoding="utf-8") if FORM_FIELDS_CSS.is_file() else ""
    st.markdown(f"<style>{css}\n{fields_css}</style>", unsafe_allow_html=True)


def inject_form_field_styles() -> None:
    """No-op: input borders are CSS-only (form_fields.css)."""


def render_logo(
    *,
    variant: str = "nav",
    width_px: int | None = None,
    height_px: int | None = None,
    pulse: bool = False,
) -> str:
    pulse_class = " tp-logo-pulse" if pulse else ""
    extra_class = f" tp-logo-{variant}"
    if variant == "nav":
        w = width_px or LOGO_WIDTH_NAV
        style = f"width:{w}px;height:auto;max-width:{w}px;display:block;"
    elif variant == "footer":
        w = width_px or LOGO_WIDTH_FOOTER
        style = f"width:{w}px;height:auto;max-width:{w}px;display:block;"
    else:
        h = height_px or LOGO_HEIGHT_LOADING
        style = f"height:{h}px;width:auto;max-height:{h}px;display:block;"
    return (
        f'<img class="tp-logo tp-logo-dark{extra_class}{pulse_class}" src="{logo_src()}" '
        f'alt="TastePilot" style="{style}" />'
    )


def render_nav() -> None:
    """Logo top-left, vertically centered with Home / About (reference: images/code.html)."""
    logo_html = render_logo(variant="nav", width_px=LOGO_WIDTH_NAV)
    st.markdown(
        f"""
        <div class="tp-glow"></div>
        <header class="tp-nav-bar">
            <div class="tp-nav-bar-inner">
                <a class="tp-nav-brand" href="#" aria-label="TastePilot home">{logo_html}</a>
                <nav class="tp-nav-links tp-nav-links-beside-logo">
                    <a href="#" class="active">Home</a>
                    <a href="#">About</a>
                </nav>
                <div class="tp-nav-icons">
                    <span class="material-symbols-outlined tp-icon-red">notifications</span>
                    <span class="material-symbols-outlined tp-icon-red">account_circle</span>
                </div>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <section class="tp-hero">
            <div class="tp-badge">
                <span class="material-symbols-outlined tp-icon-red" style="font-size:14px;">auto_awesome</span>
                Discover the future of dining
            </div>
            <h1>TastePilot <span>AI</span></h1>
            <p>Personalized restaurant discovery powered by <strong>AI</strong> and real-world dining preferences.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    area_links = "".join(f'<a href="#">{html.escape(a)}</a>' for a in FOOTER_AREAS)
    st.markdown(
        f"""
        <footer class="tp-footer">
            {render_logo(variant="footer")}
            <p>Smarter restaurant discovery for Bangalore food lovers.</p>
            <div class="tp-footer-divider"></div>
            <div class="tp-footer-links">
                {area_links}
                <span class="tp-footer-sep">|</span>
                <a href="#">Terms</a>
                <a href="#">Privacy</a>
            </div>
            <p class="tp-footer-copy">© 2026 TastePilot AI — Helping Bangalore discover better places to eat.</p>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def render_loading_screen() -> None:
    ring_uri = ""
    if LOADING_RING_PATH.is_file():
        import base64

        ring_uri = (
            "data:image/svg+xml;base64,"
            + base64.b64encode(LOADING_RING_PATH.read_bytes()).decode("ascii")
        )
    ring_html = (
        f'<img class="tp-loading-ring" src="{ring_uri}" alt="" aria-hidden="true" />'
        if ring_uri
        else ""
    )
    st.markdown(
        f"""
        <div class="tp-loading-overlay" role="dialog" aria-modal="true" aria-busy="true"
             aria-label="Finding restaurant recommendations">
            <div class="tp-loading-card">
                <div class="tp-loading-logo-wrap">
                    {ring_html}
                    {render_logo(variant="loading", pulse=True)}
                </div>
                <h2 class="tp-loading-title">Finding restaurants you'll actually love</h2>
                <p class="tp-loading-sub">Filtering real restaurants and ranking your best matches.</p>
                <ul class="tp-loading-steps" aria-live="polite">
                    <li class="tp-step tp-step-1">
                        <span class="tp-step-icon" aria-hidden="true">
                            <span class="tp-step-mark tp-step-mark-pending"></span>
                            <span class="tp-step-mark tp-step-mark-active">
                                <span class="material-symbols-outlined">progress_activity</span>
                            </span>
                            <span class="tp-step-mark tp-step-mark-done">
                                <span class="material-symbols-outlined">check</span>
                            </span>
                        </span>
                        <span class="tp-step-label">Filtering restaurants</span>
                    </li>
                    <li class="tp-step tp-step-2">
                        <span class="tp-step-icon" aria-hidden="true">
                            <span class="tp-step-mark tp-step-mark-pending"></span>
                            <span class="tp-step-mark tp-step-mark-active">
                                <span class="material-symbols-outlined">progress_activity</span>
                            </span>
                            <span class="tp-step-mark tp-step-mark-done">
                                <span class="material-symbols-outlined">check</span>
                            </span>
                        </span>
                        <span class="tp-step-label">Ranking with AI</span>
                    </li>
                    <li class="tp-step tp-step-3">
                        <span class="tp-step-icon" aria-hidden="true">
                            <span class="tp-step-mark tp-step-mark-pending"></span>
                            <span class="tp-step-mark tp-step-mark-active tp-step-mark-sparkle">✨</span>
                            <span class="tp-step-mark tp-step-mark-done">
                                <span class="material-symbols-outlined">check</span>
                            </span>
                        </span>
                        <span class="tp-step-label tp-step-label-em">Preparing recommendations</span>
                    </li>
                </ul>
                <div class="tp-loading-helpers" aria-live="polite">
                    <p class="tp-loading-detail tp-loading-detail-1">Reviewing restaurants across Bangalore…</p>
                    <p class="tp-loading-detail tp-loading-detail-2">Finding matches for your taste and mood…</p>
                    <p class="tp-loading-detail tp-loading-detail-3">Ranking restaurants based on ratings and preferences…</p>
                </div>
                <div class="tp-loading-progress-pill">
                    <span class="tp-loading-pill-sparkle" aria-hidden="true">✨</span>
                    <span>Personalized recommendations in progress</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_premium_alert(kind: str, title: str, body: str, *, show_retry: bool = False) -> bool:
    st.markdown(
        f"""
        <div class="tp-alert tp-alert-{kind}">
            <strong>{html.escape(title)}</strong>
            <p>{html.escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if show_retry:
        return st.button("Try again", type="primary", use_container_width=True)
    return False


def _empty_illustration_html() -> str:
    ill_src = ""
    if EMPTY_ILLUSTRATION_PATH.is_file():
        import base64

        ill_src = (
            "data:image/svg+xml;base64,"
            + base64.b64encode(EMPTY_ILLUSTRATION_PATH.read_bytes()).decode("ascii")
        )
    logo_badge = render_logo(variant="loading", height_px=28)
    plate = (
        f'<img class="tp-empty-plate-bg" src="{ill_src}" alt="" />' if ill_src else ""
    )
    return f"""
    <div class="tp-empty-visual">
        {plate}
        <div class="tp-empty-logo-badge">{logo_badge}</div>
    </div>
    """


def render_empty_state() -> str | None:
    st.markdown(
        f"""
        <div class="tp-empty-page">
            {_empty_illustration_html()}
            <h2>We couldn't find a perfect match</h2>
            <p class="tp-empty-body">Try adjusting your cuisine, budget, or minimum rating — TastePilot will help you discover more places worth trying.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    clicked = None
    if st.button("Adjust filters", key="empty_adjust", type="secondary"):
        clicked = "adjust_filters"
    st.markdown('<p class="tp-empty-chips-label">Try relaxing your filters</p>', unsafe_allow_html=True)
    chips = [
        ("Lower minimum rating", "lower_rating"),
        ("Expand budget", "expand_budget"),
        ("Try nearby areas", "nearby_areas"),
        ("Broaden cuisine", "broaden_cuisine"),
    ]
    c1, c2, c3, c4 = st.columns(4)
    for col, (label, key) in zip((c1, c2, c3, c4), chips, strict=True):
        with col:
            if st.button(label, key=f"empty_chip_{key}", use_container_width=True):
                clicked = key
    st.markdown(
        '<p class="tp-empty-disclaimer"><em>We search real restaurants and rank recommendations based on your preferences.</em></p>',
        unsafe_allow_html=True,
    )
    return clicked


def render_results_header(summary: str | None, *, fallback: bool) -> None:
    if fallback:
        render_premium_alert(
            "warning",
            "AI ranking unavailable",
            "Showing top-rated matches from your filters with mood-aware fallback.",
        )
    headline = summary or (
        "We found great restaurant recommendations tailored to your preferences."
    )
    st.markdown(
        f"""
        <div class="tp-results-hero">
            <h1><span class="tp-sparkle">✨</span> {html.escape(headline)}</h1>
            <p>Here are your personalized matches based on your preferences.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _match_badge_html(rank: int) -> str:
    if rank == 1:
        return '<span class="tp-badge-best">#1 Best Match</span>'
    return f'<span class="tp-badge-rank">#{rank} Match</span>'


def _result_card_html(
    rank: int,
    name: str,
    location: str,
    cuisines: list[str],
    rating: float,
    estimated_cost: float,
    explanation: str,
    mood: str | None,
) -> str:
    chips = "".join(
        f"<span class='tp-chip'>{html.escape(_format_cuisine(c))}</span>"
        for c in cuisines[:5]
    )
    footer_line = MOOD_MATCH_FOOTER.get(mood or "", "Great match for your preferences")
    return f"""
    <div class="tp-result-card">
        <div class="tp-result-card-head">
            {_match_badge_html(rank)}
            <span class="tp-rating-pill">★ {rating:.1f}</span>
        </div>
        <h3>{html.escape(name)}</h3>
        <p class="tp-result-loc">📍 {html.escape(location)} · ₹{estimated_cost:.0f} for two</p>
        <div class="tp-result-chips">{chips}</div>
        <div class="tp-why-box">
            <strong>Why TastePilot picked this:</strong>
            <p>{html.escape(explanation)}</p>
        </div>
        <p class="tp-result-footer-line">✓ {html.escape(footer_line)}</p>
    </div>
    """


def _format_cuisine(value: str) -> str:
    return " ".join(
        word.capitalize() for word in value.replace("_", " ").replace("-", " ").split()
    )


def render_results_grid(
    response: RecommendationResponse,
    mood: str | None = None,
) -> None:
    """Render cards in columns — one markdown block per card (avoids Streamlit HTML sanitization)."""
    recs = list(response.recommendations)
    for i in range(0, len(recs), 3):
        batch = recs[i : i + 3]
        cols = st.columns(3, gap="medium")
        for col, rec in zip(cols, batch, strict=False):
            r = rec.restaurant
            with col:
                st.markdown(
                    _result_card_html(
                        rank=rec.rank,
                        name=r.name,
                        location=r.location,
                        cuisines=r.cuisines,
                        rating=r.rating,
                        estimated_cost=r.estimated_cost,
                        explanation=rec.explanation,
                        mood=mood,
                    ),
                    unsafe_allow_html=True,
                )


_BUDGET_DISPLAY: dict[str, str] = {
    "low": "Budget",
    "medium": "Medium",
    "high": "Premium",
}


def _format_budget_label(budget: str) -> str:
    key = (budget or "").strip().lower()
    if key in _BUDGET_DISPLAY:
        return _BUDGET_DISPLAY[key]
    return budget.replace("_", " ").strip().title() or "your budget"


def _format_min_rating_label(min_rating: float) -> str:
    text = f"{min_rating:.1f}".rstrip("0").rstrip(".")
    return f"{text}+"


def render_match_details(
    *,
    location: str,
    cuisine: str,
    budget: str,
    min_rating: float,
) -> None:
    """Consumer-friendly explainer for how results were matched (results page only)."""
    loc = html.escape((location or "").strip() or "your area")
    cuis = html.escape((cuisine or "").strip() or "your preferred cuisine")
    bud = html.escape(_format_budget_label(budget))
    rating = html.escape(_format_min_rating_label(min_rating))

    body = f"""
    <div class="tp-match-explainer">
        <p class="tp-match-explainer-subtitle">We matched restaurants based on what matters to you.</p>
        <div class="tp-match-explainer-rows">
            <div class="tp-match-explainer-row">
                <span class="tp-match-explainer-icon" aria-hidden="true">📍</span>
                <div class="tp-match-explainer-copy">
                    <span class="tp-match-explainer-label">Location</span>
                    <p class="tp-match-explainer-text">Showing restaurants in <strong>{loc}</strong></p>
                </div>
            </div>
            <div class="tp-match-explainer-row">
                <span class="tp-match-explainer-icon" aria-hidden="true">🍽️</span>
                <div class="tp-match-explainer-copy">
                    <span class="tp-match-explainer-label">Cuisine preference</span>
                    <p class="tp-match-explainer-text">Prioritized <strong>{cuis}</strong> restaurants</p>
                </div>
            </div>
            <div class="tp-match-explainer-row">
                <span class="tp-match-explainer-icon" aria-hidden="true">💰</span>
                <div class="tp-match-explainer-copy">
                    <span class="tp-match-explainer-label">Budget</span>
                    <p class="tp-match-explainer-text">Focused on <strong>{bud}</strong> dining options</p>
                </div>
            </div>
            <div class="tp-match-explainer-row">
                <span class="tp-match-explainer-icon" aria-hidden="true">⭐</span>
                <div class="tp-match-explainer-copy">
                    <span class="tp-match-explainer-label">Minimum rating</span>
                    <p class="tp-match-explainer-text">Recommended places rated <strong>{rating}</strong></p>
                </div>
            </div>
            <div class="tp-match-explainer-row">
                <span class="tp-match-explainer-icon" aria-hidden="true">✨</span>
                <div class="tp-match-explainer-copy">
                    <span class="tp-match-explainer-label">Personalized ranking</span>
                    <p class="tp-match-explainer-text">Ranked using ratings, reviews, cuisine match, dining preferences, and overall fit for your search</p>
                </div>
            </div>
        </div>
        <p class="tp-match-explainer-trust">We evaluated multiple restaurant options to find your best matches.</p>
    </div>
    """
    with st.expander("How TastePilot matched your restaurants", expanded=False):
        st.markdown(body, unsafe_allow_html=True)


def render_results_actions() -> tuple[bool, bool]:
    st.markdown(
        '<div class="tp-results-cta"><h3>Want better recommendations?</h3></div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        adjust = st.button("Adjust filters", key="results_adjust", use_container_width=True)
    with c2:
        again = st.button("Try another search", key="results_again", use_container_width=True)
    return adjust, again
