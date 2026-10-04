
from pathlib import Path
import json


class WorkspaceManager:
    """Manages separate workspaces for different businesses."""

    def __init__(self, base_folder="data/workspaces"):
        self.base_folder = Path(base_folder)
        self.base_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_workspace(
        self,
        business_name,
        business_type,
        currency="PKR",
    ):
        """Create a new workspace for a business."""

        business_name = business_name.strip()
        business_type = business_type.strip()
        currency = currency.strip()

        if not business_name:
            raise ValueError(
                "Business name cannot be empty."
            )

        if not business_type:
            raise ValueError(
                "Business type cannot be empty."
            )

        workspace_id = self._generate_workspace_id()

        workspace_folder = (
            self.base_folder / workspace_id
        )

        workspace_folder.mkdir(
            parents=True,
            exist_ok=False,
        )

        # Create folders used by the business automation system.
        for folder_name in [
            "backup",
            "input",
            "processed",
            "archive",
        ]:
            (workspace_folder / folder_name).mkdir(
                parents=True,
                exist_ok=True,
            )

        profile = {
            "workspace_id": workspace_id,
            "business_name": business_name,
            "business_type": business_type,
            "currency": currency,
        }

        profile_path = (
            workspace_folder / "business_profile.json"
        )

        profile_path.write_text(
            json.dumps(
                profile,
                indent=4,
            ),
            encoding="utf-8",
        )

        return profile

    def get_workspace_path(self, workspace_id):
        """Return the folder path of a workspace."""

        return self.base_folder / workspace_id

    def get_database_path(self, workspace_id):
        """Return the database path for a workspace."""

        return (
            self.get_workspace_path(workspace_id)
            / "business.db"
        )

    def get_workspace_profile(self, workspace_id):
        """Return the saved business profile."""

        profile_path = (
            self.get_workspace_path(workspace_id)
            / "business_profile.json"
        )

        if not profile_path.is_file():
            return None

        return json.loads(
            profile_path.read_text(
                encoding="utf-8"
            )
        )

    def list_workspaces(self):
        """Return all existing business workspaces."""

        workspaces = []

        for folder in self.base_folder.iterdir():
            if not folder.is_dir():
                continue

            profile = self.get_workspace_profile(
                folder.name
            )

            if profile:
                workspaces.append(profile)

        return workspaces

    def _generate_workspace_id(self):
        """Generate a unique workspace ID."""

        existing_ids = {
            folder.name
            for folder in self.base_folder.iterdir()
            if folder.is_dir()
        }

        number = 1

        while True:
            workspace_id = (
                f"business_{number:03d}"
            )

            if workspace_id not in existing_ids:
                return workspace_id

            number += 1
