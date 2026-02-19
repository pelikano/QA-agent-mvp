import os


def build_feature_structure(base_dir: str) -> list:
    """
    Parse all .feature files inside base_dir and return structured data.
    """

    structured = []

    if not os.path.exists(base_dir):
        return structured

    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith(".feature"):
                continue

            file_path = os.path.join(root, file)

            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            current_feature = None
            current_scenario = None
            scenarios = []

            for line in lines:
                stripped = line.strip()

                if stripped.startswith("Feature:"):
                    current_feature = stripped.replace("Feature:", "").strip()

                elif stripped.startswith("Scenario:"):
                    if current_scenario:
                        scenarios.append(current_scenario)

                    scenario_name = stripped.replace("Scenario:", "").strip()
                    current_scenario = {
                        "name": scenario_name,
                        "steps": []
                    }

                elif stripped.startswith(("Given", "When", "Then", "And", "But")):
                    if current_scenario:
                        current_scenario["steps"].append(stripped)

            if current_scenario:
                scenarios.append(current_scenario)

            if current_feature:
                structured.append({
                    "feature": current_feature,
                    "file": file,
                    "scenarios": scenarios
                })

    return structured
