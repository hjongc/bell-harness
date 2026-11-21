"""Shared code for bin/setup and bin/doctor: what the harness manages and how to read it."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path


SKILL_DIRS = (".claude/skills", ".agents/skills")
MANAGED_ROOTS = (".claude", ".agents", ".codex", ".bell-harness")
NEVER_TOUCH_PREFIXES = ("paseo",)
NEVER_TOUCH_NAMES = ("synced", ".system")
SETTINGS = ".claude/settings.json"
CLAUDE_MD = ".claude/CLAUDE.md"
HOOKS_KEY = "core.hooksPath"
MODEL_LINE = re.compile(r"^model\s*=")


def home_dir():
    return Path(os.path.expanduser("~"))


def tilde(text, home=None):
    """Replace the home path (and its resolved form) with ~ for display."""
    home = str(home or home_dir())
    text = str(text)
    for form in sorted({home, os.path.realpath(home)}, key=len, reverse=True):
        text = text.replace(form, "~")
    return text


def never_touch(name):
    return name.startswith(NEVER_TOUCH_PREFIXES) or name in NEVER_TOUCH_NAMES


def inside(path, root):
    try:
        Path(path).relative_to(root)
        return True
    except ValueError:
        return False


def exists(path):
    """True for anything at path, including a dangling symlink."""
    return os.path.lexists(str(path))


def link_target(path):
    """Absolute target of a symlink, or None when path is not a symlink."""
    path = Path(path)
    if not path.is_symlink():
        return None
    target = Path(os.readlink(str(path)))
    if not target.is_absolute():
        target = path.parent / target
    return Path(os.path.normpath(str(target)))


def previous_roots(home):
    """Yield earlier install roots from backup manifests, including restored ones."""
    current = Path(__file__).resolve().parents[1]
    backups = Path(home) / ".bell-harness/backups"
    for manifest in backups.glob("*/manifest.jsonl"):
        try:
            with manifest.open("rb") as stream:
                for line in stream:
                    try:
                        entry = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(entry, dict) or entry.get("action") != "git-config":
                        continue
                    value = entry.get("value")
                    if isinstance(value, str) and value.endswith("/git/hooks"):
                        root = Path(value).parent.parent
                        if root != current:
                            yield root
        except OSError:
            continue


def is_managed(path, root, old_roots=()):
    target = link_target(path)
    return target is not None and any(inside(target, base) for base in (root, *old_roots))


def skill_names(root):
    skills = Path(root) / "skills"
    if not skills.is_dir():
        return []
    return sorted(p.name for p in skills.iterdir()
                  if (p / "SKILL.md").is_file() and not never_touch(p.name))


def claude_md_line(root):
    return "@{}".format(Path(root) / "global" / "CLAUDE.md")


def claude_md_ok(root, home):
    """~/.claude/CLAUDE.md is a regular file whose first line imports the harness file."""
    path = Path(home) / CLAUDE_MD
    if path.is_symlink() or not path.is_file():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    return bool(lines) and lines[0] == claude_md_line(root)


def desired_links(root, home):
    """(link path, target) pairs that setup creates."""
    root, home = Path(root), Path(home)
    links = []
    for name in skill_names(root):
        for directory in SKILL_DIRS:
            links.append((home / directory / name, root / "skills" / name))
    links.append((home / ".codex/AGENTS.md", root / "global/AGENTS.md"))
    links.append((home / ".codex/rules/bell-harness.rules", root / "config/bell-harness.rules"))
    return links


def skill_entries(home):
    """Entries in the two skill folders, never-touched names excluded."""
    entries = []
    for directory in SKILL_DIRS:
        folder = Path(home) / directory
        if folder.is_dir():
            entries += [e for e in sorted(folder.iterdir()) if not never_touch(e.name)]
    return entries


def stale_links(root, home, old_roots=()):
    """Harness links in the skill folders whose skill no longer exists."""
    names = set(skill_names(root))
    return [e for e in skill_entries(home) if e.name not in names and is_managed(e, root, old_roots)]


def unmanaged_skills(root, home):
    return [e for e in skill_entries(home) if not is_managed(e, root)]


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def safe_relative(rel):
    """A retirable home-relative path: below a managed folder, never a protected entry."""
    parts = Path(rel).parts
    return (
        len(parts) >= 3
        and not Path(rel).is_absolute()
        and ".." not in parts
        and parts[0] in MANAGED_ROOTS
        and not any(never_touch(part) for part in parts[1:])
    )


def retire_config(root, home):
    """Retired home-relative paths and Claude plugin ids, local additions included."""
    config = load_json(Path(root) / "config/retire.json", {}) or {}
    local = load_json(Path(home) / ".bell-harness/retire.local.json", {}) or {}
    paths, plugins = [], []
    for source in (config, local):
        paths += [p for p in source.get("paths", []) if p not in paths and safe_relative(p)]
        plugins += [p for p in source.get("claude_plugins", []) if p not in plugins]
    # Drop a path that lies inside another retired path; moving the parent covers it.
    paths = [p for p in paths if not any(p != q and inside(p, q) for q in paths)]
    return paths, plugins


def retired_names(paths):
    return sorted({Path(p).name[:-3] if p.endswith(".md") else Path(p).name for p in paths})


def plugin_prefixes(plugins):
    return sorted({p.split("@")[0] + ":" for p in plugins})


def settings_fragment(root):
    return load_json(Path(root) / "config/claude-settings.json", {})


def enabled_plugins(settings):
    plugins = settings.get("enabledPlugins") if isinstance(settings, dict) else None
    if not isinstance(plugins, dict):
        return []
    return [name for name, on in plugins.items() if on]


def same(a, b):
    """JSON equality that keeps types apart (0 is not false, 1 is not 1.0)."""
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def contains(items, item):
    return any(same(entry, item) for entry in items)


def settings_changes(current, fragment, prefix=()):
    """Changes needed so current contains fragment.

    Returns ("set", key_path, new_value) and ("add", key_path, item) tuples.
    Objects merge recursively, lists gain missing items, scalars take the fragment value.
    """
    changes = []
    for key, value in fragment.items():
        path = prefix + (key,)
        has = isinstance(current, dict) and key in current
        existing = current.get(key) if has else None
        if isinstance(value, dict) and isinstance(existing, dict):
            changes += settings_changes(existing, value, path)
        elif isinstance(value, list) and isinstance(existing, list):
            changes += [("add", path, item) for item in value if not contains(existing, item)]
        elif not has or not same(existing, value):
            changes.append(("set", path, value))
    return changes


def get_key(data, path):
    for key in path:
        if not isinstance(data, dict) or key not in data:
            return False, None
        data = data[key]
    return True, data


def set_key(data, path, value):
    for key in path[:-1]:
        if not isinstance(data.get(key), dict):
            data[key] = {}
        data = data[key]
    data[path[-1]] = value


def delete_key(data, path):
    for key in path[:-1]:
        data = data.get(key)
        if not isinstance(data, dict):
            return
    data.pop(path[-1], None)


def sha256(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
        return None


def git_global(key):
    try:
        result = subprocess.run(
            ["git", "config", "--global", "--get", key],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def which(name):
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(folder) / name
        if candidate.is_file() and os.access(str(candidate), os.X_OK):
            return candidate
    return None


def pinned_models(home):
    """`model =` lines at the top level or in [profiles.*] of the Codex config files."""
    codex = Path(home) / ".codex"
    files = [codex / "config.toml"] + sorted(codex.glob("*.config.toml"))
    hits = []
    for path in files:
        if not path.is_file():
            continue
        table = None
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("["):
                table = stripped.strip("[]").strip()
                continue
            if MODEL_LINE.match(stripped) and (table is None or table.startswith("profiles.")):
                hits.append("{}:{} [{}]".format(path, number, table or "top level"))
    return hits
