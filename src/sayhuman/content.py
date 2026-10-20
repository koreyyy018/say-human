"""Bundled read-only content uses importlib.resources for installed wheels."""
import json
from importlib.resources import files
from .models import Concept


def load_asset(filename: str):
    if filename not in {"concepts.json", "concepts.zh-CN.json", "corporate-phrases.json", "gold-standard.json"}:
        raise ValueError("Unrecognized asset")
    return json.loads(files("sayhuman").joinpath("assets", filename).read_text(encoding="utf-8"))


def concepts() -> list[Concept]:
    return [Concept.from_dict(x) for x in load_asset("concepts.json")]


def phrasebook() -> list[dict]:
    return load_asset("corporate-phrases.json")


def gold_examples() -> list[dict]:
    return load_asset("gold-standard.json")


def localized_concepts() -> dict:
    return load_asset("concepts.zh-CN.json")
