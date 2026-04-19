import time
from typing import Optional, Any, Dict
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from src.models.types import APIError
from src.utils.logging import logger


class BaseAPIClient:
    """Base API client with retry logic, error handling, and timeouts."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        timeout: int = 120,
    ):
        self.base_url = base_url.rstrip("/") + "/"
        self.api_key = api_key
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.timeout = timeout

        # Create session with retry
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests Session with retry configuration."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def post(
        self,
        endpoint: str,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Make a POST request with error handling.

        Args:
            endpoint: Endpoint path relative to base URL
            json_body: JSON body

        Returns:
            Response object

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = self._get_headers()

        try:
            response = self.session.post(
                url,
                headers=headers,
                json=json_body,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_body = e.response.json()
                    error_msg += f" Response: {error_body}"
                except:
                    pass
            logger.error(error_msg)
            raise APIError(error_msg) from e
