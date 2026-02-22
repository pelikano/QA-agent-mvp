QA Agent – AI Test Generation & Synchronization Engine

============================================================
🚀 Product Vision
============================================================

QA Agent is an AI-powered deterministic test suite engine designed to:

1) Generate complete structured Gherkin test suites for new projects.
2) Synchronize existing test suites incrementally with evolving documentation.

It is NOT a blind test generator.
It is NOT a full rewrite engine.

It is a controlled, deterministic, patch-based test evolution system.

Designed for:
- QA Teams
- Automation Engineers
- Product Owners
- Enterprises requiring traceable test governance

------------------------------------------------------------

============================================================
🎯 Core Value Proposition
============================================================

✅ Generates structured test suites from functional documentation  
✅ Synchronizes tests with evolving requirements  
✅ Never rewrites full features unnecessarily  
✅ Applies minimal incremental patches  
✅ Preserves step consistency and reuse  
✅ Maintains deterministic Gherkin structure  
✅ Provides safe, versioned modifications  
✅ Supports enterprise-grade governance  

------------------------------------------------------------

============================================================
🧠 Architectural Philosophy
============================================================

Single Source of Truth

Existing test suites are authoritative.

When processing new functional documentation, the engine:

1. Loads current test suite.
2. Treats existing scenarios as ground truth.
3. Compares documentation against tests.
4. Produces a deterministic UpdatePlan.
5. Applies incremental patch operations.

No uncontrolled regeneration.
No hidden mutations.
No destructive rewrites.

For empty projects:
- Generates a fully structured test suite in deterministic JSON format.
- Enforces feature grouping and Gherkin correctness.

------------------------------------------------------------

============================================================
🔧 Technical Architecture
============================================================

Backend:
- FastAPI
- OpenAI (JSON strict mode)
- Pydantic validation
- Deterministic patch engine
- Automatic versioning backups
- Structured UpdatePlan schema

Frontend:
- Diff-based preview
- Dry-run workflow
- Controlled apply confirmation
- Folder selection
- API key configuration

------------------------------------------------------------

============================================================
📐 Operating Modes
============================================================

MODE 1 — Initial Generation (Empty Project)

If no features exist:
- Detects all functional screens.
- Creates structured feature groups per screen.
- Generates positive and negative scenarios.
- Enforces strict Given / When / Then structure.
- Returns deterministic JSON structure.

MODE 2 — Synchronization (Existing Project)

If features already exist:
- Compares new documentation against existing_structure.
- Produces minimal change set.
- Uses update_step > create_scenario > create_feature priority.
- Avoids duplication.
- Preserves scenario stability.

------------------------------------------------------------

============================================================
📄 UpdatePlan Schema (Synchronization Mode)
============================================================

class ChangeAction(BaseModel):
    action: str  # create_feature | delete_feature | create_scenario | delete_scenario | update_step
    screen: str
    feature: str
    scenario: Optional[str]
    step_index: Optional[int]
    old_value: Optional[str]
    new_value: Optional[str]

class UpdatePlan(BaseModel):
    changes: List[ChangeAction]

LLM is strictly forced to return:

{
  "changes": [ ... ]
}

------------------------------------------------------------

============================================================
📄 Initial Generation Schema (Empty Project Mode)
============================================================

{
  "features": [
    {
      "screen_name": "string",
      "feature_group": "snake_case_string",
      "feature_name": "string",
      "description": "string",
      "scenarios": [
        {
          "name": "string",
          "steps": [
            "Given ...",
            "When ...",
            "Then ..."
          ]
        }
      ]
    }
  ],
  "change_summary": [
    "Initial test suite generation"
  ]
}

All fields are mandatory.
All content is strictly in English.

------------------------------------------------------------

============================================================
🔒 Robustness & Safety
============================================================

Strict JSON Mode:
- response_format={"type": "json_object"}
- Temperature = 0
- Retry with correction mechanism
- Pydantic schema enforcement

Patch Engine Safeguards:
- Structural validation per change
- Step index validation
- Required field enforcement
- Unsupported action rejection
- Safe fallback matching on update_step

Automatic Backups:

Before any modification:

_history/feature.feature.YYYYMMDD_HHMMSS.bak

Enables manual rollback at any time.

------------------------------------------------------------

============================================================
🔁 Workflow
============================================================

1) Sync Tests

POST /sync-tests

- Accepts PDF, DOCX, TXT, or raw text
- Loads current features
- Detects generation vs synchronization mode
- Returns UpdatePlan or feature generation structure
- Dry-run by default (UI first)

2) Apply Changes

POST /apply-proposed

- Applies incremental patch or initial generation
- Creates automatic backups
- Does NOT call AI again
- Fully deterministic application layer

------------------------------------------------------------

============================================================
🧪 Gherkin Strategy
============================================================

The engine enforces:

- Consistent Given / When / Then formatting
- At least one Given, When, and Then per scenario
- Step reuse across scenarios
- Parameterization over duplication
- Screen name consistency
- Stable grammar for automation reuse
- Strict English output normalization

Designed for downstream compatibility with:
- Cucumber
- Playwright
- Cypress BDD
- Selenium frameworks
- Enterprise automation pipelines

------------------------------------------------------------

============================================================
🖥 UI Capabilities
============================================================

- Feature directory selector
- IDE-style file explorer
- Git-style diff preview
- Dry-run first workflow
- Manual apply confirmation
- API key configuration
- System status monitor

------------------------------------------------------------

============================================================
🏢 Enterprise Positioning
============================================================

QA Agent is suitable for:

- Large-scale test suites
- Regulated environments
- CI/CD integration
- Multi-team collaboration
- Test governance frameworks
- Structured QA modernization initiatives

Future extensions:
- Multi-tenant isolation
- Git integration
- Audit trail logging
- Quality scoring engine
- Automation coverage insights
- Requirement traceability matrix

------------------------------------------------------------

============================================================
📊 Why This Is Different
============================================================

Most AI tools regenerate tests.
QA Agent synchronizes them deterministically.

This reduces:

- Flaky automation
- Step duplication
- Test drift
- Manual QA maintenance effort
- Regression instability

It enables controlled AI-assisted QA evolution.

------------------------------------------------------------

============================================================
🧩 System Status Endpoint
============================================================

GET /system-status

Returns:
- API configuration state
- Current features directory

------------------------------------------------------------

============================================================
⚙ Setup
============================================================

python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY="your api key here"
uvicorn api:app --reload

Open:

http://localhost:8000

------------------------------------------------------------

============================================================
📌 Summary
============================================================

QA Agent is an AI-driven test generation and synchronization engine built for deterministic, safe, incremental evolution of structured Gherkin suites.

It bridges the gap between evolving product documentation and stable automated testing.

Designed for production.
Built for control.
Ready for enterprise.