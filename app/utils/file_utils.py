import hashlib
import shutil
from pathlib import Path

class FileUtils:
    @staticmethod
    def save_upload_file(upload_file, destination: Path) -> None:
        try:
            with destination.open("wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        finally:
            upload_file.file.close()

    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
