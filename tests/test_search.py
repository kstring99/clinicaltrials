"""Tests for the SearchBuilder."""

import responses

from clinicaltrials import ClinicalTrials
from clinicaltrials.client import BASE_URL


class TestSearchBuilder:
    def test_chaining_returns_new_builder(self, ct):
        builder1 = ct.search()
        builder2 = builder1.condition("cancer")
        assert builder1 is not builder2
        assert builder1._params != builder2._params

    def test_condition(self, ct):
        builder = ct.search().condition("diabetes")
        assert builder._params["query.cond"] == "diabetes"

    def test_intervention(self, ct):
        builder = ct.search().intervention("pembrolizumab")
        assert builder._params["query.intr"] == "pembrolizumab"

    def test_sponsor(self, ct):
        builder = ct.search().sponsor("Pfizer")
        assert builder._params["query.spons"] == "Pfizer"

    def test_title(self, ct):
        builder = ct.search().title("lung cancer")
        assert builder._params["query.titles"] == "lung cancer"

    def test_phase(self, ct):
        builder = ct.search().phase(2, 3)
        advanced = builder._params["filter.advanced"]
        assert "PHASE2" in advanced
        assert "PHASE3" in advanced

    def test_status(self, ct):
        builder = ct.search().status("RECRUITING", "COMPLETED")
        assert builder._params["filter.overallStatus"] == "RECRUITING,COMPLETED"

    def test_recruiting_shortcut(self, ct):
        builder = ct.search().recruiting()
        assert builder._params["filter.overallStatus"] == "RECRUITING"

    def test_completed_shortcut(self, ct):
        builder = ct.search().completed()
        assert builder._params["filter.overallStatus"] == "COMPLETED"

    def test_near(self, ct):
        builder = ct.search().near(42.36, -71.06, 50)
        assert "distance(42.36,-71.06,50mi)" in builder._params["filter.geo"]

    def test_sort(self, ct):
        builder = ct.search().sort("LastUpdatePostDate", desc=True)
        assert builder._params["sort"] == "LastUpdatePostDate:desc"

    def test_limit(self, ct):
        builder = ct.search().limit(5)
        assert builder._limit_value == 5

    def test_fields(self, ct):
        builder = ct.search().fields("NCTId", "BriefTitle")
        assert builder._params["fields"] == "NCTId,BriefTitle"

    def test_advanced_filter(self, ct):
        builder = ct.search().advanced_filter("AREA[Phase]PHASE3")
        assert builder._params["filter.advanced"] == "AREA[Phase]PHASE3"


class TestSearchExecution:
    @responses.activate
    def test_execute(self, ct, sample_search_response):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json=sample_search_response,
            status=200,
        )
        results = ct.search().condition("cancer").execute()
        assert len(results) == 1
        assert results[0].nct_id == "NCT06000696"

    @responses.activate
    def test_first(self, ct, sample_search_response):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json=sample_search_response,
            status=200,
        )
        study = ct.search().condition("cancer").first()
        assert study is not None
        assert study.nct_id == "NCT06000696"

    @responses.activate
    def test_first_no_results(self, ct):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json={"studies": [], "totalCount": 0},
            status=200,
        )
        study = ct.search().condition("zzzzzznotreal").first()
        assert study is None

    @responses.activate
    def test_count(self, ct):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json={"totalCount": 150, "studies": []},
            status=200,
        )
        count = ct.search().condition("cancer").count()
        assert count == 150

    @responses.activate
    def test_len(self, ct):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json={"totalCount": 42, "studies": []},
            status=200,
        )
        builder = ct.search().condition("cancer")
        assert len(builder) == 42

    @responses.activate
    def test_iter(self, ct, sample_search_response):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json=sample_search_response,
            status=200,
        )
        studies = list(ct.search().condition("cancer"))
        assert len(studies) == 1


class TestPagination:
    @responses.activate
    def test_all_paginates(
        self, ct, paginated_search_response, second_page_response
    ):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json=paginated_search_response,
            status=200,
        )
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json=second_page_response,
            status=200,
        )
        results = ct.search().condition("cancer").all()
        assert len(results) == 2
        assert results[0].nct_id == "NCT06000696"
        assert results[1].nct_id == "NCT00000001"
        assert len(responses.calls) == 2

    @responses.activate
    def test_execute_respects_limit(self, ct, sample_search_response):
        responses.add(
            responses.GET,
            f"{BASE_URL}/studies",
            json=sample_search_response,
            status=200,
        )
        results = ct.search().condition("cancer").limit(1).execute()
        assert len(results) == 1
