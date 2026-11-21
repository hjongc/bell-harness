import re


SECRET_PATTERNS = [
    ("anthropic-key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai-key", re.compile(r"(?<![A-Za-z0-9])sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{32,}")),
    (
        "github-token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{20,})"),
    ),
    ("aws-key", re.compile(r"\bA(?:KI|SI)A[0-9A-Z]{16}\b")),
    (
        "private-key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    ),
    (
        "assigned-secret",
        re.compile(
            r"(?<![\w-])[\w-]*(?:api[_-]?key|secret|password|token)[\w-]*[ \t]*[:=][ \t]*"
            r'(?:"(?!\$\{|\{\{|<)(?=[^"\s]*[a-z])(?=[^"\s]*[0-9])[^"\s]{12,}"'
            r"|'(?!\$\{|\{\{|<)(?=[^'\s]*[a-z])(?=[^'\s]*[0-9])[^'\s]{12,}')",
            re.IGNORECASE,
        ),
    ),
]

HOME_PATHS = [
    re.compile(r"/Us[e]rs/[^/\s]+"),
    re.compile(r"/home/[a-z][^/\s]*"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\/\s]+", re.IGNORECASE),
]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")
EMAIL_ALLOW = ("@users.noreply.github.com", "@example.com", "@example.org", "@example.net")
