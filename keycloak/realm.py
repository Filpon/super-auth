import os
import json

def replace_placeholders(config: dict):
    """
    Replacing placeholders in the configuration dictionary with environment variable values.

    This function iterates over a set of keys and replaces any occurrences of
    placeholders in the format '${key}' within the corresponding dictionary entries
    in the config with the values of the corresponding environment variables.

    :param dict config: A dictionary containing configuration settings where placeholders
                   may be present.

    :return dict: The updated configuration dictionary with placeholders replaced by
             their corresponding environment variable values.
    """
    for key, value in config.items():
        if isinstance(value, dict):
            # Recursively replacing in nested dictionaries
            replace_placeholders(value)
        elif isinstance(value, str):
            # Replace placeholders that start with '${'
            if value.startswith("${") and value.endswith("}"):
                env_var_name = value[2:-1]  # Extract the variable name
                config[key] = os.getenv(
                    env_var_name, value
                )  # Replace with env var or keep original
            elif value.startswith("${") and "@" in value:
                env_var_name = value[2:].split("}@")[0]
                config[key] =  f"{os.getenv(env_var_name, value)}@user.com"
        elif isinstance(value, list):
            for dict_element in value:
                if isinstance(dict_element, dict):
                    # Recursively replace in nested dictionaries
                    replace_placeholders(dict_element)


def main():
    """
    Main function to load, modify, and save a JSON configuration file.

    This function performs the following steps:
    1. Loads a JSON configuration file from a specified path.
    2. Modifies the configuration by replacing placeholders with environment variable values
       using the `replace_signs` function.
    3. Saves the modified configuration back to a new JSON file.

    The input JSON file is expected to be located at "/tmp/import/realm.json",
    and the modified configuration will be saved to "/tmp/import/realm-mod.json".
    """
    # Load the JSON configuration file
    with open("realm.json", "r", encoding="utf-8") as f:  # /tmp/import/realm.json
        config = json.load(f)

    replace_placeholders(config=config)
    # Save the modified configuration back to a new JSON file
    with open(
        "realm-mod.json", "w", encoding="utf-8"
    ) as f:  # /tmp/import/realm-mod.json
        json.dump(config, f, indent=2)

    print("Configuration was saved to realm-mod.json")

if __name__ == "__main__":
    main()
