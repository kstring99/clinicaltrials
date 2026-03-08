"""Field constants and presets for CT.gov API queries."""

# Core identification and status fields
CORE_FIELDS = [
    "NCTId",
    "BriefTitle",
    "OfficialTitle",
    "OverallStatus",
    "Phase",
    "StudyType",
    "EnrollmentCount",
    "EnrollmentType",
    "StartDate",
    "PrimaryCompletionDate",
    "CompletionDate",
    "StudyFirstPostDate",
    "LastUpdatePostDate",
    "BriefSummary",
    "HasResults",
]

# Fields for conditions and interventions
CONDITION_FIELDS = [
    "Condition",
    "InterventionName",
    "InterventionType",
    "InterventionDescription",
]

# Sponsor fields
SPONSOR_FIELDS = [
    "LeadSponsorName",
    "CollaboratorName",
]

# Location fields
LOCATION_FIELDS = [
    "LocationFacility",
    "LocationCity",
    "LocationState",
    "LocationCountry",
    "LocationStatus",
]

# Eligibility fields
ELIGIBILITY_FIELDS = [
    "EligibilityCriteria",
    "Gender",
    "MinimumAge",
    "MaximumAge",
    "HealthyVolunteers",
]

# Design fields
DESIGN_FIELDS = [
    "DesignAllocation",
    "DesignInterventionModel",
    "DesignPrimaryPurpose",
    "DesignMasking",
    "DesignMaskingDescription",
]

# Outcome fields
OUTCOME_FIELDS = [
    "PrimaryOutcomeMeasure",
    "PrimaryOutcomeDescription",
    "PrimaryOutcomeTimeFrame",
    "SecondaryOutcomeMeasure",
    "SecondaryOutcomeDescription",
    "SecondaryOutcomeTimeFrame",
]

# All commonly useful fields combined
ALL_FIELDS = (
    CORE_FIELDS
    + CONDITION_FIELDS
    + SPONSOR_FIELDS
    + LOCATION_FIELDS
    + ELIGIBILITY_FIELDS
    + DESIGN_FIELDS
    + OUTCOME_FIELDS
    + [
        "DetailedDescription",
        "ContactName",
        "ContactPhone",
        "ContactEMail",
    ]
)
