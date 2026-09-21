from __future__ import annotations

import re

import streamlit as st

from services.api_client import (
    APIClientError,
    api_client,
)


# -------------------------------------------------------------------
# Styling
# -------------------------------------------------------------------

st.markdown(
    """
    <style>

    .page-eyebrow {
        color: #22D3C5;
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .page-title {
        color: #F8FAFC;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        margin-bottom: 0.3rem;
    }

    .page-description {
        color: #94A3B8;
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }

    .section-title {
        color: #F8FAFC;
        font-size: 1.15rem;
        font-weight: 750;
        margin-top: 1.7rem;
        margin-bottom: 0.25rem;
    }

    .section-description {
        color: #64748B;
        font-size: 0.8rem;
        margin-bottom: 0.8rem;
    }

    .result-card {
        background: #111C30;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 1rem;
        min-height: 145px;
    }

    .result-label {
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.45rem;
    }

    .result-value {
        color: #F8FAFC;
        font-size: 1.45rem;
        font-weight: 800;
        line-height: 1.25;
        word-break: break-word;
    }

    .category-value {
        color: #22D3C5;
    }

    .confidence-value {
        color: #F8FAFC;
    }

    .metric-caption {
        color: #64748B;
        font-size: 0.72rem;
        margin-top: 0.45rem;
    }

    .explanation-box {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 1rem;
        color: #CBD5E1;
        line-height: 1.65;
    }

    .keyword {
        display: inline-block;
        background: #3A2A05;
        border: 1px solid #8A6A00;
        border-radius: 999px;
        color: #FDE68A;
        font-size: 0.78rem;
        padding: 0.4rem 0.7rem;
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def clean_flagged_keyword(keyword: object) -> str:
    """
    Remove trailing numeric rating values from flagged keywords.

    Examples:
        "Overall satisfaction with employee behavior 4"
            -> "Overall satisfaction with employee behavior"

        "explained banking services clearly 1"
            -> "explained banking services clearly"
    """

    text = str(keyword).strip()

    # Remove one or more numeric characters at the end.
    text = re.sub(
        r"\s*\d+\s*$",
        "",
        text,
    ).strip()

    return text


def render_result_card(
    label: str,
    value: str,
    caption: str,
    *,
    category: bool = False,
) -> None:
    """
    Render an analysis metric using native Streamlit components.
    This avoids relying on multi-line raw HTML rendering.
    """

    with st.container(border=True):

        st.markdown(
            f'<div class="result-label">{label}</div>',
            unsafe_allow_html=True,
        )

        value_class = (
            "category-value"
            if category
            else "confidence-value"
        )

        st.markdown(
            f'<div class="result-value {value_class}">'
            f"{value}"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="metric-caption">{caption}</div>',
            unsafe_allow_html=True,
        )


# -------------------------------------------------------------------
# Page header
# -------------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">PulseIQ Analysis</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-title">Analyze Customer Feedback</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-description">
        Upload one or more customer feedback PDFs and let PulseIQ
        extract, retrieve, classify, and explain the customer experience.
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Upload section
# -------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Upload feedback</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Upload one or more customer feedback PDFs for end-to-end AI analysis.
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Choose PDF feedback forms",
    type=["pdf"],
    accept_multiple_files=True,
)


# -------------------------------------------------------------------
# Multi-PDF processing
# -------------------------------------------------------------------

if uploaded_files:

    st.caption(
        f"{len(uploaded_files)} PDF"
        f"{'s' if len(uploaded_files) != 1 else ''} selected"
    )

    analyze_button = st.button(
        "Analyze Selected PDFs",
        type="primary",
        use_container_width=False,
    )

    if analyze_button:

        batch_results = []
        batch_errors = []

        progress_bar = st.progress(0)

        status_placeholder = st.empty()

        total_files = len(uploaded_files)

        for index, uploaded_file in enumerate(
            uploaded_files,
            start=1,
        ):

            status_placeholder.caption(
                f"Analyzing {index}/{total_files}: "
                f"{uploaded_file.name}"
            )

            file_bytes = uploaded_file.getvalue()

            # --------------------------------------------------------
            # Validate current file
            # --------------------------------------------------------

            if not file_bytes:

                batch_errors.append(
                    {
                        "filename": uploaded_file.name,
                        "error": "The selected PDF is empty.",
                    }
                )

                progress_bar.progress(
                    index / total_files
                )

                continue

            # --------------------------------------------------------
            # Send PDF through the existing API
            # --------------------------------------------------------

            try:

                with st.spinner(
                    f"Processing {uploaded_file.name}..."
                ):

                    result = api_client.upload_pdf(
                        file_name=uploaded_file.name,
                        file_bytes=file_bytes,
                    )

                batch_results.append(result)

            except APIClientError as exc:

                batch_errors.append(
                    {
                        "filename": uploaded_file.name,
                        "error": str(exc),
                    }
                )

            except Exception as exc:

                batch_errors.append(
                    {
                        "filename": uploaded_file.name,
                        "error": (
                            f"Unexpected error: {str(exc)}"
                        ),
                    }
                )

            progress_bar.progress(
                index / total_files
            )

        status_placeholder.empty()

        # ------------------------------------------------------------
        # Store batch results
        # ------------------------------------------------------------

        st.session_state["batch_analyses"] = batch_results

        st.session_state["batch_analysis_errors"] = batch_errors

        st.session_state["latest_analysis"] = (
            batch_results[-1]
            if batch_results
            else None
        )

        # ------------------------------------------------------------
        # Batch feedback
        # ------------------------------------------------------------

        if batch_results:

            st.success(
                f"Successfully analyzed "
                f"{len(batch_results)} of "
                f"{total_files} PDF"
                f"{'s' if total_files != 1 else ''}."
            )

        if batch_errors:

            st.warning(
                f"{len(batch_errors)} PDF"
                f"{'s' if len(batch_errors) != 1 else ''} "
                f"could not be analyzed."
            )


# -------------------------------------------------------------------
# Read stored batch results
# -------------------------------------------------------------------

batch_results = st.session_state.get(
    "batch_analyses",
    [],
)

batch_errors = st.session_state.get(
    "batch_analysis_errors",
    [],
)

if not batch_results:

    if batch_errors:

        st.error(
            "No PDF could be analyzed successfully."
        )

        for error in batch_errors:

            st.write(
                f"**{error['filename']}** — "
                f"{error['error']}"
            )

    else:

        st.info(
            "Upload one or more PDFs and select "
            "**Analyze Selected PDFs** to see the analysis."
        )

    st.stop()


# -------------------------------------------------------------------
# Batch summary
# -------------------------------------------------------------------

if len(batch_results) > 1:

    st.markdown(
        '<div class="section-title">Batch Analysis Results</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-description">
            Summary of all successfully analyzed customer feedback PDFs.
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_rows = []

    for item in batch_results:

        confidence = item.get(
            "confidence",
            0.0,
        )

        summary_rows.append(
            {
                "File": item.get(
                    "filename",
                    "Unknown",
                ),
                "Category": item.get(
                    "category",
                    "Unknown",
                ),
                "Confidence": (
                    f"{confidence * 100:.1f}%"
                ),
                "Feedback ID": item.get(
                    "feedback_id",
                    "Unknown",
                ),
                "Retrieved": item.get(
                    "retrieved_count",
                    0,
                ),
            }
        )

    st.dataframe(
        summary_rows,
        use_container_width=True,
        hide_index=True,
    )

    if batch_errors:

        with st.expander(
            "View files that could not be analyzed"
        ):

            for error in batch_errors:

                st.write(
                    f"**{error['filename']}** — "
                    f"{error['error']}"
                )

    # ---------------------------------------------------------------
    # Detailed-result selector
    # ---------------------------------------------------------------

    result_labels = []

    for index, item in enumerate(
        batch_results
    ):

        result_labels.append(
            f"{index + 1}. "
            f"{item.get('filename', 'Unknown')} — "
            f"{item.get('category', 'Unknown')}"
        )

    selected_result = st.selectbox(
        "View detailed analysis",
        options=range(len(batch_results)),
        format_func=lambda index: result_labels[index],
    )

    result = batch_results[selected_result]

else:

    # Normal single-PDF experience.
    result = batch_results[0]


# -------------------------------------------------------------------
# Extract result fields
# -------------------------------------------------------------------

filename = result.get(
    "filename",
    "Unknown file",
)

feedback_id = result.get(
    "feedback_id",
    "Unknown",
)

category = result.get(
    "category",
    "Unknown",
)

confidence = result.get(
    "confidence",
    0.0,
)

explanation = result.get(
    "explanation",
    "",
)

flagged_keywords = result.get(
    "flagged_keywords",
    [],
)

retrieved_count = result.get(
    "retrieved_count",
    0,
)

extracted_text = result.get(
    "extracted_text",
    "",
)


# -------------------------------------------------------------------
# Analysis Result
# -------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Analysis Result</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        AI-generated classification based on the feedback and
        retrieved contextual evidence.
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Result cards
# -------------------------------------------------------------------

result_columns = st.columns(4)

with result_columns[0]:

    render_result_card(
        label="Classification",
        value=category,
        caption="Customer experience category",
        category=True,
    )

with result_columns[1]:

    render_result_card(
        label="Confidence",
        value=f"{confidence * 100:.1f}%",
        caption="Model confidence",
    )

with result_columns[2]:

    render_result_card(
        label="Retrieved Evidence",
        value=str(retrieved_count),
        caption="Reference examples used",
    )

with result_columns[3]:

    render_result_card(
        label="Feedback ID",
        value=feedback_id,
        caption="Stored analysis record",
    )


# -------------------------------------------------------------------
# Classification rationale
# -------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Classification Rationale</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Why PulseIQ assigned this category.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="explanation-box">
        {explanation}
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Flagged keywords
# -------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Flagged Keywords</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Keywords identified by the classification pipeline as
        supporting evidence.
    </div>
    """,
    unsafe_allow_html=True,
)

