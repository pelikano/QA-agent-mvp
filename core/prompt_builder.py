def build_prompt(story: dict) -> dict:
    system_prompt = open("tenants/default/system_prompt.txt").read()

    system_prompt += """

Debes responder EXCLUSIVAMENTE en formato JSON válido.
No incluyas texto fuera del JSON.
No incluyas explicaciones.
"""

    return {
        "system": system_prompt,
        "story": story
    }
