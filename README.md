# PulseIQ

> AI-powered customer feedback intelligence using RAG, Gemini, FAISS, FastAPI, PostgreSQL, and Streamlit.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C)](https://www.langchain.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-0467DF)](https://github.com/facebookresearch/faiss)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Data%20Layer-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

PulseIQ is a full-stack AI application for turning unstructured customer feedback into structured, explainable, searchable, and measurable insights.

The Analyze Feedback workflow supports both single-document analysis and multi-PDF batch analysis, while preserving independent per-document results and persistence.

The system accepts customer-feedback PDFs or raw feedback text, extracts and sanitizes the content, retrieves semantically similar historical feedback from a FAISS knowledge base, and uses Gemini through a LangChain RAG pipeline to classify the feedback into four business categories:

- **Excellent**
- **Good**
- **Need Improvements**
- **Poor**

The resulting classification, confidence, explanation, flagged keywords, and retrieval evidence are exposed through FastAPI and persisted in PostgreSQL. A Streamlit application provides the user-facing experience for analysis, semantic search, analytics, evaluation, and service monitoring.

---

## Why it matters

Customer feedback is often collected as PDFs, forms, and free-text responses that are difficult to analyze consistently at scale.

A useful customer-feedback intelligence system needs to answer questions such as:

- What category best describes this feedback?
- Why was that category assigned?
- Which historical feedback examples are most similar?
- What evidence supports the classification?
- What are customers repeatedly complaining about?
- How is feedback distributed across categories?
- Does retrieval actually improve classification compared with a no-RAG baseline?
- How well does the system perform on held-out evaluation data?

PulseIQ combines these capabilities in one application instead of treating classification, semantic search, analytics, and evaluation as disconnected scripts.

---

## Current implementation status

PulseIQ currently contains a working application architecture with:

- Streamlit frontend
- FastAPI backend
- LangChain-based RAG orchestration
- Gemini structured-output classification
- Sentence Transformers embeddings
- FAISS vector retrieval
- MMR-based retrieval configuration
- PostgreSQL persistence
- PDF extraction with OCR fallback
- Multi-PDF upload and batch analysis through the Streamlit Analyze Feedback workflow
- Per-document classification, confidence, rationale, and persistence within a batch
- Per-file error isolation so one failed PDF does not stop the remaining PDFs from being analyzed
- Explicit removal of selected customer-identifying fields before embedding
- Semantic search API and UI
- PostgreSQL-backed analytics API and dashboard
- Held-out RAG evaluation reports
- RAG vs No-RAG ablation reports
- Error analysis and confusion-matrix support
- FastAPI evaluation endpoints
- Streamlit evaluation dashboard
- Service-health/status monitoring
- Automated tests across backend services, API routes, database integration, and evaluation components

The repository also contains a generated FAISS index under `backend/vector_store/customer_feedback/` so the current reference knowledge base can be used without rebuilding the index immediately.

---

## MVP features

### Feedback ingestion

- Upload one or multiple customer-feedback PDFs through the Streamlit Analyze Feedback workflow.
- Each selected PDF is processed independently through the existing FastAPI upload pipeline.
- Extract text using PyMuPDF.
- Automatically fall back to OCR for pages where native extraction is unusable.
- Normalize common PDF extraction artifacts.
- Remove explicit fields such as customer name, account number, and contact number before the content is embedded.
- Generate stable feedback identifiers and extraction metadata.
- Display batch-level analysis results while preserving detailed per-document analysis.
- Isolate per-file failures so one problematic PDF does not prevent other selected PDFs from being processed.

### Multi-PDF batch analysis

PulseIQ supports selecting multiple customer-feedback PDFs from the Analyze Feedback page in a single user action.

The current batch workflow processes the selected documents sequentially:

```text
Multiple PDFs selected
        |
        v
For each PDF
        |
        v
Existing /api/upload/pdf endpoint
        |
        v
PDF extraction + cleaning
        |
        v
RAG retrieval
        |
        v
Gemini classification
        |
        v
PostgreSQL persistence
        |
        v
Individual result
        |
        +----> Next PDF
```

The Analyze Feedback page presents:

- A batch analysis summary
- Per-document classification and confidence
- Feedback IDs for persisted records
- Retrieved evidence counts
- A detailed-analysis selector for individual documents
- Per-file error reporting when a document fails

The batch feature does not introduce a separate batch API endpoint. Each document continues to use the existing single-document `/api/upload/pdf` contract, which is invoked once for each selected PDF.

### RAG-based classification

- Split and prepare reference feedback for vector retrieval.
- Generate embeddings with `sentence-transformers/all-MiniLM-L6-v2`.
- Store and search vectors with FAISS.
- Retrieve relevant reference examples with the configured MMR strategy.
- Keep evaluation documents separate from the production reference corpus.
- Pass the retrieved examples into the classification prompt.
- Classify the feedback using Gemini.
- Return structured output validated through Pydantic.

### Explainable analysis

Each classification can include:

- Category
- Confidence
- Explanation / rationale
- Flagged keywords or evidence phrases
- Retrieved reference feedback IDs
- Retrieval scores / similarity information
- Source metadata

### Semantic search

The Search & Evidence page supports natural-language queries such as:

```text
customers complaining about long resolution times
```

and returns semantically similar historical feedback rather than relying only on exact keyword matching.

### Analytics dashboard

The dashboard can retrieve analytics from PostgreSQL and supports:

- Category distribution
- Feedback counts
- Recent feedback
- Keyword-oriented summaries
- Category filters
- Date filters
- Database-backed aggregation

### Evaluation dashboard

The Evaluation page exposes persisted evaluation reports through FastAPI and Streamlit, including:

- Accuracy
- Macro precision
- Macro recall
- Macro F1
- Weighted F1
- Per-class precision/recall/F1
- Confusion matrix
- Retrieval success rate
- Reference-only retrieval rate
- Gold-category retrieval rate
- Average retrieved examples
- RAG vs No-RAG comparison
- Paired case comparison
- Detailed/raw evaluation reports

### System monitoring

The System Status page checks availability of:

- FastAPI health endpoint
- Analysis service
- PDF upload service
- Semantic search service
- Analytics service
- Evaluation service

---

## How it works

```mermaid
flowchart TD
    U[User] --> UI[Streamlit UI]
    UI --> BATCH[One or More PDFs]
    BATCH --> API[FastAPI Application API]

    API --> UP[PDF Upload / Text Analysis]
    UP --> DOC[PyMuPDF + OCR + Cleaning + PII Removal]

    DOC --> RAG[RAG Service]
    RAG --> RET[Retriever Service]
    RET --> FAISS[FAISS Vector Store]
    FAISS --> EMB[Sentence Transformer Embeddings]

    RET --> PROMPT[Classification Prompt + Retrieved Examples]
    PROMPT --> GEMINI[Gemini]
    GEMINI --> OUT[Pydantic Structured Classification]

    OUT --> DB[(PostgreSQL)]
    RET --> DB

    API --> SEARCH[Semantic Search API]
    SEARCH --> FAISS

    API --> ANALYTICS[Analytics API]
    ANALYTICS --> DB

    API --> EVAL[Evaluation API]
    EVAL --> REPORTS[Saved Evaluation Reports]

    UI --> DASH[Dashboard]
    UI --> ANALYSIS[Analyze Feedback]
    UI --> EVIDENCE[Search & Evidence]
    UI --> EVAL_UI[Evaluation]
    UI --> STATUS[System Status]

    DASH --> ANALYTICS
    ANALYSIS --> API
    EVIDENCE --> SEARCH
    EVAL_UI --> EVAL
    STATUS --> API
```

---

## End-to-end request flow

### Batch analysis orchestration

When multiple PDFs are selected, the Streamlit frontend orchestrates the existing single-document workflow once per PDF.

```text
Selected PDFs
     |
     +----> PDF 1 ---> Existing analysis pipeline ---> Result 1
     |
     +----> PDF 2 ---> Existing analysis pipeline ---> Result 2
     |
     +----> PDF 3 ---> Existing analysis pipeline ---> Result 3
     |
     +----> PDF N ---> Existing analysis pipeline ---> Result N
```

Each document is independently extracted, classified, persisted, and returned to the frontend.

### Production analysis path

```text
Customer Feedback PDF / Raw Text
              |
              v
        FastAPI API layer
              |
              v
     PDF extraction / cleaning
              |
              v
        RAG Service
              |
              +------------------+
              |                  |
              v                  v
        FAISS retrieval     Classification prompt
              |                  |
              +---------> Gemini <+
                          |
                          v
                  Structured result
                          |
              +-----------+-----------+
              |                       |
              v                       v
         PostgreSQL            FastAPI response
                                      |
                                      v
                                Streamlit UI
```

### Evaluation path

Evaluation is deliberately separate from arbitrary production uploads because evaluation requires known ground-truth labels.

```text
Held-out feedback document
        +
Known ground-truth category
        |
        v
   Evaluation engine
        |
        v
       RAG
        |
        v
    Prediction
        |
        v
Compare prediction vs gold label
        |
        v
Accuracy / Precision / Recall / F1
        |
        v
Confusion matrix + retrieval metrics
        |
        v
Saved JSON / CSV report
        |
        v
FastAPI Evaluation API
        |
        v
Streamlit Evaluation page
```

The application therefore does not attempt to compute accuracy for an arbitrary newly uploaded production document where no verified ground-truth label exists.

---

## RAG pipeline

PulseIQ uses retrieval-augmented generation primarily as a **classification support mechanism** rather than as a conversational chatbot.

### Retrieval pipeline

```text
Incoming feedback
      |
      v
Embedding
      |
      v
FAISS / MMR retrieval
      |
      v
Top-k reference feedback examples
      |
      v
Classification prompt
      |
      v
Gemini
      |
      v
Structured classification
```

The vector index is built from the reference split of the dataset rather than from the held-out evaluation documents. This separation is intended to reduce evaluation leakage.

### Reference-only retrieval

The production retrieval layer validates that retrieved examples belong to the reference corpus. This is important because evaluation documents should not become available to the production retrieval index.

---

## Classification categories

PulseIQ currently uses four categories:

| Category | Meaning in the application |
| --- | --- |
| **Excellent** | Strongly positive customer experience with high satisfaction and little or no meaningful dissatisfaction. |
| **Good** | Generally positive experience with limited shortcomings that do not dominate the overall feedback. |
| **Need Improvements** | Meaningful service gaps or constructive criticism where improvement is needed but severe dissatisfaction does not dominate. |
| **Poor** | Strong or substantial dissatisfaction, serious shortcomings, repeated negative signals, or an experience that is clearly unacceptable. |

The classification prompt is designed to distinguish the difficult category boundaries rather than relying only on a single sentiment keyword.

---

## Evaluation and benchmarking

Evaluation is treated as a separate engineering layer from the production RAG pipeline.

### Metrics tracked

#### Classification metrics

- Accuracy
- Macro precision
- Macro recall
- Macro F1
- Weighted F1
- Per-class precision
- Per-class recall
- Per-class F1
- Confusion matrix

#### Retrieval metrics

- Retrieval success rate
- Reference-only retrieval rate
- Gold-category retrieval rate
- Average retrieved count

#### Ablation metrics

PulseIQ also contains a paired **RAG vs No-RAG** evaluation so that the effect of retrieved reference context can be measured against a baseline using the same evaluation cases.

---

## Latest benchmark snapshot

The current committed final-benchmark RAG report contains 20 benchmark records, of which 19 completed successfully. Seventeen of those 19 successfully evaluated cases were classified correctly.

| Metric | RAG | No-RAG |
| --- | ---: | ---: |
| Evaluated cases | 19 | 19 |
| Accuracy | **89.47%** | 57.89% |
| Macro Precision | **95.00%** | 38.33% |
| Macro Recall | **89.58%** | 37.50% |
| Macro F1 | **91.38%** | 34.06% |
| Weighted F1 | **89.44%** | 50.34% |

Paired final-benchmark comparison:

| Paired outcome | Cases |
| --- | ---: |
| RAG better | 7 |
| No-RAG better | 1 |
| Both correct | 10 |
| Both wrong | 1 |

The remaining benchmark record was not included in the successful comparison because its RAG evaluation encountered a runtime read error. The reported accuracy is therefore `17 / 19`, not `17 / 20`.

### Why this evaluation design matters

A high accuracy number is not enough by itself. PulseIQ also tracks confusion patterns and class-level metrics to identify whether performance is being achieved by over-predicting a single category.

The RAG-vs-No-RAG experiment further provides an explicit baseline for the contribution of retrieved reference examples.

---

## Repository structure

The repository separates the application into data, backend services, evaluation infrastructure, and frontend UI.

```text
AI-Feedback-Intelligence/
├── README.md
├── requirements.txt
├── pytest.ini
│
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── database_init.py
│   ├── main.py
│   │
│   ├── data/
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── dataset_manifest_service.py
│   │   ├── error_analysis_service.py
│   │   ├── experiment_service.py
│   │   ├── rag_ablation_service.py
│   │   ├── rag_evaluation_service.py
│   │   └── results/
│   │       ├── *.json
│   │       └── *.csv
│   │
│   ├── models/
│   │   ├── classification.py
│   │   ├── database_models.py
│   │   ├── feedback.py
│   │   ├── feedback_models.py
│   │   ├── feedback_list_models.py
│   │   ├── individual_analysis_models.py
│   │   ├── search_models.py
│   │   ├── upload_models.py
│   │   └── analytics_models.py
│   │
│   ├── prompts/
│   │   └── classification_prompt.py
│   │
│   ├── routes/
│   │   ├── analysis.py
│   │   ├── analytics.py
│   │   ├── chat.py
│   │   ├── evaluation.py
│   │   ├── search.py
│   │   └── upload.py
│   │
│   ├── services/
│   │   ├── analytics_service.py
│   │   ├── chunking_service.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── evaluation_report_service.py
│   │   ├── feedback_database_service.py
│   │   ├── feedback_features_service.py
│   │   ├── gemini_service.py
│   │   ├── rag_chain_service.py
│   │   ├── rag_service.py
│   │   ├── retriever_service.py
│   │   └── vector_store_service.py
│   │
│   ├── tests/
│   │   └── ...
│   │
│   ├── utils/
│   │   └── ...
│   │
│   └── vector_store/
│       └── customer_feedback/
│           ├── index.faiss
│           └── index.pkl
│
├── frontend/
│   ├── app.py
│   ├── assets/
│   │   └── Hero.png
│   ├── pages/
│   │   ├── home.py
│   │   ├── dashboard.py
│   │   ├── analysis.py
│   │   ├── search.py
│   │   ├── evaluation.py
│   │   └── system_status.py
│   └── services/
│       └── api_client.py
│
└── Sample_Data/
    ├── data_gen.py
    ├── customer_feedback_forms/
    └── evaluation/
        └── dataset_manifest.csv
```

> The tree above reflects the current repository layout rather than a future target structure.

---

## Technology stack

| Area | Technology | Purpose |
| --- | --- | --- |
| Application language | Python | End-to-end backend, AI, evaluation, and frontend code |
| Frontend | Streamlit | User-facing application and evaluation/dashboard UI |
| Backend | FastAPI | REST API, routing, validation, and service integration |
| LLM | Google Gemini | Customer-feedback classification and structured reasoning |
| LLM integration | LangChain + `langchain-google-genai` | RAG orchestration and structured output integration |
| Embeddings | Sentence Transformers | Dense vector representations of feedback |
| Embedding model | `all-MiniLM-L6-v2` | Current local sentence-transformer embedding model |
| Vector search | FAISS | Similarity search over reference feedback |
| Retrieval strategy | MMR | Reduce redundant retrieval results and improve contextual diversity |
| PDF processing | PyMuPDF | Native text extraction and document handling |
| OCR | Tesseract through PyMuPDF OCR | Fallback for scanned/image-based PDFs |
| Structured validation | Pydantic | Classification and API model validation |
| Database | PostgreSQL | Feedback, classification, retrieval and analytics persistence |
| ORM | SQLAlchemy | PostgreSQL database access |
| API server | Uvicorn | ASGI server for FastAPI |
| Evaluation | pytest + custom evaluation services | Regression testing and benchmark analysis |
| Optional RAG evaluation dependency | Ragas | Evaluation tooling included in the environment |

---

## Backend API

The FastAPI application exposes multiple service groups.

### Core endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Basic API information |
| `GET` | `/health` | Backend health check |

### Analysis

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/analysis/classify` | Classify raw feedback through the RAG pipeline |
| `GET` | `/api/analysis/{feedback_id}` | Retrieve a persisted analysis record |
| `GET` | `/api/analysis/status` | Check analysis-service availability |

### PDF upload

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/upload/pdf` | Upload and process one customer-feedback PDF |
| `GET` | `/api/upload/status` | Check upload-service availability |

> Multi-PDF upload is currently orchestrated by the Streamlit frontend. The backend continues to expose the existing single-document `/api/upload/pdf` contract, which is invoked once for each selected PDF.

### Semantic search

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/search` | Semantic search over the feedback knowledge base |
| `GET` | `/api/search/status` | Check search-service availability |

### Analytics

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/analytics` | Retrieve PostgreSQL-backed analytics with optional category/date filters |
| `GET` | `/api/analytics/status` | Check analytics-service availability |

### Evaluation

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/evaluation/development` | Read the saved development RAG evaluation |
| `GET` | `/api/evaluation/final-benchmark` | Read the saved final-benchmark RAG evaluation |
| `GET` | `/api/evaluation/rag-vs-no-rag/development` | Read the development RAG-vs-No-RAG comparison |
| `GET` | `/api/evaluation/rag-vs-no-rag/final-benchmark` | Read the final-benchmark RAG-vs-No-RAG comparison |
| `GET` | `/api/evaluation/summary` | Read the combined saved evaluation summary |
| `GET` | `/api/evaluation/status` | Check evaluation-service availability |

> The current Evaluation API reads persisted evaluation reports. It does not automatically launch a fresh multi-case Gemini evaluation whenever the Streamlit page is opened.

---

## Setup

### Prerequisites

Install the following before running the application:

- Python 3.10+ recommended
- PostgreSQL
- Git
- A Google Gemini API key
- Tesseract OCR if you need OCR for scanned PDFs

The current `requirements.txt` provides dependencies for FastAPI, LangChain, Gemini, Sentence Transformers, FAISS, PostgreSQL, Streamlit, pytest, and evaluation tooling.

### Clone the repository

```bash
git clone https://github.com/krish-027/AI-Feedback-Intelligence.git
cd AI-Feedback-Intelligence
```

### Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment configuration

The backend loads environment variables from `.env`.

Create:

```text
backend/.env
```

Example:

```env
APP_NAME=AI Customer Feedback Intelligence
APP_VERSION=1.0.0

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/pulseiq

UPLOAD_DIR=data/feedback_pdfs
EXTRACTED_DIR=data/extracted
RESULTS_DIR=data/results
VECTOR_STORE_DIR=vector_store

OCR_LANG=eng
OCR_DPI=250
OCR_MIN_NATIVE_CHARS=50
OCR_MIN_ALNUM_RATIO=0.30

TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

### Important

- Never commit `backend/.env`.
- Do not expose `GEMINI_API_KEY` in source control, screenshots, or public logs.
- `DATABASE_URL` must point to a reachable PostgreSQL database.
- If OCR is required, Tesseract and the relevant language data must be installed.
- The frontend API client currently defaults to `http://127.0.0.1:8000`, so local backend execution should use that port unless the client is changed.

---

## Initialize the database

After configuring `DATABASE_URL`:

```bash
python -m backend.database_init
```

Expected output:

```text
Database tables initialized successfully.
```

The database initialization uses SQLAlchemy metadata to create the application tables.

---

## Run locally

PulseIQ has two application processes during local development.

### Start FastAPI

From the repository root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API should be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Start Streamlit

In a second terminal:

```bash
streamlit run frontend/app.py
```

The frontend normally opens at:

```text
http://localhost:8501
```

---

## Local application walkthrough

### 1. Home

The Home page introduces PulseIQ and the overall workflow.

### 2. Dashboard

The Dashboard requests analytics from FastAPI and displays PostgreSQL-backed feedback summaries.

Useful checks:

- category counts
- recent feedback
- category filtering
- date filtering
- keyword-oriented summaries


![PulseIQ Dashboard - View 01](./docs/Dashboard_01.png)

![PulseIQ Dashboard - View 02](./docs/Dashboard_02.png)

![PulseIQ Dashboard - View 03](./docs/Dashboard_03.png)

![PulseIQ Dashboard - View 04](./docs/Dashboard_04.png)

![PulseIQ Dashboard - View 05](./docs/Dashboard_05.png)

![PulseIQ Dashboard - View 06](./docs/Dashboard_06.png)


### 3. Analyze Feedback

The Analyze Feedback page supports selecting one or multiple customer-feedback PDFs.

For a single PDF, PulseIQ processes the document through the normal end-to-end analysis pipeline.

For multiple PDFs, PulseIQ processes each selected document independently and presents the results together in a batch summary.

The workflow is:

```text
One or More PDFs
       |
       v
Streamlit Multi-File Upload
       |
       v
Sequential Per-File Processing
       |
       v
PDF extraction (when applicable)
       |
       v
Cleaning + PII removal
       |
       v
RAG retrieval
       |
       v
Gemini classification
       |
       v
Structured response
       |
       v
PostgreSQL persistence
       |
       v
Batch results + detailed per-file analysis
```

For multi-PDF uploads, the page shows:

- Number of successfully analyzed documents
- Per-document category
- Per-document confidence
- Feedback ID
- Retrieved evidence count
- Failed documents, when applicable
- A detailed-analysis selector for inspecting an individual result

A failure in one PDF does not stop the remaining selected PDFs from being processed.

![PulseIQ Analyze Feedback - View 01](./docs/Analyze_Feedback_01.png)

![PulseIQ Analyze Feedback - View 02](./docs/Analyze_Feedback_02.png)

![PulseIQ Analyze Feedback - View 03](./docs/Analyze_Feedback_03.png)

![PulseIQ Analyze Feedback - View 04](./docs/Analyze_Feedback_04.png)




### 4. Search & Evidence

Enter a natural-language query and retrieve semantically similar reference feedback.

Example queries:

```text
customers complaining about slow issue resolution
```

```text
positive experiences with professional staff
```

```text
feedback mentioning poor communication
```


![PulseIQ Search & Evidence - View 01](./docs/Search_&_Evidence_01.png)

![PulseIQ Search & Evidence - View 02](./docs/Search_&_Evidence_02.png)

![PulseIQ Search & Evidence - View 03](./docs/Search_&_Evidence_03.png)


### 5. Evaluation

The Evaluation page loads the saved evaluation reports through FastAPI and presents:

- Classification metrics
- Per-class metrics
- Confusion matrix
- Retrieval metrics
- RAG vs No-RAG comparison
- Paired comparison
- Detailed reports


![PulseIQ Evaluation - View 01](./docs/Evaluation-01.png)

![PulseIQ Evaluation - View 02](./docs/Evaluation-02.png)

![PulseIQ Evaluation - View 03](./docs/Evaluation-03.png)


### 6. System Status

The System Status page checks whether the application's core services are reachable and reports an overall operational state.

---

## Example classification output

A simplified response from the analysis workflow has the following conceptual shape:

```json
{
  "feedback_id": "FB-6cdc8a7001a2",
  "category": "Poor",
  "confidence": 1.0,
  "explanation": "The feedback contains multiple low ratings and a negative recommendation, indicating substantial dissatisfaction.",
  "flagged_keywords": [
    "Overall satisfaction with employee behavior",
    "Recommendation: No"
  ],
  "retrieved_feedback_ids": [
    "FB-f5034132e25a",
    "FB-089f5cfbcd6b"
  ]
}
```

The exact response schema may evolve as backend contracts are extended.

---

## Search example

The semantic-search API accepts a query and result count.

Conceptually:

```http
POST /api/search
Content-Type: application/json

{
  "query": "customers complaining about long resolution times",
  "k": 4
}
```

The response contains matched feedback records, including similarity and category information.

---

## Evaluation methodology

PulseIQ separates the dataset into conceptual roles so that the vector index and evaluation datasets do not become the same source.

The current setup uses a reference corpus for production retrieval and separate development/final-benchmark splits for evaluation.

### Why the split matters

If the same feedback records are used both:

1. as retrieval examples, and
2. as evaluation cases,

then evaluation results can become misleading because the model has access to information from the test examples during retrieval.

PulseIQ therefore builds the production FAISS index from the reference split and keeps evaluation records outside the production retrieval corpus.

### Evaluation artifacts

Evaluation components live under:

```text
backend/evaluation/
```

and saved reports are stored under:

```text
backend/evaluation/results/
```

This includes RAG evaluation reports, RAG-vs-No-RAG reports, case-level CSVs, and JSON summaries.

---

## Testing

The repository includes automated tests using `pytest`.

Run the complete test suite from the repository root:

```bash
pytest
```

Run a specific backend test module:

```bash
pytest backend/tests/test_rag_evaluation_service.py -v
```

Examples of covered areas include:

- PDF/document ingestion
- OCR-related behavior
- chunking
- embedding/vector-store behavior
- retrieval
- RAG orchestration
- Gemini service behavior
- API endpoints
- PostgreSQL integration
- analytics
- evaluation calculations
- RAG-vs-No-RAG comparison
- error analysis
- integration paths

Tests should be treated as the verification layer for the implementation rather than as a substitute for benchmark evaluation.

---

## Data and sample dataset

The repository contains sample customer-feedback data under:

```text
Sample_Data/
```

This currently includes:

- sample feedback-form PDFs
- data-generation utilities
- evaluation metadata and split manifests

The evaluation manifest lives under:

```text
Sample_Data/evaluation/dataset_manifest.csv
```

The manifest is used to maintain explicit dataset roles and connect feedback IDs to evaluation behavior.

---

## Trust, safety, and data handling

PulseIQ is designed to avoid embedding several explicitly identified customer fields.

Current document sanitization removes:

- Customer Name
- Account Number
- Contact Number

This should **not** be interpreted as a complete enterprise-grade PII discovery system. Additional fields, formats, and domain-specific identifiers would require further detection rules or a dedicated entity-recognition/redaction layer.

### Human review

The generated category and explanation should be treated as decision support, not as an unquestionable ground truth. Human review remains appropriate for:

- ambiguous feedback
- unusual customer complaints
- compliance-sensitive records
- security-sensitive workflows
- high-impact customer decisions

---

## Error handling

The backend includes explicit error handling for common service boundaries.

Examples include:

- invalid API requests
- missing files
- invalid PDF input
- unavailable OCR configuration
- missing environment variables
- Gemini configuration failures
- PostgreSQL connection/configuration failures
- invalid evaluation reports
- unavailable FastAPI services from Streamlit
- malformed API responses

The Streamlit frontend centralizes backend communication through `frontend/services/api_client.py`, which converts common HTTP/network failures into user-facing errors.

---

## Design decisions

### Why FastAPI + Streamlit?

FastAPI and Streamlit give the project a clean separation between:

```text
User interface
      |
      v
Streamlit
      |
      | HTTP
      v
FastAPI
      |
      v
AI / data services
```

This makes the RAG pipeline independently testable and keeps the frontend from directly depending on implementation details of LangChain, FAISS, Gemini, or SQLAlchemy.

### Why FAISS?

The dataset is relatively small, and a local FAISS index provides a straightforward, fast, low-overhead vector retrieval layer without requiring a separate managed vector database.

### Why local Sentence Transformers embeddings?

Local embeddings avoid an additional embedding API dependency and give deterministic control over the embedding model used to build the FAISS corpus.

### Why Gemini structured output?

Customer-feedback classification benefits from a predictable response schema. Structured output plus Pydantic validation reduces the amount of fragile free-form parsing required after the LLM response.

### Why persist retrieval evidence?

Persisting retrieved feedback IDs and scores makes an individual classification easier to inspect and supports the evidence-oriented UX in the Search & Evidence and Analyze Feedback flows.

---

## What PulseIQ is not

The current repository should not be described as implementing capabilities that are only part of the future roadmap or earlier design discussions.

PulseIQ is currently **not**:

- a fully autonomous agentic AI system
- a LangGraph multi-agent workflow
- an MCP-based application
- a general-purpose conversational chatbot
- a complete adaptive/corrective RAG system
- a production-grade generalized PII detection platform
- a real-time streaming analytics platform
- a cross-document batch reasoning system that produces one unified analysis across all uploaded PDFs
- an automatic live evaluation runner that executes the full benchmark every time the UI opens

These may be useful future directions, but they are not required to understand the current implementation.

---

## Known limitations

### Small benchmark size

The current final benchmark contains 20 records, with 19 successfully evaluated in the latest saved report. With small evaluation sets, one additional correct or incorrect case can noticeably change the reported percentage.

### LLM variability

Even with low temperature, LLM-backed classification can exhibit provider/model-level variability. Benchmark results should therefore be reported with the exact model and configuration used.

### OCR dependency

Scanned PDFs require a correctly installed Tesseract environment. Native PDFs do not necessarily require OCR.

### Local FAISS index

The current vector-store workflow uses a local index. Rebuilding the index is a separate data-preparation operation and should be performed whenever the reference corpus or embedding configuration changes.

### Frontend/backend configuration

The current Streamlit HTTP client uses a local FastAPI base URL by default. Cloud deployment therefore requires environment-specific configuration changes rather than assuming the local URL is valid in production.

### Batch processing model

Multi-PDF analysis currently processes documents sequentially through the existing single-document API workflow.

This keeps the implementation simple and preserves the existing backend architecture, but processing large batches can take longer than a parallel job-processing architecture.

The current feature also treats each PDF independently. It does not yet perform a single collective analysis across all uploaded documents.

### Evaluation reports are persisted artifacts

The current Evaluation API reads saved reports. Running a new experiment and exposing its results to the UI are separate operations.

---

## Suggested future evolution

Potential future improvements include:

### Retrieval

- stronger embedding-model comparisons
- hybrid lexical + dense retrieval
- cross-encoder reranking
- category-balanced example selection
- retrieval parameter sweeps
- query transformation

### Classification

- stronger boundary-specific few-shot examples
- hierarchical classification
- pairwise category decisions
- confidence calibration
- model comparison experiments

### Evaluation

- larger external validation datasets
- automated experiment tracking
- richer retrieval metrics such as Hit@k and MRR
- deeper groundedness/faithfulness evaluation
- automated error clustering
- dataset quality and label-audit tooling

### Product

- trend analysis over time
- complaint clustering
- alerting for emerging issues
- feedback summarization by branch/product/region
- role-specific dashboards
- authentication and access control
- configurable backend URLs for production deployment

---

## Demo walkthrough

A simple demonstration can be run with the following flow:

```text
Open PulseIQ
     |
     v
Dashboard
     |
     v
Upload one or multiple feedback PDFs
     |
     v
Analyze selected documents
     |
     v
View batch analysis summary
     |
     v
Inspect category + confidence + explanation
     |
     v
Open Search & Evidence
     |
     v
Search related customer feedback
     |
     v
Open Dashboard
     |
     v
Inspect aggregated feedback analytics
     |
     v
Open Evaluation
     |
     v
Inspect benchmark metrics + RAG vs No-RAG
     |
     v
Open System Status
     |
     v
Verify application services
```

### Suggested demo queries

```text
customers complaining about response time
```

```text
positive feedback about professional staff
```

```text
customers unhappy with issue resolution
```

```text
feedback with mixed satisfaction but a clear improvement request
```

---

## Sample output shape

A high-level analysis report can be presented in a structure such as:

```markdown
# Feedback Analysis

## Classification
- Category: Poor
- Confidence: 1.00

## Explanation
The feedback contains multiple low ratings and a negative recommendation,
indicating substantial dissatisfaction.

## Flagged Evidence
- Overall satisfaction with employee behavior: 1/5
- Recommendation: No

## Retrieved Evidence
- Similar historical feedback #1
- Similar historical feedback #2
- Similar historical feedback #3
- Similar historical feedback #4
```

The exact text is generated dynamically from the supplied feedback and retrieved context.

> In the Analyze Feedback UI, displayed flagged keywords are normalized to remove trailing numeric rating values when present. The underlying backend response may still contain the original extracted phrase.

---

## Development workflow

The project was built incrementally around separable stages:

```text
Data preparation
      |
      v
Document ingestion
      |
      v
Chunking + embeddings
      |
      v
FAISS retrieval
      |
      v
LangChain RAG + Gemini
      |
      v
Evaluation + error analysis
      |
      v
FastAPI service layer
      |
      v
PostgreSQL persistence + analytics
      |
      v
Streamlit application
      |
      v
Final integration + regression testing
```

The resulting architecture intentionally keeps the AI pipeline in backend services rather than embedding business logic directly inside individual Streamlit pages.

---

## Project organization principles

### Backend services over UI logic

Streamlit pages communicate with the backend through `frontend/services/api_client.py` rather than recreating RAG, database, or analytics logic in the frontend.

### Explicit service boundaries

The backend separates concerns such as:

- document ingestion
- chunking
- embeddings
- vector-store construction
- retrieval
- RAG orchestration
- Gemini integration
- persistence
- analytics
- evaluation

### Evaluation is reproducible

Evaluation reports are saved as structured JSON/CSV artifacts so results can be inspected without rerunning the full benchmark every time the dashboard is opened.

---

## Screenshots

The frontend already contains a hero graphic at:

```text
frontend/assets/Hero.png
```

You can display it in the GitHub README with:

```markdown
![PulseIQ](frontend/assets/Hero.png)
```

### Screenshot files and exact placement

For the four main application pages, keep the screenshots in a dedicated repository folder such as:

```text
docs/screenshots/
├── dashboard.png
├── analyze-feedback.png
├── search-and-evidence.png
└── evaluation.png
```

The README intentionally marks the exact insertion point for each screenshot earlier in the **Local application walkthrough**:

| Page | Screenshot file | Exact README location |
| --- | --- | --- |
| Dashboard | `docs/screenshots/dashboard.png` | Immediately after the Dashboard bullet list, before `### 3. Analyze Feedback` |
| Analyze Feedback | `docs/screenshots/analyze-feedback.png` | Immediately after the workflow diagram, before `### 4. Search & Evidence` |
| Search & Evidence | `docs/screenshots/search-and-evidence.png` | Immediately after the final Search & Evidence sentence, before `### 5. Evaluation` |
| Evaluation | `docs/screenshots/evaluation.png` | Immediately after the Evaluation bullet list, before `### 6. System Status` |

This layout keeps each screenshot next to the explanation of the corresponding page instead of putting all UI images at the end of the README.

---

## Project files worth knowing

| File | Purpose |
| --- | --- |
| `backend/main.py` | FastAPI application entry point |
| `backend/config.py` | Environment-backed application settings |
| `backend/database.py` | PostgreSQL/SQLAlchemy setup |
| `backend/database_init.py` | Database table initialization |
| `backend/services/document_service.py` | PDF extraction, OCR fallback, cleaning, and PII removal |
| `backend/services/embedding_service.py` | Sentence Transformer embedding generation |
| `backend/services/vector_store_service.py` | FAISS index construction/loading |
| `backend/services/retriever_service.py` | Semantic retrieval |
| `backend/services/rag_chain_service.py` | LangChain retrieval + prompt + LLM orchestration |
| `backend/services/gemini_service.py` | Gemini integration and structured classification |
| `backend/services/rag_service.py` | Application-level RAG facade |
| `backend/services/feedback_database_service.py` | Feedback persistence |
| `backend/services/analytics_service.py` | PostgreSQL-backed analytics |
| `backend/services/evaluation_report_service.py` | Evaluation-report loading/serving |
| `backend/routes/upload.py` | PDF upload endpoints |
| `backend/routes/analysis.py` | Analysis endpoints |
| `backend/routes/search.py` | Semantic search endpoints |
| `backend/routes/analytics.py` | Analytics endpoints |
| `backend/routes/evaluation.py` | Evaluation endpoints |
| `frontend/app.py` | Streamlit application shell and navigation |
| `frontend/services/api_client.py` | Frontend-to-FastAPI HTTP client |
| `frontend/pages/dashboard.py` | Analytics dashboard |
| `frontend/pages/analysis.py` | Feedback analysis UI, multi-PDF upload, batch result presentation |
| `frontend/pages/search.py` | Semantic search UI |
| `frontend/pages/evaluation.py` | Evaluation UI |
| `frontend/pages/system_status.py` | Service health UI |
| `backend/evaluation/rag_evaluation_service.py` | RAG evaluation engine |
| `backend/evaluation/rag_ablation_service.py` | RAG vs No-RAG evaluation |
| `backend/evaluation/error_analysis_service.py` | Error/confusion analysis |

---

## Security and secrets

Never commit:

```text
backend/.env
API keys
Database passwords
Private customer data
Production credentials
```

Use environment variables and secret management provided by the deployment platform when moving beyond local development.

---

## Deployment

The repository is structured as a separately runnable Streamlit frontend and FastAPI backend, which makes the architecture suitable for split deployment.

A deployment should provide:

```text
Streamlit service
      |
      | HTTP
      v
FastAPI service
      |
      +------ Gemini API
      +------ PostgreSQL
      +------ local/reference FAISS artifacts
```

For a cloud deployment, update the frontend API base URL so Streamlit no longer points at `127.0.0.1:8000`, provide the necessary environment variables, and ensure the deployed environment has the dependencies and filesystem/storage behavior required by the PDF/FAISS workflow.

The current repository does not treat a particular cloud provider as the only supported production target.

---

## API documentation

When FastAPI is running locally, use:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

These are generated from the FastAPI route definitions and should be treated as the most precise source for the live API contract.

---

## Contributing

For development changes:

1. Create a focused change.
2. Update or add tests for the affected behavior.
3. Run the relevant test module.
4. Run the complete test suite before merging.
5. Verify that changes to prompts, retrieval, embeddings, or evaluation configuration do not accidentally introduce evaluation-data leakage.
6. Keep secrets and customer-identifying data out of commits.

For AI pipeline changes, record the configuration that changed and compare the resulting benchmark metrics rather than relying only on subjective output inspection.

---

## Project ownership

**PulseIQ**

AI-Powered Customer Feedback Intelligence project is maintained by **Krish Pathak**.

---

## Acknowledgements

PulseIQ builds on open-source and developer tools including:

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [Google Gemini](https://ai.google.dev/)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [Ragas](https://docs.ragas.io/)

---

## Final note

PulseIQ is designed as an end-to-end engineering project rather than a single prompt wrapped in a UI. The core objective is to demonstrate the complete lifecycle of a GenAI/RAG application:

```text
Unstructured customer feedback
            ↓
Document processing
            ↓
Embeddings + vector retrieval
            ↓
RAG context construction
            ↓
LLM classification
            ↓
Structured output
            ↓
Evidence + persistence
            ↓
Search + analytics
            ↓
Held-out evaluation
            ↓
FastAPI service layer
            ↓
Streamlit product interface
```