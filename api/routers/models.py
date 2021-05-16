from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

from ..utils import db

# get the database instance from utils
database = db.database

# create a models router
router = APIRouter()


class Model(BaseModel):
    name: str
    description: Optional[str] = None
    archived: Optional[bool]


@router.get("/", response_model=List[Model])
async def read_models(include_archived: bool = False):
    """Fetches all models"""

    query = (
        "SELECT * FROM models WHERE archived == 0"
        if not include_archived
        else "SELECT * FROM models"
    )
    return await database.fetch_all(query=query)


@router.get("/{id}", response_model=Model)
async def read_model(id: int):
    """Fetches model details based on a model id"""

    query = "SELECT * FROM models WHERE id = :id"
    return await database.fetch_one(query, values={"id": id})


@router.post("/")
async def create_model(model: Model):
    """Creates a new model, name must be unique"""

    try:
        # insert query for creating a model with name and description
        query = "INSERT INTO models(name, description) VALUES(:name, :description)"

        # build the values dictionary
        values = {"name": model.name, "description": model.description}

        # execute the query with values
        return await database.execute(query, values=values)

    except sqlite3.IntegrityError as e:
        logging.error(e)
        raise HTTPException(
            status_code=500, detail="Model already exists, name must be unique"
        )

    except:
        raise HTTPException(status_code=500, detail="Error creating the model")
