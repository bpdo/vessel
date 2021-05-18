from databases import Database

from ..utils import config

# load the configuration
_config = config.load()

# create the database object
database = Database(_config["connection_string"])


async def connect():
    await database.connect()

    # create the database tables if they don't exist
    await _init()


async def disconnect():
    await database.disconnect()


async def _init():
    """Initializes the database and creates tables if they don't exist"""

    # check if the models table exists
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name='models'"

    if not await database.fetch_one(query=query):
        query = """CREATE TABLE models (
            id INTEGER PRIMARY KEY,
            name text NOT NULL UNIQUE,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description text,
            archived integer DEFAULT 0
        )"""

        await database.execute(query=query)

    # check if the versions table exists
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name='versions'"

    if not await database.fetch_one(query=query):
        query = """CREATE TABLE versions (
          id integer PRIMARY KEY,
          model_id integer NOT NULL,
          tag text NOT NULL,
          hash NOT NULL,
          path text NOT NULL, 
          data_set text, 
          pipeline text, 
          created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
          archived integer DEFAULT 0,
          FOREIGN KEY(model_id) REFERENCES models(id),
          UNIQUE(model_id, tag)
      )"""
        await database.execute(query=query)
