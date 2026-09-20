from __future__ import annotations

from pathlib import Path
import base64

import streamlit as st


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="PulseIQ",
    page_icon="◈",
    layout="wide",
)


# ============================================================
# Hero image
# ============================================================
# Change this one line to test another image from the assets folder.
HERO_IMAGE_PATH = Path(__file__).resolve().parent.parent / "assets" / "Hero.png"

try:
    _hero_image_b64 = base64.b64encode(HERO_IMAGE_PATH.read_bytes()).decode("utf-8")
    HERO_IMAGE_DATA_URI = f"data:image/png;base64,{_hero_image_b64}"
except (FileNotFoundError, OSError):
    HERO_IMAGE_DATA_URI = ""


# ============================================================
# Home light theme — scoped to the Home page
# ============================================================

st.html(
    """
    <style>
    /* Ensure the global PulseIQ brand remains visible on the light Home page. */
    .pulseiq-header-brand,
    .pulseiq-header-brand .dark {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 2147483647 !important;
    }

    .pulseiq-header-brand .accent {
        color: #22D3C5 !important;
        -webkit-text-fill-color: #22D3C5 !important;
    }

    /* Main Home surface */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] .main,
    section.main {
        background: #0F172A !important;
    }

    [data-testid="stHeader"] {
        background: #0F172A !important;
    }

    [data-testid="stMainBlockContainer"] {
        background: #0F172A !important;
    }

    /* Default Home typography */
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stCaptionContainer"] {
        color: #F8FAFC !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #F8FAFC !important;
    }

    /* Section headings / kickers */
    .home-section-kicker {
        display: inline-flex;
        align-items: center;
        width: auto;
        padding: 0.42rem 0.9rem;
        margin: 0.25rem 0 0.55rem 0;
        border: 1px solid rgba(34, 211, 197, 0.55);
        border-radius: 999px;
        background: rgba(34, 211, 197, 0.08);
        color: #22D3C5;
        font-size: 0.78rem;
        font-weight: 900;
        letter-spacing: 0.12em;
        line-height: 1.25;
        text-transform: uppercase;
    }

    /* Dividers */
    hr {
        border-color: #22D3C5 !important;
        border-top: 2px solid #22D3C5 !important;
        opacity: 1 !important;
        box-shadow: 0 0 8px rgba(34, 211, 197, 0.18) !important;
    }

    /* Home cards */
    div[class*="st-key-home-card-"] {
        background: rgba(34, 211, 197, 0.055) !important;
        border: 1px solid rgba(34, 211, 197, 0.42) !important;
        border-radius: 14px !important;
        box-shadow: 0 6px 18px rgba(15, 118, 110, 0.08) !important;
    }

    div[class*="st-key-home-card-"] p,
    div[class*="st-key-home-card-"] [data-testid="stCaptionContainer"] {
        color: #F8FAFC !important;
    }

    div[class*="st-key-home-card-"] h1,
    div[class*="st-key-home-card-"] h2,
    div[class*="st-key-home-card-"] h3,
    div[class*="st-key-home-card-"] h4,
    div[class*="st-key-home-card-"] h5,
    div[class*="st-key-home-card-"] h6 {
        color: #F8FAFC !important;
    }

    /* Preserve the existing hover zoom, but make the accent more visible
       against the light theme. */
    div[class*="st-key-home-card-"] {
        transition:
            transform 0.22s ease,
            box-shadow 0.22s ease,
            border-color 0.22s ease;
        transform-origin: center center;
        position: relative;
        z-index: 0;
        will-change: transform;
    }

    div[class*="st-key-home-card-"]:hover {
        transform: scale(1.06);
        box-shadow: 0 16px 34px rgba(15, 118, 110, 0.18) !important;
        border-color: #22D3C5 !important;
        z-index: 5;
    }

    /* Technology pills */
    [data-testid="stMarkdownContainer"] code {
        background: rgba(34, 211, 197, 0.08) !important;
        border: 1px solid rgba(34, 211, 197, 0.42) !important;
        color: #0F766E !important;
    }

    /* Top navigation while Home is active */
    div[data-testid="stPageLink-NavLink"] a {
        color: #F8FAFC !important;
        border-color: transparent !important;
    }

    div[data-testid="stPageLink-NavLink"] a:hover {
        background: rgba(34, 211, 197, 0.10) !important;
        border-color: rgba(34, 211, 197, 0.40) !important;
        color: #0F766E !important;
    }

    div[data-testid="stPageLink-NavLink"] a[aria-current="page"] {
        background: #22D3C5 !important;
        border-color: #22D3C5 !important;
        color: #F8FAFC !important;
        box-shadow: 0 6px 16px rgba(34, 211, 197, 0.20) !important;
    }

    div[data-testid="stPageLink-NavLink"] a[aria-current="page"] * {
        color: #F8FAFC !important;
    }

    /* Keep the Streamlit hamburger visible on the light surface. */
    header button[aria-label*="sidebar" i]::before,
    header button[data-testid="stSidebarCollapseButton"]::before,
    header button[data-testid="stSidebarNavCollapseButton"]::before {
        color: #0F766E !important;
    }
    </style>
    """
)


