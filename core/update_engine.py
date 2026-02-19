
import os
import shutil
from datetime import datetime
from core import config


def is_cosmetic_change(old: str, new: str) -> bool:
    if not old or not new:
        return False

    normalized_old = old.strip().lower().rstrip(".")
    normalized_new = new.strip().lower().rstrip(".")

    trivial_replacements = [
        ("should", "must"),
        ("must", "should")
    ]

    if normalized_old == normalized_new:
        return True

    for a, b in trivial_replacements:
        if normalized_old.replace(a, b) == normalized_new:
            return True

    return False

def _backup_file(path):
    if not os.path.exists(path):
        return
    backup_dir = os.path.join(os.path.dirname(path), "_history")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(
        backup_dir,
        f"{os.path.basename(path)}.{timestamp}.bak"
    )
    shutil.copy2(path, backup_path)


def apply_update_plan(update_plan: dict):

    if "changes" not in update_plan:
        raise ValueError("Invalid UpdatePlan: missing changes")

    base = config.BASE_FEATURES_DIR

    for change in update_plan.get("changes", []):

        required = ["action", "screen", "feature"]
        for field in required:
            if field not in change:
                raise ValueError(f"Invalid change object: missing {field}")

        screen = change["screen"]
        feature = change["feature"]
        scenario = change.get("scenario")
        action = change["action"]

        screen_path = os.path.join(base, screen)
        os.makedirs(screen_path, exist_ok=True)

        feature_path = os.path.join(screen_path, f"{feature}.feature")

        # CREATE FEATURE
        if action == "create_feature":
            if not os.path.exists(feature_path):
                with open(feature_path, "w", encoding="utf-8") as f:
                    f.write(f"Feature: {feature}\n\n")

        # CREATE SCENARIO
        elif action == "create_scenario":
            if not scenario:
                raise ValueError("create_scenario requires scenario name")

            if not os.path.exists(feature_path):
                raise ValueError("Feature does not exist for scenario creation")

            _backup_file(feature_path)

            with open(feature_path, "a", encoding="utf-8") as f:
                f.write(f"  Scenario: {scenario}\n")

        # UPDATE STEP
        elif action == "update_step":
            if is_cosmetic_change(change.old_value, change.new_value):
                continue
            if not os.path.exists(feature_path):
                raise ValueError("Feature does not exist for update_step")

            old_value = change.get("old_value")
            new_value = change.get("new_value")

            if not old_value or not new_value:
                raise ValueError("update_step requires old_value and new_value")

            with open(feature_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            found = False

            for i, line in enumerate(lines):
                if old_value.strip() in line.strip():
                    lines[i] = new_value.rstrip() + "\n"
                    found = True
                    break

            if not found:
                raise ValueError("Old value not found in file")

            _backup_file(feature_path)

            with open(feature_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            with open(feature_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

        # DELETE SCENARIO (basic implementation)
        elif action == "delete_scenario":
            if not os.path.exists(feature_path):
                continue

            _backup_file(feature_path)

            with open(feature_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            skip = False
            for line in lines:
                if line.strip().startswith("Scenario:") and scenario in line:
                    skip = True
                    continue
                if skip and line.strip().startswith("Scenario:"):
                    skip = False
                if not skip:
                    new_lines.append(line)

            with open(feature_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        # DELETE FEATURE
        elif action == "delete_feature":
            if os.path.exists(feature_path):
                _backup_file(feature_path)
                os.remove(feature_path)

        else:
            raise ValueError(f"Unsupported action: {action}")

def simulate_update_plan(update_plan: dict) -> str:
    """
    Simula cambios en memoria y devuelve el nuevo contenido
    sin escribir en disco.
    """

    base = config.BASE_FEATURES_DIR
    simulated_content = read_all_features(base)

    if "changes" not in update_plan:
        return simulated_content

    lines = simulated_content.splitlines()

    for change in update_plan.get("changes", []):

        if change["action"] != "update_step":
            continue

        old_value = change.get("old_value")
        new_value = change.get("new_value")

        if not old_value or not new_value:
            continue

        for i, line in enumerate(lines):
            if old_value.strip() in line.strip():
                lines[i] = new_value.rstrip()
                break

    return "\n".join(lines)


def read_all_features(base_dir: str) -> str:
    content = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".feature"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content.append(f.read())

    return "\n".join(content)
