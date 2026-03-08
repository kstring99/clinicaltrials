"""Tests for the ClinicalTrials client."""

import pytest
import responses

from clinicaltrials import ClinicalTrials
from clinicaltrials.client import BASE_URL
from clinicaltrials.exceptions import NotFoundError, RateLimitError, ClinicalTrialsError


class TestGet:
    @responses.activate
    def test_get_study(self, ct, sample_study_response):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies/NCT06000696",
            json=sample_study_response,
            status=200,
        )
        study = ct.get("NCT06000696")
        assert study.nct_id == "NCT06000696"
        assert study.status == "RECRUITING"

    @responses.activate
    def test_get_study_case_insensitive(self, ct, sample_study_response):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies/NCT06000696",
            json=sample_study_response,
            status=200,
        )
        study = ct.get("nct06000696")
        assert study.nct_id == "NCT06000696"

    def test_get_invalid_nct_id(self, ct):
        with pytest.raises(ValueError, match="Invalid NCT ID"):
            ct.get("INVALID")

    @responses.activate
    def test_get_not_found(self, ct):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies/NCT99999999",
            json={"error": "not found"},
            status=404,
        )
        with pytest.raises(NotFoundError):
            ct.get("NCT99999999")


class TestErrorHandling:
    @responses.activate
    def test_rate_limit_error(self):
        ct = ClinicalTrials(max_retries=0)
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies/NCT06000696",
            json={"error": "rate limited"},
            status=429,
        )
        with pytest.raises(RateLimitError):
            ct.get("NCT06000696")

    @responses.activate
    def test_server_error_retries(self):
        ct = ClinicalTrials(max_retries=1, rate_limit=0)
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies/NCT06000696",
            json={"error": "server error"},
            status=500,
        )
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies/NCT06000696",
            json={
                "protocolSection": {
                    "identificationModule": {
                        "nctId": "NCT06000696",
                        "briefTitle": "Test",
                    },
                    "statusModule": {"overallStatus": "RECRUITING"},
                }
            },
            status=200,
        )
        study = ct.get("NCT06000696")
        assert study.nct_id == "NCT06000696"

    @responses.activate
    def test_client_error(self):
        ct = ClinicalTrials(max_retries=0)
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies/NCT06000696",
            json={"error": "bad request"},
            status=400,
        )
        with pytest.raises(ClinicalTrialsError):
            ct.get("NCT06000696")


class TestFieldValues:
    @responses.activate
    def test_field_values(self, ct):
        responses.add(
            responses.GET,
            f"{BASE_URL}/stats/fieldValues/OverallStatus",
            json={"values": ["RECRUITING", "COMPLETED", "ACTIVE_NOT_RECRUITING"]},
            status=200,
        )
        values = ct.field_values("OverallStatus")
        assert "RECRUITING" in values
        assert "COMPLETED" in values


class TestApiVersion:
    @responses.activate
    def test_api_version(self, ct):
        responses.add(
            responses.GET,
            f"{BASE_URL}/version",
            json={"version": "2.0.0"},
            status=200,
        )
        version = ct.api_version()
        assert version == "2.0.0"


class TestTotalCount:
    @responses.activate
    def test_total_count(self, ct):
        responses.add(
            responses.GET,
            f"{BASE_URL}/stats/size",
            json={"totalStudies": 500000},
            status=200,
        )
        count = ct.total_count()
        assert count == 500000


class TestSearchShortcuts:
    @responses.activate
    def test_search_with_query(self, ct, sample_search_response):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json=sample_search_response,
            status=200,
        )
        results = ct.search("lung cancer").execute()
        assert len(results) == 1
        assert "query.term" in responses.calls[0].request.url

    @responses.activate
    def test_count_shortcut(self, ct):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json={"totalCount": 42, "studies": []},
            status=200,
        )
        count = ct.count("diabetes")
        assert count == 42
