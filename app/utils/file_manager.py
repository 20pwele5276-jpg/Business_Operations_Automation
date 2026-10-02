from pathlib import Path


class FileManager:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)

    def create_folder(self):
        self.folder_path.mkdir(parents=True, exist_ok=True)