import logging

from keboola.component.base import ComponentBase, sync_action
from keboola.component.exceptions import UserException
from keboola.component.sync_actions import SelectElement

from configuration import Configuration
from dbx.client import DataBricksClient


class Component(ComponentBase):
    def __init__(self):
        super().__init__()
        self.params = Configuration(**self.configuration.parameters)

        self.dbx_client = DataBricksClient(self.params.base_url, self.params.api_token, self.params.ssl_verify)

    def run(self):
        logging.info("Validating Job ID.")
        job_details = self.dbx_client.get_job_detail(self.params.job_id)
        logging.info(
            f"Job named '{job_details['settings']['name']}' found. Trying to run the dbx job ID: {self.params.job_id}"
        )
        resp = self.dbx_client.run_job_now(self.params.job_id)
        self.dbx_client.wait_for_job(resp["run_id"])

        logging.info("Job finished successfully!")

    @sync_action("list_jobs")
    def list_databases(self):
        jobs = self.dbx_client.get_jobs()
        return [SelectElement(value=j.get("job_id"), label=j.get("settings", {}).get("name")) for j in jobs]


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
