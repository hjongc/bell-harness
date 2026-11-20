import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "git/hooks"


def make_env(tmp):
    tmp = Path(tmp)
    home = tmp / "home"
    home.mkdir(parents=True, exist_ok=True)
    gitconfig = tmp / "gitconfig"
    gitconfig.write_text("", encoding="utf-8")
    return {
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "CODEX_HOME": str(home / ".codex"),
        "CLAUDE_CONFIG_DIR": str(home / ".claude"),
        "TMPDIR": str(tmp),
        "PATH": f"{tmp}/bin:/usr/bin:/bin",
        "GIT_CONFIG_GLOBAL": str(gitconfig),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
        "PYTHONIOENCODING": "utf-8",
    }


def write_stub(tmp, name, body):
    path = Path(tmp) / "bin" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def init_repo(path, env):
    Path(path).mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=path, env=env, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "--file", env["GIT_CONFIG_GLOBAL"], "core.hooksPath", str(HOOKS)],
        cwd=path,
        env=env,
        check=True,
        capture_output=True,
    )
