"""Test fixtures with sample CT.gov API responses."""

import pytest

from clinicaltrials import ClinicalTrials


@pytest.fixture
def ct():
    """A ClinicalTrials client instance."""
    return ClinicalTrials()


@pytest.fixture
def sample_study_response():
    """A realistic (trimmed) CT.gov v2 API study response."""
    return {
        "protocolSection": {
            "identificationModule": {
                "nctId": "NCT06000696",
                "briefTitle": "Study of Drug X in Lung Cancer",
                "officialTitle": "A Phase 3 Randomized Study of Drug X vs Placebo in Advanced Non-Small Cell Lung Cancer",
            },
            "statusModule": {
                "overallStatus": "RECRUITING",
                "startDateStruct": {"date": "2023-06-15", "type": "ACTUAL"},
                "primaryCompletionDateStruct": {"date": "2025-12-01", "type": "ESTIMATED"},
                "completionDateStruct": {"date": "2026-06-01", "type": "ESTIMATED"},
                "studyFirstPostDateStruct": {"date": "2023-07-01", "type": "ACTUAL"},
                "lastUpdatePostDateStruct": {"date": "2024-01-15", "type": "ACTUAL"},
            },
            "designModule": {
                "studyType": "INTERVENTIONAL",
                "phases": ["PHASE3"],
                "enrollmentInfo": {"count": 500, "type": "ESTIMATED"},
                "designInfo": {
                    "allocation": "RANDOMIZED",
                    "interventionModel": "PARALLEL",
                    "primaryPurpose": "TREATMENT",
                    "maskingInfo": {
                        "masking": "DOUBLE",
                        "maskingDescription": "Double-blind study",
                    },
                },
            },
            "conditionsModule": {
                "conditions": ["Non-Small Cell Lung Cancer", "NSCLC"],
            },
            "armsInterventionsModule": {
                "interventions": [
                    {
                        "name": "Drug X",
                        "type": "DRUG",
                        "description": "Experimental drug X 200mg IV",
                    },
                    {
                        "name": "Placebo",
                        "type": "DRUG",
                        "description": "Matching placebo IV",
                    },
                ],
            },
            "sponsorCollaboratorsModule": {
                "leadSponsor": {"name": "Pharma Corp", "class": "INDUSTRY"},
                "collaborators": [
                    {"name": "National Cancer Institute", "class": "NIH"},
                ],
            },
            "descriptionModule": {
                "briefSummary": "This study evaluates Drug X in patients with advanced NSCLC.",
                "detailedDescription": "A detailed description of the study protocol.",
            },
            "eligibilityModule": {
                "eligibilityCriteria": "Inclusion: Age >= 18\nExclusion: Prior treatment",
                "sex": "ALL",
                "minimumAge": "18 Years",
                "maximumAge": "85 Years",
                "healthyVolunteers": "No",
            },
            "contactsLocationsModule": {
                "centralContacts": [
                    {
                        "name": "John Smith, MD",
                        "phone": "555-0100",
                        "email": "jsmith@example.com",
                    },
                ],
                "locations": [
                    {
                        "facility": "City Hospital",
                        "city": "Boston",
                        "state": "Massachusetts",
                        "country": "United States",
                        "status": "RECRUITING",
                    },
                    {
                        "facility": "University Medical Center",
                        "city": "New York",
                        "state": "New York",
                        "country": "United States",
                        "status": "RECRUITING",
                    },
                ],
            },
            "outcomesModule": {
                "primaryOutcomes": [
                    {
                        "measure": "Overall Survival",
                        "description": "Time from randomization to death",
                        "timeFrame": "Up to 36 months",
                    },
                ],
                "secondaryOutcomes": [
                    {
                        "measure": "Progression-Free Survival",
                        "description": "Time from randomization to progression",
                        "timeFrame": "Up to 24 months",
                    },
                ],
            },
        },
        "hasResults": False,
    }


@pytest.fixture
def minimal_study_response():
    """A minimal study response with many missing fields."""
    return {
        "protocolSection": {
            "identificationModule": {
                "nctId": "NCT00000001",
                "briefTitle": "Minimal Study",
            },
            "statusModule": {
                "overallStatus": "COMPLETED",
            },
        },
    }


@pytest.fixture
def sample_search_response(sample_study_response):
    """A sample search results response."""
    return {
        "studies": [sample_study_response],
        "totalCount": 1,
        "nextPageToken": None,
    }


@pytest.fixture
def paginated_search_response(sample_study_response):
    """Search response with pagination."""
    return {
        "studies": [sample_study_response],
        "totalCount": 2,
        "nextPageToken": "token_page2",
    }


@pytest.fixture
def second_page_response(minimal_study_response):
    """Second page of paginated results."""
    return {
        "studies": [minimal_study_response],
        "totalCount": 2,
        "nextPageToken": None,
    }
