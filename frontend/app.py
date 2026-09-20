from __future__ import annotations

import streamlit as st


# -------------------------------------------------------------------
# Page configuration
# -------------------------------------------------------------------

st.set_page_config(
    page_title="PulseIQ",
    page_icon="◈",
    layout="wide",
)


# -------------------------------------------------------------------
# Global application styling
# -------------------------------------------------------------------

st.markdown(
    """
    <style>

    /* =============================================================
       Global
       ============================================================= */

    .stApp {
        background: #0B1220;
        color: #F8FAFC;
    }

    .main {
        background: #0B1220;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }


    /* =============================================================
       Top navigation
       ============================================================= */

    /* The top navigation lives inside a keyed Streamlit container.
       Target the container and the actual anchor/icon nodes so the
       styling survives Streamlit DOM variations. */
    div.st-key-top-navigation {
        width: 100%;
        background: #0F172A !important;
        border-radius: 12px;
        padding: 1.05rem 0.2rem 0.15rem 0.2rem;
        margin-top: 0.65rem;
        margin-bottom: 0.7rem;
    }

    div.st-key-top-navigation a,
    div.st-key-top-navigation a *,
    div.st-key-top-navigation svg,
    div.st-key-top-navigation span.material-symbols-rounded,
    div.st-key-top-navigation span[class*="material-symbols"] {
        color: #F8FAFC !important;
        fill: #F8FAFC !important;
        stroke: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }

    /* Support both known Streamlit st.page_link DOM shapes. */
    div.st-key-top-navigation [data-testid="stPageLink-NavLink"],
    div.st-key-top-navigation a[data-testid="stPageLink-NavLink"],
    div.st-key-top-navigation [data-testid="stPageLink-NavLink"] a {
        width: 100% !important;
        min-height: 50px;
        box-sizing: border-box;
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 0.72rem 0.9rem;
        justify-content: center;
        text-decoration: none !important;
        cursor: pointer;
        display: flex !important;
        align-items: center;
    }

    div.st-key-top-navigation [data-testid="stPageLink-NavLink"]:hover,
    div.st-key-top-navigation a[data-testid="stPageLink-NavLink"]:hover,
    div.st-key-top-navigation [data-testid="stPageLink-NavLink"] a:hover {
        background: rgba(34, 211, 197, 0.10) !important;
        border-color: rgba(34, 211, 197, 0.45) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(15, 118, 110, 0.10);
    }

    div.st-key-top-navigation [data-testid="stPageLink-NavLink"][aria-current="page"],
    div.st-key-top-navigation a[data-testid="stPageLink-NavLink"][aria-current="page"],
    div.st-key-top-navigation [data-testid="stPageLink-NavLink"] a[aria-current="page"] {
        background: #22D3C5 !important;
        border-color: #22D3C5 !important;
    }

    div.st-key-top-navigation [data-testid="stPageLink-NavLink"][aria-current="page"],
    div.st-key-top-navigation [data-testid="stPageLink-NavLink"][aria-current="page"] *,
    div.st-key-top-navigation a[data-testid="stPageLink-NavLink"][aria-current="page"],
    div.st-key-top-navigation a[data-testid="stPageLink-NavLink"][aria-current="page"] *,
    div.st-key-top-navigation [data-testid="stPageLink-NavLink"] a[aria-current="page"],
    div.st-key-top-navigation [data-testid="stPageLink-NavLink"] a[aria-current="page"] * {
        color: #F8FAFC !important;
        fill: #F8FAFC !important;
        stroke: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }

    @media (max-width: 900px) {
        div.st-key-top-navigation [data-testid="stPageLink-NavLink"],
        div.st-key-top-navigation a[data-testid="stPageLink-NavLink"],
        div.st-key-top-navigation [data-testid="stPageLink-NavLink"] a {
            justify-content: flex-start;
        }
    }

    /* Separate System Status icon beside Evaluation. The existing five-item
       navigation remains untouched; only this new sibling is positioned. */
    div.st-key-top-navigation-shell {
        position: relative;
        width: 100%;
    }

    div.st-key-top-system-status {
        /* Keep the settings control pinned to the viewport so it remains
           visible regardless of the active page's own layout/CSS. */
        position: fixed !important;
        top: 0.65rem !important;
        right: 0.65rem !important;
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        min-height: 50px !important;
        max-width: 50px !important;
        max-height: 50px !important;
        padding: 0 !important;
        margin: 0 !important;
        z-index: 2147483647 !important;
        isolation: isolate !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        overflow: visible !important;
        pointer-events: auto !important;
    }

    div.st-key-top-system-status,
    div.st-key-top-system-status > div,
    div.st-key-top-system-status [data-testid="stPageLink-NavLink"],
    div.st-key-top-system-status a[data-testid="stPageLink-NavLink"],
    div.st-key-top-system-status [data-testid="stPageLink-NavLink"] a {
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        min-height: 50px !important;
        max-width: 50px !important;
        max-height: 50px !important;
        padding: 0 !important;
        margin: 0 !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        background: transparent !important;
        color: #0F172A !important;
        text-decoration: none !important;
        cursor: pointer !important;
    }

    /* The settings control uses a plain text gear instead of a Material icon.
       This avoids Streamlit-version/font rendering differences while keeping the
       control icon-only and dark navy. */
    /* The settings control uses one plain text gear only. The page definition
       deliberately has no icon, preventing a second smaller Material-symbol icon. */
    div.st-key-top-system-status [data-testid="stPageLink-NavLink"] [data-testid="stPageLink-NavLinkText"] {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 100% !important;
    }

    div.st-key-top-system-status [data-testid="stPageLink-NavLink"] a,
    div.st-key-top-system-status [data-testid="stPageLink-NavLink"] a * {
        color: #0F172A !important;
        fill: #0F172A !important;
        stroke: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        line-height: 1 !important;
    }

    div.st-key-top-system-status [data-testid="stPageLink-NavLink"] a span {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        align-items: center !important;
        justify-content: center !important;
        width: 32px !important;
        max-width: 32px !important;
        height: 32px !important;
        max-height: 32px !important;
        overflow: visible !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-family: "Segoe UI Symbol", "Noto Sans Symbols 2", "Noto Sans Symbols", sans-serif !important;
        font-size: 1.95rem !important;
        font-weight: 700 !important;
        font-style: normal !important;
        line-height: 1 !important;
        visibility: visible !important;
        opacity: 1 !important;
        text-rendering: geometricPrecision !important;
    }

    div.st-key-top-system-status [data-testid="stPageLink-NavLink"] a:hover,
    div.st-key-top-system-status [data-testid="stPageLink-NavLink"] a:focus-visible {
        background: rgba(34, 211, 197, 0.10) !important;
        border-color: rgba(34, 211, 197, 0.45) !important;
    }

    /* =============================================================
       Global buttons / dividers / cleanup
       ============================================================= */

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #155E63;
        background: #134E4A;
        color: #F8FAFC;
        font-weight: 650;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #22D3C5;
        background: #16615C;
        color: #FFFFFF;
    }

    hr {
        border-color: #1E293B;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Page definitions
# -------------------------------------------------------------------

home_page = st.Page(
    "pages/home.py",
    title="Home",
    icon=":material/home:",
    url_path="",
    default=True,
)

dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    url_path="dashboard",
)

analysis_page = st.Page(
    "pages/analysis.py",
    title="Analyze Feedback",
    icon=":material/analytics:",
    url_path="analyze",
)

search_page = st.Page(
    "pages/search.py",
    title="Search & Evidence",
    icon=":material/search:",
    url_path="search",
)

evaluation_page = st.Page(
    "pages/evaluation.py",
    title="Evaluation",
    icon=":material/monitoring:",
    url_path="evaluation",
)

system_status_page = st.Page(
    "pages/system_status.py",
    title="System Status",
    icon=None,
    url_path="system-status",
)


# -------------------------------------------------------------------
# Header brand — replaces the former sidebar toggle position.
# -------------------------------------------------------------------

st.html(
    """
    <style>
    .pulseiq-header-brand {
        position: fixed;
        top: 0.72rem;
        left: 1rem;
        z-index: 1200;
        font-size: 1.35rem;
        font-weight: 850;
        letter-spacing: -0.045em;
        line-height: 1;
        pointer-events: none;
        user-select: none;
    }

    .pulseiq-header-brand,
    .pulseiq-header-brand .dark {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    .pulseiq-header-brand .accent {
        color: #22D3C5 !important;
        -webkit-text-fill-color: #22D3C5 !important;
    }

    .pulseiq-header-brand {
        position: fixed !important;
        top: 0.72rem !important;
        left: 1rem !important;
        z-index: 2147483647 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        mix-blend-mode: normal !important;
        isolation: isolate !important;
    }
    </style>

    <div class="pulseiq-header-brand">
        <span class="dark">P</span><span class="accent">ulse</span><span class="dark">IQ</span>
    </div>
    """
)


# -------------------------------------------------------------------
# Global top navigation
# This renders on every page because app.py is the entrypoint.
# The existing five-item navigation is kept visually unchanged.
# A separate System Status icon is positioned beside Evaluation.
# -------------------------------------------------------------------

with st.container(key="top-navigation-shell"):
    with st.container(key="top-navigation"):
        nav_columns = st.columns(
            [1, 1, 1, 1, 1],
            gap="small",
        )

        with nav_columns[0]:
            st.page_link(home_page, label="Home", icon=":material/home:", use_container_width=True)

        with nav_columns[1]:
            st.page_link(dashboard_page, label="Dashboard", icon=":material/dashboard:", use_container_width=True)

        with nav_columns[2]:
            st.page_link(analysis_page, label="Analyze Feedback", icon=":material/analytics:", use_container_width=True)

        with nav_columns[3]:
            st.page_link(search_page, label="Search & Evidence", icon=":material/search:", use_container_width=True)

        with nav_columns[4]:
            st.page_link(evaluation_page, label="Evaluation", icon=":material/monitoring:", use_container_width=True)

# Keep the settings control OUTSIDE the navigation container. This prevents
# the Home page content from clipping or covering the fixed control.
with st.container(key="top-system-status"):
    st.page_link(
        system_status_page,
        label="⚙",
        use_container_width=True,
    )


# -------------------------------------------------------------------
# Application navigation
# -------------------------------------------------------------------

page = st.navigation(
    [
        home_page,
        dashboard_page,
        analysis_page,
        search_page,
        evaluation_page,
        system_status_page,
    ],
    position="hidden",
)


# -------------------------------------------------------------------
# Run selected page
# -------------------------------------------------------------------

page.run()
