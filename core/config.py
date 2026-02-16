import os
import platform


def get_default_documents_path():
    home = os.path.expanduser("~")

    if platform.system() == "Windows":
        return os.path.join(home, "Documents")
    else:
        return os.path.join(home, "Documents")


BASE_FEATURES_DIR = os.environ.get(
    "QA_FEATURES_DIR",
    os.path.join(get_default_documents_path(), "generated_tests")
)

