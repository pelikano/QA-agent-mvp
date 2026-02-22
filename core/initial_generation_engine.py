import os
from core import config


def apply_initial_generation(initial_plan: dict, simulate: bool = False):

    base = config.BASE_FEATURES_DIR
    in_memory_files = {}

    for feature in initial_plan["features"]:

        screen = feature["screen_name"]
        feature_name = feature["feature_name"]

        screen_dir = os.path.join(base, screen)
        os.makedirs(screen_dir, exist_ok=True)

        filename = feature_name.lower().replace(" ", "_") + ".feature"
        path = os.path.join(screen_dir, filename)

        lines = []
        lines.append(f"Feature: {feature_name}\n\n")

        for scenario in feature["scenarios"]:

            lines.append(f"  Scenario: {scenario['name']}\n")

            for step in scenario["steps"]:
                lines.append(f"    {step}\n")

            lines.append("\n")

        in_memory_files[path] = lines

    if simulate:
        return {path: "".join(lines) for path, lines in in_memory_files.items()}

    for path, lines in in_memory_files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return True