# QA Agent MVP

AI-powered QA assistant designed to improve user story quality and automatically generate Gherkin test suites from functional documentation.

This service provides two main capabilities:

1. User Story Quality Analysis
2. Automatic Test Generation from PDF Specifications

It is built with FastAPI and OpenAI models, includes schema validation, retry logic, and is ready to integrate into CI pipelines.

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

2. Test Generation from PDF

Endpoint:
POST /generate-tests-pdf

Accepts a functional specification in PDF format and automatically:

* Detects distinct functional areas
* Generates one Gherkin Feature per area
* Generates multiple realistic Scenarios per feature
* Saves .feature files to:

generated_tests/

The generated files are compatible with:

* Cucumber
* Behave
* SpecFlow
* CI pipelines

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

4. Configure OpenAI API key

export OPENAI_API_KEY="your_api_key_here"  (If you know Pelicano, just ask him for it)

Never commit API keys to the repository.

---

# RUNNING THE SERVICE

Start the API server:

uvicorn api:app --reload

The service will run at:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

Swagger UI (interactive API documentation):

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

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

B) Generate Tests from a PDF

Go to /docs, select:

POST /generate-tests-pdf

1. Click "Try it out"
2. Upload a functional specification PDF
3. Execute

The API will:

* Process the document
* Generate structured test definitions
* Create .feature files in:

generated_tests/

You can immediately integrate these files into your automation framework.

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
* Retry mechanism for malformed responses
* Modular ingestion layer (JSON, PDF)
* Designed for future multi-tenant SaaS architecture
* Ready for Jira / CI integration

---

# CURRENT STATUS

* Stable MVP
* Production-structured
* CI-ready test output
* Extensible ingestion pipeline

---

This project provides a foundation for a scalable AI-assisted QA workflow.
