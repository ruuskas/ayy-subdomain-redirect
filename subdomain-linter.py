import os
from typing import List, Tuple
import yaml
import argparse
from pprint import pprint

SUBDOMAINS_FOLDER = "subdomains"
SUBDOMAIN_VALUE_SCHEMA = {
    "redirect_from": {"type": list, "required": True},
    "redirect_to": {"type": str, "required": True},
    "include_path": {"type": bool, "required": False},
    "permanent": {"type": bool, "required": False},
}


class LintError(Exception):
    pass


def check_yaml_format(file_path):
    with open(file_path, "r") as f:
        try:
            yaml.safe_load(f)

        except yaml.YAMLError as e:
            raise LintError(f"Error in {file_path}: {e}")


def check_business_rules(file_path):
    with open(file_path, "r") as f:
        subdomain = yaml.safe_load(f)

        # Check if subdomain is a dict
        if not isinstance(subdomain, dict):
            raise LintError(f"{file_path}: Subdomain should be a dict")

        # Check that subdomain has at least one key
        if len(subdomain) == 0:
            raise LintError(f"{file_path}: Subdomain should have at least one key")

        subdomain_keys = list(subdomain.keys())
        # Check if subdomain keys are strings
        for key in subdomain_keys:
            if not isinstance(key, str):
                raise LintError(f"{file_path}: Subdomain key {key} should be a string")

        # Check that the values of the subdomain key are valid
        for subdomain_key in subdomain_keys:
            subdomain_value = subdomain[subdomain_key]
            for key, value in subdomain_value.items():
                if key not in SUBDOMAIN_VALUE_SCHEMA:
                    raise LintError(f"{file_path}: {key} is not a valid key")
                if not isinstance(value, SUBDOMAIN_VALUE_SCHEMA[key]["type"]):
                    raise LintError(
                        f"{file_path}: {key} should be a {SUBDOMAIN_VALUE_SCHEMA[key]['type']}"
                    )

            # Check that the required keys are present
            for key, value in SUBDOMAIN_VALUE_SCHEMA.items():
                if value["required"] and key not in subdomain_value:
                    raise LintError(f"{file_path}: {key} is required")

            # All values in redirect_from should be end with '.ayy.fi' or '.otax.fi'.
            for redirect_from in subdomain_value["redirect_from"]:
                if not redirect_from.endswith(".ayy.fi") and not redirect_from.endswith(
                    ".otax.fi"
                ):
                    raise LintError(
                        f"{file_path}: {redirect_from} should end with '.ayy.fi' or '.otax.fi'"
                    )
            
            # Check that redirect_to is a valid URL
            if not subdomain_value["redirect_to"].startswith("http"):
                raise LintError(f"{file_path}: redirect_to should be a valid URL")


def get_subdomain_key(file_path):
    with open(file_path, "r") as f:
        subdomain = yaml.safe_load(f)
        subdomain_key = list(subdomain.keys())[0]
        return subdomain_key


def check_no_duplicate_keys(keys_and_filename: List[Tuple[str, str]]):
    keys = [key for key, _ in keys_and_filename]
    duplicate_keys = set([key for key in keys if keys.count(key) > 1])
    files_with_duplicate_keys = [
        file_name for key, file_name in keys_and_filename if key in duplicate_keys
    ]
    if duplicate_keys:
        raise LintError(
            f"Duplicate keys: {duplicate_keys} in {files_with_duplicate_keys}"
        )


def main(args):
    linting_errors = []
    keys_and_filename = []
    for file_name in os.listdir(args.folder):
        if file_name.endswith(".yaml") or file_name.endswith(".yml"):
            file_path = os.path.join(args.folder, file_name)
            try:
                check_yaml_format(file_path)
                check_business_rules(file_path)
                keys_and_filename.append((get_subdomain_key(file_path), file_name))
            except LintError as e:
                print("Error in file: ", file_path)
                linting_errors.append(e)
        else:
            linting_errors.append(
                LintError(f"{file_name} is not a .yaml or .yml file. Only YAML files are allowed")
            )
    try:
        check_no_duplicate_keys(keys_and_filename)
    except LintError as e:
        linting_errors.append(e)

    if linting_errors:
        print("Linting errors:")
        pprint(linting_errors)
        exit(1)
    else:
        print("No errors found")
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check YAML files in subdomains folder"
    )
    parser.add_argument("folder", type=str, help="Path to subdomains folder")
    args = parser.parse_args()
    main(args)
