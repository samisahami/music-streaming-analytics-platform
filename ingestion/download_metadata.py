"""
Download public music metadata.

Sprint 2:
Read the source dataset identifier from project configuration.
"""

from pathlib import Path
from typing import Any

import yaml
from datasets import load_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "project.yml"


def load_config(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    """Load project configuration from YAML."""

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if not config:
        raise ValueError("The project configuration file is empty.")

    return config


def main() -> None:
    """Download the configured music metadata dataset."""

    config = load_config()

    dataset_name = config["datasets"]["music_metadata"]["dataset"]

    print(f"Connecting to dataset: {dataset_name}")

    dataset = load_dataset(
        dataset_name,
        split="train",
    )

    print(dataset)


if __name__ == "__main__":
    main()