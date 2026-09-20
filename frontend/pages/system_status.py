import streamlit as st

from services.api_client import APIClientError, api_client


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .status-header {
        padding: 0.5rem 0 1.25rem 0;
    }

    .status-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .status-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .status-card {
        background: #111827;
        border: 1px solid #243244;
        border-radius: 12px;
        padding: 1rem;
        min-height: 115px;
    }

    .status-card-title {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-bottom: 0.55rem;
    }

    .status-ready {
        color: #22c55e;
        font-size: 1rem;
        font-weight: 650;
    }

    .status-error {
        color: #ef4444;
        font-size: 1rem;
        font-weight: 650;
    }

    .status-detail {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 0.45rem;
    }

    .overall-card {
        background: #0f172a;
        border: 1px solid #243244;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
    }

    .overall-title {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 0.4rem;
    }

    .overall-status {
        color: #22c55e;
        font-size: 1.4rem;
        font-weight: 700;
    }

    .overall-status-error {
        color: #ef4444;
        font-size: 1.4rem;
        font-weight: 700;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def status_card(title, ready, detail):
    """Render a production-style service status card."""

    if ready:
        status_text = "● Ready"
        status_class = "status-ready"
    else:
        status_text = "● Unavailable"
        status_class = "status-error"

    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-card-title">{title}</div>
            <div class="{status_class}">{status_text}</div>
            <div class="status-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def check_endpoint(callable_endpoint):
    """
    Call a status endpoint and return:
        (success, response, error_message)
    """

    try:
        response = callable_endpoint()
        return True, response, None

    except APIClientError as exc:
        return False, None, str(exc)

    except Exception as exc:
        return False, None, str(exc)



st.markdown(
    """
    <style>
    /* =============================================================
       PulseIQ dark navy page theme
       Visual styling only — no application/data logic changes.
       ============================================================= */

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] .main,
    [data-testid="stMainBlockContainer"],
    section.main,
    .main,
    .block-container {
        background: #0F172A !important;
        color: #F8FAFC !important;
    }

    /* Standard page text */
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] em,
    [data-testid="stCaptionContainer"],
    [data-testid="stHeader"],
    h1, h2, h3, h4, h5, h6,
    p, label, small {
        color: #F8FAFC !important;
    }

    /* Streamlit form controls */
    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-baseweb="select"] > div,
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stDateInput"] input,
    [data-testid="stFileUploader"] section {
        background: #111827 !important;
        color: #F8FAFC !important;
        border-color: #334155 !important;
    }

    [data-baseweb="input"] *,
    [data-baseweb="textarea"] *,
    [data-baseweb="select"] *,
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }

    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stDateInput"] label,
    [data-testid="stFileUploader"] label {
        color: #F8FAFC !important;
    }

    /* Expanders, tabs, alerts and standard containers */
    [data-testid="stExpander"],
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stAlert"],
    [data-testid="stAlert"] p {
        color: #F8FAFC !important;
    }

    /* Dataframes/tables */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] *,
    [data-testid="stTable"],
    [data-testid="stTable"] * {
        color: #F8FAFC !important;
    }

    /* Native metric components */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: #F8FAFC !important;
    }

    /* Keep the page's dark navy surface continuous around the content. */
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {
        color: #F8FAFC;
    }

    /* Keep the Streamlit header visually compatible with the dark theme.
       Global top navigation styling remains controlled by app.py. */
    header[data-testid="stHeader"] {
        background: #0F172A !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="status-header">
        <div class="status-title">System Status</div>
        <div class="status-subtitle">
            Monitor the availability of the PulseIQ application services.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------

refresh_col, _ = st.columns([1.6, 4.4])

with refresh_col:
    if st.button(
        "Refresh Status",
        icon=":material/refresh:",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()


# ---------------------------------------------------------------------------
# Service checks
# ---------------------------------------------------------------------------

with st.spinner("Checking PulseIQ services…"):

    health_ok, health_data, health_error = check_endpoint(
        api_client.get_health
    )

    analysis_ok, analysis_data, analysis_error = check_endpoint(
        api_client.get_analysis_status
    )

    upload_ok, upload_data, upload_error = check_endpoint(
        api_client.get_upload_status
    )

    search_ok, search_data, search_error = check_endpoint(
        api_client.get_search_status
    )

    analytics_endpoint = getattr(api_client, "get_analytics_status", None)
    if callable(analytics_endpoint):
        analytics_ok, analytics_data, analytics_error = check_endpoint(
            analytics_endpoint
        )
    else:
        analytics_ok, analytics_data, analytics_error = (
            False,
            None,
            "Analytics status endpoint is unavailable.",
        )

    evaluation_ok, evaluation_data, evaluation_error = check_endpoint(
        api_client.get_evaluation_status
    )


all_services_ready = all(
    [
        health_ok,
        analysis_ok,
        upload_ok,
        search_ok,
        analytics_ok,
        evaluation_ok,
    ]
)


# ---------------------------------------------------------------------------
# Overall status
# ---------------------------------------------------------------------------

if all_services_ready:
    st.markdown(
        """
        <div class="overall-card">
            <div class="overall-title">Overall System Status</div>
            <div class="overall-status">● Operational</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="overall-card">
            <div class="overall-title">Overall System Status</div>
            <div class="overall-status-error">● Attention Required</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Core API</div>',
    unsafe_allow_html=True,
)

api_col1, api_col2, api_col3 = st.columns(3)

with api_col1:
    status_card(
        "FastAPI",
        health_ok,
        (
            "Backend API is responding."
            if health_ok
            else "Backend API could not be reached."
        ),
    )

with api_col2:
    status_card(
        "Analysis Service",
        analysis_ok,
        (
            "Analysis route is ready."
            if analysis_ok
            else "Analysis route is unavailable."
        ),
    )

with api_col3:
    status_card(
        "PDF Upload",
        upload_ok,
        (
            "Upload route is ready."
            if upload_ok
            else "Upload route is unavailable."
        ),
    )


# ---------------------------------------------------------------------------
# Application services
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Application Services</div>',
    unsafe_allow_html=True,
)

