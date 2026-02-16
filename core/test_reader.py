import os
from core.config import BASE_FEATURES_DIR
TEST_DIR = BASE_FEATURES_DIR


def read_existing_tests():
    content = ""

    if not os.path.exists(TEST_DIR):
        return ""

    for file in os.listdir(TEST_DIR):
        if file.endswith(".feature"):
            with open(os.path.join(TEST_DIR, file), encoding="utf-8") as f:
                content += f.read() + "\n\n"

    return content
