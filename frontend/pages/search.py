import streamlit as st

from services.api_client import APIClientError, api_client


st.set_page_config(
    page_title="Search & Evidence | PulseIQ",
    page_icon="🔎",
    layout="wide",
)


# ============================================================
# Page Styling
# ============================================================

st.markdown(
    """
    <style>
    .search-header {
        margin-bottom: 1.5rem;
    }

    .search-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .search-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
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

# ============================================================
# Header
# ============================================================

st.markdown(
    """
    <div class="search-header">
        <div class="search-title">Search & Evidence</div>
        <div class="search-subtitle">
            Find semantically similar customer feedback and inspect the
            evidence retrieved from the feedback knowledge base.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Search Controls
# ============================================================

with st.container(border=True):
    st.markdown("### Semantic Search")

    query = st.text_area(
        "Search query",
        placeholder=(
            "Example: Customers complaining about slow service "
            "and unresolved issues"
        ),
        height=100,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        result_count = st.slider(
            "Number of results",
            min_value=1,
            max_value=10,
            value=5,
        )

    with col2:
        search_button = st.button(
            "🔎 Search Feedback",
            type="primary",
            use_container_width=True,
        )


# ============================================================
# Search Execution
# ============================================================

if search_button:
    if not query.strip():
        st.warning("Enter a search query before searching.")
        st.stop()

    with st.spinner("Searching customer feedback..."):
        try:
            response = api_client.search_feedback(
                query=query.strip(),
                k=result_count,
            )

            st.session_state["search_results"] = response
            st.session_state["search_query"] = query.strip()

        except APIClientError as exc:
            st.error(f"Search failed: {exc}")
            st.stop()


# ============================================================
# Results
# ============================================================

response = st.session_state.get("search_results")

if response:
    results = response.get("results", [])

    st.markdown("---")

    searched_query = st.session_state.get("search_query", "")

    st.markdown("### Search Results")

    if searched_query:
        st.caption(f'Query: "{searched_query}"')

    if not results:
        st.info("No matching feedback was found.")
        st.stop()

    st.success(f"Found {len(results)} relevant result(s).")

    for index, result in enumerate(results, start=1):
        filename = result.get("filename", "Unknown file")
        feedback_id = result.get("feedback_id", "Unknown")
        category = result.get("category", "Unknown")
        similarity = result.get("similarity")
        content = result.get("content") or result.get("feedback", "")

        # ----------------------------------------------------
        # Similarity formatting
        # ----------------------------------------------------

        if similarity is not None:
            try:
                similarity_value = float(similarity)
                similarity_text = f"{similarity_value:.3f}"
            except (TypeError, ValueError):
                similarity_text = str(similarity)
        else:
            similarity_text = "N/A"

        # ----------------------------------------------------
        # Result Card
        # ----------------------------------------------------

        with st.container(border=True):

            col1, col2, col3 = st.columns([3, 1.5, 1.5])

            with col1:
                st.markdown(f"**{index}. {filename}**")
                st.caption(f"Feedback ID: {feedback_id}")

            with col2:
                with st.container(border=True):
                    st.caption("Similarity")
                    st.write(similarity_text)

            with col3:
                with st.container(border=True):
                    st.caption("Category")
                    st.write(category)

            # ------------------------------------------------
            # Evidence
            # ------------------------------------------------

            st.markdown("**Retrieved Evidence**")

            if content:
                with st.container(border=True):
                    evidence_lines = [
                        line.strip()
                        for line in content.splitlines()
                        if line.strip()
                    ]

                    for line in evidence_lines or [content.strip()]:
                        st.write(line)
            else:
                st.caption("No evidence text returned by the API.")

            # ------------------------------------------------
            # Metadata
            # ------------------------------------------------

            with st.expander("View retrieval details"):

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:
                    st.markdown(
                        f"""
                        **Source file**

                        `{filename}`

                        **Feedback ID**

                        `{feedback_id}`
                        """
                    )

                with detail_col2:
                    st.markdown(
                        f"""
                        **Category**

                        `{category}`

                        **Similarity** (higher is more similar)

                        `{similarity_text}`
                        """
                    )

                st.markdown("**Raw API result**")

                st.json(result)

else:
    # ========================================================
    # Empty State
    # ========================================================

    with st.container(border=True):
        st.markdown("### Explore your feedback corpus")

        st.caption(
            "Enter a natural-language query to retrieve semantically "
            "similar customer feedback from the reference knowledge base."
        )

        st.info(
            "Search uses semantic retrieval rather than simple keyword "
            "matching. Results are retrieved from the FAISS-backed "
            "feedback corpus."
        )