cleaned_keywords = []

for keyword in flagged_keywords:

    cleaned_keyword = clean_flagged_keyword(
        keyword
    )

    if cleaned_keyword:
        cleaned_keywords.append(
            cleaned_keyword
        )

if cleaned_keywords:

    keyword_html = " ".join(
        f'<span class="keyword">{keyword}</span>'
        for keyword in cleaned_keywords
    )

    st.markdown(
        keyword_html,
        unsafe_allow_html=True,
    )

else:

    st.caption(
        "No flagged keywords were returned for this feedback."
    )


# -------------------------------------------------------------------
# Extracted feedback
# -------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Extracted Feedback</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Text extracted from the uploaded PDF before AI analysis.
    </div>
    """,
    unsafe_allow_html=True,
)

if extracted_text:

    st.text_area(
        "Extracted text",
        value=extracted_text,
        height=300,
        label_visibility="collapsed",
    )

else:

    st.info(
        "No extracted text was returned by the backend."
    )


# -------------------------------------------------------------------
# Analysis Metadata
# -------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Analysis Metadata</div>',
    unsafe_allow_html=True,
)

metadata_column1, metadata_column2 = st.columns(2)

with metadata_column1:

    with st.container(border=True):

        st.markdown(
            "**Source Document**"
        )

        st.write(
            filename
        )

with metadata_column2:

    with st.container(border=True):

        st.markdown(
            "**Processing Status**"
        )

        st.write(
            result.get(
                "status",
                "Unknown",
            )
        )

        st.caption(
            result.get(
                "message",
                "",
            )
        )