from enum import Enum

from keboola.component.exceptions import UserException
from pydantic import BaseModel, Field, ValidationError


class AuthType(str, Enum):
    """Supported Databricks authentication methods."""

    TOKEN = "token"
    SERVICE_PRINCIPAL = "service_principal"


class JobParameter(BaseModel):
    """A single key-value parameter forwarded to the Databricks job run."""

    key: str
    value: str = ""


class Configuration(BaseModel):
    auth_type: AuthType = AuthType.TOKEN
    api_token: str = Field(default="", alias="#api_token")
    client_id: str = ""
    client_secret: str = Field(default="", alias="#client_secret")
    base_url: str
    job_id: int = 0
    job_parameters: list[JobParameter] = Field(default_factory=list)
    wait_for_finish: bool = True
    ssl_verify: bool = True
    debug: bool = False

    def __init__(self, **data):
        if "job_id" in data and isinstance(data["job_id"], str):
            data["job_id"] = int(data["job_id"]) if data["job_id"].strip() else 0
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise UserException(f"Validation Error: {', '.join(error_messages)}")
        self._validate_auth()

    def _validate_auth(self):
        """Ensure the credentials required by the selected auth method are present."""
        if self.auth_type == AuthType.TOKEN:
            if not self.api_token:
                raise UserException(
                    "Databricks API token (#api_token) is required for Personal Access Token authentication."
                )
        elif self.auth_type == AuthType.SERVICE_PRINCIPAL:
            missing = []
            if not self.client_id:
                missing.append("client_id")
            if not self.client_secret:
                missing.append("#client_secret")
            if missing:
                raise UserException(
                    f"Service principal (OAuth M2M) authentication requires: {', '.join(missing)}."
                )

    def job_parameters_dict(self) -> dict:
        """Return the configured job parameters as a {key: value} mapping (empty keys ignored)."""
        return {param.key: param.value for param in self.job_parameters if param.key}
