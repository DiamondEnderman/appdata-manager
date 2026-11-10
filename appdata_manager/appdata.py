from dataclasses import dataclass, field
import os
from enum import Enum, StrEnum, auto
from typing import Optional


class FileType(StrEnum): #These are all of the currently supported file types
    JSON = ".json"
    DB = ".db"

class _RootKey(StrEnum):
    WINDOWS = "appdata"

class StandardLinuxPath(StrEnum):
    """
    These are some of the industry standard linux paths for appdata.
    If you want something completely custom you will have to use your own paths.
    """
    CONFIG = os.path.expanduser("~/.config")
    SHARE = os.path.expanduser("~/.local/share")
    STATE = os.path.expanduser("~/.local/state")

@dataclass
class StorageConfig:
    """
    is_test is True by default, which appends -test to your base directory name
    """
    base_path_override: Optional[str | StandardLinuxPath] = None
    is_test: bool = True 
    subfolders: list[str | list | tuple] = field(default_factory = list)

#--------------------------------
#So far not needed in this module
@dataclass
class File:
    name: str
    file_type: FileType
#--------------------------------

class AppData:
    """
    Storage manager that handles directory management.
    Functional on both Windows and Linux.
    
    On linux, the base directory defaults to .local/share/
    but this can be overridden with standard linux paths or a completely custom override
    """

    def __init__(self, app_name: str, config: Optional[StorageConfig] | None = None, populate: bool = True):
        self.app_name: str = app_name
        self.config: StorageConfig = config or StorageConfig()

        self.APPDATA_PATH = os.getenv("APPDATA") or StandardLinuxPath.SHARE

        self.base_directory = self.config.base_path_override or os.path.join(self.APPDATA_PATH, self.app_name)
