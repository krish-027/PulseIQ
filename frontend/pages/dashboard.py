from __future__ import annotations

from datetime import date
from typing import Any, Literal

import pandas as pd
import streamlit as st

from services.api_client import (
    APIClientError,
    api_client,
)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

CATEGORIES = [
    "All",
    "Excellent",
    "Good",
    "Need Improvements",
    "Poor",
]


def format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_count(value: int) -> str:
    return f"{value:,}"


def get_category_counts(
    category_distribution: list[dict[str, Any]],
) -> dict[str, int]:
    return {
        item["category"]: item["count"]
        for item in category_distribution
    }


def get_confidence_counts(
    confidence_distribution: list[dict[str, Any]],
) -> dict[str, int]:
    return {
        item["band"]: item["count"]
        for item in confidence_distribution
    }


def render_category_badge(category: str) -> None:
    """Render a compact native Streamlit category badge."""
    colors: dict[
        str,
        Literal["red", "orange", "blue", "green", "gray"],
    ] = {
        "Excellent": "green",
        "Good": "blue",
        "Need Improvements": "orange",
        "Poor": "red",
    }

    badge_color = colors.get(category, "gray")

    if hasattr(st, "badge"):
        st.badge(category, color=badge_color)
    else:
        # Compatibility fallback for older Streamlit versions.
        st.caption(category)


def render_page_header() -> None:
    st.caption("PULSEIQ ANALYTICS")
    st.title("Customer Feedback Dashboard")
    st.write(
        "Monitor customer satisfaction, confidence, recurring concerns, "
        "and feedback requiring attention across the analyzed dataset."
    )


def render_metric_group(
    items: list[tuple[str, str, str]],
) -> None:
    columns = st.columns(len(items))

    for column, (label, value, help_text) in zip(columns, items):
        with column:
            with st.container(border=True):
                st.metric(
                    label=label,
                    value=value,
                    help=help_text,
                )


def build_trend_dataframe(
    category_trends: list[dict[str, Any]],
) -> pd.DataFrame:
    trend_dates = sorted(
        {
            item["date"]
            for item in category_trends
            if item.get("date")
        }
    )

    trend_data: dict[str, dict[str, int]] = {}

    for current_date in trend_dates:
        trend_data[current_date] = {
            category_name: 0
            for category_name in CATEGORIES[1:]
        }

    for item in category_trends:
        current_date = item.get("date")
        category = item.get("category")

        if current_date in trend_data and category in CATEGORIES[1:]:
            trend_data[current_date][category] = item.get("count", 0)

    rows = [
        {
            "Date": current_date,
            **trend_data[current_date],
        }
        for current_date in trend_dates
    ]

    if not rows:
        return pd.DataFrame()

    dataframe = pd.DataFrame(rows)
    dataframe["Date"] = pd.to_datetime(dataframe["Date"])
    return dataframe.sort_values("Date").set_index("Date")



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

# -------------------------------------------------------------------
# Page header
# -------------------------------------------------------------------

render_page_header()


# -------------------------------------------------------------------
# Filters
# -------------------------------------------------------------------

with st.expander("Filters", expanded=False):
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        selected_category = st.selectbox(
            "Category",
            CATEGORIES,
            index=0,
        )

    with filter_col2:
        start_date = st.date_input(
            "Start date",
            value=None,
        )

    with filter_col3:
        end_date = st.date_input(
            "End date",
            value=None,
        )

category_filter = (
    None
    if selected_category == "All"
    else selected_category
)

start_date_value: date | None = start_date
end_date_value: date | None = end_date


# -------------------------------------------------------------------
# Retrieve analytics
# -------------------------------------------------------------------

try:
    with st.spinner("Loading customer feedback analytics..."):
        analytics = api_client.get_analytics(
            keyword_limit=15,
            recent_limit=10,
            category=category_filter,
            start_date=(
                start_date_value.isoformat()
                if start_date_value
                else None
            ),
            end_date=(
                end_date_value.isoformat()
                if end_date_value
                else None
            ),
        )

