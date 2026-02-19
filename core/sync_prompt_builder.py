import json


def build_sync_prompt(current_tests: str, existing_structure: list, new_document: str) -> dict:

    system_prompt = open(
        "tenants/default/system_prompt.txt",
        encoding="utf-8"
    ).read()

    user_payload = {
        "existing_structure": existing_structure,
        "current_test_suite": current_tests,
        "new_functional_input": new_document
    }

    return {
        "system": system_prompt,
        "data": user_payload
    }
