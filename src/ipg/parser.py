import json
import yaml

from pathlib import Path
from typing import Any, Dict
from pydantic import ValidationError

from src.ipg.models import Incident


class IncidentParseError(Exception):
    """Raised when an incident file cannot be parsed or validated."""


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise IncidentParseError(f"Input file not found: {path}") from e
    except OSError as e:
        raise IncidentParseError(f"Failed to read input file: {path} ({e})") from e


def _parse_yaml(text: str) -> Dict[str, Any]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise IncidentParseError(f"Invalid YAML: {e}") from e

    if not isinstance(data, dict):
        raise IncidentParseError("YAML root must be a mapping/object.")
    return data


def _parse_json(text: str) -> Dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise IncidentParseError(f"Invalid JSON: {e}") from e

    if not isinstance(data, dict):
        raise IncidentParseError("JSON root must be an object.")
    return data


def load_incident(path: Path) -> Incident:
    """
    Load and validate an incident definition file (YAML or JSON) into an Incident model.

    Supported extensions:
      - .yml / .yaml
      - .json
    """
    if not path.suffix:
        raise IncidentParseError("Input file must have an extension (.yml/.yaml/.json).")

    ext = path.suffix.lower()
    text = _read_text(path)

    if ext in {".yml", ".yaml"}:
        raw = _parse_yaml(text)
    elif ext == ".json":
        raw = _parse_json(text)
    else:
        raise IncidentParseError(f"Unsupported file type: {ext}. Use .yml/.yaml or .json")

    try:
        return Incident.model_validate(raw)
    except ValidationError as e:
        errors = []
        for err in e.errors():
            loc = ".".join(str(x) for x in err.get("loc", []))
            msg = err.get("msg", "Invalid value")
            errors.append(f"- {loc}: {msg}" if loc else f"- {msg}")
        detail = "\n".join(errors)
        raise IncidentParseError(f"Schema validation failed:\n{detail}") from e