# ============================================================
# Home card hover animation
# ============================================================

st.html(
    """
    <style>
    /* Robust hover animation for keyed Home cards. */
    div[class*="st-key-home-card-"] {
        transition:
            transform 0.22s ease,
            box-shadow 0.22s ease,
            border-color 0.22s ease;
        transform-origin: center center;
        position: relative;
        z-index: 0;
        will-change: transform;
    }

    div[class*="st-key-home-card-"]:hover {
        transform: scale(1.06);
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.26);
        border-color: rgba(94, 234, 212, 0.42);
        z-index: 5;
    }

    /* Architecture arrows: teal circular outline with a visible teal arrow. */
    div[class*="st-key-home-architecture-arrow-"] {
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        min-height: 38px !important;
        margin: 0.18rem auto !important;
        border: 2px solid #22D3C5 !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        background: rgba(34, 211, 197, 0.06) !important;
    }

    div[class*="st-key-home-architecture-arrow-"] {
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        transform-origin: center center;
        will-change: transform;
    }

    div[class*="st-key-home-architecture-arrow-"]:hover {
        transform: scale(1.16);
        box-shadow: 0 8px 20px rgba(34, 211, 197, 0.20) !important;
    }

    div[class*="st-key-home-architecture-arrow-"] [data-testid="stCaptionContainer"],
    div[class*="st-key-home-architecture-arrow-"] [data-testid="stCaptionContainer"] *,
    div[class*="st-key-home-architecture-arrow-"] p {
        color: #22D3C5 !important;
        -webkit-text-fill-color: #22D3C5 !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        margin: 0 !important;
        text-align: center !important;
    }
    </style>
    """
)


# ============================================================
# Hero section
# ============================================================

st.html(
    """
    <style>
    .pulseiq-hero {
        position: relative;
        width: 100%;
        min-height: clamp(540px, 62vw, 700px);
        border-radius: 18px;
        overflow: hidden;
        margin-top: 0.9rem;
        margin-bottom: 2.6rem;
        background: #6B7280;
        border: 1px solid rgba(15, 23, 42, 0.14);
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.14);
    }

    .pulseiq-hero-image {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
        display: block;
        z-index: 0;
    }

    .pulseiq-hero-content {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        padding: clamp(2rem, 5vw, 5rem);
        z-index: 2;
    }

    .pulseiq-hero-copy {
        max-width: 820px;
    }

    .pulseiq-hero-brand {
        color: #F8FAFC;
        font-size: clamp(1.7rem, 2.8vw, 2.2rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.1rem;
    }

    .pulseiq-hero-brand span {
        color: #22D3C5;
    }

    .pulseiq-hero-tagline {
        color: #F8FAFC;
        font-size: clamp(0.95rem, 1.25vw, 1.15rem);
        margin-bottom: clamp(1.8rem, 4vw, 3.8rem);
    }

    .pulseiq-hero-eyebrow {
        color: #22D3C5;
        font-size: clamp(0.95rem, 1.15vw, 1.12rem);
        font-weight: 850;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .pulseiq-hero-title {
        color: #F8FAFC;
        font-size: clamp(2rem, 5vw, 4.45rem);
        font-weight: 850;
        line-height: 1.02;
        letter-spacing: -0.055em;
        margin-bottom: 1.15rem;
    }

    .pulseiq-hero-title span {
        color: #22D3C5;
    }

    .pulseiq-hero-description {
        color: #F8FAFC;
        font-size: clamp(0.85rem, 1.3vw, 1.08rem);
        line-height: 1.7;
        max-width: 760px;
    }

    @media (max-width: 768px) {
        .pulseiq-hero {
            min-height: 600px;
        }

        .pulseiq-hero-content {
            padding: 1.5rem;
            align-items: flex-end;
        }

        .pulseiq-hero-tagline {
            margin-bottom: 1.5rem;
        }
    }
    </style>

    <section class="pulseiq-hero">
        __HERO_IMAGE__
        <div class="pulseiq-hero-content">
            <div class="pulseiq-hero-copy">
                <div class="pulseiq-hero-brand">
                    P<span>ulse</span>IQ
                </div>

                <div class="pulseiq-hero-tagline">
                    AI-Powered Customer Feedback Intelligence
                </div>

                <div class="pulseiq-hero-eyebrow">
                    Customer Feedback Intelligence
                </div>

                <div class="pulseiq-hero-title">
                    Turn customer feedback into
                    <span> actionable insight.</span>
                </div>

                <div class="pulseiq-hero-description">
                    PulseIQ transforms customer feedback documents
                    into structured, explainable intelligence using
                    document processing, semantic retrieval, and
                    generative AI.
                </div>
            </div>
        </div>
    </section>
    """.replace(
        "__HERO_IMAGE__",
        f'<img class="pulseiq-hero-image" src="{HERO_IMAGE_DATA_URI}" alt="PulseIQ hero image" />'
        if HERO_IMAGE_DATA_URI
        else "",
    ),
    unsafe_allow_javascript=False,
)


