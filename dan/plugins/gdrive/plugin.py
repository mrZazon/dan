"""Google Drive plugin — handles OAuth and provides a shared Drive service."""

from __future__ import annotations

import json
import logging
import webbrowser
from pathlib import Path
from typing import Any

from dan.plugins.base import Plugin, PluginMetadata
from dan.plugins.decorators import plugin

logger = logging.getLogger(__name__)

TOKEN_FILE = Path.home() / ".config" / "dan" / "gdrive_token.json"
CLIENT_SECRET_FILE = Path.home() / ".config" / "dan" / "gdrive_client_secret.json"

SCOPES = ["https://www.googleapis.com/auth/drive"]


@plugin
class GoogleDrivePlugin(Plugin):
    """Authenticates with Google Drive and exposes a Drive API service.

    Tools can access the service via GoogleDrivePlugin.get_instance().
    Expects a client secret JSON at ~/.config/dan/gdrive_client_secret.json.
    """

    _instance: GoogleDrivePlugin | None = None

    name = "google_drive"
    description = "Google Drive integration — list, upload, download, search files"

    def __init__(self) -> None:
        self._service: Any = None
        self._credentials: Any = None

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="google_drive",
            version="0.1.0",
            description=self.description,
            author="D.A.N.",
            dependencies=["google-api-python-client", "google-auth-oauthlib"],
        )

    @classmethod
    def get_instance(cls) -> GoogleDrivePlugin | None:
        return cls._instance

    async def initialize(self) -> None:
        """Authenticate with Google Drive."""
        GoogleDrivePlugin._instance = self

        if not CLIENT_SECRET_FILE.exists():
            logger.warning(
                "Google Drive client secret not found at %s. "
                "Download it from https://console.cloud.google.com/apis/credentials "
                "and save as gdrive_client_secret.json in ~/.config/dan/",
                CLIENT_SECRET_FILE,
            )
            return

        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow

            if TOKEN_FILE.exists():
                token_data = json.loads(TOKEN_FILE.read_text())
                self._credentials = Credentials.from_authorized_user_info(
                    token_data, SCOPES
                )

            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                self._credentials.refresh(Request())
                TOKEN_FILE.write_text(
                    json.dumps(json.loads(self._credentials.to_json()))
                )
                logger.info("Refreshed Google Drive token")

            if not self._credentials or not self._credentials.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CLIENT_SECRET_FILE), SCOPES
                )
                logger.info("Opening browser for Google Drive authentication...")
                webbrowser.open(flow.authorization_url()[0])
                self._credentials = flow.run_local_server(port=0)
                TOKEN_FILE.write_text(
                    json.dumps(json.loads(self._credentials.to_json()))
                )
                logger.info("Google Drive authentication complete")

            from googleapiclient.discovery import build

            self._service = build("drive", "v3", credentials=self._credentials)
            logger.info("Google Drive plugin initialized")

        except ImportError:
            logger.warning(
                "Google API libraries not installed. "
                "Run: pip install dan[gdrive] or pip install google-api-python-client google-auth-oauthlib"
            )
        except Exception:
            logger.exception("Failed to initialize Google Drive plugin")

    async def shutdown(self) -> None:
        """Clean up Drive service."""
        self._service = None
        self._credentials = None
        GoogleDrivePlugin._instance = None
        logger.info("Google Drive plugin shut down")

    @property
    def service(self) -> Any:
        if self._service is None:
            raise RuntimeError(
                "Google Drive not authenticated. "
                "Place gdrive_client_secret.json in ~/.config/dan/ and restart."
            )
        return self._service

    @property
    def ready(self) -> bool:
        return self._service is not None
