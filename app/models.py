from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Markdown(Model):
    type: str
    content: str
