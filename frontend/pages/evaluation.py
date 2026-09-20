import streamlit as st
import pandas as pd

from concurrent.futures import ThreadPoolExecutor

from services.api_client import APIClientError, api_client


# ---------------------------------------------------------------------------
# Page configuration / styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .eval-header {
        padding: 0.5rem 0 1.25rem 0;
    }

    .eval-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .eval-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: #111827;
        border: 1px solid #243244;
        border-radius: 12px;
        padding: 1rem;
        min-height: 105px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 1.65rem;
        font-weight: 700;
    }

    .metric-delta {
        color: #22c55e;
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    .info-box {
        background: #0f172a;
        border: 1px solid #243244;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        color: #cbd5e1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def percentage(value):
    """Convert a decimal metric to percentage text."""
    if value is None:
        return "N/A"

    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def percentage_point_delta(value):
    """Convert a decimal difference to percentage-point text."""
    if value is None:
        return "N/A"

    try:
        value = float(value)
        sign = "+" if value >= 0 else ""
        return f"{sign}{value * 100:.2f} pp"
    except (TypeError, ValueError):
        return "N/A"


def get_classification_metric(report, metric_name):
    """Read a metric from the standard RAG evaluation report."""
    if not isinstance(report, dict):
        return None

    classification_metrics = report.get("classification_metrics")

    if not isinstance(classification_metrics, dict):
        return None

    return classification_metrics.get(metric_name)


def get_ablation_metric(report, section, metric_name):
    """Read a metric from a RAG-vs-No-RAG report section."""
    if not isinstance(report, dict):
        return None

    section_data = report.get(section)

    if not isinstance(section_data, dict):
        return None

    return section_data.get(metric_name)


def get_paired_metric(report, metric_name):
    """Read a comparison metric from paired_comparison."""
    if not isinstance(report, dict):
        return None

    paired = report.get("paired_comparison")

    if not isinstance(paired, dict):
        return None

    return paired.get(metric_name)


def show_metric_card(label, value, delta=None):
    """Render a small metric card."""
    delta_html = ""

    if delta is not None:
        delta_html = f"""
            <div class="metric-delta">{delta}</div>
        """

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# API loading
# ---------------------------------------------------------------------------

@st.cache_data(ttl=30, show_spinner=False)
def load_evaluation_data():
    """
    Load all evaluation reports concurrently.

    RAG metrics come from the canonical RAG evaluation reports.
    No-RAG metrics and paired comparisons come from the ablation reports.
    """

    requests = {
        "development": api_client.get_development_evaluation,
        "final_benchmark": api_client.get_final_benchmark_evaluation,
        "development_ablation": api_client.get_development_rag_vs_no_rag,
        "final_ablation": api_client.get_final_rag_vs_no_rag,
    }

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            name: executor.submit(request)
            for name, request in requests.items()
        }

        return {
            name: future.result()
            for name, future in futures.items()
        }



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
    <div class="eval-header">
        <div class="eval-title">Evaluation & Benchmarking</div>
        <div class="eval-subtitle">
            Measure classification quality, retrieval quality, and the impact
            of retrieval-augmented generation.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Load reports
# ---------------------------------------------------------------------------

try:
    with st.spinner("Loading evaluation data…"):
        reports = load_evaluation_data()

except APIClientError as exc:
    st.error(
        "Evaluation data could not be loaded. "
        "Please make sure the PulseIQ backend is running."
    )
    st.caption(f"Details: {exc}")
    st.stop()

except Exception as exc:
    st.error(
        "An unexpected error occurred while loading evaluation data."
    )
    st.caption(f"Details: {exc}")
    st.stop()


development = reports["development"]
final_benchmark = reports["final_benchmark"]

development_ablation = reports["development_ablation"]
final_ablation = reports["final_ablation"]


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Evaluation Overview</div>',
    unsafe_allow_html=True,
)

overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

with overview_col1:
    total = development.get("total_evaluation_records")

    show_metric_card(
        "Development Cases",
        str(total) if total is not None else "N/A",
    )

with overview_col2:
    evaluated = get_classification_metric(
        development,
        "evaluated_cases",
    )

    show_metric_card(
        "Development Evaluated",
        str(evaluated) if evaluated is not None else "N/A",
    )

with overview_col3:
    final_total = final_benchmark.get("total_evaluation_records")

    show_metric_card(
        "Final Benchmark Cases",
        str(final_total) if final_total is not None else "N/A",
    )

