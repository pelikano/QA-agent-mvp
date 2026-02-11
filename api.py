from fastapi import FastAPI, UploadFile, File
import tempfile
import os


from core.agent import run_agent
from core.test_prompt_builder import build_test_prompt
from core.feature_writer import save_features_to_disk
from core.retry import retry_with_correction
from core.llm import call_llm
from core.evolve_prompt_builder import build_evolve_prompt
from core.test_reader import read_existing_tests
from core.schemas_tests import UpdatedTestSuite
from core.document_reader import extract_document


app = FastAPI()

@app.post("/analyze")
def analyze_story(story: dict):
    return run_agent(story)

@app.post("/sync-tests")
async def sync_tests(
    file: UploadFile = File(None),
    text_input: str = None,
    dry_run: bool = True
):

    if not file and not text_input:
        return {"error": "Provide file or text_input."}

    # Extract document
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

    # Load current tests
    current_tests = read_existing_tests()

    # CASE 1 — Initial generation
    if not current_tests:

        prompt = build_test_prompt(new_document)

        test_suite = retry_with_correction(
            call_fn=call_llm,
            prompt=prompt,
            schema_cls=UpdatedTestSuite
        )

        if not dry_run:
            save_features_to_disk(test_suite)

        return {
            "mode": "initial_generation",
            "result": test_suite
        }

    # CASE 2 — Evolution
    else:

        prompt = build_evolve_prompt(current_tests, new_document)

        updated_suite = retry_with_correction(
            call_fn=call_llm,
            prompt=prompt,
            schema_cls=UpdatedTestSuite
        )

        if not dry_run:
            save_features_to_disk(updated_suite)

        return {
            "mode": "evolution",
            "result": updated_suite
        }

