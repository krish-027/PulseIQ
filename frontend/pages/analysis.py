import re

import streamlit as st

from services.api_client import APIClientError, api_client


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Analyze Feedback | PulseIQ",
    page_icon="📄",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .analysis-header {
            margin-bottom: 1.5rem;
        }

        .analysis-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .analysis-subtitle {
            color: #94a3b8;
            font-size: 1rem;
        }

        .result-card {
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }

        .result-label {
            color: #94a3b8;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.35rem;
        }

        .result-value {
            font-size: 1.25rem;
            font-weight: 600;
        }

        .category-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .category-excellent {
            background: rgba(34, 197, 94, 0.15);
            color: #4ade80;
        }

        .category-good {
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
        }

        .category-improvements {
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
        }

        .category-poor {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
        }

        /* Compact upload / processing metadata cards */
        .upload-meta-card {
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            min-height: 76px;
        }

        .upload-meta-label {
            color: #94a3b8;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.3rem;
        }

        .upload-meta-value {
            color: #e2e8f0;
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.3;
            overflow-wrap: anywhere;
            word-break: break-word;
        }

        .section-description {
            color: #94a3b8;
            margin-bottom: 1rem;
        }

        .metric-card {
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }

        .metric-value {
            font-size: 1.7rem;
            font-weight: 700;
        }

        .metric-label {
            color: #94a3b8;
            font-size: 0.85rem;
        }

        .keyword-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        .keyword {
            display: inline-block;
            background: rgba(245, 158, 11, 0.10);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 7px;
            padding: 0.4rem 0.65rem;
            font-size: 0.8rem;
            line-height: 1.3;
            white-space: normal;
            overflow-wrap: anywhere;
        }

        .evidence-empty {
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 1rem;
            color: #94a3b8;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_category_class(category: str) -> str:
    """Return CSS class for a classification category."""

    mapping = {
        "Excellent": "category-excellent",
        "Good": "category-good",
        "Need Improvements": "category-improvements",
        "Poor": "category-poor",
    }

    return mapping.get(category, "")


def format_file_size(size_bytes: int) -> str:
    """
    Format uploaded file size using a human-readable unit.

    Examples:
        2150 -> 2.10 KB
        1048576 -> 1.00 MB
    """

    if size_bytes < 1024:
        return f"{size_bytes} B"

    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"

    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_retrieved_examples(result: dict) -> list:
    """
    Extract retrieved RAG examples from the API response.

    The current upload API returns `retrieved_examples`.
    The additional fallbacks keep the frontend tolerant of equivalent
    response names during integration.
    """

    candidates = [
        result.get("retrieved_examples"),
        result.get("retrieved_documents"),
        result.get("retrieved_evidence"),
        result.get("evidence"),
    ]

    for candidate in candidates:
        if isinstance(candidate, list):
            return candidate

    return []


def render_category_badge(category: str) -> None:
    """Render a styled classification category badge."""

    css_class = get_category_class(category)

    st.markdown(
        f"""
        <span class="category-badge {css_class}">
            {category}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_flagged_keywords(keywords: list) -> None:
    """Render flagged keywords as clean, separated tags."""

    if not keywords:
        st.caption("No flagged keywords identified.")
        return

    cleaned_keywords = []
    seen = set()

    for keyword in keywords:
        keyword = str(keyword).strip()

        if not keyword:
            continue

        # Remove a trailing numeric rating such as:
        # "Employee greeted you politely 4"
        # "Employee listened carefully to your concerns 1"
        keyword = re.sub(r"\s+\d+(?:\.\d+)?$", "", keyword).strip()

        if not keyword or keyword in seen:
            continue

        seen.add(keyword)
        cleaned_keywords.append(keyword)

    if not cleaned_keywords:
        st.caption("No flagged keywords identified.")
        return

    keyword_html = "".join(
        f"""
        <span class="keyword">
            {keyword}
        </span>
        """
        for keyword in cleaned_keywords
    )

    st.markdown(
        f"""
        <div class="keyword-container">
            {keyword_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_retrieved_evidence(retrieved_examples: list) -> None:
    """
    Render the reference feedback examples retrieved by the RAG pipeline.

    Uses native Streamlit components rather than custom HTML so that the
    evidence layout remains stable and no raw HTML appears in the UI.
    """

    if not retrieved_examples:
        st.info(
            "No retrieved evidence was returned by the API."
        )
        return

    for index, evidence in enumerate(
        retrieved_examples,
        start=1,
    ):
        if not isinstance(evidence, dict):
            continue

        feedback_id = evidence.get(
            "feedback_id",
            "Unknown",
        )

        category = evidence.get(
            "category",
            "Unknown",
        )

        split = evidence.get(
            "split",
            "Unknown",
        )

        feedback = evidence.get(
            "feedback",
            "",
        )

        # ---------------------------------------------------------------
        # Evidence card
        # ---------------------------------------------------------------

        with st.container(border=True):

            # Header
            header_col1, header_col2 = st.columns(
                [5, 1],
                vertical_alignment="center",
            )

            with header_col1:
                st.markdown(
                    f"**Reference Example {index}**"
                )

            with header_col2:
                render_category_badge(category)

            # Metadata
            meta_col1, meta_col2 = st.columns(2)

            with meta_col1:
                st.caption("FEEDBACK ID")
                st.write(feedback_id)

            with meta_col2:
                st.caption("CORPUS")
                st.write(split)

            st.divider()

            # Retrieved feedback
            st.caption("RETRIEVED FEEDBACK")

            if feedback:
                st.text_area(
                    f"Retrieved feedback {index}",
                    value=feedback,
                    height=190,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"retrieved_feedback_{index}",
                )
            else:
                st.info(
                    "No feedback text was returned for this reference."
                )



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
    <div class="analysis-header">
        <div class="analysis-title">Analyze Feedback</div>
        <div class="analysis-subtitle">
            Upload a customer feedback PDF and let PulseIQ extract,
            retrieve, classify, and explain the feedback.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Upload section
# ---------------------------------------------------------------------------

st.subheader("Upload Feedback PDF")

st.markdown(
    """
    <div class="section-description">
        Upload a digital customer feedback form. PulseIQ will process the
        document, run the RAG pipeline, classify the feedback, and return
        supporting evidence.
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a PDF feedback form",
    type=["pdf"],
    help="Upload a customer feedback PDF for analysis.",
)


if uploaded_file is not None:
    file_size = format_file_size(
        uploaded_file.size
    )

    file_col1, file_col2, file_col3 = st.columns(
        [2.8, 1, 0.8]
    )

    with file_col1:
        st.markdown(
            f"""
            <div class="upload-meta-card">
                <div class="upload-meta-label">
                    File
                </div>
                <div class="upload-meta-value">
                    {uploaded_file.name}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with file_col2:
        st.markdown(
            f"""
            <div class="upload-meta-card">
                <div class="upload-meta-label">
                    Size
                </div>
                <div class="upload-meta-value">
                    {file_size}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with file_col3:
        st.markdown(
            """
            <div class="upload-meta-card">
                <div class="upload-meta-label">
                    Type
                </div>
                <div class="upload-meta-value">
                    PDF
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    analyze_button = st.button(
        "Analyze Feedback",
        type="primary",
        use_container_width=True,
    )

    if analyze_button:
        file_bytes = uploaded_file.getvalue()

        try:
            with st.spinner(
                "Processing PDF and running RAG analysis..."
            ):
                result = api_client.upload_pdf(
                    file_name=uploaded_file.name,
                    file_bytes=file_bytes,
                )

            st.session_state["latest_analysis"] = result

            st.success(
                "Feedback analyzed successfully."
            )

        except APIClientError as exc:
            st.error(
                f"Analysis failed: {exc}"
            )

        except Exception as exc:
            st.error(
                f"Unexpected error during analysis: {exc}"
            )


# ---------------------------------------------------------------------------
# Latest analysis result
# ---------------------------------------------------------------------------

result = st.session_state.get(
    "latest_analysis"
)

if not result:
    st.info(
        "Upload a feedback PDF and click **Analyze Feedback** "
        "to see the classification and RAG evidence."
    )
    st.stop()


# ---------------------------------------------------------------------------
# Normalize response
# ---------------------------------------------------------------------------

feedback_id = result.get(
    "feedback_id",
    "Unknown",
)

filename = result.get(
    "filename",
    uploaded_file.name
    if uploaded_file is not None
    else "Unknown",
)

feedback_text = result.get(
    "feedback",
    result.get(
        "extracted_text",
        "",
    ),
)

classification = result.get(
    "classification",
    {},
)

if not isinstance(classification, dict):
    classification = {}


category = classification.get(
    "category",
    result.get(
        "category",
        "Unknown",
    ),
)

confidence = classification.get(
    "confidence",
    result.get(
        "confidence",
    ),
)

explanation = classification.get(
    "explanation",
    result.get(
        "explanation",
        "",
    ),
)

flagged_keywords = classification.get(
    "flagged_keywords",
    result.get(
        "flagged_keywords",
        [],
    ),
)

retrieved_examples = get_retrieved_examples(
    result
)

retrieved_count = result.get(
    "retrieved_count",
    len(retrieved_examples),
)


# ---------------------------------------------------------------------------
# Result header
# ---------------------------------------------------------------------------

st.divider()

st.subheader("Analysis Result")

result_col1, result_col2, result_col3 = st.columns(
    [1.5, 1, 1]
)

with result_col1:
    st.markdown(
        '<div class="result-label">Classification</div>',
        unsafe_allow_html=True,
    )

    render_category_badge(category)


with result_col2:
    st.markdown(
        '<div class="result-label">Confidence</div>',
        unsafe_allow_html=True,
    )

    if confidence is not None:
        try:
            confidence_value = float(
                confidence
            )

            st.markdown(
                f"""
                <div class="result-value">
                    {confidence_value:.1%}
                </div>
                """,
                unsafe_allow_html=True,
            )

        except (TypeError, ValueError):
            st.markdown(
                f"""
                <div class="result-value">
                    {confidence}
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.markdown(
            '<div class="result-value">N/A</div>',
            unsafe_allow_html=True,
        )


with result_col3:
    st.markdown(
        '<div class="result-label">RAG Evidence</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="result-value">
            {retrieved_count}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Classification rationale
# ---------------------------------------------------------------------------

st.markdown("### Classification Rationale")

if explanation:
    st.markdown(
        f"""
        <div class="result-card">
            {explanation}
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.info(
        "No classification explanation was returned by the backend."
    )


# ---------------------------------------------------------------------------
# Flagged keywords
# ---------------------------------------------------------------------------

st.markdown("### Flagged Keywords")

st.caption(
    "Keywords identified by the classification pipeline as useful "
    "evidence for understanding the feedback."
)

render_flagged_keywords(
    flagged_keywords
)


# ---------------------------------------------------------------------------
# RAG retrieved evidence
# ---------------------------------------------------------------------------

st.markdown("### Retrieved Evidence")

st.caption(
    "Reference feedback retrieved from the FAISS knowledge base "
    "and provided to the classification model. "
    "These examples are supporting evidence, not independent votes."
)

render_retrieved_evidence(
    retrieved_examples
)


# ---------------------------------------------------------------------------
# Extracted feedback
# ---------------------------------------------------------------------------

st.markdown("### Extracted Feedback")

if feedback_text:
    st.text_area(
        "Feedback text",
        value=feedback_text,
        height=260,
        disabled=True,
        label_visibility="collapsed",
    )

else:
    st.info(
        "No extracted feedback text was returned by the backend."
    )


# ---------------------------------------------------------------------------
# Processing metadata
# ---------------------------------------------------------------------------

st.markdown("### Processing Details")

metadata_col1, metadata_col2 = st.columns(2)

with metadata_col1:
    st.markdown(
        f"""
        <div class="upload-meta-card">
            <div class="upload-meta-label">
                Feedback ID
            </div>
            <div class="upload-meta-value">
                {feedback_id}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metadata_col2:
    st.markdown(
        f"""
        <div class="upload-meta-card">
            <div class="upload-meta-label">
                Retrieved References
            </div>
            <div class="upload-meta-value">
                {retrieved_count}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Backend response metadata
# ---------------------------------------------------------------------------

status = result.get(
    "status"
)

message = result.get(
    "message"
)

if status or message:
    with st.expander("Processing Status"):

        if status:
            st.write(
                f"**Status:** {status}"
            )

        if message:
            st.write(
                f"**Message:** {message}"
            )


# ---------------------------------------------------------------------------
# Debug information
# ---------------------------------------------------------------------------

with st.expander("API Response"):
    st.json(result)