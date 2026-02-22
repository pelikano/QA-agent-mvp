from fastapi import FastAPI, UploadFile, File, Body, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

import tempfile
import os
import difflib
import json

from core.agent import run_agent, run_analyze_agent
from core.feature_structure import build_feature_structure
from core.update_engine import apply_update_plan, read_all_features_map
from core.initial_generation_engine import apply_initial_generation
from core.llm import call_llm
from core.sync_prompt_builder import build_sync_prompt
from core.test_reader import read_existing_tests
from core.schemas_tests import UpdatePlan
from core.schemas_initial import InitialGeneration
from core.document_reader import extract_document
from core import config


app = FastAPI()


# =========================================================
# USER STORY ANALYSIS
# =========================================================

@app.post("/analyze")
def analyze_story(story: dict):
    return run_analyze_agent(story)


# =========================================================
# SYNC TESTS (AUTO-DETECT MODE)
# =========================================================

@app.post("/sync-tests")
async def sync_tests(
    file: UploadFile = File(None),
    text_input: str = None,
    dry_run: bool = Query(False)
):
    try:

        # ======================================================
        # 1️⃣ Validate input
        # ======================================================
        if not file and not text_input:
            return JSONResponse(
                status_code=400,
                content={"error": "Provide file or text_input."}
            )

        # ======================================================
        # 2️⃣ Extract new document
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
        # 3️⃣ Read current suite
        # ======================================================
        current_files_raw = read_all_features_map(config.BASE_FEATURES_DIR)

        current_files = {
            os.path.abspath(path): content
            for path, content in current_files_raw.items()
        }

        existing_structure = build_feature_structure(config.BASE_FEATURES_DIR)

        # ======================================================
        # 4️⃣ Build prompt
        # ======================================================
        prompt = build_sync_prompt(
            current_tests="\n".join(current_files.values()),
            existing_structure=existing_structure,
            new_document=new_document
        )

        # ======================================================
        # 5️⃣ Call LLM (RAW)
        # ======================================================
        raw_response = call_llm(prompt)

        print("LLM RAW RESPONSE:", raw_response)

        # --------------------------------------------------
        # NORMALIZE RESPONSE TYPE
        # --------------------------------------------------

        if isinstance(raw_response, dict):
            parsed = raw_response

        elif isinstance(raw_response, str):

            cleaned = raw_response.strip()

            # Remove code fences
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]

            # Extract JSON safely
            first = cleaned.find("{")
            last = cleaned.rfind("}")

            if first == -1 or last == -1:
                return JSONResponse(
                    status_code=500,
                    content={"error": "No JSON found in LLM response"}
                )

            cleaned = cleaned[first:last+1]

            try:
                parsed = json.loads(cleaned)
            except Exception as e:
                print("JSON PARSE ERROR:", str(e))
                return JSONResponse(
                    status_code=500,
                    content={"error": "Malformed JSON from LLM"}
                )

        else:
            return JSONResponse(
                status_code=500,
                content={"error": f"Unsupported LLM response type: {type(raw_response)}"}
            )

        # ======================================================
        # 6️⃣ Detect response type
        # ======================================================

        if "features" in parsed:

            validated = InitialGeneration(**parsed)

            simulated_files_raw = apply_initial_generation(
                validated.model_dump(),
                simulate=True
            )

            result_payload = validated.model_dump()

        elif "changes" in parsed:

            validated = UpdatePlan(**parsed)

            simulated_files_raw = apply_update_plan(
                validated.model_dump(),
                simulate=True
            )

            result_payload = validated.model_dump()

        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Unknown response format from LLM"}
            )

        simulated_files = {
            os.path.abspath(path): content
            for path, content in simulated_files_raw.items()
        }

        # ======================================================
        # 7️⃣ Build diff
        # ======================================================
        diff_by_file = {}

        for path, new_content in simulated_files.items():

            old_content = current_files.get(path)

            if old_content is None:
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

        print("==== DIFF BY FILE ====")
        print(diff_by_file)

        return {
            "result": result_payload,
            "diff": diff_by_file
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# =========================================================
# APPLY PROPOSED
# =========================================================

@app.post("/apply-proposed")
async def apply_proposed(payload: dict):
    try:

        if "features" in payload:
            apply_initial_generation(payload, simulate=False)

        elif "changes" in payload:
            apply_update_plan(payload, simulate=False)

        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid payload format"}
            )

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

    base = config.BASE_FEATURES_DIR
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
# SET FEATURES DIRECTORY
# =========================================================

@app.post("/set-features-directory")
def set_features_directory(payload: dict = Body(...)):

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

    config.BASE_FEATURES_DIR = directory
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

    return {
        "api_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "features_directory": config.BASE_FEATURES_DIR
    }


# =========================================================
# SERVE UI
# =========================================================

app.mount("/", StaticFiles(directory="ui", html=True), name="ui")