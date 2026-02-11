# QA Agent MVP

AI-powered QA assistant designed to improve user story quality and automatically synchronize Gherkin test suites with evolving functional documentation.

This service provides two main capabilities:

1. User Story Quality Analysis
2. Autonomous Test Synchronization from Functional Documents (PDF, DOCX, TXT or raw text)

It is built with FastAPI and OpenAI models, includes strict schema validation, retry logic, JSON enforcement, and is ready to integrate into CI pipelines.

---

# FEATURES

1. User Story Analysis

Endpoint:
POST /analyze

Analyzes a user story and returns structured QA feedback including:

* Summary
* Risk level (LOW / MEDIUM / HIGH)
* Missing definitions
* Proposed acceptance criteria
* Edge cases
* Automation considerations

The output is strictly validated against a schema to ensure consistency.

---

2. Autonomous Test Synchronization

Endpoint:
POST /sync-tests

Accepts:

* PDF
* DOCX
* TXT
* Raw text input

The agent automatically decides whether to:

A) Generate an initial test suite (if no tests exist)
B) Evolve an existing suite (if tests already exist)

This makes the system a synchronization engine rather than a simple generator.

The process:

* Detects SCREEN sections
* Generates one Gherkin Feature per screen
* Generates structured Given / When / Then scenarios
* Modifies only impacted scenarios
* Marks obsolete scenarios as @deprecated
* Preserves unchanged tests
* Adds new features when required

All output is strictly validated against a JSON schema before being written to disk.

Generated files are saved in:

generated_tests/

The generated files are compatible with:

* Cucumber
* Behave
* SpecFlow
* CI pipelines

---

# DRY RUN MODE (VERY IMPORTANT)

The endpoint supports:

dry_run = true | false

If dry_run = true:

* The system generates the full updated test suite
* Returns the structured JSON response
* DOES NOT modify any .feature files
* Ideal for previewing changes safely

If dry_run = false:

* The test suite is written to disk
* Existing features are overwritten if modified
* New features are created
* Deprecated scenarios are marked accordingly

Recommended workflow:

1) First call with dry_run=true to inspect changes
2) If satisfied, call again with dry_run=false to apply changes

This prevents accidental overwrites and allows safe CI integration.

---

# REQUIREMENTS

* Python 3.9+
* OpenAI API key with billing enabled (If you know Pelicano, just ask him for it)

---

# INSTALLATION

1. Clone the repository

git clone <repository-url>
cd qa-agent-mvp

2. Create and activate a virtual environment

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

Make sure requirements.txt includes:

fastapi
uvicorn
openai
pydantic
faiss-cpu
numpy
pypdf
python-docx

4. Configure OpenAI API key

export OPENAI_API_KEY="your_api_key_here"  (If you know Pelicano, just ask him for it)

Never commit API keys to the repository.

---

# RUNNING THE SERVICE

Start the API server:

uvicorn api:app --reload

The service will run at:

http://127.0.0.1:8000

Swagger UI (interactive API documentation):

http://127.0.0.1:8000/docs

---

USAGE

A) Analyze a User Story

Go to /docs, select:

POST /analyze

Provide a JSON body like:

{
  "issue_id": "PROJ-101",
  "title": "User Registration",
  "description": "As a user, I want to register with email and password.",
  "acceptance_criteria": "User must be over 18 years old."
}

Execute the request to receive structured QA feedback.

---

B) Synchronize Tests with Functional Documentation

Go to /docs, select:

POST /sync-tests

You can:

1. Upload a PDF / DOCX / TXT file
OR
2. Paste text directly

Then choose dry_run:

* dry_run=true → preview changes only
* dry_run=false → apply changes to .feature files

The API will:

* Detect functional screens
* Generate or evolve Gherkin features
* Enforce strict Given / When / Then structure
* Validate output schema
* Save .feature files in:

generated_tests/

---

# GIT AND GENERATED FILES

The following are excluded from version control:

* generated_tests/
* .feature files
* RAG index files
* Virtual environments
* Environment variable files

Generated tests are considered build artifacts unless intentionally versioned.

---

# ARCHITECTURE NOTES

* Strict JSON schema validation for LLM output
* Automatic retry mechanism for malformed responses
* Single synchronization endpoint (no duplicated logic)
* Modular ingestion layer (PDF, DOCX, TXT, raw text)
* Tests are treated as the source of truth
* Evolution engine detects changes instead of regenerating blindly
* Ready for Jira / CI integration

---

# CURRENT STATUS

* Stable MVP
* Unified synchronization architecture
* Strict contract-based LLM interaction
* Gherkin-compliant output
* CI-ready test output
* Extensible ingestion pipeline

---

This project provides a foundation for a scalable AI-assisted QA workflow and intelligent automated test maintenance.
