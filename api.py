from fastapi import FastAPI, UploadFile, File, Body, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

import tempfile
import os
import difflib

from core.agent import run_agent
from core.feature_structure import build_feature_structure
from core.update_engine import apply_update_plan, read_all_features_map
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

        # ======================================================
        # 1️⃣ Validación input
        # ======================================================
        if not file and not text_input:
            return JSONResponse(
                status_code=400,
                content={"error": "Provide file or text_input."}
            )

        # ======================================================
        # 2️⃣ Extraer documento nuevo
        # ======================================================
        if file:
            ext = os.path.splitext(file.filename)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            new_document = extract_document(tmp_path)
        else:
            new_document = text_input

        # ======================================================
        # 3️⃣ Leer suite actual (MAPA DE ARCHIVOS)
        # ======================================================
        current_files_raw = read_all_features_map(config.BASE_FEATURES_DIR)

        current_files = {
            os.path.abspath(path): content
            for path, content in current_files_raw.items()
        }

        # ======================================================
        # 4️⃣ Construir prompt
        # ======================================================
        prompt = build_sync_prompt(
            current_tests="\n".join(current_files.values()),
            existing_structure=build_feature_structure(config.BASE_FEATURES_DIR),
            new_document=new_document
        )

        # ======================================================
        # 5️⃣ LLM → UpdatePlan
        # ======================================================
        update_plan = retry_with_correction(
            call_fn=call_llm,
            prompt=prompt,
            schema_cls=UpdatePlan
        )

        # ======================================================
        # 6️⃣ Simulación REAL
        # ======================================================
        simulated_files_raw = apply_update_plan(
            update_plan,
            simulate=True
        )

        simulated_files = {
            os.path.abspath(path): content
            for path, content in simulated_files_raw.items()
        }

        # ======================================================
        # 7️⃣ Generar diff por archivo
        # ======================================================
        diff_by_file = {}

        for path, new_content in simulated_files.items():

            old_content = current_files.get(path)

            if old_content is None:
                # Archivo nuevo
                diff = list(difflib.unified_diff(
                    [],
                    new_content.splitlines(),
                    lineterm=""
                ))
            else:
                diff = list(difflib.unified_diff(
                    old_content.splitlines(),
                    new_content.splitlines(),
                    lineterm=""
                ))

            if diff:
                file_key = os.path.relpath(path, config.BASE_FEATURES_DIR)
                diff_by_file[file_key] = diff

        # ======================================================
        # DEBUG
        # ======================================================
        print("==== DIFF BY FILE ====")
        print(diff_by_file)

        return {
            "result": update_plan,
            "diff": diff_by_file
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
async def apply_proposed(update_plan: dict):
    try:
        apply_update_plan(update_plan, simulate=False)
        return {"status": "ok"}
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