with overview_col4:
    final_evaluated = get_classification_metric(
        final_benchmark,
        "evaluated_cases",
    )

    show_metric_card(
        "Final Evaluated",
        str(final_evaluated) if final_evaluated is not None else "N/A",
    )


# ---------------------------------------------------------------------------
# Development vs Final Benchmark
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Development vs Final Benchmark</div>',
    unsafe_allow_html=True,
)

comparison_rows = [
    {
        "Metric": "Accuracy",
        "Development": percentage(
            get_classification_metric(
                development,
                "accuracy",
            )
        ),
        "Final Benchmark": percentage(
            get_classification_metric(
                final_benchmark,
                "accuracy",
            )
        ),
    },
    {
        "Metric": "Macro Precision",
        "Development": percentage(
            get_classification_metric(
                development,
                "macro_precision",
            )
        ),
        "Final Benchmark": percentage(
            get_classification_metric(
                final_benchmark,
                "macro_precision",
            )
        ),
    },
    {
        "Metric": "Macro Recall",
        "Development": percentage(
            get_classification_metric(
                development,
                "macro_recall",
            )
        ),
        "Final Benchmark": percentage(
            get_classification_metric(
                final_benchmark,
                "macro_recall",
            )
        ),
    },
    {
        "Metric": "Macro F1",
        "Development": percentage(
            get_classification_metric(
                development,
                "macro_f1",
            )
        ),
        "Final Benchmark": percentage(
            get_classification_metric(
                final_benchmark,
                "macro_f1",
            )
        ),
    },
    {
        "Metric": "Weighted F1",
        "Development": percentage(
            get_classification_metric(
                development,
                "weighted_f1",
            )
        ),
        "Final Benchmark": percentage(
            get_classification_metric(
                final_benchmark,
                "weighted_f1",
            )
        ),
    },
]

st.dataframe(
    pd.DataFrame(comparison_rows),
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------------------------
# Classification performance
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Classification Performance</div>',
    unsafe_allow_html=True,
)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    show_metric_card(
        "Accuracy",
        percentage(
            get_classification_metric(
                development,
                "accuracy",
            )
        ),
    )

with metric_col2:
    show_metric_card(
        "Macro Precision",
        percentage(
            get_classification_metric(
                development,
                "macro_precision",
            )
        ),
    )

with metric_col3:
    show_metric_card(
        "Macro Recall",
        percentage(
            get_classification_metric(
                development,
                "macro_recall",
            )
        ),
    )

with metric_col4:
    show_metric_card(
        "Macro F1",
        percentage(
            get_classification_metric(
                development,
                "macro_f1",
            )
        ),
    )


# ---------------------------------------------------------------------------
# Per-class performance
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Per-Class Performance</div>',
    unsafe_allow_html=True,
)

per_class = (
    development
    .get("classification_metrics", {})
    .get("per_class", {})
)

if isinstance(per_class, dict) and per_class:
    per_class_rows = []

    for category, metrics in per_class.items():
        if not isinstance(metrics, dict):
            continue

        per_class_rows.append(
            {
                "Category": category,
                "Support": metrics.get("support", 0),
                "Precision": percentage(metrics.get("precision")),
                "Recall": percentage(metrics.get("recall")),
                "F1": percentage(metrics.get("f1")),
            }
        )

    st.dataframe(
        pd.DataFrame(per_class_rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Per-class evaluation data is not available.")


# ---------------------------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Confusion Matrix</div>',
    unsafe_allow_html=True,
)

confusion_matrix = (
    development
    .get("classification_metrics", {})
    .get("confusion_matrix", {})
)

if isinstance(confusion_matrix, dict) and confusion_matrix:
    confusion_df = pd.DataFrame.from_dict(
        confusion_matrix,
        orient="index",
    )

    confusion_df.index.name = "Actual"

    st.dataframe(
        confusion_df,
        use_container_width=True,
    )
else:
    st.info("Confusion matrix is not available.")


# ---------------------------------------------------------------------------
# Retrieval quality
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-title">Retrieval Quality</div>',
    unsafe_allow_html=True,
)

retrieval_metrics = development.get("retrieval_metrics", {})

retrieval_col1, retrieval_col2, retrieval_col3, retrieval_col4 = st.columns(4)

with retrieval_col1:
    show_metric_card(
        "Retrieval Success",
        percentage(
            retrieval_metrics.get("retrieval_success_rate")
        ),
    )

with retrieval_col2:
    show_metric_card(
        "Reference-Only",
        percentage(
            retrieval_metrics.get("reference_only_rate")
        ),
    )

