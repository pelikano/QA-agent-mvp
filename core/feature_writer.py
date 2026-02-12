import os


OUTPUT_DIR = "generated_tests"


def normalize(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def save_features_to_disk(test_suite: dict):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for feature in test_suite["features"]:

        screen_folder = os.path.join(
            OUTPUT_DIR,
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
