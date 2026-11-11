from dataclasses import dataclass, field
import os
from enum import Enum, StrEnum, auto
from typing import Optional


class FileType(StrEnum):
    """
    These are all of the currently supported file types.
    """
    JSON = ".json"
    DB = ".db"

class StandardLinuxPath(StrEnum):
    """
    These are some of the industry standard linux paths for appdata.
    If you want something completely custom you will have to use your own paths.
    """
    CONFIG = os.path.expanduser("~/.config")
    SHARE = os.path.expanduser("~/.local/share")
    STATE = os.path.expanduser("~/.local/state")
        # NOTE:
        # it is of note that even if you are on windows, these will execute and your 
        # expanded user profile (ie.. C:/Users/{Your Username}/.config) will be stored in memory, I will 
        # find a way to fix this later but it isn't a massive deal for now

@dataclass
class StorageConfig:
    """
    Setting is_test to True appends -test to your base directory name.
    I set this up this way so that you can have multiple appdata directories
    in the same place for the same app, but split between testing data and live
    data.
    """
    base_path_override: Optional[str | StandardLinuxPath] = None
    subfolders: list[str | list[str] | tuple[str, ...]] = field(default_factory=list) 
    is_test: bool = False 
        #TODO Something I want to add is just in time provisioning,
        #So I want to make this StorageConfig object work without NEEDING predetermined subfolders
        #Thats sort of a for later project since IMO having a base folder setup is going to be quite useful
        #for anything I make.

@dataclass
class File:
    name: str
    file_type: FileType
        #NOTE So far not needed in this module, might move to another

class AppData:
    """
    Storage manager that handles directory management.
    Functional on both Windows and Linux.
    
    On linux, the base directory defaults to .local/share/
    but this can be overridden with standard linux paths or a completely custom override
    """

    def __init__(self, app_name: str, config: Optional[StorageConfig] = None, provision: bool = True) -> None:
        self.app_name: str = app_name
        self.config: StorageConfig = config or StorageConfig()

        self.APPDATA_PATH = os.getenv("APPDATA") or StandardLinuxPath.SHARE

        self.base_path = self.config.base_path_override or self.APPDATA_PATH

        _formatted_name = f"{self.app_name}-test" if self.config.is_test else self.app_name
        self.app_directory = os.path.join(self.base_path, _formatted_name)

        if provision:
            self.provision()

    def provision(self) -> None:
        """
        Creates the base directory if it has not already been created
        and does the same with all subfolders given in the StorageConfig instance
        """
        self.create_folder()
        for item in self.config.subfolders:
            if isinstance(item, list | tuple):
                self.create_folder(*item)
            else:
                self.create_folder(item)
            

    def create_folder(self, *folders: str) -> str: 
        """
        Creates a folder within the base app directory.
        If more than one argument is given, it will create nested folders
        in the base app directory, with each previous argument being the parent folder
        of the successive argument.

        If the data is in list or tuple format, be sure to unpack it into arguments when
        calling this function.

        If no arguments are given, it will just create the base app directory.
        """
        folder_path = os.path.join(self.app_directory, *folders)
        os.makedirs(folder_path, exist_ok=True)

        return folder_path