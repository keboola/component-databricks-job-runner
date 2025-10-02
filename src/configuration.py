from keboola.component.exceptions import UserException
from pydantic import BaseModel, Field, ValidationError


class Configuration(BaseModel):
    api_token: str = Field(alias="#api_token")
    base_url: str
    job_id: str = ""
    ssl_verify: bool = True
    debug: bool = False

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise UserException(f"Validation Error: {', '.join(error_messages)}")
