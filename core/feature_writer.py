import os
from core import config


def normalize(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def save_features_to_disk(test_suite: dict, base_path: str = None):

    # Use dynamic base directory
    output_dir = base_path if base_path else config.BASE_FEATURES_DIR

    os.makedirs(output_dir, exist_ok=True)

    for feature in test_suite["features"]:

        screen_folder = os.path.join(
            output_dir,
            normalize(feature["screen_name"])
        )

        os.makedirs(screen_folder, exist_ok=True)

        filename = normalize(feature["feature_group"]) + ".feature"
        filepath = os.path.join(screen_folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:

            f.write(f"Feature: {feature['feature_name']}\n")
            f.write(f"  {feature['description']}\n\n")

            for scenario in feature["scenarios"]:

                f.write(f"  Scenario: {scenario['name']}\n")

                for step in scenario["steps"]:
                    f.write(f"    {step}\n")

                f.write("\n")
