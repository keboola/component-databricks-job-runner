import logging

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

# configuration variables
from dbx.client import DataBricksClient

KEY_API_TOKEN = "#api_token"
KEY_BASE_URL = "base_url"
KEY_JOB_ID = "job_id"
KEY_SSL_VERIFY = "ssl_verify"

REQUIRED_PARAMETERS = [KEY_API_TOKEN, KEY_BASE_URL]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    def __init__(self):
        super().__init__()
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.dbx_client = DataBricksClient(
            self.configuration.parameters[KEY_BASE_URL], self.configuration.parameters[KEY_API_TOKEN], ssl_verify=False
        )

    def run(self):
        params = self.configuration.parameters
        self.validate_configuration_parameters([KEY_JOB_ID])
        job_id = params[KEY_JOB_ID]

        logging.info("Validating Job ID.")
        job_details = self.dbx_client.get_job_detail(job_id)
        logging.info(f"Job named '{job_details['settings']['name']}' found. Trying to run the dbx job ID: {job_id}")
        resp = self.dbx_client.run_job_now(job_id)
        self.dbx_client.wait_for_job(resp["run_id"])

        logging.info("Job finished successfully!")


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
