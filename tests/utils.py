"""test utility function"""
import yaml


def load_yml(file_name) -> dict[str, dict[str, float | str]]:
    with open(file_name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
