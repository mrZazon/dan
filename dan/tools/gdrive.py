"""Tools for Google Drive operations via the gdrive plugin."""

from __future__ import annotations

import io
from typing import Any

from dan.plugins.gdrive.plugin import GoogleDrivePlugin
from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool


def _get_service():
    plugin = GoogleDrivePlugin.get_instance()
    if plugin is None or not plugin.ready:
        raise RuntimeError(
            "Google Drive plugin not initialized. "
            "Run with --plugins or check that gdrive_client_secret.json exists."
        )
    return plugin.service


@tool
class DriveListTool(Tool):
    name = "drive_list"
    description = "Lists files and folders in Google Drive"
    aliases = ("drive files", "google drive list", "gdrive list")
    intents = {"list drive files": 5, "google drive files": 4, "show drive": 3}

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query", "trashed=false")
        page_size = min(kwargs.get("page_size", 20), 100)

        try:
            service = _get_service()
            results = (
                service.files()
                .list(
                    q=query,
                    pageSize=page_size,
                    fields="files(id, name, mimeType, size, modifiedTime)",
                )
                .execute()
            )
            files = results.get("files", [])
            if not files:
                return ToolResult(success=True, message="No files found.")
            lines = []
            for f in files:
                size = f.get("size", "?")
                mtime = f.get("modifiedTime", "?")[:10]
                kind = "📁" if f["mimeType"] == "application/vnd.google-apps.folder" else "📄"
                lines.append(f"  {kind} {f['name']:40s} {size:>8s}  {mtime}")
            msg = f"Files ({len(files)}):\n" + "\n".join(lines)
            return ToolResult(success=True, message=msg, data={"files": files})
        except RuntimeError as e:
            return ToolResult(success=False, message=str(e))
        except Exception as e:
            return ToolResult(success=False, message=f"Drive error: {e}")


@tool
class DriveUploadTool(Tool):
    name = "drive_upload"
    description = "Uploads a file to Google Drive"
    aliases = ("upload to drive", "gdrive upload", "drive upload")
    intents = {"upload to drive": 5, "upload file": 4, "drive upload": 4}

    async def execute(self, **kwargs: Any) -> ToolResult:
        from pathlib import Path

        file_path = Path(kwargs.get("path", ""))
        parent_id = kwargs.get("parent_id", "root")

        if not file_path.exists():
            return ToolResult(success=False, message=f"File not found: {file_path}")

        try:
            service = _get_service()
            from googleapiclient.http import MediaFileUpload

            name = kwargs.get("name", file_path.name)
            media = MediaFileUpload(str(file_path), resumable=True)
            body = {"name": name, "parents": [parent_id]}
            uploaded = (
                service.files()
                .create(body=body, media_body=media, fields="id, name, size")
                .execute()
            )
            return ToolResult(
                success=True,
                message=f"Uploaded '{uploaded['name']}' (id: {uploaded['id']})",
                data={"id": uploaded["id"], "name": uploaded["name"]},
            )
        except RuntimeError as e:
            return ToolResult(success=False, message=str(e))
        except Exception as e:
            return ToolResult(success=False, message=f"Upload error: {e}")


@tool
class DriveDownloadTool(Tool):
    name = "drive_download"
    description = "Downloads a file from Google Drive"
    aliases = ("download from drive", "gdrive download", "drive download")
    intents = {"download from drive": 5, "download file": 4, "drive download": 4}

    async def execute(self, **kwargs: Any) -> ToolResult:
        from pathlib import Path

        file_id = kwargs.get("file_id", "")
        output = Path(kwargs.get("output", "."))

        if not file_id:
            return ToolResult(success=False, message="file_id required")

        try:
            service = _get_service()
            from googleapiclient.http import MediaIoBaseDownload

            meta = service.files().get(fileId=file_id, fields="name, mimeType").execute()
            name = kwargs.get("name", meta["name"])
            out_path = output / name

            request = service.files().get_media(fileId=file_id)
            with io.FileIO(str(out_path), "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()

            return ToolResult(
                success=True,
                message=f"Downloaded '{name}' to {out_path}",
                data={"path": str(out_path), "name": name},
            )
        except RuntimeError as e:
            return ToolResult(success=False, message=str(e))
        except Exception as e:
            return ToolResult(success=False, message=f"Download error: {e}")


@tool
class DriveSearchTool(Tool):
    name = "drive_search"
    description = "Searches for files in Google Drive"
    aliases = ("search drive", "gdrive search", "find in drive")
    intents = {"search drive": 5, "find in drive": 4, "search google drive": 4}

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query", "")
        page_size = min(kwargs.get("page_size", 20), 100)

        if not query:
            return ToolResult(success=False, message="query required")

        try:
            service = _get_service()
            safe_query = query.replace("'", "\\'")
            results = (
                service.files()
                .list(
                    q=f"name contains '{safe_query}' and trashed=false",
                    pageSize=page_size,
                    fields="files(id, name, mimeType, size, modifiedTime)",
                )
                .execute()
            )
            files = results.get("files", [])
            if not files:
                return ToolResult(success=True, message=f"No files matching '{query}'.")
            lines = []
            for f in files:
                kind = "📁" if f["mimeType"] == "application/vnd.google-apps.folder" else "📄"
                lines.append(f"  {kind} {f['name']:40s} {f['id']}")
            msg = f"Results for '{query}' ({len(files)}):\n" + "\n".join(lines)
            return ToolResult(success=True, message=msg, data={"files": files})
        except RuntimeError as e:
            return ToolResult(success=False, message=str(e))
        except Exception as e:
            return ToolResult(success=False, message=f"Search error: {e}")


@tool
class DriveMkdirTool(Tool):
    name = "drive_mkdir"
    description = "Creates a folder in Google Drive"
    aliases = ("create folder drive", "gdrive mkdir", "drive mkdir")
    intents = {"create drive folder": 5, "make drive folder": 4, "new drive folder": 4}

    async def execute(self, **kwargs: Any) -> ToolResult:
        name = kwargs.get("name", "")
        parent_id = kwargs.get("parent_id", "root")

        if not name:
            return ToolResult(success=False, message="name required")

        try:
            service = _get_service()
            body = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id],
            }
            folder = service.files().create(body=body, fields="id, name").execute()
            return ToolResult(
                success=True,
                message=f"Created folder '{folder['name']}' (id: {folder['id']})",
                data={"id": folder["id"], "name": folder["name"]},
            )
        except RuntimeError as e:
            return ToolResult(success=False, message=str(e))
        except Exception as e:
            return ToolResult(success=False, message=f"Error creating folder: {e}")
