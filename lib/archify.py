"""Provision the pinned, optional Archify skill in the harness checkout."""
import hashlib
import io
import os
import stat
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


VERSION = "v3.2.0"
URL = f"https://github.com/tt-a1i/archify/releases/download/{VERSION}/archify.zip"
SHA256 = "70e210265c59f24dcbdf2a502ff671104b5454e7ee7d3554aecd86bad32384f5"
MAX_DOWNLOAD = 8 * 1024 * 1024
MARKER = ".bell-harness-sha256"


def cache_path(root):
    return Path(root) / ".harness-tools" / f"archify-{VERSION}"


def cached_skill(root):
    path = cache_path(root)
    marker = path / MARKER
    if (path.parent.is_symlink() or path.is_symlink() or marker.is_symlink()
            or not (path / "SKILL.md").is_file()
            or not (path / "bin/archify.mjs").is_file()):
        return None
    try:
        return path if marker.read_text(encoding="ascii").strip() == SHA256 else None
    except (OSError, UnicodeError):
        return None


def provision(root):
    """Publish a verified release atomically, or reuse an existing complete release."""
    path = cache_path(root)
    if cached_skill(root) is not None:
        return
    if path.parent.is_symlink() or os.path.lexists(path):
        raise ValueError("Archify cache is a symlink or incomplete; inspect it before retrying")
    with urllib.request.urlopen(URL, timeout=30) as response:
        data = response.read(MAX_DOWNLOAD + 1)
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Archify release does not match the pinned SHA-256")

    path.parent.mkdir(exist_ok=True)
    if path.parent.is_symlink():
        raise ValueError("Archify cache directory is a symlink")
    with tempfile.TemporaryDirectory(prefix=".archify-", dir=path.parent) as temporary:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for member in archive.infolist():
                parts = PurePosixPath(member.filename).parts
                if (not parts or parts[0] != "archify" or ".." in parts
                        or stat.S_ISLNK(member.external_attr >> 16)):
                    raise ValueError("Archify archive has an unexpected entry")
            archive.extractall(temporary)
        release = Path(temporary) / "archify"
        if not ((release / "SKILL.md").is_file() and (release / "bin/archify.mjs").is_file()):
            raise ValueError("Archify archive is missing the skill or its CLI")
        (release / MARKER).write_text(SHA256 + "\n", encoding="ascii")
        try:
            release.rename(path)
        except OSError:
            if cached_skill(root) is None:
                raise
