import time
import uuid

import requests
from keboola.http_client import HttpClient
from requests.exceptions import HTTPError, RequestException


class DataBricksClientClientException(Exception):
    pass


class DataBricksClient(HttpClient):
    WAIT_TIMEOUT_SECONDS = 3600.0
    WAIT_POLL_INTERVAL_SECONDS = 3.0
    # OAuth token endpoint (workspace-level) and refresh safety margin.
    OAUTH_TOKEN_PATH = "/oidc/v1/token"
    OAUTH_SCOPE = "all-apis"
    OAUTH_REFRESH_MARGIN_SECONDS = 60.0

    def __init__(
        self,
        base_url: str,
        ssl_verify: bool,
        token: str = None,
        client_id: str = None,
        client_secret: str = None,
    ):
        self.base_url = base_url
        self.ssl_verify = ssl_verify
        self._client_id = client_id
        self._client_secret = client_secret
        self._use_oauth = bool(client_id and client_secret)
        self._oauth_expires_at = 0.0

        if self._use_oauth:
            token = self._fetch_oauth_token()

        self.token = token
        super().__init__(base_url, auth_header={"Authorization": f"Bearer {token}"})

    def _fetch_oauth_token(self) -> str:
        """
        Obtain a workspace access token for a service principal using the OAuth
        machine-to-machine (client credentials) grant.
        """
        token_url = self.base_url.rstrip("/") + self.OAUTH_TOKEN_PATH
        try:
            response = requests.post(
                token_url,
                auth=(self._client_id, self._client_secret),
                data={"grant_type": "client_credentials", "scope": self.OAUTH_SCOPE},
                verify=self.ssl_verify,
            )
            response.raise_for_status()
        except HTTPError as http_err:
            raise DataBricksClientClientException(
                "Failed to obtain an OAuth token for the service principal. Please verify the client ID, "
                "client secret and that OAuth (M2M) is enabled for the workspace.",
                http_err,
            ) from http_err
        except RequestException as err:
            raise DataBricksClientClientException(
                f"Failed to reach the Databricks OAuth token endpoint at {token_url}: {err}"
            ) from err

        payload = response.json()
        token = payload.get("access_token")
        if not token:
            raise DataBricksClientClientException(
                "The Databricks OAuth token endpoint did not return an access token."
            )
        expires_in = payload.get("expires_in", 3600)
        self._oauth_expires_at = time.time() + expires_in - self.OAUTH_REFRESH_MARGIN_SECONDS
        return token

    def _ensure_token(self):
        """Refresh the OAuth token before it expires (no-op for PAT auth)."""
        if not self._use_oauth:
            return
        if time.time() >= self._oauth_expires_at:
            token = self._fetch_oauth_token()
            self.token = token
            self.update_auth_header({"Authorization": f"Bearer {token}"}, overwrite=True)

    def run_job_now(self, job_id: int) -> dict:
        """
        Run single job.
        Args:
            job_id:

        Returns:

        """

        self._ensure_token()
        body = {"job_id": job_id, "idempotency_token": str(uuid.uuid1())}
        try:
            return self.post(endpoint_path="/api/2.1/jobs/run-now", json=body, verify=self.ssl_verify)

        except HTTPError as http_err:
            raise DataBricksClientClientException(http_err) from http_err

    def get_job_run(self, run_id: int) -> dict:
        """
        Retrieve the metadata of a run.

        Args:
            run_id:

        Returns:

        """
        self._ensure_token()
        parameters = {"run_id": run_id}
        try:
            return self.get(endpoint_path="/api/2.1/jobs/runs/get", params=parameters, verify=self.ssl_verify)
        except HTTPError as http_err:
            raise DataBricksClientClientException(http_err) from http_err

    def get_job_detail(self, job_id: int) -> dict:
        """
        Retrieve the metadata of a job.

        Args:
            job_id: Existing DBX job ID

        Returns:

        """
        self._ensure_token()
        parameters = {"job_id": job_id}
        try:
            return self.get(endpoint_path="/api/2.1/jobs/get", params=parameters, verify=self.ssl_verify)
        except HTTPError as http_err:
            raise DataBricksClientClientException(
                f"Failed to retrieve job ID: {job_id}. Please check if it's correct", http_err
            ) from http_err

    def wait_for_job(self, run_id: int, timeout_seconds: float = None, poll_interval_seconds: float = None) -> dict:
        """
        Wait for the DBX job to finish. Raises exception when state is not SUCCESS
        Args:
            run_id:
            timeout_seconds:
            poll_interval_seconds:

        Returns:

        """

        timeout_seconds = timeout_seconds or self.WAIT_TIMEOUT_SECONDS
        poll_interval_seconds = poll_interval_seconds or self.WAIT_POLL_INTERVAL_SECONDS
        expires_at = time.time() + timeout_seconds
        exit_states = ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]
        while True:
            run_meta = self.get_job_run(run_id)
            run_state = run_meta["state"]["life_cycle_state"]
            if run_state in exit_states:
                break
            if time.time() > expires_at:
                raise DataBricksClientClientException(f"Timeout of {timeout_seconds} seconds reached for run {run_id}.")
            time.sleep(poll_interval_seconds)

        if run_meta["state"]["result_state"] != "SUCCESS":
            raise DataBricksClientClientException(
                f"Job execution failed with status: "
                f"{run_meta['state']['result_state']}, "
                f"Reason: {run_meta['state']['state_message']}",
                run_meta,
            )
        return run_meta

    def get_jobs(self) -> list:
        """
        Get list of all jobs.
        """
        self._ensure_token()
        jobs = []
        has_more = True
        offset = 0
        page_size = 25
        while has_more:
            self._ensure_token()
            parameters = {"limit": page_size, "offset": offset}
            try:
                response = self.get(endpoint_path="/api/2.1/jobs/list", params=parameters, verify=self.ssl_verify)
                jobs.extend(response.get("jobs", []))
                has_more = response.get("has_more", False)
                offset += page_size
            except HTTPError as http_err:
                raise DataBricksClientClientException(http_err) from http_err
        return jobs
