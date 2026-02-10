from pydantic import ValidationError

def retry_with_correction(call_fn, prompt, schema_cls, max_retries=2):
    last_error = None

    for attempt in range(max_retries + 1):
        print(f"[QA-AGENT] Retry attempt {attempt + 1}")
        result = call_fn(prompt)

        try:
            return schema_cls(**result).dict()
        except ValidationError as e:
            last_error = str(e)

            # Inyectamos el error al prompt para autocorrección
            prompt["system"] += f"""

La respuesta anterior NO cumplía el esquema requerido.
Errores detectados:
{last_error}

Corrige la respuesta y devuelve SOLO el JSON válido.
"""

    raise ValueError(f"Invalid output after {max_retries + 1} attempts: {last_error}")
