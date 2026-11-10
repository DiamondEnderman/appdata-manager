import os
import json
from dataclasses import dataclass, field

class ArgTypeError(Exception):
    pass

@dataclass
class StorageConfig:
    is_test: bool = False
    default_encoding: str = "utf-8"
    subfolders: list[str | list | tuple] = field(default_factory = list)

class FileControls:
    """
    File Controller with support for json files
    """
    def __init__(self, file_path: str, encoding: str = "utf-8") -> None:
        self.file_path = file_path
        self.encoding = encoding

    def push_data(self, data: dict | list) -> None:
        if not isinstance(data, dict | list):
            raise ArgTypeError(                
                f"Invalid folder argument type: '{type(data).__name__}'. "
                "Expected dict | list."
            )
        
        parent_dir = os.path.dirname(self.file_path)

        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        temp_path = f"{self.file_path}.tmp"

        with open(temp_path, "w", encoding = self.encoding) as file:
            json.dump(data, file, indent = 4)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_path, self.file_path)

    def pull_data(self, default = None) -> dict | list:
        if not os.path.exists(self.file_path):
            return default if default is not None else {}

        with open(self.file_path, "r", encoding = self.encoding) as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return default if default is not None else {} 

class AppData:
    """
    Storage manager that handles directory creations and file controls within the bounds of the appdata folder
    """

    ROOT_KEY = "appdata"

    def __init__(self, app_name: str, config: StorageConfig | None = None):
        self.app_name = app_name
        self.config: StorageConfig = config or StorageConfig()
        self.appdata_path = os.getenv("APPDATA")

        self.base_dir = self.appdata_path or os.path.expanduser("~/.config")

        self.main_path = ""

    def initialize(self):
        """
        Initializes the main folder and all subfolders
        """
        folder_name = f"{self.app_name}-Test" if self.config.is_test else self.app_name

        self.main_path = os.path.join(self.base_dir, folder_name)

        if not os.path.exists(self.main_path):
            os.makedirs(self.main_path)

        for subfolder in self.config.subfolders:
            if isinstance(subfolder, (list, tuple)):
                sub_path = os.path.join(self.main_path, *subfolder)
            else:
                sub_path = os.path.join(self.main_path, subfolder)   

            if not os.path.exists(sub_path):
                os.makedirs(sub_path)

    def add_folder(self, folder: str | list | tuple) -> None:
        """
        Accepts strings to add folders directly to the main directory,
        A list or tuple can be given to created nested directories.
        """
        if isinstance(folder, (str, list, tuple)):
            self.config.subfolders.append(folder)
        else:
            raise ArgTypeError(
                f"Invalid folder argument type: '{type(folder).__name__}'. "
                "Expected str, list, or tuple."
            )

    def get_file(self, relative_path: str | list | tuple) -> FileControls:
        """
        Factory method that returns a FileControls instance bound to this Appdata Directory and encoding
        """
        if not self.main_path:
            raise RuntimeError("Appdata has not been initialized. Call initialize() before accessing files")

        if isinstance(relative_path, (list, tuple)):
            absolute_path = os.path.join(self.main_path, *relative_path)
        else:
            absolute_path = os.path.join(self.main_path, relative_path)

        return FileControls(file_path = absolute_path, encoding = self.config.default_encoding)


