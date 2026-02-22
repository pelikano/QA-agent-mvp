import os
import shutil
from datetime import datetime
from core import config


# ============================================================
# Helpers
# ============================================================

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


def read_all_features_map(base_dir: str):
    files = {}

    for root, _, file_list in os.walk(base_dir):
        for file in file_list:
            if file.endswith(".feature"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    files[path] = f.read()

    return files


# ============================================================
# Core Engine
# ============================================================

def apply_update_plan(update_plan: dict, simulate: bool = False):

    print("\n==============================")
    print("ENTER apply_update_plan")
    print("==============================")

    if "changes" not in update_plan:
        raise ValueError("Invalid UpdatePlan: missing changes")

    base = config.BASE_FEATURES_DIR
    in_memory_files = {}

    # -------------------------------------------------
    # 1️⃣ Load existing feature files
    # -------------------------------------------------
    if os.path.exists(base):
        for root, _, files in os.walk(base):
            for file in files:
                if file.endswith(".feature"):
                    full_path = os.path.abspath(os.path.join(root, file))
                    with open(full_path, "r", encoding="utf-8") as f:
                        in_memory_files[full_path] = f.readlines()

    print("Loaded files:")
    for k in in_memory_files.keys():
        print("  ", k)

    # -------------------------------------------------
    # 2️⃣ Helper to build feature path
    # -------------------------------------------------
    def build_feature_path(screen, feature):
        screen_dir = os.path.join(base, screen)
        filename = f"{feature.lower().replace(' ', '_')}.feature"
        return os.path.abspath(os.path.join(screen_dir, filename))

    # -------------------------------------------------
    # 3️⃣ Apply changes
    # -------------------------------------------------
    for change in update_plan.get("changes", []):

        print("\nProcessing change:", change)

        screen = change["screen"]
        feature = change["feature"]
        action = change["action"]

        feature_path = build_feature_path(screen, feature)

        # =====================================================
        # CREATE FEATURE (NO PRIOR VALIDATION)
        # =====================================================
        if action == "create_feature":

            if feature_path not in in_memory_files:
                print("Creating feature:", feature_path)

                os.makedirs(os.path.dirname(feature_path), exist_ok=True)

                lines = [
                    f"Feature: {feature}\n",
                    "\n"
                ]

                scenario = change.get("scenario")
                new_value = change.get("new_value")

                if scenario and new_value:
                    print("Adding initial scenario:", scenario)

                    lines.append(f"  Scenario: {scenario}\n")

                    for step in new_value.split("\n"):
                        step = step.strip()
                        if step:
                            lines.append(f"    {step}\n")

                    lines.append("\n")

                in_memory_files[feature_path] = lines

            continue  # 🔥 critical

        # =====================================================
        # VALIDATE FILE EXISTS FOR OTHER ACTIONS
        # =====================================================
        if feature_path not in in_memory_files:
            print("⚠️ Feature file not found:", feature_path)
            continue

        lines = in_memory_files[feature_path]

        # =====================================================
        # CREATE SCENARIO
        # =====================================================
        if action == "create_scenario":

            scenario = change.get("scenario")
            new_value = change.get("new_value")

            if scenario and new_value:

                print("Adding scenario:", scenario)

                lines.append(f"  Scenario: {scenario}\n")

                for step in new_value.split("\n"):
                    step = step.strip()
                    if not step:
                        continue

                    if step.startswith(("Given", "When", "Then", "And", "But")):
                        lines.append(f"    {step}\n")

                lines.append("\n")

        # =====================================================
        # UPDATE STEP
        # =====================================================
        elif action == "update_step":

            scenario_name = change.get("scenario")
            step_index = change.get("step_index")
            old_value = change.get("old_value")
            new_value = change.get("new_value")

            print("Updating scenario:", scenario_name)

            # Find scenario start
            scenario_start = None
            for idx, line in enumerate(lines):
                if line.strip().startswith("Scenario:") and scenario_name in line:
                    scenario_start = idx
                    break

            if scenario_start is None:
                print("⚠️ Scenario not found:", scenario_name)
                continue

            # Collect scenario steps
            scenario_indices = []
            for i in range(scenario_start + 1, len(lines)):
                if lines[i].strip().startswith("Scenario:"):
                    break
                if lines[i].strip().startswith(("Given", "When", "Then", "And", "But")):
                    scenario_indices.append(i)

            print("Scenario indices:", scenario_indices)
            print("Requested step_index:", step_index)

            # Primary strategy: index
            if step_index is not None and step_index < len(scenario_indices):
                target_line_index = scenario_indices[step_index]
                print("BEFORE:", lines[target_line_index].strip())
                lines[target_line_index] = "    " + new_value + "\n"
                print("AFTER :", lines[target_line_index].strip())

            # Fallback strategy: match old_value
            else:
                print("⚠️ step_index invalid, fallback to old_value match")

                replaced = False
                for i in scenario_indices:
                    if old_value and old_value.strip() in lines[i]:
                        print("BEFORE:", lines[i].strip())
                        lines[i] = lines[i].replace(old_value.strip(), new_value.strip())
                        print("AFTER :", lines[i].strip())
                        replaced = True
                        break

                if not replaced:
                    print("⚠️ Could not update step via fallback")

    # -------------------------------------------------
    # 4️⃣ SIMULATION MODE
    # -------------------------------------------------
    if simulate:
        print("Returning simulated files")
        return {
            path: "".join(lines)
            for path, lines in in_memory_files.items()
        }

    # -------------------------------------------------
    # 5️⃣ APPLY REAL
    # -------------------------------------------------
    print("Writing to disk")

    for path, lines in in_memory_files.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _backup_file(path)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return True