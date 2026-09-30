import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

_test_data = tempfile.TemporaryDirectory(prefix="rsl-test-db-")
os.environ["RSL_DATABASE_URL"] = f"sqlite+pysqlite:///{Path(_test_data.name) / 'test.sqlite3'}"
os.environ["RSL_JWT_SECRET"] = "test-signing-key-for-rsl-api-with-32-bytes"


class MemoryObjectStorage:
    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def store(self, object_key: str, content: bytes, *, content_type: str, sha256: str) -> None:
        self.objects[object_key] = content

    def read(self, object_key: str) -> bytes:
        return self.objects[object_key]

    def remove(self, object_key: str) -> None:
        self.objects.pop(object_key, None)


from backend.api import service

service.set_object_storage(MemoryObjectStorage())
