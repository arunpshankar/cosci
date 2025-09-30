"""
Authentication Module for Cosci SDK
====================================
Handles Google Cloud authentication for the Co-Scientist Discovery Engine API.
"""

import os
from datetime import datetime
from typing import Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2 import service_account

from cosci.exceptions import AuthenticationError
from cosci.logger import LogIcons, LogLevel, get_logger


class Authenticator:
    """
    Manages authentication for Google Cloud APIs using service account credentials.
    """

    SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

    def __init__(
        self,
        service_account_path: str,
        project_id: Optional[str] = None,
        logger_name: str = "Auth",
        log_level: LogLevel = LogLevel.INFO,
    ):
        """
        Initialize the authenticator.
        """
        self.logger = get_logger(logger_name, log_level)

        if not service_account_path:
            raise AuthenticationError("Service account path is required")

        self.service_account_path = service_account_path
        self.project_id = project_id

        self._credentials = None
        self._auth_req = Request()
        self._service_account_email = None

    def authenticate(self) -> str:
        """
        Load service account credentials and return initial access token.
        """
        self.logger.process_start("Authentication")

        try:
            self._load_service_account()
            token = self.get_token()
            self.logger.process_complete("Authentication")
            self._log_auth_info()
            return token

        except Exception as e:
            self.logger.process_failed("Authentication", str(e))
            raise AuthenticationError(f"Authentication failed: {e}")

    def _load_service_account(self):
        """
        Load service account credentials from file.
        """
        self.logger.info("Loading service account credentials", LogIcons.AUTH)
        self.logger.debug(f"Service account path: {self.service_account_path}")

        if not os.path.exists(self.service_account_path):
            raise FileNotFoundError(
                f"Service account file not found: {self.service_account_path}"
            )

        try:
            self._credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path, scopes=self.SCOPES
            )

            self._service_account_email = self._credentials.service_account_email
            self.logger.success(
                f"Loaded service account: {self._service_account_email}",
                LogIcons.SUCCESS,
            )

        except Exception as e:
            raise AuthenticationError(
                f"Failed to load service account credentials: {e}"
            )

    def get_token(self) -> str:
        """
        Get current access token.
        """
        if not self._credentials:
            raise AuthenticationError("Not authenticated. Call authenticate() first.")

        self.logger.debug("Getting access token...")

        try:
            if not self._credentials.valid:
                self.logger.debug("Token expired or not yet fetched, refreshing...")
                self._credentials.refresh(self._auth_req)
                self.logger.success("Token refreshed", LogIcons.SUCCESS)
            else:
                self.logger.debug("Token is valid")

            return self._credentials.token

        except Exception as e:
            raise AuthenticationError(f"Failed to get access token: {e}")

    def _refresh_token(self):
        """
        Refresh the access token.
        """
        if self._credentials:
            self._credentials.refresh(self._auth_req)

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authentication.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_token()}",
        }

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        """
        return self._credentials is not None

    def get_auth_info(self) -> Dict[str, any]:
        """
        Get information about current authentication.
        """
        info = {
            "authenticated": self.is_authenticated(),
            "project_id": self.project_id,
            "service_account": self._service_account_email,
        }

        if self._credentials and self._credentials.expiry:
            info["token_expiry"] = self._credentials.expiry.isoformat()
            info["token_remaining"] = str(self._credentials.expiry - datetime.now())

        return info

    def _log_auth_info(self):
        """
        Log authentication information.
        """
        info = self.get_auth_info()

        self.logger.info("Authentication Status:", LogIcons.AUTH)
        self.logger.indent()
        self.logger.info(f"Project: {info.get('project_id', 'not set')}")
        self.logger.info(f"Service Account: {info.get('service_account', 'unknown')}")

        if "token_remaining" in info:
            self.logger.info(f"Token valid for: {info['token_remaining']}")

        self.logger.dedent()

    def revoke(self):
        """
        Clear authentication state.
        """
        self.logger.info("Clearing authentication state", LogIcons.AUTH)

        if self._service_account_email:
            self.logger.debug(
                f"Clearing credentials for: {self._service_account_email}"
            )

        self._credentials = None
        self._service_account_email = None

        self.logger.success("Authentication state cleared", LogIcons.SUCCESS)


def authenticate(
    service_account_path: str, project_id: Optional[str] = None, **kwargs
) -> Authenticator:
    """
    Quick authentication helper.
    """
    auth = Authenticator(service_account_path, project_id, **kwargs)
    auth.authenticate()
    return auth
