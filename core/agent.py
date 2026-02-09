from .prompt_builder import build_prompt
from .llm import call_llm
from .validator import validate_output

def run_agent(story):
    prompt = build_prompt(story)
    result = call_llm(prompt)
    return validate_output(result)
