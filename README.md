
# QA Agent – AI Test Synchronization Engine

## 🚀 Product Vision

QA Agent is an AI-powered deterministic test synchronization engine designed to keep Gherkin test suites aligned with evolving functional documentation.

It is NOT a test generator.
It is NOT a rewrite engine.

It is a controlled, incremental, patch-based synchronization system.

Designed for:
- QA Teams
- Automation Engineers
- Product Owners
- Enterprises needing traceable test evolution

---

# 🎯 Core Value Proposition

✅ Synchronizes tests with evolving requirements  
✅ Never rewrites full features  
✅ Applies minimal incremental patches  
✅ Preserves step consistency and reuse  
✅ Maintains deterministic Gherkin structure  
✅ Safe, versioned modifications  

---

# 🧠 Architectural Philosophy

## Single Source of Truth

Existing test suites are authoritative.

When reading new functional documentation, the engine:

1. Loads current test suite.
2. Treats all existing scenarios as ground truth.
3. Compares documentation against tests.
4. Produces a minimal `UpdatePlan`.
5. Applies incremental patch operations.

No full rewrites.
No uncontrolled regeneration.

---

# 🔧 Technical Architecture

## Backend

- FastAPI
- OpenAI (JSON strict mode)
- Pydantic validation
- Incremental patch engine
- Automatic versioning backups
- Deterministic UpdatePlan schema

---

## UpdatePlan Schema

```python
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
```

The LLM is strictly forced to return:

```json
{
  "changes": [ ... ]
}
```

---

# 🔒 Robustness & Safety

## Strict JSON Mode
- `response_format={"type": "json_object"}`
- Temperature = 0
- Two-phase validation

## Patch Engine Safeguards
- Structural validation per change
- Step index validation
- Required field enforcement
- Unsupported action rejection

## Automatic Backups

Before any modification:

```
_history/feature.feature.YYYYMMDD_HHMMSS.bak
```

Enables manual rollback at any time.

---

# 🔁 Workflow

## 1. Sync Tests

`POST /sync-tests`

- Accepts PDF, DOCX, TXT, or raw text
- Loads current features
- Returns UpdatePlan only

## 2. Apply Changes

`POST /apply-proposed`

- Applies incremental patch
- Creates backups
- Does NOT call AI again

---

# 🧪 Gherkin Strategy

The engine enforces:

- Consistent Given / When / Then formatting
- Step reuse across scenarios
- Parameterization over duplication
- Screen name consistency
- Stable grammar for automation reuse

Designed to support downstream automation frameworks without rewriting steps.

---

# 🖥 UI Capabilities

- Feature folder selector
- IDE-style viewer
- Diff preview
- Dry-run first workflow
- Manual apply confirmation
- API key configuration

---

# 🏢 Enterprise Positioning

QA Agent is suitable for:

- Large-scale test suites
- Regulated environments
- CI/CD integration
- Multi-team collaboration
- Test governance frameworks

Future extensions:
- Multi-tenant isolation
- Git integration
- Audit trail logging
- Quality scoring engine
- Automation coverage insights

---

# 📈 Why This Is Different

Most AI tools regenerate tests.
QA Agent synchronizes them deterministically.

This reduces:
- Flaky automation
- Step duplication
- Test drift
- Manual QA maintenance effort

---

# 🧩 System Status Endpoint

`GET /system-status`

Returns:
- API configuration state
- Current features directory

---

# ⚙ Setup

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY="your api key here"
uvicorn api:app --reload
```

Then open:

http://localhost:8000

---

# 📌 Summary

QA Agent is an AI-driven test synchronization engine built for deterministic, safe, incremental evolution of Gherkin suites.

It bridges the gap between evolving product documentation and stable automated testing.

Designed for production.
Built for control.
Ready for enterprise.


