#!/usr/bin/env python3
"""Quick validation script for Nexus skills."""

import re
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Nexus skill frontmatter fields
ALLOWED_PROPERTIES = {"name", "description", "user-invocable", "argument-hint"}
REQUIRED_PROPERTIES = {"name", "description"}


def validate_skill(skill_path: str | Path) -> tuple[bool, str]:
    skill_path = Path(skill_path)

    skill_md = skill_path / "skill.md"
    if not skill_md.exists():
        return False, "skill.md not found"

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format (no closing ---)"

    frontmatter_text = match.group(1)

    if HAS_YAML:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return False, "Frontmatter must be a YAML dictionary"
        except yaml.YAMLError as e:
            return False, f"Invalid YAML in frontmatter: {e}"
    else:
        # Fallback: minimal line-based parsing when PyYAML is not available
        frontmatter = {}
        for line in frontmatter_text.splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                frontmatter[key.strip()] = val.strip().strip('"').strip("'")

    unexpected = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected:
        return False, (
            f"Unexpected key(s) in frontmatter: {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    for field in REQUIRED_PROPERTIES:
        if field not in frontmatter:
            return False, f"Missing required field: '{field}'"

    name = str(frontmatter.get("name", "")).strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, f"Name '{name}' must be kebab-case (lowercase letters, digits, hyphens)"
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        if len(name) > 64:
            return False, f"Name too long ({len(name)} chars, max 64)"

    description = str(frontmatter.get("description", "")).strip()
    if description:
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets"
        if len(description) > 1024:
            return False, f"Description too long ({len(description)} chars, max 1024)"
        if len(description) < 20:
            return False, f"Description too short ({len(description)} chars) — should describe when to invoke and what it does"

    user_invocable = frontmatter.get("user-invocable")
    if user_invocable is not None and not isinstance(user_invocable, bool):
        return False, f"'user-invocable' must be a boolean (true/false), got: {user_invocable!r}"

    body = content[match.end():].strip()
    if not body:
        return False, "skill.md has no body content after the frontmatter"

    return True, "Skill is valid"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
