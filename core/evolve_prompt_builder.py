def build_evolve_prompt(current_tests: str, new_document: str) -> dict:
    system_prompt = open(
        "tenants/default/system_prompt_evolve_tests.txt",
        encoding="utf-8"
    ).read()

    return {
        "system": system_prompt,
        "data": {
            "current_test_suite": current_tests[:20000],
            "new_functional_input": new_document[:20000]
        }
    }
