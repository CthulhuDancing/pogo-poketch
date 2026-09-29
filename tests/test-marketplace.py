import json
import re
import sys
from pathlib import Path
from typing import NoReturn


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"

SEMVER = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?"
    r"(?:\+[0-9A-Za-z.-]+)?$"
)

errors = []


def fail(message) -> NoReturn:
    """Hard stop: nothing else can run."""
    print(f"FAIL: {message}")
    sys.exit(1)


def error(message):
    """Soft failure: record it and keep going."""
    errors.append(message)


def load_json(path):
    """Raises ValueError so the caller decides whether this is a hard or soft stop."""
    if not path.is_file():
        raise ValueError(f"Missing file: {path.relative_to(ROOT)}")

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")


def check_plugin(entry, index, seen_names):
    label = f"plugins[{index}]"

    # Guards: each `return` means the checks below would crash without it.
    if not isinstance(entry, dict):
        error(f"{label}: entry must be an object, got {type(entry).__name__}")
        return

    name = entry.get("name")

    if not isinstance(name, str) or not name:
        error(f"{label}: missing a valid name")
        return

    label = name

    # Independent: record it, keep checking this entry.
    if name in seen_names:
        error(f"{label}: duplicate marketplace plugin name")
    seen_names.add(name)

    source = entry.get("source")

    if not isinstance(source, dict):
        error(f"{label}: missing source configuration")
        return

    if source.get("source") != "local":
        error(f"{label}: expected local source")
        return

    relative_path = source.get("path")

    if not isinstance(relative_path, str) or not relative_path.startswith("./"):
        error(f"{label}: source path must begin with './'")
        return

    plugin_dir = (ROOT / relative_path).resolve()

    try:
        plugin_dir.relative_to(ROOT)
    except ValueError:
        error(f"{label}: source path escapes repository root")
        return

    if not plugin_dir.is_dir():
        error(f"{label}: plugin directory does not exist: {relative_path}")
        return

    try:
        manifest = load_json(plugin_dir / "plugin.json")
    except ValueError as exc:
        error(f"{label}: {exc}")
        return

    if not isinstance(manifest, dict):
        error(f"{label}: plugin.json must contain an object")
        return

    # Independent checks on the manifest.
    manifest_name = manifest.get("name")

    if manifest_name != name:
        error(
            f"{label}: marketplace name does not match "
            f"plugin.json name '{manifest_name}'"
        )

    schema = manifest.get("$schema")

    if not isinstance(schema, str) or not schema:
        error(f"{label}: plugin.json is missing $schema")

    version = manifest.get("version")

    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        error(f"{label}: invalid semantic version '{version}'")

    skills_dir = plugin_dir / "skills"

    if skills_dir.exists():
        if not skills_dir.is_dir():
            error(f"{label}: skills exists but is not a directory")
            return

        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue

            if not (skill_dir / "SKILL.md").is_file():
                error(
                    f"{label}: skill '{skill_dir.name}' "
                    "does not contain SKILL.md"
                )


def main():
    # Hard stops: without these there is nothing to loop over.
    try:
        marketplace = load_json(MARKETPLACE)
    except ValueError as exc:
        fail(str(exc))

    if not isinstance(marketplace, dict):
        fail("marketplace.json must contain an object")

    plugins = marketplace.get("plugins")

    if not isinstance(plugins, list):
        fail("marketplace.json must contain a plugins array")

    if not plugins:
        fail("marketplace.json contains no plugins")

    seen_names = set()

    for index, entry in enumerate(plugins):
        check_plugin(entry, index, seen_names)

    if errors:
        for message in errors:
            print(f"FAIL: {message}")
        print(f"\n{len(errors)} problem(s) found")
        sys.exit(1)

    print(
        f"PASS: marketplace integrity verified "
        f"for {len(plugins)} plugin(s)"
    )


if __name__ == "__main__":
    main()