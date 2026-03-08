"""Custom exceptions for the clinicaltrials library."""


class ClinicalTrialsError(Exception):
    """Base exception for clinicaltrials library errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(ClinicalTrialsError):
    """Raised when a study or resource is not found (404)."""

    def __init__(self, nct_id: str):
        super().__init__(f"Study not found: {nct_id}", status_code=404)


class RateLimitError(ClinicalTrialsError):
    """Raised when the API rate limit is exceeded (429)."""

    def __init__(self):
        super().__init__(
            "Rate limit exceeded. Please slow down requests.", status_code=429
        )
