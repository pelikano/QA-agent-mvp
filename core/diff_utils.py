
import difflib


def generate_diff(old_content: str, new_content: str):
    diff = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        lineterm=""
    )
    return "\n".join(diff)
