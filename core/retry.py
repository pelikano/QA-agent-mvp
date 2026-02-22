from pydantic import ValidationError
import copy


def retry_with_correction(prompt, call_fn, response_model, max_retries=2):
    last_error = None

    # Avoid mutating original prompt
    base_prompt = copy.deepcopy(prompt)

    for attempt in range(max_retries + 1):
        print(f"[QA-AGENT] Retry attempt {attempt + 1}")

        result = call_fn(prompt)

        try:
            # Validate dynamically using provided schema
            validated = response_model.model_validate(result)

            # Ensure proper JSON serialization (enums, etc.)
            return validated.model_dump(mode="json")

        except ValidationError as e:
            last_error = str(e)

            # Build corrected prompt without stacking infinite system text
            prompt = copy.deepcopy(base_prompt)

            prompt["system"] += f"""

The previous response did NOT comply with the required schema.
Validation errors:
{last_error}

Return ONLY valid JSON matching the required schema.
"""

    raise ValueError(
        f"Invalid output after {max_retries + 1} attempts: {last_error}"
    )