"""Fluent search builder for CT.gov API queries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

from .models import Study
from .parsers import parse_study

if TYPE_CHECKING:
    from .client import ClinicalTrials


_PHASE_MAP = {
    1: "PHASE1",
    2: "PHASE2",
    3: "PHASE3",
    4: "PHASE4",
    0: "EARLY_PHASE1",
}


class SearchBuilder:
    """Fluent builder for constructing and executing CT.gov study searches.

    Use ClinicalTrials.search() to create a SearchBuilder instance rather
    than constructing one directly.

    Example::

        ct = ClinicalTrials()
        results = (ct.search()
            .condition("breast cancer")
            .phase(2, 3)
            .recruiting()
            .limit(10)
            .execute())
    """

    def __init__(self, client: ClinicalTrials):
        self._client = client
        self._params: dict[str, Any] = {}
        self._limit_value: int | None = None

    def _copy(self, **updates: Any) -> SearchBuilder:
        """Create a copy of this builder with additional params."""
        new = SearchBuilder(self._client)
        new._params = {**self._params, **updates}
        new._limit_value = self._limit_value
        return new

    def term(self, term: str) -> SearchBuilder:
        """Set general search term.

        Args:
            term: Free-text search query.
        """
        return self._copy(**{"query.term": term})

    def condition(self, cond: str) -> SearchBuilder:
        """Filter by condition or disease.

        Args:
            cond: Condition name (e.g., "diabetes", "lung cancer").
        """
        return self._copy(**{"query.cond": cond})

    def intervention(self, intr: str) -> SearchBuilder:
        """Filter by intervention or treatment.

        Args:
            intr: Intervention name (e.g., "pembrolizumab").
        """
        return self._copy(**{"query.intr": intr})

    def sponsor(self, spons: str) -> SearchBuilder:
        """Filter by sponsor or collaborator.

        Args:
            spons: Sponsor name (e.g., "Pfizer").
        """
        return self._copy(**{"query.spons": spons})

    def title(self, title: str) -> SearchBuilder:
        """Filter by study title.

        Args:
            title: Title search text.
        """
        return self._copy(**{"query.titles": title})

    def outcome(self, outc: str) -> SearchBuilder:
        """Filter by outcome measure.

        Args:
            outc: Outcome measure text.
        """
        return self._copy(**{"query.outc": outc})

    def lead_sponsor(self, lead: str) -> SearchBuilder:
        """Filter by lead sponsor.

        Args:
            lead: Lead sponsor name.
        """
        return self._copy(**{"query.lead": lead})

    def nct_id(self, *ids: str) -> SearchBuilder:
        """Filter by NCT ID(s).

        Args:
            *ids: One or more NCT IDs.
        """
        return self._copy(**{"query.id": ",".join(ids)})

    def phase(self, *phases: int) -> SearchBuilder:
        """Filter by trial phase(s).

        Args:
            *phases: Phase numbers (0 for Early Phase 1, 1-4 for Phases 1-4).
        """
        api_phases = []
        for p in phases:
            mapped = _PHASE_MAP.get(p)
            if mapped:
                api_phases.append(mapped)
        if not api_phases:
            return self
        if len(api_phases) == 1:
            phase_expr = f"AREA[Phase]{api_phases[0]}"
        else:
            phase_expr = "AREA[Phase](" + " OR ".join(api_phases) + ")"
        # Merge with existing filter.advanced if present
        existing = self._params.get("filter.advanced", "")
        if existing:
            combined = f"{existing} AND {phase_expr}"
        else:
            combined = phase_expr
        return self._copy(**{"filter.advanced": combined})

    def status(self, *statuses: str) -> SearchBuilder:
        """Filter by overall study status.

        Args:
            *statuses: Status values (e.g., "RECRUITING", "COMPLETED").
        """
        return self._copy(**{"filter.overallStatus": ",".join(statuses)})

    def recruiting(self) -> SearchBuilder:
        """Shortcut to filter for currently recruiting studies."""
        return self.status("RECRUITING")

    def completed(self) -> SearchBuilder:
        """Shortcut to filter for completed studies."""
        return self.status("COMPLETED")

    def fields(self, *field_names: str) -> SearchBuilder:
        """Specify which fields to return.

        Args:
            *field_names: Field names to include in results.
        """
        return self._copy(fields=",".join(field_names))

    def sort(self, field: str, desc: bool = False) -> SearchBuilder:
        """Set sort order for results.

        Args:
            field: Field name to sort by.
            desc: If True, sort descending.
        """
        direction = "desc" if desc else "asc"
        return self._copy(sort=f"{field}:{direction}")

    def limit(self, n: int) -> SearchBuilder:
        """Limit the number of results returned.

        Args:
            n: Maximum number of results.
        """
        new = self._copy()
        new._limit_value = n
        return new

    def near(self, lat: float, lon: float, radius_miles: int = 100) -> SearchBuilder:
        """Filter by geographic location.

        Args:
            lat: Latitude.
            lon: Longitude.
            radius_miles: Search radius in miles.
        """
        return self._copy(**{"filter.geo": f"distance({lat},{lon},{radius_miles}mi)"})

    def advanced_filter(self, expression: str) -> SearchBuilder:
        """Apply an advanced filter expression.

        Args:
            expression: CT.gov advanced filter expression.
        """
        existing = self._params.get("filter.advanced", "")
        if existing:
            combined = f"{existing} AND {expression}"
        else:
            combined = expression
        return self._copy(**{"filter.advanced": combined})

    def _build_params(self, page_size: int | None = None) -> dict[str, Any]:
        """Build the query params dict for the API request."""
        params = dict(self._params)
        params["format"] = "json"
        if page_size is not None:
            params["pageSize"] = page_size
        return params

    def _fetch_page(
        self, page_token: str | None = None, page_size: int = 20
    ) -> dict:
        """Fetch a single page of results."""
        params = self._build_params(page_size=page_size)
        if page_token:
            params["pageToken"] = page_token
        return self._client._request("GET", "/studies", params=params)

    def execute(self) -> list[Study]:
        """Execute the search and return a list of Study objects.

        Returns up to `limit` results (default: first page of 20).
        """
        limit = self._limit_value or 20
        page_size = min(limit, 1000)
        results: list[Study] = []

        page_token = None
        while len(results) < limit:
            remaining = limit - len(results)
            fetch_size = min(remaining, page_size)
            data = self._fetch_page(page_token=page_token, page_size=fetch_size)

            studies = data.get("studies", [])
            if not studies:
                break

            for study_data in studies:
                results.append(parse_study(study_data))
                if len(results) >= limit:
                    break

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return results

    def all(self) -> list[Study]:
        """Fetch ALL matching results, handling pagination automatically.

        Warning: This may make many API requests for broad queries.

        Returns:
            List of all matching Study objects.
        """
        results: list[Study] = []
        page_token = None

        while True:
            data = self._fetch_page(page_token=page_token, page_size=1000)
            studies = data.get("studies", [])
            if not studies:
                break
            results.extend(parse_study(s) for s in studies)
            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return results

    def first(self) -> Study | None:
        """Get the first matching result, or None if no results.

        Returns:
            The first Study, or None.
        """
        data = self._fetch_page(page_size=1)
        studies = data.get("studies", [])
        if not studies:
            return None
        return parse_study(studies[0])

    def count(self) -> int:
        """Count matching studies without fetching full results.

        Returns:
            The number of matching studies.
        """
        params = self._build_params(page_size=0)
        params["countTotal"] = "true"
        data = self._client._request("GET", "/studies", params=params)
        return data.get("totalCount", 0)

    def to_dataframe(self):
        """Return results as a pandas DataFrame.

        Requires pandas to be installed.

        Returns:
            A pandas DataFrame with one row per study.

        Raises:
            ImportError: If pandas is not installed.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install it with: pip install clinicaltrials[pandas]"
            )
        studies = self.execute()
        return pd.DataFrame([s.to_dict() for s in studies])

    def __iter__(self) -> Iterator[Study]:
        """Iterate over results with lazy pagination."""
        page_token = None
        count = 0
        limit = self._limit_value

        while True:
            data = self._fetch_page(page_token=page_token, page_size=1000)
            studies = data.get("studies", [])
            if not studies:
                break
            for study_data in studies:
                yield parse_study(study_data)
                count += 1
                if limit and count >= limit:
                    return
            page_token = data.get("nextPageToken")
            if not page_token:
                break

    def __len__(self) -> int:
        """Return the count of matching studies."""
        return self.count()
