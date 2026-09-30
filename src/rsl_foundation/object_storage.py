from __future__ import annotations

from io import BytesIO
from pathlib import Path, PurePosixPath

from minio import Minio
from minio.versioningconfig import ENABLED, VersioningConfig


class S3ObjectStorage:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str = "rsl-artifacts",
        secure: bool = False,
    ) -> None:
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        self.bucket = bucket

    def store(self, object_key: str, content: bytes, *, content_type: str, sha256: str) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            self.client.set_bucket_versioning(self.bucket, VersioningConfig(ENABLED))
        self.client.put_object(
            self.bucket,
            object_key,
            BytesIO(content),
            length=len(content),
            content_type=content_type,
            metadata={"sha256": sha256},
        )

    def read(self, object_key: str) -> bytes:
        response = self.client.get_object(self.bucket, object_key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def remove(self, object_key: str) -> None:
        self.client.remove_object(self.bucket, object_key)


class FileSystemObjectStorage:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, object_key: str) -> Path:
        normalized_key = object_key.replace("\\", "/")
        key_path = PurePosixPath(normalized_key)
        if key_path.is_absolute() or not key_path.parts or ".." in key_path.parts:
            raise ValueError("invalid object key")
        destination = (self.root / Path(*key_path.parts)).resolve()
        if not destination.is_relative_to(self.root):
            raise ValueError("invalid object key")
        return destination

    def store(self, object_key: str, content: bytes, *, content_type: str, sha256: str) -> None:
        destination = self._path(object_key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    def read(self, object_key: str) -> bytes:
        return self._path(object_key).read_bytes()

    def remove(self, object_key: str) -> None:
        self._path(object_key).unlink(missing_ok=True)
