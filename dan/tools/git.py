from __future__ import annotations
from typing import Any
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.services.shell import ShellService


@tool
class GitStatusTool(Tool):
    name = "git_status"
    description = "Shows git status"
    aliases = ("status", "git status")
    intents = {"git status": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("git status")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitLogTool(Tool):
    name = "git_log"
    description = "Shows git log"
    aliases = ("log", "git log")
    intents = {"git log": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("git log --oneline -20")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitDiffTool(Tool):
    name = "git_diff"
    description = "Shows git diff"
    aliases = ("diff", "git diff")
    intents = {"git diff": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("git diff")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitAddTool(Tool):
    name = "git_add"
    description = "Stages files"
    aliases = ("add", "git add")
    intents = {"git add": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        result = await self._service.execute(f"git add {path}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitCommitTool(Tool):
    name = "git_commit"
    description = "Commits changes"
    aliases = ("commit", "git commit")
    intents = {"git commit": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        message = kwargs.get("message", "Update")
        result = await self._service.execute(f'git commit -m "{message}"')
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitPushTool(Tool):
    name = "git_push"
    description = "Pushes changes"
    aliases = ("push", "git push")
    intents = {"git push": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("git push")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitPullTool(Tool):
    name = "git_pull"
    description = "Pulls changes"
    aliases = ("pull", "git pull")
    intents = {"git pull": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("git pull")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitBranchTool(Tool):
    name = "git_branch"
    description = "Lists branches"
    aliases = ("branch", "git branch")
    intents = {"git branch": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("git branch -a")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitCheckoutTool(Tool):
    name = "git_checkout"
    description = "Switches branch"
    aliases = ("checkout", "git checkout")
    intents = {"git checkout": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        branch = kwargs.get("branch", "")
        result = await self._service.execute(f"git checkout {branch}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitStashTool(Tool):
    name = "git_stash"
    description = "Stashes changes"
    aliases = ("stash", "git stash")
    intents = {"git stash": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("git stash")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitCloneTool(Tool):
    name = "git_clone"
    description = "Clones a repository"
    aliases = ("clone", "git clone")
    intents = {"git clone": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "")
        result = await self._service.execute(f"git clone {url}")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})


@tool
class GitRemoteTool(Tool):
    name = "git_remote"
    description = "Shows git remotes"
    aliases = ("remote", "git remote")
    intents = {"git remote": 5}

    def __init__(self) -> None:
        self._service = ShellService()

    async def execute(self, **kwargs: Any) -> ToolResult:
        result = await self._service.execute("git remote -v")
        return ToolResult(success=result.success, message=result.stdout or result.stderr, data={"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})
