"""Tests for data models."""

import json
from datetime import date

from clinicaltrials.models import Study, Intervention, Sponsor, Location


class TestStudy:
    def test_url_property(self):
        study = Study(nct_id="NCT12345678", title="Test Study")
        assert study.url == "https://clinicaltrials.gov/study/NCT12345678"

    def test_to_dict_excludes_raw(self):
        study = Study(nct_id="NCT12345678", title="Test", raw={"big": "data"})
        d = study.to_dict()
        assert "raw" not in d
        assert d["nct_id"] == "NCT12345678"
        assert d["url"] == "https://clinicaltrials.gov/study/NCT12345678"

    def test_to_dict_converts_dates(self):
        study = Study(
            nct_id="NCT12345678",
            title="Test",
            start_date=date(2024, 1, 15),
        )
        d = study.to_dict()
        assert d["start_date"] == "2024-01-15"

    def test_to_json(self):
        study = Study(nct_id="NCT12345678", title="Test Study")
        j = study.to_json()
        parsed = json.loads(j)
        assert parsed["nct_id"] == "NCT12345678"
        assert parsed["title"] == "Test Study"

    def test_defaults(self):
        study = Study(nct_id="NCT12345678", title="Test")
        assert study.conditions == []
        assert study.interventions == []
        assert study.sponsors == []
        assert study.locations == []
        assert study.contacts == []
        assert study.outcomes == []
        assert study.documents == []
        assert study.status == ""
        assert study.phase is None
        assert study.enrollment is None
        assert study.results is False
        assert study.raw == {}


class TestIntervention:
    def test_creation(self):
        i = Intervention(name="Drug X", type="DRUG", description="Test drug")
        assert i.name == "Drug X"
        assert i.type == "DRUG"
        assert i.description == "Test drug"

    def test_optional_description(self):
        i = Intervention(name="Drug X", type="DRUG")
        assert i.description is None


class TestSponsor:
    def test_creation(self):
        s = Sponsor(name="Pharma Corp", role="LEAD")
        assert s.name == "Pharma Corp"
        assert s.role == "LEAD"


class TestLocation:
    def test_all_fields(self):
        loc = Location(
            facility="Hospital",
            city="Boston",
            state="MA",
            country="United States",
            status="RECRUITING",
        )
        assert loc.facility == "Hospital"
        assert loc.country == "United States"

    def test_defaults(self):
        loc = Location()
        assert loc.facility is None
        assert loc.city is None
