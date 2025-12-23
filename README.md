# Incident Postmortem Generator (IPG)

Generate clean, consistent **incident postmortems** from a structured YAML/JSON incident file.

IPG turns your incident notes into:
- **`postmortem-INCIDENT_ID.md`** (publishable Markdown)
- **`postmortem-INCIDENT_ID.json`** (structured export)
- **`action_items-INCIDENT_ID.csv`** (easy to import into a tracker/spreadsheet)

---

## Why this project

Teams often write postmortems in inconsistent formats, which makes learning and follow-up harder.  
This tool enforces a **repeatable incident schema** and produces a **standardized postmortem** output.

---

## Features

- ✅ YAML/JSON input with strict schema validation (Pydantic)
- ✅ Deterministic Markdown output via Jinja2 templates
- ✅ Exports: JSON + action-items CSV
- ✅ Clear CLI UX + exit codes (0 success, 2 input/schema error, 1 unexpected error)
- ✅ Custom templates supported (`--templates-dir`, `--template`)

---

## Project structure

```

incident-postmortem-generator/
examples_in/
incident.sample.yml
src/ipg/
cli.py
models.py
parser.py
renderer.py
exporters.py
templates/default.md.j2
tests/
test_parser.py
test_renderer.py

````

---

## Requirements

- Python **3.12+** recommended

Dependencies (installed via your package manager):
- typer
- pydantic
- pyyaml
- jinja2

---

## Installation

### Option A) Using `uv` (recommended)
```bash
uv sync
````

Run via:

```bash
uv run ipg --help
```

### Option B) Standard pip install (editable)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run via:

```bash
ipg --help
```

---

## Usage

### 1) Validate an incident file

```bash
ipg validate -i examples/incident.sample.yml
```

### 2) Generate outputs

```bash
ipg generate -i examples/incident.sample.yml -o out
```

This will create (for example):

* `out/postmortem-INC-2025-0017.md`
* `out/postmortem-INC-2025-0017.json`
* `out/action_items-INC-2025-0017.csv`

### 3) Disable exports

```bash
ipg generate -i examples/incident.sample.yml -o out --no-json
ipg generate -i examples/incident.sample.yml -o out --no-csv
```

### 4) Use a custom template directory

```bash
ipg generate -i examples/incident.sample.yml -o out --templates-dir ./my-templates --template custom.md.j2
```

---

## Input format (schema)

See: `examples/incident.sample.yml`

High-level fields:

* `incident_id`, `title`, `severity`, `status`
* `service` (name, owner_team, environment, tier)
* `time` (start/end/detected/mitigated + timezone)
* `summary`, `impact`, `detection`
* `timeline[]` events (sorted ascending by time)
* `root_cause`, `response`, `communication`
* `action_items[]`, `tags`, `references`

---

## Templates

Templates live in:

* `src/ipg/templates/default.md.j2`

Templates use Jinja2 and receive:

* `incident` (validated Pydantic model)

You can create your own templates and point to them using `--templates-dir`.

---

## Development

### Run locally

```bash
uv run ipg validate -i examples/incident.sample.yml
uv run ipg generate -i examples/incident.sample.yml -o out
```

### Run tests

```bash
uv run pytest
```

---

## TODO (Roadmap)

### GitHub Actions

* [ ] Add CI workflow to run:

  * `ruff` (lint)
  * `pytest` (tests)
* [ ] Add release workflow:

  * build package
  * attach artifacts on version tags

### Tests

* [ ] Add snapshot testing for Markdown output (golden file)
* [ ] Add tests for JSON/CSV exporters
* [ ] Add tests for invalid YAML/JSON parsing edge cases

### Features (nice-to-have)

* [ ] `--format` option (markdown/json/csv selection)
* [ ] GitHub Issue importer (pull title/body/timeline signals)
* [ ] Postmortem quality checks (missing sections detector)
* [ ] Action-items “owner resolution” (map team aliases)

---

## License

[MIT License](LICENCE) © 2025 Mohamadreza Najarbashi
