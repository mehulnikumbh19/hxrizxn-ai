from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.core.config import Settings


class ObjectStorageProvider:
    name = "base"

    def save_bytes(self, case_id: str, filename: str, content: bytes) -> str:
        raise NotImplementedError


class LocalObjectStorageProvider(ObjectStorageProvider):
    name = "local"

    def __init__(self, settings: Settings):
        self.settings = settings

    def save_bytes(self, case_id: str, filename: str, content: bytes) -> str:
        upload_dir = Path(self.settings.upload_dir) / case_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(filename).suffix or ".bin"
        target = upload_dir / f"{uuid4()}{suffix}"
        target.write_bytes(content)
        return str(target)


class AzureBlobStorageProvider(ObjectStorageProvider):
    name = "azure-blob"

    def __init__(self, settings: Settings):
        self.settings = settings

    def save_bytes(self, case_id: str, filename: str, content: bytes) -> str:
        if not self.settings.azure_storage_connection_string:
            return LocalObjectStorageProvider(self.settings).save_bytes(case_id, filename, content)
        from azure.storage.blob import BlobServiceClient

        suffix = Path(filename).suffix or ".bin"
        blob_name = f"{case_id}/{uuid4()}{suffix}"
        client = BlobServiceClient.from_connection_string(self.settings.azure_storage_connection_string)
        blob = client.get_blob_client(container=self.settings.azure_blob_container, blob=blob_name)
        blob.upload_blob(content, overwrite=True)
        return blob.url


def get_storage_provider(settings: Settings) -> ObjectStorageProvider:
    if settings.azure_storage_connection_string:
        return AzureBlobStorageProvider(settings)
    return LocalObjectStorageProvider(settings)
