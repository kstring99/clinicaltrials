"""Utility functions for the clinicaltrials library."""

import re
from datetime import date


_NCT_PATTERN = re.compile(r"^NCT\d{8}$")


def validate_nct_id(nct_id: str) -> str:
    """Validate and normalize an NCT ID.

    Args:
        nct_id: An NCT identifier (e.g., "NCT12345678" or "nct12345678").

    Returns:
        The uppercase NCT ID.

    Raises:
        ValueError: If the NCT ID format is invalid.
    """
    nct_id = nct_id.strip().upper()
    if not _NCT_PATTERN.match(nct_id):
        raise ValueError(
            f"Invalid NCT ID: {nct_id!r}. Expected format: NCT followed by 8 digits."
        )
    return nct_id


def parse_api_date(date_value: str | dict | None) -> date | None:
    """Parse a date from the CT.gov API response.

    The API returns dates in various formats:
    - As a string: "2024-01-15" or "January 15, 2024" or "January 2024"
    - As a dict: {"date": "2024-01-15", "type": "ACTUAL"}

    Args:
        date_value: The date value from the API response.

    Returns:
        A date object, or None if parsing fails.
    """
    if date_value is None:
        return None

    if isinstance(date_value, dict):
        date_value = date_value.get("date")
        if date_value is None:
            return None

    if not isinstance(date_value, str):
        return None

    # Try ISO format: "2024-01-15"
    try:
        return date.fromisoformat(date_value)
    except ValueError:
        pass

    # Try "Month Day, Year": "January 15, 2024"
    try:
        from datetime import datetime

        return datetime.strptime(date_value, "%B %d, %Y").date()
    except ValueError:
        pass

    # Try "Month Year": "January 2024" (set day to 1)
    try:
        from datetime import datetime

        return datetime.strptime(date_value, "%B %Y").date()
    except ValueError:
        pass

    return None


def normalize_phase(phase: str | None) -> str | None:
    """Normalize phase strings from the API.

    Converts API format (e.g., "PHASE1") to display format (e.g., "Phase 1").

    Args:
        phase: The phase string from the API.

    Returns:
        A normalized phase string, or None.
    """
    if phase is None:
        return None

    phase_map = {
        "EARLY_PHASE1": "Early Phase 1",
        "PHASE1": "Phase 1",
        "PHASE2": "Phase 2",
        "PHASE3": "Phase 3",
        "PHASE4": "Phase 4",
        "NA": "N/A",
    }
    return phase_map.get(phase, phase)
