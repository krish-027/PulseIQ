from __future__ import annotations

from typing import Any

import requests


class APIClientError(Exception):
    """Raised when the PulseIQ FastAPI backend returns an error."""


class APIClient:
    """
    HTTP client for the PulseIQ FastAPI backend.

    Streamlit pages should communicate with the backend through
    this class rather than making direct HTTP requests.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Internal request helpers
    # ------------------------------------------------------------------

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request(
            method="GET",
            endpoint=endpoint,
            params=params,
        )

    def _post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request(
            method="POST",
            endpoint=endpoint,
            json=json,
            files=files,
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json,
                files=files,
                timeout=self.timeout,
            )

        except requests.exceptions.ConnectionError as exc:
            raise APIClientError(
                "Unable to connect to the PulseIQ backend. "
                "Make sure the FastAPI server is running."
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise APIClientError(
                "The PulseIQ backend request timed out."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise APIClientError(
                f"Backend request failed: {exc}"
            ) from exc

        if not response.ok:
            detail = self._extract_error(response)

            raise APIClientError(
                f"PulseIQ backend returned "
                f"HTTP {response.status_code}: {detail}"
            )

        try:
            return response.json()

        except ValueError as exc:
            raise APIClientError(
                "The PulseIQ backend returned an invalid JSON response."
            ) from exc

    @staticmethod
    def _extract_error(
        response: requests.Response,
    ) -> str:
        try:
            payload = response.json()

            if isinstance(payload, dict):
                detail = payload.get("detail")

                if detail:
                    return str(detail)

            return str(payload)

        except ValueError:
            return response.text or "Unknown backend error"

    # ------------------------------------------------------------------
    # System / health
    # ------------------------------------------------------------------

    def get_root(self) -> dict[str, Any]:
        """Get basic API information."""

        return self._get("/")

    def get_health(self) -> dict[str, Any]:
        """Check whether the FastAPI backend is healthy."""

        return self._get("/health")

    def get_analysis_status(self) -> dict[str, Any]:
        """Get analysis service status."""

        return self._get("/api/analysis/status")

    def get_upload_status(self) -> dict[str, Any]:
        """Get upload service status."""

        return self._get("/api/upload/status")

    def get_search_status(self) -> dict[str, Any]:
        """Get semantic search service status."""

        return self._get("/api/search/status")


        return self._get("/api/analytics/status")

    def get_evaluation_status(self) -> dict[str, Any]:
        """Get evaluation service status."""

        return self._get("/api/evaluation/status")

    # ------------------------------------------------------------------
    # Feedback analysis
    # ------------------------------------------------------------------

    def classify_feedback(
        self,
        feedback: str,
        filename: str = "manual_input.txt",
    ) -> dict[str, Any]:
        """
        Classify feedback through the FastAPI RAG pipeline.
        """

        return self._post(
            "/api/analysis/classify",
            json={
                "feedback": feedback,
                "filename": filename,
            },
        )

    def get_feedback_analysis(
        self,
        feedback_id: str,
    ) -> dict[str, Any]:
        """
        Retrieve a previously analyzed feedback record.
        """

        return self._get(
            f"/api/analysis/{feedback_id}"
        )

    # ------------------------------------------------------------------
    # PDF upload
    # ------------------------------------------------------------------

    def upload_pdf(
        self,
        file_name: str,
        file_bytes: bytes,
    ) -> dict[str, Any]:
        """
        Upload a PDF to the FastAPI backend.

        The backend is responsible for PDF extraction,
        processing, classification, and persistence.
        """

        files = {
            "file": (
                file_name,
                file_bytes,
                "application/pdf",
            )
        }

        return self._post(
            "/api/upload/pdf",
            files=files,
        )

    # ------------------------------------------------------------------
    # Semantic search
    # ------------------------------------------------------------------

    def search_feedback(
        self,
        query: str,
        k: int = 4,
    ) -> dict[str, Any]:
        """
        Perform semantic search over the feedback knowledge base.
        """

        return self._post(
            "/api/search",
            json={
                "query": query,
                "k": k,
            },
        )

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_analytics_status(self) -> dict[str, Any]:
        """Get analytics service status."""

        return self._get(
            "/api/analytics/status"
        )

    def get_analytics(
        self,
        keyword_limit: int = 10,
        recent_limit: int = 10,
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve customer feedback analytics.

        Optional filters are passed directly to the FastAPI
        analytics endpoint.
        """

        params: dict[str, Any] = {
            "keyword_limit": keyword_limit,
            "recent_limit": recent_limit,
        }

        if category:
            params["category"] = category

        if start_date:
            params["start_date"] = start_date

        if end_date:
            params["end_date"] = end_date

        return self._get(
            "/api/analytics",
            params=params,
        )

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def get_development_evaluation(
        self,
    ) -> dict[str, Any]:
        """Retrieve the latest development-set RAG evaluation."""

        return self._get(
            "/api/evaluation/development"
        )

    def get_final_benchmark_evaluation(
        self,
    ) -> dict[str, Any]:
        """Retrieve the frozen final-benchmark RAG evaluation."""

        return self._get(
            "/api/evaluation/final-benchmark"
        )

    def get_development_rag_vs_no_rag(
        self,
    ) -> dict[str, Any]:
        """Retrieve the development RAG vs No-RAG comparison."""

        return self._get(
            "/api/evaluation/rag-vs-no-rag/development"
        )

    def get_final_rag_vs_no_rag(
        self,
    ) -> dict[str, Any]:
        """Retrieve the final-benchmark RAG vs No-RAG comparison."""

        return self._get(
            "/api/evaluation/rag-vs-no-rag/final-benchmark"
        )

    def get_evaluation_summary(
        self,
    ) -> dict[str, Any]:
        """Retrieve the combined evaluation summary."""

        return self._get(
            "/api/evaluation/summary"
        )


# ----------------------------------------------------------------------
# Shared frontend client
# ----------------------------------------------------------------------

api_client = APIClient()