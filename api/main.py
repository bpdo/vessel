from databases import Database
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
import hashlib
import os
from pathlib import Path
from pydantic import BaseModel
import shutil
from typing import List, Optional
import uuid

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "8192"))
REGISTRY_PATH = os.getenv("REGISTRY_PATH", "/tmp/vessel")

app = FastAPI()
database = Database("sqlite:///vessel.db")

# default version for url path
version = "/v0"


@app.on_event("startup")
async def startup():
    await database.connect()

    # check if a table exists
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name='models'"

    if not await database.fetch_all(query=query):
        query = """CREATE TABLE models (
            id INTEGER PRIMARY KEY, 
            version text NOT NULL UNIQUE, 
            path text NOT NULL, 
            data_set text, 
            pipeline text, 
            tag text, 
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            archived integer DEFAULT 0
        )"""
        await database.execute(query=query)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


class Model(BaseModel):
    version: str
    path: str
    data_set: Optional[str] = None
    pipeline: Optional[str] = None
    tag: Optional[str] = None
    created: str
    archived: bool


@app.get(f"{version}/models", response_model=List[Model])
async def read_models(include_archived: bool = False):
    query = (
        "SELECT * FROM models WHERE archived == 0"
        if not include_archived
        else "SELECT * FROM models"
    )
    return await database.fetch_all(query=query)


@app.post(f"{version}/models")
async def create_model_data(
    data_set: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    pipeline: Optional[str] = Form(None),
    tag: Optional[str] = Form(None),
):
    # create a random uuid for temp file storage
    random_uuid = str(uuid.uuid4())

    # create a temp storage location for model upload
    temp_path = Path(REGISTRY_PATH, "scratch", random_uuid)

    try:
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
        if versioned_path.exists():
            raise HTTPException(status_code=500, detail="Version already exists")

        # write to database
        query = "INSERT INTO models(version, path, data_set, pipeline, tag) VALUES (:version, :path, :data_set, :pipeline, :tag)"
        values = [
            {
                "version": sha1Hashed,
                "path": str(versioned_path),
                "data_set": data_set,
                "pipeline": pipeline,
                "tag": tag,
            },
        ]
        await database.execute_many(query=query, values=values)

        # move the scratch folder to version-based folder
        os.rename(temp_path, versioned_path)

        # return registred model
        return {
            "version": sha1Hashed,
            "path": versioned_path,
            "data_set": data_set,
            "pipeline": pipeline,
            "tag": tag,
        }
    finally:
        # delete the scratch model folder
        if temp_path.exists():
            shutil.rmtree(temp_path)


@app.get(f"{version}/models/{{id}}")
async def read_model(id: str):
    query = "SELECT * FROM models WHERE version = :version"
    return await database.fetch_one(query=query, values={"version": id})


class Metadata(BaseModel):
    archived: Optional[bool] = None


@app.put(f"{version}/models/{{id}}")
async def read_model(id: str, metadata: Metadata):
    # build the set query part
    update_set = ""

    if metadata.archived is not None:
        update_set += "archived = :archived"

    if not update_set:
        return 0

    # build the query and query values
    query = f"UPDATE models SET {update_set} WHERE version = :version"
    values = {"archived": int(metadata.archived == True), "version": id}

    # update the model
    return await database.execute(query=query, values=values)


@app.delete(f"{version}/models/{{id}}")
async def delete_model(id: str):
    # build the query and query values
    query = "UPDATE models SET archived = 1 WHERE version = :version"
    values = {"version": id}

    # set the model archive value to "true"
    return await database.execute(query=query, values=values)
