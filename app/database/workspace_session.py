
from pathlib import Path
import json


class WorkspaceSession:
    """Stores and manages the currently selected business workspace."""

    def __init__(
        self,
        session_file="data/current_workspace.json",
    ):
        self.session_file = Path(session_file)

        # Make sure the folder for the session file exists.
        self.session_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def set_workspace(self, workspace_id):
        """Save the workspace that is currently active."""

        if not workspace_id or not str(workspace_id).strip():
            raise ValueError(
                "Workspace ID cannot be empty."
            )

        data = {
            "workspace_id": str(workspace_id).strip()
        }

        self.session_file.write_text(
            json.dumps(
                data,
                indent=4,
            ),
            encoding="utf-8",
        )

    def get_workspace_id(self):
        """Return the currently active workspace ID."""

        if not self.session_file.is_file():
            return None

        try:
            data = json.loads(
                self.session_file.read_text(
                    encoding="utf-8"
                )
            )

            return data.get("workspace_id")

        except (json.JSONDecodeError, OSError):
            return None

    def clear_workspace(self):
        """Remove the currently active workspace selection."""

        if self.session_file.is_file():
            self.session_file.unlink()

    def has_workspace(self):
        """Check whether an active workspace is selected."""

        return self.get_workspace_id() is not None
