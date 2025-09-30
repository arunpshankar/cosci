"""
API Client Module for Cosci SDK
================================
Core API client for interacting with Google's Co-Scientist Discovery Engine.
"""

import json
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import requests

from cosci.auth import Authenticator
from cosci.exceptions import APIError
from cosci.logger import LogIcons, LogLevel, get_logger


class APIClient:
    """
    Core API client for Co-Scientist Discovery Engine.

    Handles all low-level HTTP interactions with the Discovery Engine API,
    including authentication, retries, and error handling.
    """

    BASE_URL = "https://discoveryengine.googleapis.com"
    API_VERSION = "v1alpha"
    DEFAULT_TIMEOUT = 30
    DEFAULT_CONNECT_TIMEOUT = 10
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2

    def __init__(
        self,
        authenticator: Authenticator,
        project_id: str,
        engine: str,
        location: str = "global",
        collection: str = "default_collection",
        assistant: str = "default_assistant",
        logger_name: str = "API",
        log_level: LogLevel = LogLevel.INFO,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        """
        Initialize the API client.

        Args:
            authenticator: Authenticator instance for handling auth
            project_id: Google Cloud project ID
            engine: Discovery Engine name
            location: API location (default: "global")
            collection: Collection name
            assistant: Assistant name
            logger_name: Name for logger instance
            log_level: Logging level
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.logger = get_logger(logger_name, log_level)
        self.logger.section("API Client Initialization", "-", 50)

        self.authenticator = authenticator
        self.project_id = project_id
        self.engine = engine
        self.location = location
        self.collection = collection
        self.assistant = assistant

        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.MAX_RETRIES

        self.logger.info("API Client Configuration:", LogIcons.DATA)
        self.logger.indent()
        self.logger.info(f"Base URL: {self.BASE_URL}")
        self.logger.info(f"API Version: {self.API_VERSION}")
        self.logger.info(f"Project: {self.project_id}")
        self.logger.info(f"Engine: {self.engine}")
        self.logger.info(f"Location: {self.location}")
        self.logger.info(f"Timeout: {self.timeout}s")
        self.logger.info(f"Max Retries: {self.max_retries}")
        self.logger.dedent()

        self.base_path = self._build_base_path()
        self.logger.info(f"Base Path: {self.base_path}", LogIcons.API)

        self.logger.debug("Creating requests session for connection pooling")
        self.session = requests.Session()

        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_retries": 0,
            "total_time": 0.0,
            "status_codes": {},
        }

        self.logger.success("API Client ready", LogIcons.SUCCESS)

    def _build_base_path(self) -> str:
        """
        Build the base path for API endpoints.
        """
        path = (
            f"projects/{self.project_id}/locations/{self.location}/"
            f"collections/{self.collection}/engines/{self.engine}"
        )
        self.logger.debug(f"Built base path: {path}")
        return path

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL for an API endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Full URL for the endpoint
        """
        self.logger.debug(f"Building URL for endpoint: {endpoint}")

        # Handle absolute URLs
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            self.logger.debug(f"Using absolute URL: {endpoint}")
            return endpoint

        # Remove leading slash if present
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        # Build base URL
        base = f"{self.BASE_URL}/{self.API_VERSION}/"

        # Add base path if not already in endpoint
        if not endpoint.startswith(self.base_path):
            endpoint = f"{self.base_path}/{endpoint}"

        url = urljoin(base, endpoint)
        self.logger.debug(f"Built URL: {url}")
        return url

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry: bool = True,
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Make an API request with automatic retries and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data (for POST/PUT)
            params: URL parameters
            headers: Additional headers
            retry: Whether to retry on failure

        Returns:
            Response data as dictionary or list

        Raises:
            APIError: If request fails after retries
        """
        url = self._build_url(endpoint)

        self.logger.subsection(f"{method} Request")
        self.logger.info(f"URL: {url}", LogIcons.API)

        # Get authentication headers
        self.logger.debug("Getting authentication headers")
        auth_headers = self.authenticator.get_headers()

        # Merge with additional headers
        if headers:
            auth_headers.update(headers)
            self.logger.debug(f"Added custom headers: {list(headers.keys())}")

        # Log request details
        if data:
            self.logger.debug(f"Request body: {json.dumps(data, indent=2)[:500]}...")
        if params:
            self.logger.debug(f"Query params: {params}")

        # Update statistics
        self.stats["total_requests"] += 1
        start_time = time.time()
        self.logger.info(
            f"Request #{self.stats['total_requests']} starting", LogIcons.PROCESS
        )

        # Retry logic
        last_error = None
        retries = 0
        max_attempts = self.max_retries if retry else 1

        while retries < max_attempts:
            attempt_start = time.time()

            try:
                self.logger.info(f"Attempt {retries + 1}/{max_attempts}", LogIcons.TIME)

                # Make the request based on method
                if method.upper() == "GET":
                    self.logger.debug("Sending GET request")
                    response = self.session.get(
                        url,
                        headers=auth_headers,
                        params=params,
                        timeout=(self.DEFAULT_CONNECT_TIMEOUT, self.timeout),
                    )
                elif method.upper() == "POST":
                    self.logger.debug("Sending POST request")
                    response = self.session.post(
                        url,
                        headers=auth_headers,
                        json=data,
                        params=params,
                        timeout=(self.DEFAULT_CONNECT_TIMEOUT, self.timeout),
                    )
                elif method.upper() == "PUT":
                    self.logger.debug("Sending PUT request")
                    response = self.session.put(
                        url,
                        headers=auth_headers,
                        json=data,
                        params=params,
                        timeout=(self.DEFAULT_CONNECT_TIMEOUT, self.timeout),
                    )
                elif method.upper() == "DELETE":
                    self.logger.debug("Sending DELETE request")
                    response = self.session.delete(
                        url,
                        headers=auth_headers,
                        params=params,
                        timeout=(self.DEFAULT_CONNECT_TIMEOUT, self.timeout),
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Track status code
                status_code = response.status_code
                self.stats["status_codes"][status_code] = (
                    self.stats["status_codes"].get(status_code, 0) + 1
                )

                attempt_time = time.time() - attempt_start
                icon = LogIcons.SUCCESS if status_code == 200 else LogIcons.WARNING
                self.logger.info(
                    f"Response: {status_code} in {attempt_time:.2f}s", icon
                )

                # Log response preview
                if response.text:
                    self.logger.debug(f"Response preview: {response.text[:500]}...")
                else:
                    self.logger.debug("Response: Empty body")

                # Check for success
                if response.status_code == 200:
                    # Parse response
                    try:
                        if response.text:
                            result = response.json()
                        else:
                            result = {}
                    except json.JSONDecodeError as e:
                        self.logger.error(
                            f"Failed to parse JSON response: {e}", LogIcons.ERROR
                        )
                        raise APIError(
                            f"Invalid JSON response: {e}",
                            response.status_code,
                            response.text,
                        )

                    # Update statistics
                    self.stats["successful_requests"] += 1
                    total_time = time.time() - start_time
                    self.stats["total_time"] += total_time

                    self.logger.success(
                        f"Request successful ({total_time:.2f}s total)",
                        LogIcons.SUCCESS,
                    )

                    # Log response structure
                    if isinstance(result, dict):
                        self.logger.debug(f"Response keys: {list(result.keys())}")
                    elif isinstance(result, list):
                        self.logger.debug(f"Response: List with {len(result)} items")
                    else:
                        self.logger.debug(f"Response type: {type(result).__name__}")

                    self.logger.end_subsection()
                    return result

                # Handle specific error codes
                if response.status_code == 401:
                    # Unauthorized - try to refresh token
                    self.logger.warning(
                        "Got 401 Unauthorized, refreshing token", LogIcons.AUTH
                    )
                    self.authenticator._refresh_token()
                    auth_headers = self.authenticator.get_headers()
                    retries += 1
                    self.stats["total_retries"] += 1
                    continue

                elif response.status_code == 429:
                    # Rate limited
                    wait_time = self._get_retry_after(response)
                    self.logger.warning(
                        f"Rate limited (429). Waiting {wait_time}s before retry",
                        LogIcons.TIME,
                    )
                    time.sleep(wait_time)
                    retries += 1
                    self.stats["total_retries"] += 1
                    continue

                elif response.status_code >= 500:
                    # Server error - retry with backoff
                    if retries < max_attempts - 1:
                        wait_time = self.RETRY_BACKOFF**retries
                        self.logger.warning(
                            f"Server error {response.status_code}. Retrying in {wait_time}s",
                            LogIcons.WARNING,
                        )
                        time.sleep(wait_time)
                        retries += 1
                        self.stats["total_retries"] += 1
                        continue

                # Other errors - don't retry
                self.logger.error(
                    f"Request failed with status {response.status_code}", LogIcons.ERROR
                )
                raise APIError(
                    f"API request failed with status {response.status_code}",
                    response.status_code,
                    response.text,
                )

            except requests.exceptions.Timeout as e:
                last_error = f"Request timeout after {self.timeout}s: {e}"
                self.logger.error(last_error, LogIcons.TIME)

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {e}"
                self.logger.error(last_error, LogIcons.ERROR)

            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {e}"
                self.logger.error(last_error, LogIcons.ERROR)

            except APIError:
                raise  # Re-raise API errors

            except Exception as e:
                last_error = f"Unexpected error: {e}"
                self.logger.error(last_error, LogIcons.ERROR)
                self.logger.debug(f"Exception type: {type(e).__name__}")

            # Retry with backoff
            if retries < max_attempts - 1:
                wait_time = self.RETRY_BACKOFF**retries
                self.logger.info(
                    f"Retrying in {wait_time}s (attempt {retries + 2}/{max_attempts})...",
                    LogIcons.TIME,
                )
                time.sleep(wait_time)
                retries += 1
                self.stats["total_retries"] += 1
            else:
                break

        # All retries exhausted
        self.stats["failed_requests"] += 1
        self.stats["total_time"] += time.time() - start_time

        self.logger.error(
            f"Request failed after {retries + 1} attempts", LogIcons.ERROR
        )
        self.logger.debug(f"Last error: {last_error}")
        self.logger.end_subsection()

        raise APIError(f"Request failed after {retries + 1} attempts: {last_error}")

    def _get_retry_after(self, response: requests.Response) -> int:
        """
        Extract retry-after header value or use default.

        Args:
            response: HTTP response object

        Returns:
            Number of seconds to wait before retry
        """
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            try:
                wait_time = int(retry_after)
                self.logger.debug(f"Retry-After header: {wait_time}s")
                return wait_time
            except (ValueError, TypeError):
                self.logger.debug(f"Invalid Retry-After header: {retry_after}")

        # Default wait time for rate limiting
        default_wait = 60
        self.logger.debug(f"Using default wait time: {default_wait}s")
        return default_wait

    def get(self, endpoint: str, **kwargs) -> Union[Dict[str, Any], List[Any]]:
        """
        Convenience method for GET requests.

        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for request()

        Returns:
            Response data
        """
        self.logger.debug(f"GET request to: {endpoint}")
        return self.request("GET", endpoint, **kwargs)

    def post(
        self, endpoint: str, data: Dict[str, Any], **kwargs
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Convenience method for POST requests.

        Args:
            endpoint: API endpoint
            data: Request body data
            **kwargs: Additional arguments for request()

        Returns:
            Response data
        """
        self.logger.debug(f"POST request to: {endpoint}")
        return self.request("POST", endpoint, data=data, **kwargs)

    def put(
        self, endpoint: str, data: Dict[str, Any], **kwargs
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Convenience method for PUT requests.

        Args:
            endpoint: API endpoint
            data: Request body data
            **kwargs: Additional arguments for request()

        Returns:
            Response data
        """
        self.logger.debug(f"PUT request to: {endpoint}")
        return self.request("PUT", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Union[Dict[str, Any], List[Any]]:
        """
        Convenience method for DELETE requests.

        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for request()

        Returns:
            Response data
        """
        self.logger.debug(f"DELETE request to: {endpoint}")
        return self.request("DELETE", endpoint, **kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get request statistics.

        Returns:
            Dictionary with request statistics including success rate,
            average response time, and status code distribution.
        """
        stats = self.stats.copy()

        # Calculate derived statistics
        if stats["successful_requests"] > 0:
            stats["avg_request_time"] = (
                stats["total_time"] / stats["successful_requests"]
            )
        else:
            stats["avg_request_time"] = 0.0

        if stats["total_requests"] > 0:
            stats["success_rate"] = (
                stats["successful_requests"] / stats["total_requests"]
            )
            stats["retry_rate"] = stats["total_retries"] / stats["total_requests"]
        else:
            stats["success_rate"] = 0.0
            stats["retry_rate"] = 0.0

        self.logger.debug(f"Statistics calculated: {stats}")
        return stats

    def log_stats(self):
        """
        Log current statistics to the logger.
        """
        stats = self.get_stats()

        self.logger.section("API Statistics", "=", 50)
        self.logger.info(f"Total Requests: {stats['total_requests']}", LogIcons.DATA)
        self.logger.info(
            f"Successful: {stats['successful_requests']} ({stats['success_rate']:.1%})",
            LogIcons.SUCCESS,
        )
        self.logger.info(f"Failed: {stats['failed_requests']}", LogIcons.ERROR)
        self.logger.info(
            f"Total Retries: {stats['total_retries']} ({stats['retry_rate']:.1f} per request)",
            LogIcons.TIME,
        )
        self.logger.info(f"Total Time: {stats['total_time']:.2f}s", LogIcons.TIME)
        self.logger.info(
            f"Avg Response Time: {stats['avg_request_time']:.2f}s", LogIcons.TIME
        )

        if stats["status_codes"]:
            self.logger.info("Status Code Distribution:", LogIcons.DATA)
            self.logger.indent()
            for code, count in sorted(stats["status_codes"].items()):
                if stats["total_requests"] > 0:
                    percentage = (count / stats["total_requests"]) * 100
                    self.logger.info(f"{code}: {count} ({percentage:.1f}%)")
                else:
                    self.logger.info(f"{code}: {count}")
            self.logger.dedent()

    def close(self):
        """
        Close the API client and clean up resources.
        """
        self.logger.section("Closing API Client", "-", 50)

        # Log final statistics
        self.log_stats()

        # Close HTTP session
        self.logger.info("Closing HTTP session", LogIcons.PROCESS)
        self.session.close()

        self.logger.success("API Client closed", LogIcons.SUCCESS)
