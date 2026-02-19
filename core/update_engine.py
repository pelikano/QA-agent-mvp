
import os
import shutil
from datetime import datetime
from core import config


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
            if not os.path.exists(feature_path):
                raise ValueError("Feature does not exist for update_step")

            step_index = change.get("step_index")
            new_value = change.get("new_value")

            if step_index is None or new_value is None:
                raise ValueError("update_step requires step_index and new_value")

            with open(feature_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not (0 <= step_index < len(lines)):
                raise ValueError("Invalid step_index")

            _backup_file(feature_path)

            lines[step_index] = new_value.rstrip() + "\n"

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
