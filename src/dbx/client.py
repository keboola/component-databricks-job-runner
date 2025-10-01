import time
import uuid

from keboola.http_client import HttpClient
from requests.exceptions import HTTPError


class DataBricksClientClientException(Exception):
    pass


class DataBricksClient(HttpClient):
    WAIT_TIMEOUT_SECONDS = 3600.0
    WAIT_POLL_INTERVAL_SECONDS = 3.0

    def __init__(self, base_url: str, token: str, ssl_verify: bool):
        self.token = token
        self.ssl_verify = ssl_verify
        super().__init__(base_url, auth_header={"Authorization": f"Bearer {token}"})

    def run_job_now(self, job_id: str) -> dict:
        """
        Run single job.
        Args:
            job_id:

        Returns:

        """

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
        parameters = {"run_id": run_id}
        try:
            return self.get(endpoint_path="/api/2.1/jobs/runs/get", params=parameters, verify=self.ssl_verify)
        except HTTPError as http_err:
            raise DataBricksClientClientException(http_err) from http_err

    def get_job_detail(self, job_id: str) -> dict:
        """
        Retrieve the metadata of a job.

        Args:
            job_id: Existing DBX job ID

        Returns:

        """
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