service_col1, service_col2, service_col3 = st.columns(3)

with service_col1:
    status_card(
        "Semantic Search",
        search_ok,
        (
            "Search route is ready."
            if search_ok
            else "Search route is unavailable."
        ),
    )

with service_col2:
    status_card(
        "Analytics",
        analytics_ok,
        (
            "Analytics route is ready."
            if analytics_ok
            else "Analytics route is unavailable."
        ),
    )

with service_col3:
    status_card(
        "Evaluation",
        evaluation_ok,
        (
            "Evaluation API is ready."
            if evaluation_ok
            else "Evaluation API is unavailable."
        ),
    )


# ---------------------------------------------------------------------------
# Evaluation availability
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Evaluation Availability</div>',
    unsafe_allow_html=True,
)

if evaluation_ok and isinstance(evaluation_data, dict):

    supported_splits = evaluation_data.get(
        "supported_splits",
        [],
    )

    if supported_splits:
        split_col1, split_col2 = st.columns(2)

        development_available = (
            "development" in supported_splits
        )

        final_available = (
            "final_benchmark" in supported_splits
        )

        with split_col1:
            status_card(
                "Development Evaluation",
                development_available,
                (
                    "Evaluation report is supported."
                    if development_available
                    else "Development report is not available."
                ),
            )

        with split_col2:
            status_card(
                "Final Benchmark",
                final_available,
                (
                    "Benchmark evaluation is supported."
                    if final_available
                    else "Final benchmark is not available."
                ),
            )

    else:
        st.info(
            "The Evaluation API is available, but no supported "
            "evaluation splits were reported."
        )

else:
    st.info(
        "Evaluation availability could not be determined because "
        "the Evaluation API is unavailable."
    )


# ---------------------------------------------------------------------------
# Diagnostic details
# ---------------------------------------------------------------------------

with st.expander(
    "Service diagnostics",
    expanded=False,
):
    diagnostics = {
        "FastAPI": health_data if health_ok else health_error,
        "Analysis": analysis_data if analysis_ok else analysis_error,
        "Upload": upload_data if upload_ok else upload_error,
        "Search": search_data if search_ok else search_error,
        "Analytics": analytics_data if analytics_ok else analytics_error,
        "Evaluation": evaluation_data if evaluation_ok else evaluation_error,
    }

    st.json(diagnostics)