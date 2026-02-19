import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def call_llm(prompt: dict):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "UpdatePlan",
                "schema": {
                    "type": "object",
                    "properties": {
                        "changes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "enum": [
                                            "create_feature",
                                            "delete_feature",
                                            "create_scenario",
                                            "delete_scenario",
                                            "update_step"
                                        ]
                                    },
                                    "screen": {"type": "string"},
                                    "feature": {"type": "string"},
                                    "scenario": {"type": ["string", "null"]},
                                    "step_index": {"type": ["integer", "null"]},
                                    "old_value": {"type": ["string", "null"]},
                                    "new_value": {"type": ["string", "null"]}
                                },
                                "required": ["action", "screen", "feature"]
                            }
                        }
                    },
                    "required": ["changes"]
                }
            }
        },
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": json.dumps(prompt["data"])}
        ]
    )

    content = response.choices[0].message.content

    # Debug log (opcional pero recomendado)
    print("LLM RAW RESPONSE:", content)

    return json.loads(content)
