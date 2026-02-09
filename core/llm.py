from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt: dict) -> dict:
    print(">>> CALLING OPENAI <<<")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt["system"]},
            {
                "role": "user",
                "content": (
                    "Analiza la siguiente historia de usuario y responde en JSON.\n\n"
                    + json.dumps(prompt["story"], ensure_ascii=False)
                )
            }
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