with retrieval_col3:
    show_metric_card(
        "Gold Category Retrieved",
        percentage(
            retrieval_metrics.get("gold_category_retrieval_rate")
        ),
    )

with retrieval_col4:
    average_retrieved = retrieval_metrics.get(
        "average_retrieved_count"
    )

    show_metric_card(
        "Avg. Retrieved",
        (
            f"{float(average_retrieved):.2f}"
            if average_retrieved is not None
            else "N/A"
        ),
    )


# ===========================================================================
# RAG VS NO-RAG
# ===========================================================================

st.markdown(
    '<div class="section-title">RAG vs No-RAG</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="info-box">
        RAG metrics are taken from the corresponding RAG evaluation report.
        No-RAG metrics are taken from the ablation evaluation.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Accuracy comparison
# ---------------------------------------------------------------------------

st.markdown("#### Accuracy")

development_rag_accuracy = get_classification_metric(
    development,
    "accuracy",
)

development_no_rag_accuracy = get_ablation_metric(
    development_ablation,
    "no_rag_metrics",
    "accuracy",
)

# Calculate this directly from the two displayed metrics.
# We intentionally do not use paired_comparison here.
development_accuracy_difference = None

if (
    development_rag_accuracy is not None
    and development_no_rag_accuracy is not None
):
    development_accuracy_difference = (
        float(development_rag_accuracy)
        - float(development_no_rag_accuracy)
    )


final_rag_accuracy = get_classification_metric(
    final_benchmark,
    "accuracy",
)

final_no_rag_accuracy = get_ablation_metric(
    final_ablation,
    "no_rag_metrics",
    "accuracy",
)

final_accuracy_difference = None

if (
    final_rag_accuracy is not None
    and final_no_rag_accuracy is not None
):
    final_accuracy_difference = (
        float(final_rag_accuracy)
        - float(final_no_rag_accuracy)
    )


accuracy_comparison = pd.DataFrame(
    [
        {
            "Benchmark": "Development",
            "RAG": percentage(development_rag_accuracy),
            "No-RAG": percentage(development_no_rag_accuracy),
            "Difference": percentage_point_delta(
                development_accuracy_difference
            ),
        },
        {
            "Benchmark": "Final Benchmark",
            "RAG": percentage(final_rag_accuracy),
            "No-RAG": percentage(final_no_rag_accuracy),
            "Difference": percentage_point_delta(
                final_accuracy_difference
            ),
        },
    ]
)

st.dataframe(
    accuracy_comparison,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------------------------
# Macro F1 comparison
# ---------------------------------------------------------------------------

st.markdown("#### Macro F1")

development_rag_f1 = get_classification_metric(
    development,
    "macro_f1",
)

development_no_rag_f1 = get_ablation_metric(
    development_ablation,
    "no_rag_metrics",
    "macro_f1",
)

# Calculate directly from the displayed RAG and No-RAG values.
development_f1_difference = None

if (
    development_rag_f1 is not None
    and development_no_rag_f1 is not None
):
    development_f1_difference = (
        float(development_rag_f1)
        - float(development_no_rag_f1)
    )


final_rag_f1 = get_classification_metric(
    final_benchmark,
    "macro_f1",
)

final_no_rag_f1 = get_ablation_metric(
    final_ablation,
    "no_rag_metrics",
    "macro_f1",
)

final_f1_difference = None

if (
    final_rag_f1 is not None
    and final_no_rag_f1 is not None
):
    final_f1_difference = (
        float(final_rag_f1)
        - float(final_no_rag_f1)
    )


f1_comparison = pd.DataFrame(
    [
        {
            "Benchmark": "Development",
            "RAG": percentage(development_rag_f1),
            "No-RAG": percentage(development_no_rag_f1),
            "Difference": percentage_point_delta(
                development_f1_difference
            ),
        },
        {
            "Benchmark": "Final Benchmark",
            "RAG": percentage(final_rag_f1),
            "No-RAG": percentage(final_no_rag_f1),
            "Difference": percentage_point_delta(
                final_f1_difference
            ),
        },
    ]
)

st.dataframe(
    f1_comparison,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------------------------
# Paired case comparison
# ---------------------------------------------------------------------------

st.markdown("#### Paired Case Comparison")

# Development is intentionally omitted.
# The development ablation report currently contains inconsistent paired
# comparison information, so the product UI uses the frozen final benchmark
# paired comparison only.

final_paired_comparison = {
    "Benchmark": "Final Benchmark",
    "RAG Better": get_paired_metric(
        final_ablation,
        "rag_better_cases",
    ),
    "No-RAG Better": get_paired_metric(
        final_ablation,
        "no_rag_better_cases",
    ),
    "Both Correct": get_paired_metric(
        final_ablation,
        "both_correct_cases",
    ),
    "Both Wrong": get_paired_metric(
        final_ablation,
        "both_wrong_cases",
    ),
}

st.dataframe(
    pd.DataFrame([final_paired_comparison]),
    use_container_width=True,
    hide_index=True,
)


# ===========================================================================
# EXPANDED REPORTS
# ===========================================================================

st.markdown(
    '<div class="section-title">Detailed Evaluation Reports</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Development RAG-vs-No-RAG expanded report
# ---------------------------------------------------------------------------

with st.expander(
    "Development — RAG vs No-RAG detailed report",
    expanded=False,
):
    st.markdown("##### RAG Evaluation")

    # RAG comes from the canonical development evaluation report.
    development_rag_report = {
        "evaluation_split": development.get(
            "evaluation_split",
            "development",
        ),
        "evaluation_timestamp": development.get(
            "evaluation_timestamp"
        ),
        "total_evaluation_records": development.get(
            "total_evaluation_records"
        ),
        "classification_metrics": development.get(
            "classification_metrics",
            {},
        ),
        "retrieval_metrics": development.get(
            "retrieval_metrics",
            {},
        ),
    }

    st.json(development_rag_report)

    st.markdown("##### No-RAG Evaluation")

    development_no_rag_report = {
        "evaluation_split": development_ablation.get(
            "evaluation_split",
            "development",
        ),
        "total_cases": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("total_cases"),
        "correct_cases": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("correct_cases"),
        "accuracy": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("accuracy"),
        "macro_precision": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("macro_precision"),
        "macro_recall": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("macro_recall"),
        "macro_f1": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("macro_f1"),
        "weighted_f1": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("weighted_f1"),
        "per_class": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("per_class", {}),
        "confusion_matrix": development_ablation.get(
            "no_rag_metrics",
            {},
        ).get("confusion_matrix", {}),
    }

    st.json(development_no_rag_report)

    st.markdown("##### Paired Comparison")

    # Development paired comparison is intentionally not displayed because
    # the development ablation report contains inconsistent paired values.
    st.info(
        "Paired case comparison is shown for the final benchmark only."
    )


# ---------------------------------------------------------------------------
# Final benchmark RAG-vs-No-RAG expanded report
# ---------------------------------------------------------------------------

with st.expander(
    "Final Benchmark — RAG vs No-RAG detailed report",
    expanded=False,
):
    st.markdown("##### RAG Evaluation")

    final_rag_report = {
        "evaluation_split": final_benchmark.get(
            "evaluation_split",
            "final_benchmark",
        ),
        "evaluation_timestamp": final_benchmark.get(
            "evaluation_timestamp"
        ),
        "total_evaluation_records": final_benchmark.get(
            "total_evaluation_records"
        ),
        "classification_metrics": final_benchmark.get(
            "classification_metrics",
            {},
        ),
        "retrieval_metrics": final_benchmark.get(
            "retrieval_metrics",
            {},
        ),
    }

    st.json(final_rag_report)

    st.markdown("##### No-RAG Evaluation")

    final_no_rag_report = {
        "evaluation_split": final_ablation.get(
            "evaluation_split",
            "final_benchmark",
        ),
        "total_cases": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("total_cases"),
        "correct_cases": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("correct_cases"),
        "accuracy": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("accuracy"),
        "macro_precision": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("macro_precision"),
        "macro_recall": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("macro_recall"),
        "macro_f1": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("macro_f1"),
        "weighted_f1": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("weighted_f1"),
        "per_class": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("per_class", {}),
        "confusion_matrix": final_ablation.get(
            "no_rag_metrics",
            {},
        ).get("confusion_matrix", {}),
    }

    st.json(final_no_rag_report)

    st.markdown("##### Paired Comparison")

    final_paired = final_ablation.get(
        "paired_comparison",
        {},
    )

    st.json(final_paired)


# ---------------------------------------------------------------------------
# Raw canonical evaluation reports
# ---------------------------------------------------------------------------

with st.expander(
    "Raw Development Evaluation Report",
    expanded=False,
):
    st.json(development)

with st.expander(
    "Raw Final Benchmark Evaluation Report",
    expanded=False,
):
    st.json(final_benchmark)