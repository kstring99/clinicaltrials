"""clinicaltrials — A clean Python library for the ClinicalTrials.gov API."""

from .client import ClinicalTrials
from .models import (
    Contact,
    Eligibility,
    Intervention,
    Location,
    Outcome,
    Sponsor,
    Study,
    StudyDesign,
)
from .search import SearchBuilder
from .exceptions import ClinicalTrialsError, NotFoundError, RateLimitError
from ._version import __version__

__all__ = [
    "ClinicalTrials",
    "Contact",
    "ClinicalTrialsError",
    "Eligibility",
    "Intervention",
    "Location",
    "NotFoundError",
    "Outcome",
    "RateLimitError",
    "SearchBuilder",
    "Sponsor",
    "Study",
    "StudyDesign",
    "__version__",
]
