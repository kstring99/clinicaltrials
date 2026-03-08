# clinicaltrials

A Python library for the ClinicalTrials.gov API. Clean, Pythonic, and easy to use.

Wraps the [ClinicalTrials.gov v2 API](https://clinicaltrials.gov/data-api/api) with clean data models, a fluent search builder, and automatic pagination -- no API key required.

## Installation

```bash
pip install clinicaltrials
```

With pandas support:

```bash
pip install clinicaltrials[pandas]
```

## Quick Start

```python
from clinicaltrials import ClinicalTrials

ct = ClinicalTrials()

# Fetch a single study
study = ct.get("NCT06000696")
print(study.title)
print(study.status)       # "RECRUITING"
print(study.phase)        # "Phase 3"
print(study.enrollment)   # 500

# Search for studies
results = ct.search("pembrolizumab").limit(10).execute()
for trial in results:
    print(f"{trial.nct_id}: {trial.title}")
```

## Search Builder

The fluent search builder lets you construct queries step by step:

```python
ct = ClinicalTrials()

# Chain filters together
results = (ct.search()
    .condition("breast cancer")
    .intervention("pembrolizumab")
    .phase(2, 3)
    .recruiting()
    .limit(50)
    .execute())

# Shortcuts for common statuses
results = ct.search().condition("diabetes").completed().execute()
results = ct.search().condition("NSCLC").recruiting().execute()

# Geographic filtering
results = (ct.search()
    .condition("lung cancer")
    .recruiting()
    .near(42.36, -71.06, radius_miles=50)  # Near Boston
    .execute())

# Get just the first result
study = ct.search().condition("alzheimer").first()

# Count matching studies without fetching
count = ct.search().condition("covid-19").recruiting().count()

# Fetch ALL results (handles pagination)
all_studies = ct.search().condition("rare disease").completed().all()

# Iterate lazily (paginated behind the scenes)
for study in ct.search().condition("cancer").phase(3).recruiting():
    print(study.nct_id, study.title)
```

### Available Filters

| Method | Description |
|---|---|
| `.condition(str)` | Filter by condition/disease |
| `.intervention(str)` | Filter by intervention/treatment |
| `.sponsor(str)` | Filter by sponsor/collaborator |
| `.lead_sponsor(str)` | Filter by lead sponsor |
| `.title(str)` | Search study titles |
| `.term(str)` | General search term |
| `.outcome(str)` | Filter by outcome measure |
| `.nct_id(*ids)` | Filter by NCT ID(s) |
| `.phase(*ints)` | Filter by phase (0=Early Phase 1, 1-4) |
| `.status(*strs)` | Filter by status (RECRUITING, COMPLETED, etc.) |
| `.recruiting()` | Shortcut for `.status("RECRUITING")` |
| `.completed()` | Shortcut for `.status("COMPLETED")` |
| `.near(lat, lon, radius)` | Geographic proximity filter |
| `.fields(*strs)` | Select specific fields to return |
| `.sort(field, desc=bool)` | Sort results |
| `.limit(n)` | Limit number of results |
| `.advanced_filter(str)` | Raw CT.gov advanced filter expression |

### Execution Methods

| Method | Returns |
|---|---|
| `.execute()` | `list[Study]` -- up to `limit` results |
| `.all()` | `list[Study]` -- all results (auto-paginates) |
| `.first()` | `Study \| None` -- first result |
| `.count()` | `int` -- count without fetching |
| `.to_dataframe()` | `pd.DataFrame` -- requires pandas |

## Study Model

Every search result is a `Study` dataclass with clean, typed fields:

```python
study = ct.get("NCT06000696")

# Basic info
study.nct_id           # "NCT06000696"
study.title            # Official title (or brief title if no official)
study.brief_title      # Short title
study.official_title   # Full official title
study.status           # "RECRUITING"
study.phase            # "Phase 3"
study.study_type       # "INTERVENTIONAL"
study.url              # "https://clinicaltrials.gov/study/NCT06000696"

# Enrollment
study.enrollment       # 500
study.enrollment_type  # "ESTIMATED"

# Dates (datetime.date objects)
study.start_date
study.completion_date
study.primary_completion
study.first_posted
study.last_updated

# Lists of dataclasses
study.conditions       # ["Non-Small Cell Lung Cancer", "NSCLC"]
study.interventions    # [Intervention(name="Drug X", type="DRUG", ...)]
study.sponsors         # [Sponsor(name="Pharma Corp", role="LEAD")]
study.locations        # [Location(facility="...", city="Boston", ...)]
study.contacts         # [Contact(name="...", email="...", phone="...")]
study.outcomes         # [Outcome(measure="Overall Survival", type="PRIMARY")]

# Eligibility
study.eligibility.criteria
study.eligibility.min_age    # "18 Years"
study.eligibility.max_age    # "85 Years"
study.eligibility.gender     # "ALL"

# Study design
study.design.allocation          # "RANDOMIZED"
study.design.intervention_model  # "PARALLEL"
study.design.masking             # "DOUBLE"

# Descriptions
study.brief_summary
study.detailed_description

# Serialization
study.to_dict()   # Plain dict (dates as ISO strings, no raw data)
study.to_json()   # JSON string

# Power users: access the raw API response
study.raw
```

## Pandas Integration

```python
df = (ct.search()
    .condition("breast cancer")
    .phase(3)
    .recruiting()
    .limit(100)
    .to_dataframe())

print(df[["nct_id", "title", "enrollment", "status"]])
```

Requires pandas: `pip install clinicaltrials[pandas]`

## Client Options

```python
ct = ClinicalTrials(
    max_retries=3,     # Retries on 429/5xx errors (default: 3)
    rate_limit=10,     # Max requests per second (default: 10)
)
```

## Utility Methods

```python
# Total studies on ClinicalTrials.gov
ct.total_count()

# Valid values for a field
ct.field_values("OverallStatus")
# ["RECRUITING", "COMPLETED", "ACTIVE_NOT_RECRUITING", ...]

# API version
ct.api_version()
```

## Error Handling

```python
from clinicaltrials import ClinicalTrials, NotFoundError, RateLimitError

ct = ClinicalTrials()

try:
    study = ct.get("NCT99999999")
except NotFoundError:
    print("Study not found")
except RateLimitError:
    print("Rate limited -- slow down")
```

## Development

```bash
git clone https://github.com/kstring99/clinicaltrials.git
cd clinicaltrials
pip install -e ".[dev]"
pytest
```

## License

MIT
