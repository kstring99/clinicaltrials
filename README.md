# clinicaltrials

A Python library for the ClinicalTrials.gov API. Clean, Pythonic, and easy to use.

## Installation

```bash
pip install clinicaltrials
```

## Quick Start

```python
from clinicaltrials import ClinicalTrials

ct = ClinicalTrials()
trials = ct.search("pembrolizumab", phase=3, status="RECRUITING")

for trial in trials:
    print(f"{trial.nct_id}: {trial.title} (Phase {trial.phase})") 
```

## Features

- Zero config — no API key needed
- Clean data models — no nested dict diving
- Fluent search builder
- Pandas integration
- Automatic pagination and rate limiting
- Full type hints

## License

MIT
