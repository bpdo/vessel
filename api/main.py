from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

version = "/v1"


class Model(BaseModel):
    data_set_id: Optional[str] = None
    pipeline_id: Optional[str] = None


@app.get(f"{version}/models")
def read_models():
    return [
        {
            "id": "0000-000",
            "version": "hash",
            "s3_location": "http://localhost",
            "data_set_id": "123",
            "pipeline_id": "456",
        }
    ]


@app.post(f"{version}/models")
def create_model(model: Model):
    return model


@app.get(f"{version}/models/{{id}}")
def read_model(id: str):
    return {"id": id}


@app.put(f"{version}/models/{{id}}")
def update_model(id: str):
    return {"model_id": id, "updated": True}


@app.delete(f"{version}/models/{{id}}")
def delete_model(id: str):
    return {"id": id, "deleted": True}