# ============================================================
# What We Solve
# ============================================================

st.divider()

st.html("<div class='home-section-kicker'>WHAT WE SOLVE</div>")
st.subheader("Feedback forms are valuable — but often left unread")

st.write(
    "Customer feedback contains important signals about satisfaction, "
    "service quality, complaints, and customer loyalty. Manual review "
    "makes it difficult to analyze this information consistently and at scale."
)

problem_columns = st.columns(4)

problems = [
    (
        "01",
        "Thousands of PDFs arrive",
        "Customer feedback forms can accumulate rapidly, while a large "
        "portion remains unread or only partially analyzed.",
    ),
    (
        "02",
        "Manual review is slow",
        "Reviewing forms one by one is time-consuming, inconsistent, "
        "and vulnerable to differences in human judgment.",
    ),
    (
        "03",
        "Critical signals stay buried",
        "Complaints, churn-risk indicators, praise, and recurring service "
        "issues can remain hidden inside individual documents.",
    ),
    (
        "04",
        "The opportunity",
        "AI can read, understand, retrieve context for, and classify "
        "every feedback form in seconds.",
    ),
]

for column, (number, title, description) in zip(problem_columns, problems):
    with column:
        with st.container(border=True, key=f"home-card-problem-{number}"):
            st.caption(number)
            st.markdown(f"### {title}")
            st.write(description)


# ============================================================
# What We Built
# ============================================================

st.divider()

st.html("<div class='home-section-kicker'>WHAT WE BUILT</div>")
st.subheader("From raw feedback to meaningful insight")

st.write(
    "PulseIQ provides an end-to-end workflow for understanding customer "
    "feedback. The platform processes feedback documents, retrieves relevant "
    "historical examples, classifies the overall customer experience, and "
    "presents the reasoning and evidence behind the result."
)

feature_columns = st.columns(4)

features = [
    (
        "01",
        "Document Intelligence",
        "Extract and process customer feedback from PDF documents before "
        "sending it through the analysis pipeline.",
    ),
    (
        "02",
        "RAG-Powered Classification",
        "Use semantically relevant historical feedback as contextual "
        "evidence during classification.",
    ),
    (
        "03",
        "Explainable Results",
        "Return a satisfaction category, confidence score, concise "
        "rationale, and relevant flagged keywords.",
    ),
    (
        "04",
        "Analytics & Evaluation",
        "Monitor customer feedback patterns and objectively evaluate "
        "model performance using benchmark data.",
    ),
]

for column, (number, title, description) in zip(feature_columns, features):
    with column:
        with st.container(border=True, key=f"home-card-feature-{number}"):
            st.caption(number)
            st.markdown(f"### {title}")
            st.write(description)


# ============================================================
# Classification Categories
# ============================================================

st.divider()

st.html("<div class='home-section-kicker'>CLASSIFICATION</div>")
st.subheader("Four levels of customer experience")

st.write(
    "PulseIQ evaluates the overall experience rather than relying on "
    "isolated keywords or numerical ratings alone."
)

category_columns = st.columns(4)

