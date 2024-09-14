import os
import json
import yaml


def convert_json_to_yaml(json_dir, yaml_dir):
    # Iterate over all files in the directory
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            json_path = os.path.join(json_dir, filename)

            # Read JSON file
            with open(json_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

            # Convert to YAML
            yaml_data = yaml.dump(
                data,
                default_flow_style=None,
                encoding="utf-8",
                allow_unicode=True,
                width=float("inf"),
                sort_keys=False,
            )

            # Write YAML file
            yaml_path = os.path.join(yaml_dir, filename.replace(".json", ".yaml"))
            with open(yaml_path, "wb") as yaml_file:
                yaml_file.write(yaml_data)

    print("Conversion completed.")


if __name__ == "__main__":
    json_dir = "json_remake"
    yaml_dir = "yaml_groups"

    convert_json_to_yaml(json_dir, yaml_dir)

    pass
