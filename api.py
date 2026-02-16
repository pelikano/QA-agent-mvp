from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

import tempfile
import os
import zipfile
import shutil

from core.agent import run_agent
from core.test_prompt_builder import build_test_prompt
from core.feature_writer import save_features_to_disk
from core.retry import retry_with_correction
from core.llm import call_llm
from core.evolve_prompt_builder import build_evolve_prompt
from core.test_reader import read_existing_tests
from core.schemas_tests import UpdatedTestSuite
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
    dry_run: bool = True
):
    try:

        if not file and not text_input:
            return JSONResponse(
                status_code=400,
                content={"error": "Provide file or text_input."}
            )

        # -----------------------------
        # Extract document
        # -----------------------------

        if file:
            original_filename = file.filename
            ext = os.path.splitext(original_filename)[1].lower()

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name

            new_document = extract_document(tmp_path)
        else:
            new_document = text_input

        # -----------------------------
        # Load existing tests
        # -----------------------------

        current_tests = read_existing_tests()

        # -----------------------------
        # INITIAL GENERATION
        # -----------------------------

        if not current_tests:

            prompt = build_test_prompt(new_document)

            test_suite = retry_with_correction(
                call_fn=call_llm,
                prompt=prompt,
                schema_cls=UpdatedTestSuite
            )

            return {
                "mode": "initial_generation",
                "result": test_suite
            }

        # -----------------------------
        # EVOLUTION
        # -----------------------------

        prompt = build_evolve_prompt(current_tests, new_document)

        updated_suite = retry_with_correction(
            call_fn=call_llm,
            prompt=prompt,
            schema_cls=UpdatedTestSuite
        )

        return {
            "mode": "evolution",
            "result": updated_suite
        }

    except Exception as e:

        error_message = str(e)

        if "401" in error_message or "invalid" in error_message.lower():
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key"}
            )

        return JSONResponse(
            status_code=500,
            content={"error": error_message}
        )


# =========================================================
# APPLY PROPOSED (NO IA CALL)
# =========================================================

@app.post("/apply-proposed")
async def apply_proposed(payload: dict = Body(...)):

    try:
        if not payload.get("features"):
            return JSONResponse(
                status_code=400,
                content={"error": "No proposed features provided"}
            )

        save_features_to_disk(payload)

        return {"status": "Changes applied successfully"}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# =========================================================
# DOWNLOAD PROPOSED ONLY
# =========================================================

@app.post("/download-proposed")
async def download_proposed(payload: dict = Body(...)):

    try:
        if not payload.get("features"):
            return JSONResponse(
                status_code=400,
                content={"error": "No proposed features provided"}
            )

        temp_dir = "temp_proposed"

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        os.makedirs(temp_dir, exist_ok=True)

        save_features_to_disk(payload, base_path=temp_dir)

        zip_path = "proposed_tests.zip"

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, temp_dir)
                    zipf.write(full_path, arcname)

        shutil.rmtree(temp_dir)

        return FileResponse(zip_path, filename="proposed_tests.zip")

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
