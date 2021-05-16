from dotenv import load_dotenv
import logging
import os

load_dotenv()


def load():
    """Load configuration from environment variables"""

    config = {
        "chunk_size": int(os.getenv("CHUNK_SIZE", "8192")),
        "connection_string": os.getenv("CONNECTION_STRING", "sqlite:///vessel.db"),
        "file_path": os.getenv("FILE_PATH", "/tmp/vessel"),
    }

    logging.info(f"Using chunk size: {config['chunk_size']}")
    logging.info(f"Using connection string: {config['connection_string']}")
    logging.info(f"Using file path: {config['file_path']}")

    return config