except APIClientError as exc:
    st.error(str(exc))
    st.stop()


# -------------------------------------------------------------------
# Extract response sections
# -------------------------------------------------------------------

total_feedback = analytics["total_feedback"]
average_confidence = analytics["average_confidence"]

category_distribution = analytics.get(
    "category_distribution",
    [],
)

confidence_distribution = analytics.get(
    "confidence_distribution",
    [],
)

attention = analytics.get(
    "attention",
    {},
)

flagged_keywords = analytics.get(
    "flagged_keywords",
    [],
)

category_trends = analytics.get(
    "category_trends",
    [],
)

recent_feedback = analytics.get(
    "recent_feedback",
    [],
)


# -------------------------------------------------------------------
# Derived KPI values
# -------------------------------------------------------------------

category_counts = get_category_counts(category_distribution)

excellent_count = category_counts.get("Excellent", 0)
good_count = category_counts.get("Good", 0)
need_improvements_count = category_counts.get("Need Improvements", 0)
poor_count = category_counts.get("Poor", 0)


# -------------------------------------------------------------------
# KPI overview
# -------------------------------------------------------------------

st.subheader("Overview")
st.caption(
    "Key indicators for the currently selected dataset. "
    "Category counts represent all four classification categories."
)

# Keep the KPI cards in rows of three so long labels such as
# "Average Confidence" and "Need Improvements" have enough room.
render_metric_group(
    [
        (
            "Total Feedback",
            format_count(total_feedback),
            "Number of analyzed feedback records.",
        ),
        (
            "Average Confidence",
            format_percentage(average_confidence),
            "Mean model confidence across the selected records.",
        ),
        (
            "Excellent",
            format_count(excellent_count),
            "Feedback classified as Excellent.",
        ),
    ]
)

st.write("")

render_metric_group(
    [
        (
            "Good",
            format_count(good_count),
            "Feedback classified as Good.",
        ),
        (
            "Need Improvements",
            format_count(need_improvements_count),
            "Feedback containing specific service gaps or concerns.",
        ),
        (
            "Poor",
            format_count(poor_count),
            "Feedback classified as Poor and requiring attention.",
        ),
    ]
)


# -------------------------------------------------------------------
# Distribution charts
# -------------------------------------------------------------------

st.subheader("Distributions")
st.caption("How feedback is distributed across categories and confidence bands.")

left_column, right_column = st.columns(2)

with left_column:
    with st.container(border=True):
        st.markdown("**Customer Experience Distribution**")
        st.caption(
            "Distribution of feedback across the four PulseIQ satisfaction categories."
        )

        if category_distribution:
            category_chart_data = pd.DataFrame(
                [
                    {
                        "Category": item["category"],
                        "Feedback": item["count"],
                    }
                    for item in category_distribution
                ]
            ).set_index("Category")

            st.bar_chart(
                category_chart_data,
                y="Feedback",
                horizontal=True,
                use_container_width=True,
            )
        else:
            st.info("No category data is available for the selected filters.")

with right_column:
    with st.container(border=True):
        st.markdown("**Confidence Distribution**")
        st.caption(
            "Confidence bands help identify results that may require additional review."
        )

        if confidence_distribution:
            confidence_chart_data = pd.DataFrame(
                [
                    {
                        "Confidence Band": item["band"],
                        "Feedback": item["count"],
                    }
                    for item in confidence_distribution
                ]
            ).set_index("Confidence Band")

            st.bar_chart(
                confidence_chart_data,
                y="Feedback",
                use_container_width=True,
            )
        else:
            st.info("No confidence data is available for the selected filters.")


# -------------------------------------------------------------------
# Category performance
# -------------------------------------------------------------------

st.subheader("Category Performance")
st.caption(
    "Detailed category-level distribution across the selected dataset."
)