categories = [
    ("Excellent", "Strong satisfaction, delight, or customer advocacy."),
    ("Good", "Generally satisfied with only minor reservations."),
    ("Need Improvements", "Specific service gaps or constructive criticism."),
    ("Poor", "Strong dissatisfaction, frustration, or serious negative experience."),
]

for column, (title, description) in zip(category_columns, categories):
    with column:
        with st.container(border=True, key=f"home-card-category-{title.lower().replace(chr(32), chr(45))}"):
            st.markdown(f"### {title}")
            st.write(description)


# ============================================================
# How the System Works
# ============================================================

st.divider()

st.html("<div class='home-section-kicker'>WORKFLOW</div>")
st.subheader("How PulseIQ works")

st.write(
    "The system combines document processing, semantic retrieval, "
    "and structured generative AI classification into one workflow."
)

workflow_columns = st.columns(5)

workflow = [
    ("01", "Input", "Customer feedback PDF is uploaded to the system."),
    ("02", "Extraction", "Feedback text is extracted and prepared for analysis."),
    ("03", "Retrieval", "Relevant reference feedback is retrieved from the vector store."),
    ("04", "Classification", "Gemini analyzes the feedback with retrieved context."),
    ("05", "Insight", "PulseIQ presents the category, confidence, rationale, and evidence."),
]

for column, (number, title, description) in zip(workflow_columns, workflow):
    with column:
        with st.container(border=True, key=f"home-card-workflow-{number}"):
            st.caption(number)
            st.markdown(f"### {title}")
            st.write(description)


# ============================================================
# Architecture
# ============================================================

st.divider()

st.html("<div class='home-section-kicker'>ARCHITECTURE</div>")
st.subheader("A layered AI application")

st.write(
    "The frontend is intentionally separated from the AI and application "
    "layers. Streamlit communicates with FastAPI, while the backend manages "
    "the RAG pipeline, model interaction, retrieval, and persistence."
)

architecture_layers = [
    (
        "Streamlit — Product Interface",
        "Dashboards, analysis screens, search, evaluation, and system monitoring.",
    ),
    (
        "FastAPI — Application API",
        "Upload, classification, analytics, semantic search, persistence, and evaluation APIs.",
    ),
    (
        "LangChain — RAG Orchestration",
        "Retrieval, prompt orchestration, structured generation, and contextual classification.",
    ),
    (
        "AI & Data Layer",
        "Gemini, Sentence Transformers, FAISS, PostgreSQL, and processed customer feedback.",
    ),
]

for index, (title, description) in enumerate(architecture_layers):
    with st.container(border=True, key=f"home-card-architecture-{index + 1}"):
        st.markdown(f"### {title}")
        st.caption(description)

    if index < len(architecture_layers) - 1:
        arrow_columns = st.columns([1, 0.18, 1])
        with arrow_columns[1]:
            with st.container(key=f"home-architecture-arrow-{index + 1}"):
                st.caption("↓")


# ============================================================
# Technology Stack
# ============================================================

st.divider()

st.html("<div class='home-section-kicker'>TECHNOLOGY</div>")
st.subheader("Built with a practical AI stack")

technologies = [
    "Python",
    "Streamlit",
    "FastAPI",
    "LangChain",
    "Gemini",
    "Sentence Transformers",
    "FAISS",
    "PostgreSQL",
    "PyMuPDF",
    "RAG",
]

for row in (technologies[:5], technologies[5:]):
    columns = st.columns(len(row))
    for column, technology in zip(columns, row):
        with column:
            st.markdown(f"`{technology}`")


# ============================================================
# Contact Us
# ============================================================

st.divider()

st.html("<div class='home-section-kicker'>CONTACT US</div>")
st.subheader("Connect with the PulseIQ team")

st.write(
    "Have a question, partnership idea, or feedback about PulseIQ? "
    "Reach out through any of the channels below."
)

contact_columns = st.columns(5)

contacts = [
    ("✉️", "Email", "hello@pulseiq.ai"),
    ("📞", "Phone", "+91 98765 XXXXX"),
    ("💼", "LinkedIn", "linkedin.com/comp/pulseiq"),
    ("🐙", "GitHub", "github.com/pulseiq"),
    ("𝕏", "Follow", "@PulseIQ_AI"),
]

for index, (column, (icon, title, value)) in enumerate(zip(contact_columns, contacts), start=1):
    with column:
        with st.container(border=True, key=f"home-card-contact-{index}"):
            st.markdown(f"### {icon} {title}")
            st.caption(value)
