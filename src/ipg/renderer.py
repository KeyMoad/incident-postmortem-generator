from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ipg.models import Incident


def _build_jinja_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_markdown(
    incident: Incident,
    templates_dir: Path,
    template_name: str = "default.md.j2",
) -> str:
    """
    Render a postmortem Markdown string using a Jinja2 template.
    """
    env = _build_jinja_env(templates_dir)
    template = env.get_template(template_name)
    return template.render(incident=incident).rstrip() + "\n"


def write_postmortem_files(
    incident: Incident,
    out_dir: Path,
    templates_dir: Path,
    template_name: str = "default.md.j2",
) -> Path:
    """
    Writes postmortem.md to out_dir and returns the file path.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    md = render_markdown(incident=incident, templates_dir=templates_dir, template_name=template_name)

    out_path = out_dir / f"postmortem-{incident.incident_id}.md"
    out_path.write_text(md, encoding="utf-8")
    return out_path
