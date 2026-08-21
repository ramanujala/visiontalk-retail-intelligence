from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):
    """Abstract Base Class defining the storage abstraction interface for file handling."""

    @abstractmethod
    def save_file(self, file_data: BinaryIO, filename: str, destination_folder: str = "") -> str:
        """Saves a file to storage and returns the stored file path or URI."""
        pass

    @abstractmethod
    def get_file(self, file_path: str) -> bytes:
        """Retrieves file binary content given its path or URI."""
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Deletes a file given its path or URI."""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Checks if a file exists in storage."""
        pass