if category_distribution:
    category_table = pd.DataFrame(
        [
            {
                "Category": item["category"],
                "Feedback": item["count"],
                "Share": f'{item["percentage"]:.1f}%',
            }
            for item in category_distribution
        ]
    )

    st.dataframe(
        category_table,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No category records are available.")


# -------------------------------------------------------------------
# Attention required
# -------------------------------------------------------------------

st.subheader("Attention Required")
st.caption(
    "Feedback categories that may require operational attention or human review."
)

attention_items = [
    (
        "Poor Feedback",
        format_count(poor_count),
        "Strong negative experience",
    ),
    (
        "Need Improvements",
        format_count(need_improvements_count),
        "Specific service gaps",
    ),
]

attention_columns = st.columns(2)

for column, (label, value, description) in zip(
    attention_columns,
    attention_items,
):
    with column:
        with st.container(border=True):
            st.metric(label, value)
            st.caption(description)


# -------------------------------------------------------------------
# Keywords and confidence bands
# -------------------------------------------------------------------

st.subheader("Signals")
st.caption("Recurring keywords and confidence-band details in the selected dataset.")

keyword_column, confidence_column = st.columns(2)

with keyword_column:
    with st.container(border=True):
        st.markdown("**Frequently Flagged Keywords**")
        st.caption(
            "Keywords repeatedly identified by the classification pipeline as useful evidence."
        )

        if flagged_keywords:
            keyword_table = pd.DataFrame(
                [
                    {
                        "Keyword": item["keyword"],
                        "Occurrences": item["count"],
                    }
                    for item in flagged_keywords
                ]
            )

            st.dataframe(
                keyword_table,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No flagged keywords are available for the selected data.")

with confidence_column:
    with st.container(border=True):
        st.markdown("**Confidence Bands**")
        st.caption(
            "Distribution of model confidence across analyzed feedback."
        )

        if confidence_distribution:
            confidence_table = pd.DataFrame(
                [
                    {
                        "Band": item["band"],
                        "Range": (
                            f'{item["min_confidence"] * 100:.0f}%'
                            " – "
                            f'{item["max_confidence"] * 100:.0f}%'
                        ),
                        "Feedback": item["count"],
                        "Share": f'{item["percentage"]:.1f}%',
                    }
                    for item in confidence_distribution
                ]
            )

            st.dataframe(
                confidence_table,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No confidence-band data is available.")


# -------------------------------------------------------------------
# Category trend
# -------------------------------------------------------------------

st.subheader("Feedback Trend")
st.caption(
    "Category counts over time based on feedback creation dates."
)

trend_dataframe = build_trend_dataframe(category_trends)

if not trend_dataframe.empty:
    st.line_chart(
        trend_dataframe,
        use_container_width=True,
    )
else:
    st.info(
        "Not enough timestamped feedback is available to display a trend."
    )


# -------------------------------------------------------------------
# Recent feedback
# -------------------------------------------------------------------

st.subheader("Recent Feedback")
st.caption("Most recently analyzed feedback records.")

if recent_feedback:
    for item in recent_feedback:
        filename = item.get("filename", "Unknown file")
        feedback_id = item.get("feedback_id", "Unknown")
        category = item.get("category", "Unknown")
        confidence = item.get("confidence", 0.0)
        created_at = item.get("created_at", "")

        with st.container(border=True):
            top_col, category_col, confidence_col = st.columns(
                [4.5, 1.5, 1.2],
                vertical_alignment="center",
            )

            with top_col:
                st.markdown(f"**{filename}**")
                st.caption(f"Feedback ID: {feedback_id}")

            with category_col:
                st.caption("CATEGORY")
                render_category_badge(category)

            with confidence_col:
                st.caption("CONFIDENCE")
                st.write(format_percentage(confidence))

            if created_at:
                st.caption(f"Created: {created_at}")
else:
    st.info("No recent feedback records are available.")
