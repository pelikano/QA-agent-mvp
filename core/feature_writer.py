import os

OUTPUT_DIR = "generated_tests"


def save_features_to_disk(test_suite: dict):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for feature in test_suite["features"]:

        filename = (
            feature["feature_name"]
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
        ) + ".feature"

        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:

            f.write(f"Feature: {feature['feature_name']}\n")
            f.write(f"  {feature['description']}\n\n")

            for scenario in feature["scenarios"]:

                f.write(f"  Scenario: {scenario['name']}\n")

                for step in scenario["steps"]:
                    f.write(f"    {step}\n")

                f.write("\n")
