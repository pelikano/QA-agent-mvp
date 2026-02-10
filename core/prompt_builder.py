from .rag import retrieve_context

def build_prompt(story: dict) -> dict:
    system_prompt = open("tenants/default/system_prompt.txt").read()

    rag_context = retrieve_context(
        query=story["title"] + " " + story["description"],
        rag_path="tenants/default/rag"
    )

    system_prompt += f"""

CONTEXTO DEL PROYECTO:
{rag_context}
"""

    return {
        "system": system_prompt,
        "story": story
    }
