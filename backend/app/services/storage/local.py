import os
from typing import BinaryIO
from app.services.storage.base import StorageService


class LocalStorageProvider(StorageService):
    """Concrete implementation of StorageService using local filesystem."""

    def __init__(self, base_dir: str = "storage_uploads"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def save_file(self, file_data: BinaryIO, filename: str, destination_folder: str = "") -> str:
        target_dir = os.path.join(self.base_dir, destination_folder)
        os.makedirs(target_dir, exist_ok=True)

        full_path = os.path.join(target_dir, filename)
        with open(full_path, "wb") as f:
            f.write(file_data.read())

        # Return relative path from base_dir for storage portability
        return os.path.relpath(full_path, self.base_dir)

    def get_file(self, file_path: str) -> bytes:
        full_path = os.path.join(self.base_dir, file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(full_path, "rb") as f:
            return f.read()

    def delete_file(self, file_path: str) -> bool:
        full_path = os.path.join(self.base_dir, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def file_exists(self, file_path: str) -> bool:
        full_path = os.path.join(self.base_dir, file_path)
        return os.path.exists(full_path)
