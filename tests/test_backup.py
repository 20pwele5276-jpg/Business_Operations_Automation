
from app.automation.backup_service import BackupService


def test_database_backup(tmp_path):
    """Test that a database file is copied to the backup folder."""
    database_file = tmp_path / "business.db"
    backup_folder = tmp_path / "backup"

    database_file.write_bytes(
        b"test database content"
    )

    service = BackupService(
        database_path=database_file,
        backup_folder=backup_folder,
    )

    backup_file = service.backup_database()

    assert backup_file.exists()
    assert backup_file.parent == backup_folder
    assert backup_file.read_bytes() == database_file.read_bytes()


def test_database_backup_requires_database(tmp_path):
    """Test that backup fails when the database does not exist."""
    database_file = tmp_path / "missing.db"
    backup_folder = tmp_path / "backup"

    service = BackupService(
        database_path=database_file,
        backup_folder=backup_folder,
    )

    try:
        service.backup_database()
        assert False, "Backup should fail when the database is missing."

    except Exception as error:
        assert "Database file does not exist" in str(error)
