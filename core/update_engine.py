import os
import shutil
from datetime import datetime
from core import config


# ============================================================
# Helpers
# ============================================================

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


def _read_feature(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def _write_feature(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


# ============================================================
# Core Engine
# ============================================================

def apply_update_plan(update_plan: dict, simulate: bool = False):

    if "changes" not in update_plan:
        raise ValueError("Invalid UpdatePlan: missing changes")

    base = config.BASE_FEATURES_DIR
    in_memory_files = {}

    # Load all features in memory if simulate
    if simulate:
        for root, _, files in os.walk(base):
            for file in files:
                if file.endswith(".feature"):
                    full_path = os.path.join(root, file)
                    in_memory_files[full_path] = _read_feature(full_path)

    for change in update_plan.get("changes", []):

        screen = change["screen"]
        feature = change["feature"]
        action = change["action"]

        screen_path = os.path.join(base, screen)
        feature_path = os.path.join(screen_path, f"{feature}.feature")

        if simulate:
            lines = in_memory_files.get(feature_path, [])
        else:
            if not os.path.exists(feature_path) and action != "create_feature":
                continue
            lines = _read_feature(feature_path)

        # ====================================================
        # CREATE FEATURE
        # ====================================================
        if action == "create_feature":
            if simulate:
                in_memory_files[feature_path] = [f"Feature: {feature}\n\n"]
            else:
                os.makedirs(screen_path, exist_ok=True)
                _write_feature(feature_path, [f"Feature: {feature}\n\n"])
            continue

        # ====================================================
        # UPDATE STEP (robusto)
        # ====================================================
        if action == "update_step":

            old_value = change.get("old_value")
            new_value = change.get("new_value")
            step_index = change.get("step_index")

            if not new_value:
                continue

            if old_value and is_cosmetic_change(old_value, new_value):
                continue

            updated = False

            # 1️⃣ Try by text match first (robust)
            if old_value:
                for i, line in enumerate(lines):
                    if old_value.strip() in line.strip():
                        lines[i] = new_value.rstrip() + "\n"
                        updated = True
                        break

            # 2️⃣ Fallback to index
            if not updated and step_index is not None:
                if 0 <= step_index < len(lines):
                    lines[step_index] = new_value.rstrip() + "\n"
                    updated = True

            if not updated:
                continue

        # ====================================================
        # CREATE SCENARIO
        # ====================================================
        elif action == "create_scenario":

            scenario_name = change.get("scenario")
            scenario_body = change.get("new_value")

            if not scenario_name:
                continue

            lines.append(f"\n  Scenario: {scenario_name}\n")

            if scenario_body:
                for step in scenario_body.split(","):
                    lines.append(f"    {step.strip()}\n")

        # ====================================================
        # DELETE SCENARIO
        # ====================================================
        elif action == "delete_scenario":

            scenario_name = change.get("scenario")
            if not scenario_name:
                continue

            new_lines = []
            skip = False

            for line in lines:
                if line.strip().startswith("Scenario:") and scenario_name in line:
                    skip = True
                    continue
                if skip and line.strip().startswith("Scenario:"):
                    skip = False
                if not skip:
                    new_lines.append(line)

            lines = new_lines

        # ====================================================
        # DELETE FEATURE
        # ====================================================
        elif action == "delete_feature":

            if simulate:
                in_memory_files.pop(feature_path, None)
                continue

            if os.path.exists(feature_path):
                _backup_file(feature_path)
                os.remove(feature_path)
                continue

        # ====================================================
        # SAVE
        # ====================================================
        if simulate:
            in_memory_files[feature_path] = lines
        else:
            _backup_file(feature_path)
            _write_feature(feature_path, lines)

    # ========================================================
    # RETURN SIMULATION RESULT
    # ========================================================
    if simulate:
        combined_content = []
        for path in sorted(in_memory_files.keys()):
            combined_content.extend(in_memory_files[path])
            combined_content.append("\n")
        return "".join(combined_content)

    return True