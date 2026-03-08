"""Main client for the ClinicalTrials.gov v2 API."""

from __future__ import annotations

import time
from typing import Any

import requests

from .exceptions import ClinicalTrialsError, NotFoundError, RateLimitError
from .models import Study
from .parsers import parse_study
from .search import SearchBuilder
from .utils import validate_nct_id

BASE_URL = "https://clinicaltrials.gov/api/v2"


class ClinicalTrials:
    """Client for the ClinicalTrials.gov v2 API.

    No API key is needed. Handles rate limiting and retries automatically.

    Args:
        max_retries: Number of retries on 429/5xx errors.
        rate_limit: Maximum requests per second.

    Example::

        ct = ClinicalTrials()
        study = ct.get("NCT06000696")
        print(study.title)
    """

    def __init__(self, max_retries: int = 3, rate_limit: float = 10):
        self.max_retries = max_retries
        self.rate_limit = rate_limit
        self._min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self._last_request_time = 0.0
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _throttle(self) -> None:
        """Enforce rate limiting between requests."""
        if self._min_interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)

    def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        """Make an API request with retry and rate limiting.

        Args:
            method: HTTP method.
            path: API path (appended to base URL).
            **kwargs: Passed to requests.Session.request.

        Returns:
            Parsed JSON response.

        Raises:
            NotFoundError: On 404 responses.
            RateLimitError: On 429 after all retries exhausted.
            ClinicalTrialsError: On other HTTP errors.
        """
        url = f"{BASE_URL}{path}"
        last_error = None

        for attempt in range(self.max_retries + 1):
            self._throttle()
            self._last_request_time = time.monotonic()

            try:
                response = self.session.request(method, url, **kwargs)
            except requests.RequestException as e:
                last_error = ClinicalTrialsError(f"Request failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(2**attempt)
                    continue
                raise last_error from e

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise NotFoundError(path)
            elif response.status_code == 429:
                last_error = RateLimitError()
                if attempt < self.max_retries:
                    retry_after = float(
                        response.headers.get("Retry-After", 2**attempt)
                    )
                    time.sleep(retry_after)
                    continue
            elif response.status_code >= 500:
                last_error = ClinicalTrialsError(
                    f"Server error: {response.status_code}", response.status_code
                )
                if attempt < self.max_retries:
                    time.sleep(2**attempt)
                    continue
            else:
                raise ClinicalTrialsError(
                    f"API error {response.status_code}: {response.text}",
                    response.status_code,
                )

        raise last_error  # type: ignore[misc]

    def get(self, nct_id: str) -> Study:
        """Fetch a single study by NCT ID.

        Args:
            nct_id: The NCT identifier (e.g., "NCT06000696").

        Returns:
            A Study object with all available data.

        Raises:
            ValueError: If the NCT ID format is invalid.
            NotFoundError: If the study doesn't exist.
        """
        nct_id = validate_nct_id(nct_id)
        data = self._request("GET", f"/studies/{nct_id}")
        return parse_study(data)

    def search(self, query: str | None = None, **kwargs: Any) -> SearchBuilder:
        """Start a search query. Returns a SearchBuilder for chaining.

        Args:
            query: A general search term.
            **kwargs: Shortcut filters — condition, intervention, status, phase, etc.

        Returns:
            A SearchBuilder that can be further refined or executed.

        Example::

            # Simple search
            results = ct.search("lung cancer").execute()

            # Fluent builder
            results = (ct.search()
                .condition("diabetes")
                .phase(2, 3)
                .recruiting()
                .execute())
        """
        builder = SearchBuilder(self)
        if query:
            builder = builder.term(query)

        # Apply shortcut kwargs
        if "condition" in kwargs:
            builder = builder.condition(kwargs["condition"])
        if "intervention" in kwargs:
            builder = builder.intervention(kwargs["intervention"])
        if "status" in kwargs:
            status = kwargs["status"]
            if isinstance(status, str):
                builder = builder.status(status)
            else:
                builder = builder.status(*status)
        if "phase" in kwargs:
            phase = kwargs["phase"]
            if isinstance(phase, int):
                builder = builder.phase(phase)
            else:
                builder = builder.phase(*phase)
        if "sponsor" in kwargs:
            builder = builder.sponsor(kwargs["sponsor"])
        if "title" in kwargs:
            builder = builder.title(kwargs["title"])

        return builder

    def count(self, query: str | None = None, **kwargs: Any) -> int:
        """Count matching studies without fetching them.

        Accepts the same arguments as search().

        Args:
            query: A general search term.
            **kwargs: Shortcut filters.

        Returns:
            The number of matching studies.
        """
        return self.search(query, **kwargs).count()

    def field_values(self, field: str) -> list[str]:
        """Get valid values for a specific field.

        Args:
            field: The field name (e.g., "OverallStatus", "Phase").

        Returns:
            List of valid values for the field.
        """
        data = self._request("GET", f"/stats/fieldValues/{field}")
        return data.get("values", data.get("fieldValues", []))

    def api_version(self) -> str:
        """Get the current CT.gov API version.

        Returns:
            The API version string.
        """
        data = self._request("GET", "/version")
        return data.get("version", data.get("apiVersion", "unknown"))

    def total_count(self) -> int:
        """Get the total number of studies on ClinicalTrials.gov.

        Returns:
            The total study count.
        """
        data = self._request("GET", "/stats/size")
        return data.get("totalStudies", data.get("total", 0))
