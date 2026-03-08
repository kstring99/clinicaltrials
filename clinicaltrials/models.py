"""Data models for clinical trial studies."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import date


@dataclass
class Intervention:
    """A study intervention (drug, device, procedure, etc.)."""

    name: str
    type: str
    description: str | None = None


@dataclass
class Sponsor:
    """A study sponsor or collaborator."""

    name: str
    role: str  # "LEAD" or "COLLABORATOR"


@dataclass
class Location:
    """A study site location."""

    facility: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    status: str | None = None


@dataclass
class Contact:
    """A study contact."""

    name: str | None = None
    phone: str | None = None
    email: str | None = None


@dataclass
class Outcome:
    """A study outcome measure."""

    measure: str
    description: str | None = None
    time_frame: str | None = None
    type: str = "PRIMARY"  # "PRIMARY" or "SECONDARY"


@dataclass
class Eligibility:
    """Study eligibility criteria."""

    criteria: str | None = None
    gender: str | None = None
    min_age: str | None = None
    max_age: str | None = None
    healthy_volunteers: bool | None = None


@dataclass
class StudyDesign:
    """Study design information."""

    allocation: str | None = None
    intervention_model: str | None = None
    primary_purpose: str | None = None
    masking: str | None = None
    masking_description: str | None = None


@dataclass
class Study:
    """A clinical trial study from ClinicalTrials.gov."""

    nct_id: str
    title: str
    brief_title: str | None = None
    official_title: str | None = None
    status: str = ""
    phase: str | None = None
    study_type: str | None = None
    conditions: list[str] = field(default_factory=list)
    interventions: list[Intervention] = field(default_factory=list)
    sponsors: list[Sponsor] = field(default_factory=list)
    enrollment: int | None = None
    enrollment_type: str | None = None
    start_date: date | None = None
    primary_completion: date | None = None
    completion_date: date | None = None
    first_posted: date | None = None
    last_updated: date | None = None
    locations: list[Location] = field(default_factory=list)
    contacts: list[Contact] = field(default_factory=list)
    brief_summary: str | None = None
    detailed_description: str | None = None
    eligibility: Eligibility | None = None
    outcomes: list[Outcome] = field(default_factory=list)
    design: StudyDesign | None = None
    results: bool = False
    documents: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def url(self) -> str:
        """URL to the study on ClinicalTrials.gov."""
        return f"https://clinicaltrials.gov/study/{self.nct_id}"

    def to_dict(self) -> dict:
        """Convert study to a plain dictionary.

        Dates are converted to ISO format strings. The raw API response
        is excluded.
        """
        d = asdict(self)
        d.pop("raw", None)
        d["url"] = self.url
        # Convert date objects to strings
        for key, value in d.items():
            if isinstance(value, date):
                d[key] = value.isoformat()
        return d

    def to_json(self) -> str:
        """Convert study to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
