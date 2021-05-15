from typing import List, Optional

from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel
import hashlib
import os
from pathlib import Path
import uuid

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "8192"))
REGISTRY_PATH = os.getenv("REGISTRY_PATH", "/tmp/vessel")

app = FastAPI()

# default version for url path
version = "/v0"


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


# @app.post(f"{version}/models")
# def create_model(model: Model):
#     return model


@app.post(f"{version}/models")
async def create_model_data(
    data_set_id: str = Form(...),
    pipeline_id: str = Form(...),
    files: List[UploadFile] = File(...),
):
    try:
        # create a random uuid for temp file storage
        random_uuid = str(uuid.uuid4())

        temp_path = Path(REGISTRY_PATH, "scratch", random_uuid)

        # create a folder that will be renamed once the hash is calculated
        temp_path.mkdir(parents=True, exist_ok=True)

        # create a new sha1 object
        sha1Hash = hashlib.sha1()

        # loop through the uploaded files
        for file in files:
            # open the spooled temporary file
            with file.file as f:
                # create a new binary file with the same filename
                with open(Path(temp_path, file.filename), "wb") as wf:
                    # read the file chunk by chunk until there are no more chunks
                    while True:
                        # read a chunk from the file
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break

                        # update the hash with the chunk
                        sha1Hash.update(chunk)

                        # write the chunk to storage
                        wf.write(chunk)

        # get first 16 hex digits of the hash
        sha1Hashed = sha1Hash.hexdigest()[:16]

        # create path with model version
        versioned_path = Path(REGISTRY_PATH, sha1Hashed)

        # check if this version already exists
        if not versioned_path.exists():
            # move the scratch folder to version-based folder
            os.rename(temp_path, versioned_path)

        return {"version": sha1Hashed}
    finally:
        print("done")


@app.get(f"{version}/models/{{id}}")
def read_model(id: str):
    return {"id": id}


@app.put(f"{version}/models/{{id}}")
def update_model(id: str):
    return {"model_id": id, "updated": True}


@app.delete(f"{version}/models/{{id}}")
def delete_model(id: str):
    return {"id": id, "deleted": True}
