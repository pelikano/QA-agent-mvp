import json
from openai import OpenAI

client = OpenAI()


def call_llm(prompt: dict):

    system_message = prompt.get("system", "")
    user_payload = prompt.get("data") or prompt.get("story") or prompt

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": json.dumps(user_payload, ensure_ascii=False)
            }
        ]
    )

    return json.loads(response.choices[0].message.content)
