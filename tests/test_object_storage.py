from rsl_foundation.object_storage import FileSystemObjectStorage


def test_filesystem_object_storage_round_trips_content_and_cleans_up(tmp_path):
    storage = FileSystemObjectStorage(tmp_path)
    content = b"persisted local artifact"

    storage.store("project/version/file.pdf", content, content_type="application/pdf", sha256="digest")

    assert storage.read("project/version/file.pdf") == content
    assert (tmp_path / "project" / "version" / "file.pdf").read_bytes() == content
    storage.remove("project/version/file.pdf")
    assert not (tmp_path / "project" / "version" / "file.pdf").exists()


def test_filesystem_object_storage_rejects_path_traversal(tmp_path):
    storage = FileSystemObjectStorage(tmp_path)

    try:
        storage.read("../../outside.pdf")
    except ValueError as error:
        assert "invalid object key" in str(error)
    else:
        raise AssertionError("path traversal must be rejected")