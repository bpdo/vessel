import os


def load():
    """Load configuration from environment variables"""

    return {
        "chunk_size": int(os.getenv("CHUNK_SIZE", "8192")),
        "connection_string": os.getenv("CONNECTION_STRING", "sqlite:///vessel.db"),
        "file_path": os.getenv("FILE_PATH", "/tmp/vessel"),
    }
