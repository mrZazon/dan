from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

DESTRUCTIVE_PATTERNS: list[tuple[str, str]] = [
    (r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+|--recursive)", "Recursive file deletion"),
    (r"\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+|--force)", "Force file deletion"),
    (r"\brm\s+-rf\s", "Recursive force deletion"),
    (r"\brm\s+-fr\s", "Recursive force deletion"),
    (r"\bmkfs\.\w+\s", "Format disk/filesystem"),
    (r"\bdd\s+.*of=/dev/", "Direct disk write"),
    (r"\bchmod\s+-R\s+777\s", "Recursive open permissions"),
    (r"\bsudo\s+rm\b", "Root file deletion"),
    (r"\bsudo\s+chmod\b", "Root permission change"),
    (r"\bsudo\s+chown\b", "Root ownership change"),
    (r">\s*/dev/sd[a-z]", "Direct disk overwrite"),
    (r"\bkillall\b", "Kill all processes"),
    (r"\bpkill\s+-9\b", "Force kill processes"),
    (r"\bshutdown\b", "System shutdown"),
    (r"\breboot\b", "System reboot"),
    (r"\binit\s+[06]\b", "System halt/reboot"),
    (r"\bsystemctl\s+stop\b", "Stop system service"),
    (r"\bsystemctl\s+disable\b", "Disable system service"),
    (r"\biptables\s+-F\b", "Flush firewall rules"),
    (r"\bdrop\s+table\b", "Database drop table"),
    (r"\bdrop\s+database\b", "Database drop database"),
    (r"\bDELETE\s+FROM\b", "Database delete rows"),
    (r"\bTRUNCATE\b", "Database truncate"),
    (r"\bgit\s+push\s+--force\b", "Force git push"),
    (r"\bgit\s+reset\s+--hard\b", "Hard git reset"),
    (r"\bgit\s+clean\s+-fd\b", "Git clean untracked"),
]

SAFE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bls\b"),
    re.compile(r"\bcat\b"),
    re.compile(r"\bgrep\b"),
    re.compile(r"\bfind\b"),
    re.compile(r"\bdate\b"),
    re.compile(r"\bwhoami\b"),
    re.compile(r"\buptime\b"),
    re.compile(r"\bps\b"),
    re.compile(r"\btop\b"),
    re.compile(r"\bdf\b"),
    re.compile(r"\bdu\b"),
    re.compile(r"\bfree\b"),
    re.compile(r"\buname\b"),
    re.compile(r"\bping\b"),
    re.compile(r"\bcurl\b"),
    re.compile(r"\bwget\b"),
]


@dataclass
class SafetyVerdict:
    safe: bool
    reason: str = ""
    command: str = ""


def check_command_safety(command: str) -> SafetyVerdict:
    """Check if a shell command is potentially destructive."""
    cmd = command.strip()

    for pat in SAFE_PATTERNS:
        if pat.search(cmd):
            return SafetyVerdict(safe=True, command=cmd)

    for pattern, reason in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return SafetyVerdict(safe=False, reason=reason, command=cmd)

    if cmd.startswith("sudo"):
        return SafetyVerdict(safe=False, reason="Root privilege escalation", command=cmd)

    return SafetyVerdict(safe=True, command=cmd)


TOOL_DANGER_LEVELS: dict[str, str] = {
    "sudo": "dangerous",
    "command": "dangerous",
    "kill_process": "dangerous",
    "kill_by_name": "dangerous",
    "delete_file": "dangerous",
    "chmod_file": "dangerous",
    "chown": "dangerous",
    "service_stop": "caution",
    "service_disable": "caution",
    "service_mask": "caution",
    "docker_rm": "caution",
    "docker_stop": "caution",
    "git_push": "caution",
    "git_commit": "caution",
    "apt_install": "caution",
    "apt_upgrade": "caution",
    "pip_install": "caution",
    "npm_install": "caution",
}

DANGEROUS = "dangerous"
CAUTION = "caution"
SAFE = "safe"


def get_tool_danger_level(tool_name: str) -> str:
    return TOOL_DANGER_LEVELS.get(tool_name, SAFE)
