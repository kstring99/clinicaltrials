"""Parse CT.gov v2 API responses into clean data models."""

from __future__ import annotations

from .models import (
    Study,
    Intervention,
    Sponsor,
    Location,
    Contact,
    Outcome,
    Eligibility,
    StudyDesign,
)
from .utils import parse_api_date, normalize_phase


def _get(data: dict, *keys, default=None):
    """Safely navigate nested dicts."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _parse_interventions(data: dict) -> list[Intervention]:
    """Parse interventions from armsInterventionsModule."""
    module = _get(data, "protocolSection", "armsInterventionsModule")
    if not module:
        return []
    items = module.get("interventions", [])
    return [
        Intervention(
            name=item.get("name", ""),
            type=item.get("type", ""),
            description=item.get("description"),
        )
        for item in items
    ]


def _parse_sponsors(data: dict) -> list[Sponsor]:
    """Parse sponsors from sponsorCollaboratorsModule."""
    module = _get(data, "protocolSection", "sponsorCollaboratorsModule")
    if not module:
        return []
    sponsors = []
    lead = module.get("leadSponsor")
    if lead:
        sponsors.append(Sponsor(name=lead.get("name", ""), role="LEAD"))
    for collab in module.get("collaborators", []):
        sponsors.append(Sponsor(name=collab.get("name", ""), role="COLLABORATOR"))
    return sponsors


def _parse_locations(data: dict) -> list[Location]:
    """Parse locations from contactsLocationsModule."""
    module = _get(data, "protocolSection", "contactsLocationsModule")
    if not module:
        return []
    items = module.get("locations", [])
    return [
        Location(
            facility=loc.get("facility"),
            city=loc.get("city"),
            state=loc.get("state"),
            country=loc.get("country"),
            status=loc.get("status"),
        )
        for loc in items
    ]


def _parse_contacts(data: dict) -> list[Contact]:
    """Parse contacts from contactsLocationsModule."""
    module = _get(data, "protocolSection", "contactsLocationsModule")
    if not module:
        return []
    contacts = []
    for key in ("centralContacts", "overallOfficials"):
        for item in module.get(key, []):
            contacts.append(
                Contact(
                    name=item.get("name"),
                    phone=item.get("phone"),
                    email=item.get("email"),
                )
            )
    return contacts


def _parse_outcomes(data: dict) -> list[Outcome]:
    """Parse outcomes from outcomesModule."""
    module = _get(data, "protocolSection", "outcomesModule")
    if not module:
        return []
    outcomes = []
    for item in module.get("primaryOutcomes", []):
        outcomes.append(
            Outcome(
                measure=item.get("measure", ""),
                description=item.get("description"),
                time_frame=item.get("timeFrame"),
                type="PRIMARY",
            )
        )
    for item in module.get("secondaryOutcomes", []):
        outcomes.append(
            Outcome(
                measure=item.get("measure", ""),
                description=item.get("description"),
                time_frame=item.get("timeFrame"),
                type="SECONDARY",
            )
        )
    return outcomes


def _parse_eligibility(data: dict) -> Eligibility | None:
    """Parse eligibility from eligibilityModule."""
    module = _get(data, "protocolSection", "eligibilityModule")
    if not module:
        return None
    healthy = module.get("healthyVolunteers")
    if isinstance(healthy, str):
        healthy = healthy.upper() == "YES"
    return Eligibility(
        criteria=module.get("eligibilityCriteria"),
        gender=module.get("sex"),
        min_age=module.get("minimumAge"),
        max_age=module.get("maximumAge"),
        healthy_volunteers=healthy,
    )


def _parse_design(data: dict) -> StudyDesign | None:
    """Parse study design from designModule."""
    module = _get(data, "protocolSection", "designModule")
    if not module:
        return None
    design_info = module.get("designInfo", {})
    if not design_info:
        return None
    masking_info = design_info.get("maskingInfo", {})
    return StudyDesign(
        allocation=design_info.get("allocation"),
        intervention_model=design_info.get("interventionModel"),
        primary_purpose=design_info.get("primaryPurpose"),
        masking=masking_info.get("masking") if masking_info else None,
        masking_description=(
            masking_info.get("maskingDescription") if masking_info else None
        ),
    )


def _parse_phases(data: dict) -> str | None:
    """Parse and normalize phase list."""
    module = _get(data, "protocolSection", "designModule")
    if not module:
        return None
    phases = module.get("phases", [])
    if not phases:
        return None
    # Normalize each phase and join with " / " for multi-phase trials
    normalized = [normalize_phase(p) for p in phases]
    return " / ".join(p for p in normalized if p)


def parse_study(data: dict) -> Study:
    """Parse a full CT.gov v2 API study response into a Study object.

    Handles missing/null fields gracefully throughout.

    Args:
        data: The raw study dict from the API response.

    Returns:
        A populated Study dataclass.
    """
    id_module = _get(data, "protocolSection", "identificationModule") or {}
    status_module = _get(data, "protocolSection", "statusModule") or {}
    design_module = _get(data, "protocolSection", "designModule") or {}
    desc_module = _get(data, "protocolSection", "descriptionModule") or {}
    conditions_module = _get(data, "protocolSection", "conditionsModule") or {}
    enrollment_info = design_module.get("enrollmentInfo", {}) or {}

    nct_id = id_module.get("nctId", "")
    brief_title = id_module.get("briefTitle")
    official_title = id_module.get("officialTitle")
    title = official_title or brief_title or nct_id

    return Study(
        nct_id=nct_id,
        title=title,
        brief_title=brief_title,
        official_title=official_title,
        status=status_module.get("overallStatus", ""),
        phase=_parse_phases(data),
        study_type=design_module.get("studyType"),
        conditions=conditions_module.get("conditions", []),
        interventions=_parse_interventions(data),
        sponsors=_parse_sponsors(data),
        enrollment=enrollment_info.get("count"),
        enrollment_type=enrollment_info.get("type"),
        start_date=parse_api_date(status_module.get("startDateStruct")),
        primary_completion=parse_api_date(
            status_module.get("primaryCompletionDateStruct")
        ),
        completion_date=parse_api_date(status_module.get("completionDateStruct")),
        first_posted=parse_api_date(status_module.get("studyFirstPostDateStruct")),
        last_updated=parse_api_date(status_module.get("lastUpdatePostDateStruct")),
        locations=_parse_locations(data),
        contacts=_parse_contacts(data),
        brief_summary=desc_module.get("briefSummary"),
        detailed_description=desc_module.get("detailedDescription"),
        eligibility=_parse_eligibility(data),
        outcomes=_parse_outcomes(data),
        design=_parse_design(data),
        results=_get(data, "hasResults", default=False) or False,
        documents=[],
        raw=data,
    )
