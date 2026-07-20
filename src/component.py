import logging

from keboola.component.base import ComponentBase, sync_action
from keboola.component.exceptions import UserException
from keboola.component.sync_actions import SelectElement

from configuration import AuthType, Configuration
from dbx.client import DataBricksClient


class Component(ComponentBase):
    def __init__(self):
        super().__init__()
        self.params = Configuration(**self.configuration.parameters)

        if self.params.auth_type == AuthType.SERVICE_PRINCIPAL:
            self.dbx_client = DataBricksClient(
                self.params.base_url,
                self.params.ssl_verify,
                client_id=self.params.client_id,
                client_secret=self.params.client_secret,
            )
        else:
            self.dbx_client = DataBricksClient(
                self.params.base_url,
                self.params.ssl_verify,
                token=self.params.api_token,
            )

    def run(self):
        if not self.params.job_id:
            raise UserException(
                "Job ID is not set. Enter a Databricks Job ID - use the 'Load jobs' action to pick one, "
                "or type it manually if you don't have permission to list jobs."
            )
        logging.info("Validating Job ID.")
        job_details = self.dbx_client.get_job_detail(self.params.job_id)
        logging.info(
            f"Job named '{job_details['settings']['name']}' found. Trying to run the dbx job ID: {self.params.job_id}"
        )
        job_parameters = self.params.job_parameters_dict()
        if job_parameters:
            logging.info(f"Passing {len(job_parameters)} job parameter(s): {sorted(job_parameters)}")
        resp = self.dbx_client.run_job_now(self.params.job_id, job_parameters=job_parameters)
        run_id = resp["run_id"]

        if self.params.wait_for_finish:
            logging.info(f"Waiting for run {run_id} to finish...")
            self.dbx_client.wait_for_job(run_id)
            logging.info("Job finished successfully!")
        else:
            logging.info(
                f"Job triggered (run ID: {run_id}). Not waiting for completion "
                "(wait_for_finish is disabled); the component will not reflect the job's final status."
            )

    @sync_action("list_jobs")
    def list_jobs(self):
        jobs = self.dbx_client.get_jobs()
        if not jobs:
            raise UserException(
                "No jobs were returned. The configured credentials likely lack permission to list jobs "
                "(a service principal needs at least CAN_VIEW on the jobs). "
                "You can still enter the Job ID manually."
            )
        return [
            SelectElement(value=str(j.get("job_id")), label=(j.get("settings") or {}).get("name")) for j in jobs
        ]


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        detail = ""
        if len(exc.args) > 1:
            detail = exc.args[1]
        logging.exception(exc, extra={"full_message": detail})
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
