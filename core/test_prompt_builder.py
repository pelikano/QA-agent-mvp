
def build_test_prompt(text: str) -> dict:
    system_prompt = open("tenants/default/system_prompt_tests.txt").read()

    return {
        "system": system_prompt,
        "story": {
            "document": text[:12000]
        }
    }
