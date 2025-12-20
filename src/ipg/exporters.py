import csv
import json

from pathlib import Path
from typing import Any, Dict

from ipg.models import Incident


def export_json(incident: Incident, out_path: Path) -> Path:
    """
    Export the full incident data as JSON (normalized & validated).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    data: Dict[str, Any] = incident.model_dump(mode="json")

    out_path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out_path


def export_action_items_csv(incident: Incident, out_path: Path) -> Path:
    """
    Export action items to CSV for easy importing into spreadsheets/tools.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "id",
        "title",
        "owner",
        "priority",
        "due",
        "type",
        "status",
        "success_criteria",
        "links",
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for a in incident.action_items:
            links_joined = "; ".join(
                f"{l.label}: {str(l.url)}" for l in (a.links or [])
            )
            writer.writerow(
                {
                    "id": a.id,
                    "title": a.title,
                    "owner": a.owner,
                    "priority": a.priority,
                    "due": a.due.isoformat(),
                    "type": a.type,
                    "status": a.status,
                    "success_criteria": a.success_criteria or "",
                    "links": links_joined,
                }
            )

    return out_path


def export_all(
    incident: Incident,
    out_dir: Path,
    json_name: str = "postmortem",
    action_items_csv_name: str = "action_items",
) -> Dict[str, Path]:
    """
    Convenience exporter that writes common files to out_dir.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = export_json(incident, out_dir / f"{json_name}-{incident.incident_id}.json")
    csv_path = export_action_items_csv(incident, out_dir / f"{action_items_csv_name}-{incident.incident_id}.csv")

    return {"json": json_path, "action_items_csv": csv_path}
