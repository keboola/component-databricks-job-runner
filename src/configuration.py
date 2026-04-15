from keboola.component.exceptions import UserException
from pydantic import BaseModel, Field, ValidationError


class Configuration(BaseModel):
    api_token: str = Field(alias="#api_token")
    base_url: str
    job_id: int = 0
    ssl_verify: bool = True
    debug: bool = False

    def __init__(self, **data):
        if "job_id" in data and isinstance(data["job_id"], str) and data["job_id"]:
            data["job_id"] = int(data["job_id"])
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise UserException(f"Validation Error: {', '.join(error_messages)}")
