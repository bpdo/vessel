from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import hashlib
import logging
import os
from pathlib import Path
from pydantic import BaseModel
import shutil
import sqlite3
from typing import List, Optional
import uuid

from ..utils import config, db

# load the configuration
_config = config.load()

# get the database instance from utils
database = db.database

# create a models router
router = APIRouter()


class Version(BaseModel):
    model_id: int
    tag: str
    hash: str
    path: str
    data_set: Optional[str] = None
    pipeline: Optional[str] = None
    created: str
    archived: bool


@router.get("/", response_model=List[Version])
async def read_model(model_id: int):
    """Fetch all model versions based on a model id"""

    query = "SELECT * FROM versions WHERE model_id = :model_id"
    return await database.fetch_all(query=query, values={"model_id": model_id})


@router.post("/", response_model=Version)
async def create_model_data(
    data_set: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    model_id: int = Form(...),
    pipeline: Optional[str] = Form(None),
    tag: str = Form(...),
):
    # create a random uuid for temp file storage
    random_uuid = str(uuid.uuid4())

    # create a temp storage location for model upload
    temp_path = Path(_config["file_path"], ".tmp", random_uuid)

    try:
        # check if the model exists
        query = "SELECT id FROM models WHERE id = :id"
        model = await database.fetch_one(query=query, values={"id": model_id})

        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

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
                        chunk = f.read(_config["chunk_size"])
                        if not chunk:
                            break

                        # update the hash with the chunk
                        sha1Hash.update(chunk)

                        # write the chunk to storage
                        wf.write(chunk)

        # get first 16 hex digits of the hash
        sha1Hashed = sha1Hash.hexdigest()[:16]

        # create path with model version
        versioned_path = Path(_config["file_path"], sha1Hashed)

        # fetch the model version by tag and model id
        query = "SELECT id FROM versions WHERE tag = :tag AND model_id = :model_id"
        values = {"tag": tag, "model_id": model_id}
        result = await database.fetch_one(query=query, values=values)

        # check if this version already exists
        if result:
            raise HTTPException(
                status_code=500,
                detail="Version already exists, tag and model id must be unique",
            )

        # write the model version to the database
        query = "INSERT INTO versions(model_id, tag, path, data_set, pipeline, hash) VALUES (:model_id, :tag, :path, :data_set, :pipeline, :hash)"
        values = {
            "model_id": model.id,
            "tag": tag,
            "hash": sha1Hashed,
            "path": str(versioned_path),
            "data_set": data_set,
            "pipeline": pipeline,
        }
        result = await database.execute(query=query, values=values)

        if result < 1:
            raise HTTPException(status_code=500, detail="Model version failed to save")

        # move the scratch folder to version-based folder
        if not versioned_path.exists():
            os.rename(temp_path, versioned_path)

        # select the newly create model from the database
        query = "SELECT * FROM versions WHERE model_id = :model_id AND tag = :tag"
        values = {"model_id": model_id, "tag": tag}
        return await database.fetch_one(query=query, values=values)

    except sqlite3.IntegrityError as db_error:
        print(db_error)
        raise HTTPException(
            status_code=500, detail="Error saving version to the database"
        )
    finally:
        # delete the scratch model folder
        if temp_path.exists():
            shutil.rmtree(temp_path)


@router.get("/{tag}", response_model=Version)
async def read_model(tag: str, model_id: int):
    """Fetch model version details based on a model id and a version tag"""

    query = "SELECT * FROM versions WHERE model_id = :model_id AND tag = :tag"
    values = {"model_id": model_id, "tag": tag}
    return await database.fetch_one(query=query, values=values)


class Metadata(BaseModel):
    archived: Optional[bool] = None


@router.put("/{tag}")
async def read_model(tag: str, model_id: int, metadata: Metadata):
    """Updates the metadata for a specific model version"""

    # build the set query part
    update_set = ""

    if metadata.archived is not None:
        update_set += "archived = :archived"

    if not update_set:
        return 0

    # build the query and query values
    query = (
        f"UPDATE versions SET {update_set} WHERE model_id = :model_id AND tag = :tag"
    )
    values = {
        "archived": int(metadata.archived == True),
        "model_id": model_id,
        "tag": tag,
    }

    # update the model
    return await database.execute(query=query, values=values)


@router.delete("/{tag}")
async def delete_model(tag: str, model_id: str):
    """Deletes a model version by setting the archived flag, true"""

    # build the query and query values
    query = "UPDATE versions SET archived = 1 WHERE model_id = :model_id AND tag = :tag"
    values = {"model_id": model_id, "tag": tag}

    # set the model archive value to "true"
    return await database.execute(query=query, values=values)
