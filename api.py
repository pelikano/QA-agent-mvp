from fastapi import FastAPI, UploadFile, File, Body, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

import tempfile
import os
import zipfile
import shutil
import difflib

from core.agent import run_agent
from core.feature_structure import build_feature_structure
from core.update_engine import apply_update_plan, simulate_update_plan
from core.retry import retry_with_correction
from core.llm import call_llm
from core.sync_prompt_builder import build_sync_prompt
from core.test_reader import read_existing_tests
from core.schemas_tests import UpdatePlan
from core.document_reader import extract_document
from core import config  # ✅ CENTRAL CONFIG


app = FastAPI()


# =========================================================
# USER STORY ANALYSIS
# =========================================================

@app.post("/analyze")
def analyze_story(story: dict):
    return run_agent(story)


# =========================================================
# SYNC TESTS (ALWAYS DRY RUN FROM UI)
# =========================================================

@app.post("/sync-tests")
async def sync_tests(
    file: UploadFile = File(None),
    text_input: str = None,
    dry_run: bool = Query(False)
):
    try:

        if not file and not text_input:
            return JSONResponse(
                status_code=400,
                content={"error": "Provide file or text_input."}
            )

        # 1️⃣ Extract new document
        if file:
            ext = os.path.splitext(file.filename)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            new_document = extract_document(tmp_path)
        else:
            new_document = text_input

        # 2️⃣ Read full test suite (raw text)
        current_tests = read_existing_tests() or ""

        # 3️⃣ Build structured representation
        existing_structure = build_feature_structure(config.BASE_FEATURES_DIR)

        # 4️⃣ Build sync prompt
        prompt = build_sync_prompt(
            current_tests=current_tests,
            existing_structure=existing_structure,
            new_document=new_document
        )

        # 5️⃣ Call LLM
        update_plan = retry_with_correction(
            call_fn=call_llm,
            prompt=prompt,
            schema_cls=UpdatePlan
        )

        simulated_new_content = simulate_update_plan(update_plan)

        diff = list(difflib.unified_diff(
            current_tests.splitlines(),
            simulated_new_content.splitlines(),
            lineterm=""
        ))

        return {
            "mode": "sync",
            "result": update_plan
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )



# =========================================================
# APPLY PROPOSED (NO IA CALL)
# =========================================================

@app.post("/apply-proposed")
async def apply_proposed(payload: dict = Body(...)):

    try:
        if not payload.get("changes"):
            return JSONResponse(
                status_code=400,
                content={"error": "No proposed features provided"}
            )

        apply_update_plan(payload)

        return {"status": "Changes applied successfully"}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# =========================================================
# CURRENT TEST STRUCTURE
# =========================================================

@app.get("/test-structure")
def get_test_structure():

    base = config.BASE_FEATURES_DIR  # ✅ CENTRALIZED
    structure = {}

    if not os.path.exists(base):
        return structure

    for screen in os.listdir(base):

        screen_path = os.path.join(base, screen)

        if os.path.isdir(screen_path):

            structure[screen] = {}

            for file in os.listdir(screen_path):

                file_path = os.path.join(screen_path, file)

                if file.endswith(".feature"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        structure[screen][file] = f.read()

    return structure


# =========================================================
# SET FEATURES DIRECTORY (PERSISTENT)
# =========================================================

@app.post("/set-features-directory")
def set_features_directory(payload: dict = Body(...)):

    from core import config

    directory = payload.get("directory")

    if not directory:
        return JSONResponse(
            status_code=400,
            content={"error": "Directory required"}
        )

    if not os.path.exists(directory):
        return JSONResponse(
            status_code=400,
            content={"error": "Directory does not exist"}
        )

    # Update runtime config
    config.BASE_FEATURES_DIR = directory

    # Persist in environment for current process
    os.environ["QA_FEATURES_DIR"] = directory

    return {
        "status": "Features directory updated",
        "directory": directory
    }


# =========================================================
# API KEY MANAGEMENT
# =========================================================

@app.post("/set-api-key")
def set_api_key(payload: dict = Body(...)):

    api_key = payload.get("api_key")

    if not api_key:
        return JSONResponse(
            status_code=400,
            content={"error": "API key required"}
        )

    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid API key"}
        )

    os.environ["OPENAI_API_KEY"] = api_key

    return {"status": "API key stored successfully"}


@app.get("/check-api-key")
def check_api_key():
    return {
        "configured": bool(os.environ.get("OPENAI_API_KEY"))
    }

# =========================================================
# SYSTEM STATUS
# =========================================================

@app.get("/system-status")
def system_status():

    from core import config

    return {
        "api_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "features_directory": config.BASE_FEATURES_DIR
    }

# =========================================================
# SERVE UI (MUST BE LAST)
# =========================================================

app.mount("/", StaticFiles(directory="ui", html=True), name="ui")
