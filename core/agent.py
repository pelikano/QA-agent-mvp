from .prompt_builder import build_prompt
from .llm import call_llm
from .schemas import QAAnalysis
from .retry import retry_with_correction

def run_agent(story):
    prompt = build_prompt(story)
    return retry_with_correction(
        call_fn=call_llm,
        prompt=prompt,
        schema_cls=QAAnalysis
    )
