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

    # -------------------------------------------------
    # 1️⃣ Cargar archivos actuales
    # -------------------------------------------------
    in_memory_files = {}

    for root, _, files in os.walk(base):
        for file in files:
            if file.endswith(".feature"):
                full_path = os.path.abspath(os.path.join(root, file))
                with open(full_path, "r", encoding="utf-8") as f:
                    in_memory_files[full_path] = f.readlines()

    print("Loaded feature files:")
    for k in in_memory_files.keys():
        print("   ", k)

    # -------------------------------------------------
    # 2️⃣ Buscar archivo REAL dentro de memoria
    # -------------------------------------------------
    def find_feature_file(screen: str, feature_name: str):

        print("\n--- find_feature_file ---")
        print("Looking for screen:", screen)
        print("Looking for feature:", feature_name)

        for path, lines in in_memory_files.items():

            # screen match por carpeta
            if screen.lower() not in path.lower():
                continue

            # leer primera línea
            first_line = lines[0].strip() if lines else ""

            if first_line.lower() == f"feature: {feature_name}".lower():
                print("MATCH FOUND:", path)
                return path

        print("No match found.")
        return None

    # -------------------------------------------------
    # 3️⃣ Aplicar cambios
    # -------------------------------------------------
    for change in update_plan.get("changes", []):

        print("\nProcessing change:", change)

        screen = change["screen"]
        feature = change["feature"]
        action = change["action"]

        feature_path = find_feature_file(screen, feature)

        if not feature_path:
            print("❌ Feature file NOT FOUND")
            continue

        lines = in_memory_files.get(feature_path)

        if not lines:
            print("❌ File has no lines loaded")
            continue

        # -----------------------------
        # UPDATE STEP
        # -----------------------------
        if action == "update_step":

            old_value = change.get("old_value")
            new_value = change.get("new_value")

            print("Old value:", old_value)
            print("New value:", new_value)

            replaced = False

            for i, line in enumerate(lines):
                if old_value.strip() in line.strip():
                    print("MATCH LINE FOUND:")
                    print("   BEFORE:", line.strip())

                    lines[i] = line.replace(
                        old_value.strip(),
                        new_value.strip()
                    )

                    print("   AFTER :", lines[i].strip())
                    replaced = True
                    break

            if not replaced:
                print("⚠️ old_value NOT found inside file.")

        in_memory_files[feature_path] = lines

    # -------------------------------------------------
    # 4️⃣ SIMULATION
    # -------------------------------------------------
    if simulate:
        print("\nReturning simulated files.")
        return {
            path: "".join(lines)
            for path, lines in in_memory_files.items()
        }

    # -------------------------------------------------
    # 5️⃣ APPLY REAL
    # -------------------------------------------------
    print("\nApplying changes to disk.")
    for path, lines in in_memory_files.items():
        _backup_file(path)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return True