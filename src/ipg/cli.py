import typer

from pathlib import Path
from typing import Optional

from ipg.exporters import export_all
from ipg.parser import IncidentParseError, load_incident
from ipg.renderer import write_postmortem_files

app = typer.Typer(
    name="ipg",
    help="Incident Postmortem Generator — generate Markdown postmortems from YAML/JSON incident data.",
    add_completion=False,
)

DEFAULT_TEMPLATE = "default.md.j2"


def _default_templates_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


def _err(message: str) -> None:
    typer.echo(message, err=True)


@app.command("generate")
def generate(
    input_file: Path = typer.Option(
        ...,
        "--input",
        "-i",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to incident file (.yml/.yaml/.json).",
    ),
    out_dir: Path = typer.Option(
        Path("out"),
        "--out",
        "-o",
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        help="Output directory (default: ./out).",
    ),
    template: str = typer.Option(
        DEFAULT_TEMPLATE,
        "--template",
        "-t",
        help="Template filename inside templates directory (default: default.md.j2).",
    ),
    templates_dir: Optional[Path] = typer.Option(
        None,
        "--templates-dir",
        help="Optional custom templates directory (defaults to package templates/).",
    ),
    no_json: bool = typer.Option(
        False,
        "--no-json",
        help="Do not export postmortem.json.",
    ),
    no_csv: bool = typer.Option(
        False,
        "--no-csv",
        help="Do not export action_items.csv.",
    ),
) -> None:
    """
    Generate a postmortem Markdown file (and optional JSON/CSV exports) from an incident file.
    """
    tdir = templates_dir or _default_templates_dir()

    try:
        incident = load_incident(input_file)

        md_path = write_postmortem_files(
            incident=incident,
            out_dir=out_dir,
            templates_dir=tdir,
            template_name=template,
        )

        exports = {}
        if not (no_json and no_csv):
            exports = export_all(incident, out_dir=out_dir)

            if no_json and "json" in exports:
                try:
                    exports["json"].unlink(missing_ok=True)
                except OSError:
                    pass
                exports.pop("json", None)

            if no_csv and "action_items_csv" in exports:
                try:
                    exports["action_items_csv"].unlink(missing_ok=True)
                except OSError:
                    pass
                exports.pop("action_items_csv", None)

        typer.echo(f"✅ Generated: {md_path}")
        if exports.get("json"):
            typer.echo(f"✅ Exported:  {exports['json']}")
        if exports.get("action_items_csv"):
            typer.echo(f"✅ Exported:  {exports['action_items_csv']}")

    except IncidentParseError as e:
        _err(f"❌ Input error:\n{e}")
        raise typer.Exit(code=2)
    except FileNotFoundError as e:
        _err(f"❌ File not found: {e}")
        raise typer.Exit(code=2)
    except Exception as e:
        _err(f"❌ Unexpected error: {e}")
        raise typer.Exit(code=1)


@app.command("validate")
def validate(
    input_file: Path = typer.Option(
        ...,
        "--input",
        "-i",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to incident file (.yml/.yaml/.json).",
    ),
) -> None:
    """
    Validate an incident file against the schema (no output files written).
    """
    try:
        incident = load_incident(input_file)
        typer.echo(f"✅ Valid: {input_file}")
        typer.echo(f"   Incident ID: {incident.incident_id}")
        typer.echo(f"   Title:       {incident.title}")
        typer.echo(f"   Severity:    {incident.severity}")
        typer.echo(f"   Status:      {incident.status}")
    except IncidentParseError as e:
        _err(f"❌ Validation failed:\n{e}")
        raise typer.Exit(code=2)
    except Exception as e:
        _err(f"❌ Unexpected error: {e}")
        raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
