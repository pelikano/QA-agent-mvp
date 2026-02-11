from fastapi import FastAPI, UploadFile, File
import tempfile

from core.agent import run_agent
from core.pdf_reader import extract_text_from_pdf
from core.test_prompt_builder import build_test_prompt
from core.feature_writer import save_features_to_disk
from core.schemas_tests import TestSuite
from core.retry import retry_with_correction
from core.llm import call_llm


app = FastAPI()

@app.post("/analyze")
def analyze_story(story: dict):
    return run_agent(story)

@app.post("/generate-tests-pdf")
async def generate_tests_from_pdf(file: UploadFile = File(...)):

    # Guardar temporalmente el PDF
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Extraer texto del PDF
    extracted_text = extract_text_from_pdf(tmp_path)

    # Construir prompt
    prompt = build_test_prompt(extracted_text)

    # Llamar al LLM con retry + validación
    test_suite = retry_with_correction(
        call_fn=call_llm,
        prompt=prompt,
        schema_cls=TestSuite
    )

    # Guardar archivos .feature
    save_features_to_disk(test_suite)

    return {
        "status": "Test suite generated successfully",
        "features_created": len(test_suite["features"])
    }

