"""Tests for the API response parser."""

from datetime import date

from clinicaltrials.parsers import parse_study


class TestParseStudy:
    def test_parses_full_response(self, sample_study_response):
        study = parse_study(sample_study_response)

        assert study.nct_id == "NCT06000696"
        assert study.brief_title == "Study of Drug X in Lung Cancer"
        assert "Phase 3 Randomized" in study.official_title
        assert study.title == study.official_title
        assert study.status == "RECRUITING"
        assert study.phase == "Phase 3"
        assert study.study_type == "INTERVENTIONAL"

    def test_parses_conditions(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert "Non-Small Cell Lung Cancer" in study.conditions
        assert "NSCLC" in study.conditions

    def test_parses_interventions(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert len(study.interventions) == 2
        assert study.interventions[0].name == "Drug X"
        assert study.interventions[0].type == "DRUG"
        assert study.interventions[1].name == "Placebo"

    def test_parses_sponsors(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert len(study.sponsors) == 2
        assert study.sponsors[0].name == "Pharma Corp"
        assert study.sponsors[0].role == "LEAD"
        assert study.sponsors[1].name == "National Cancer Institute"
        assert study.sponsors[1].role == "COLLABORATOR"

    def test_parses_enrollment(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert study.enrollment == 500
        assert study.enrollment_type == "ESTIMATED"

    def test_parses_dates(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert study.start_date == date(2023, 6, 15)
        assert study.primary_completion == date(2025, 12, 1)
        assert study.completion_date == date(2026, 6, 1)
        assert study.first_posted == date(2023, 7, 1)
        assert study.last_updated == date(2024, 1, 15)

    def test_parses_locations(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert len(study.locations) == 2
        assert study.locations[0].facility == "City Hospital"
        assert study.locations[0].city == "Boston"
        assert study.locations[0].country == "United States"

    def test_parses_contacts(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert len(study.contacts) >= 1
        assert study.contacts[0].name == "John Smith, MD"
        assert study.contacts[0].email == "jsmith@example.com"

    def test_parses_outcomes(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert len(study.outcomes) == 2
        primary = [o for o in study.outcomes if o.type == "PRIMARY"]
        secondary = [o for o in study.outcomes if o.type == "SECONDARY"]
        assert len(primary) == 1
        assert primary[0].measure == "Overall Survival"
        assert len(secondary) == 1
        assert secondary[0].measure == "Progression-Free Survival"

    def test_parses_eligibility(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert study.eligibility is not None
        assert "Age >= 18" in study.eligibility.criteria
        assert study.eligibility.gender == "ALL"
        assert study.eligibility.min_age == "18 Years"
        assert study.eligibility.max_age == "85 Years"
        assert study.eligibility.healthy_volunteers is False

    def test_parses_design(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert study.design is not None
        assert study.design.allocation == "RANDOMIZED"
        assert study.design.intervention_model == "PARALLEL"
        assert study.design.primary_purpose == "TREATMENT"
        assert study.design.masking == "DOUBLE"

    def test_parses_descriptions(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert "Drug X" in study.brief_summary
        assert study.detailed_description is not None

    def test_preserves_raw(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert study.raw is sample_study_response

    def test_url(self, sample_study_response):
        study = parse_study(sample_study_response)
        assert study.url == "https://clinicaltrials.gov/study/NCT06000696"


class TestParseMinimalStudy:
    def test_handles_missing_fields(self, minimal_study_response):
        study = parse_study(minimal_study_response)
        assert study.nct_id == "NCT00000001"
        assert study.brief_title == "Minimal Study"
        assert study.title == "Minimal Study"
        assert study.status == "COMPLETED"

    def test_missing_fields_default_to_none_or_empty(self, minimal_study_response):
        study = parse_study(minimal_study_response)
        assert study.phase is None
        assert study.study_type is None
        assert study.conditions == []
        assert study.interventions == []
        assert study.sponsors == []
        assert study.enrollment is None
        assert study.start_date is None
        assert study.locations == []
        assert study.contacts == []
        assert study.brief_summary is None
        assert study.eligibility is None
        assert study.outcomes == []
        assert study.design is None
        assert study.results is False


class TestParseEdgeCases:
    def test_empty_dict(self):
        study = parse_study({})
        assert study.nct_id == ""
        assert study.title == ""

    def test_multi_phase(self):
        data = {
            "protocolSection": {
                "identificationModule": {"nctId": "NCT00000001", "briefTitle": "Test"},
                "statusModule": {"overallStatus": "RECRUITING"},
                "designModule": {"phases": ["PHASE1", "PHASE2"]},
            }
        }
        study = parse_study(data)
        assert study.phase == "Phase 1 / Phase 2"

    def test_healthy_volunteers_yes(self):
        data = {
            "protocolSection": {
                "identificationModule": {"nctId": "NCT00000001", "briefTitle": "Test"},
                "statusModule": {"overallStatus": "RECRUITING"},
                "eligibilityModule": {"healthyVolunteers": "Yes"},
            }
        }
        study = parse_study(data)
        assert study.eligibility.healthy_volunteers is True
