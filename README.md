# SteelEye Data Engineer Technical Assessment

ETL pipeline that downloads financial instrument data from ESMA,
transforms it and stores it in cloud storage.

## Installation

Requirements: Python 3.12+, uv

```bash
git clone https://github.com/jordan21pt/dataTechnicalSE.git
cd dataTechnicalSE
uv sync
```

## Usage

```bash
uv run python -m datatechnicalse.main
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ESMA_URL` | ESMA registry URL | default ESMA URL |
| `OUTPUT_PATH` | Output path (local or cloud) | `/tmp/output.csv` |

It uses default values if env vars do not exist.

Examples:
```bash
# Local
OUTPUT_PATH=/tmp/output.csv uv run python -m datatechnicalse.main

# S3
OUTPUT_PATH=s3://bucket/output.csv uv run python -m datatechnicalse.main

# Azure
OUTPUT_PATH=az://container/output.csv uv run python -m datatechnicalse.main
```

Did not run the cloud provider option,because I don't have valid credentials. But it worked well on my local machine

## Running Tests

```bash
uv run pytest --cov=datatechnicalse
```

## Project Structure
src/datatechnicalse/
   - downloader.py # Downloads XML and ZIP from ESMA
   - parser.py # Extracts XML from ZIP and converts to DataFrame
   - transformer.py # Adds a_count and contains_a columns
   - storage.py # Saves CSV to cloud storage via fsspec or to local machine on memory
   - main.py # Pipeline entrypoint

## Tech Stack

- Python 3.12
- Pandas
- fsspec / s3fs / adlfs
- pytest
- Ruff, Black, mypy

## Design Decisions

**In-memory processing** -- the ZIP and XML are processed in memory 
without writing to disk, keeping the pipeline simple and fast. It could
start using the disk if the size of the files would become to big that we risk
getting the ram full, but for this assignment is completly fine.

**Cloud-agnostic storage** -- fsspec abstracts the storage backend.
The same code works for local, S3 and Azure by changing the 
OUTPUT_PATH environment variable.

**OOP structure** -- each class has a single responsibility:
- `WebClient` -- generic HTTP client
- `ESMADownloader` -- ESMA-specific download logic
- `XMLParser` -- XML to DataFrame conversion
- `DataTransformer` -- business logic transformations
- `Storage` -- cloud-agnostic persistence

**CICD Pipeline** 
GitHub Actions runs the same checks as the pre-commit 
hooks (Ruff, Black, mypy, pytest) on every push and pull request. 
Code only reaches main after passing all checks, ensuring consistency
across environments.

**Code Quality** -- Ruff and Black enforce PEP 8 and formatting automatically
via pre-commit hooks. mypy ensures type safety. All checks run on every
commit locally and on every push via GitHub Actions.