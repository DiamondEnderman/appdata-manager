from dataclasses import dataclass, field
import os
from enum import StrEnum
from typing import Optional
import sys
import warnings

from .exceptions import (
    InvalidNameError, InvalidPathError, UnsupportedOS, SkillIssue, 
    WrongOSPathOverrideWarning, ManualOverrideWarning, MissingEnvironmentVariable,
    IncompatibleOSError
)

class _OperatingSystem(StrEnum):
    WINDOWS = "win32"
    LINUX = "linux"
    MAC = "darwin"

class StandardPaths(StrEnum):
    def resolve(self) -> str:
        raise NotImplementedError

class StandardWindowsPath(StandardPaths):
    """
    Standard Windows paths for appdata.
    These can be passed directly as a base path override
    """
    ROAMING = "APPDATA"
    LOCAL = "LOCALAPPDATA"

    def resolve(self) -> str:
        if sys.platform != _OperatingSystem.WINDOWS:
            raise IncompatibleOSError(self, "Cannot use Windows environment variables on non-Windows machines.")
        
        envelope = os.getenv(self)
        if envelope is None:
            raise MissingEnvironmentVariable(self)
        
        return envelope


class StandardLinuxPath(StandardPaths):
    """
    These are some of the industry standard linux paths for appdata.
    These can be passed directly as a base path override
    """
    CONFIG = "~/.config"
    SHARE = "~/.local/share"
    STATE = "~/.local/state"

    def resolve(self) -> str:
        if sys.platform != _OperatingSystem.LINUX:
            warnings.warn("Path provided is a Linux standard.", WrongOSPathOverrideWarning)

        return os.path.expanduser(self)

class StandardMacOSPath(StandardPaths):
    """
    Standard Mac paths for appdata.
    These can be passed directly as a base path override
    """
    APPLICATION_SUPPORT = "~/Library/Application Support"
    CACHES = "~/Library/Caches"
    LOGS = "~/Library/Logs"

    def resolve(self) -> str:
        if sys.platform != _OperatingSystem.MAC:
            warnings.warn("Path provided is a MacOS standard.", WrongOSPathOverrideWarning)

        return os.path.expanduser(self)

@dataclass
class StorageConfig:
    """
    Setting is_test to True appends -test to your base directory name.
    I set this up this way so that you can have multiple appdata directories
    in the same place for the same app, but split between testing data and live
    data.

    Base path override accepts members from the StandardPath enumclasses, full paths, or ~ paths.
    """
    base_path_override: Optional[str | StandardPaths] = None
    subfolders: list[str | list[str] | tuple[str, ...]] = field(default_factory=list) 
    is_test: bool = False 
        #TODO Something I want to add is just in time provisioning,
        #So I want to make this StorageConfig object work without NEEDING predetermined subfolders
        #Thats sort of a for later project since IMO having a base folder setup is going to be quite useful
        #for anything I personally make.

    def __post_init__(self):
        if not isinstance(self.base_path_override, str | None):
            raise SkillIssue(f"You haven't even got the prerequisites ready. Type: {type(self.base_path_override).__name__}")

        if self.base_path_override is not None and not self.base_path_override.strip():
            raise InvalidPathError(self.base_path_override, notes="Base path override cannot be empty or consist of only whitespace")

class AppData:
    """
    Storage manager that handles directory management.
    Functional on Windows, Linux, and MacOS.
    
    On linux, the base directory defaults to .local/share/
    but this can be overridden with standard linux paths or a completely custom override
    """

    def __init__(self, app_name: str, config: Optional[StorageConfig] = None, provision: bool = True) -> None:
        if not isinstance(app_name, str):
            raise SkillIssue(notes=f"Why did you think you could name your app anything other than a string??? Type: {type(app_name).__name__}")
        
        if not app_name.strip():
            raise InvalidNameError(app_name, notes="Application name cannot be empty or consist of only whitespace.")

        self.app_name: str = app_name
        self.config: StorageConfig = config or StorageConfig()

        self._load_app_directory_path()

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
        folder_path: str = os.path.join(self.app_directory_path, *folders)
        os.makedirs(folder_path, exist_ok=True)

        return folder_path

    def _get_appdata_path(self) -> str:
        match sys.platform:
            case _OperatingSystem.WINDOWS:
                local_appdata = os.getenv(StandardWindowsPath.LOCAL)
                if local_appdata is None:
                    raise MissingEnvironmentVariable(StandardWindowsPath.LOCAL) #this is pretty much here to make pylance shut up
                
                appdata_path: str = local_appdata

            case _OperatingSystem.LINUX:
                appdata_path: str = os.path.expanduser(StandardLinuxPath.SHARE)

            case _OperatingSystem.MAC:
                appdata_path: str = os.path.expanduser(StandardMacOSPath.APPLICATION_SUPPORT)

            case _:
                raise UnsupportedOS(operating_system=sys.platform)

        return appdata_path

    def _load_app_directory_path(self) -> None:
            #TODO this one is kinda ugly, gotta clean it up later

        if self.config.base_path_override is not None:
            match self.config.base_path_override:
                case StandardWindowsPath() as environment_key:
                    if sys.platform != _OperatingSystem.WINDOWS:
                        raise OSError("Cannot use a standard windows path as a base path override. Incompatible OS.")

                    envelope = os.getenv(environment_key)
                    if envelope is None:
                        raise MissingEnvironmentVariable(environment_key) 
                    
                    self.base_path: str = envelope
                    
                case StandardLinuxPath() as linux_path:
                    if sys.platform != _OperatingSystem.LINUX:
                        warnings.warn("Path provided is a Linux standard.", WrongOSPathOverrideWarning)

                    self.base_path: str = os.path.expanduser(linux_path)

                case StandardMacOSPath() as mac_path:
                    if sys.platform != _OperatingSystem.MAC:
                        warnings.warn("Path provided is a MacOS standard.", WrongOSPathOverrideWarning)

                    self.base_path: str = os.path.expanduser(mac_path)

                case str():
                    warnings.warn("Use with caution.", ManualOverrideWarning)
                    self.base_path: str = os.path.expanduser(self.config.base_path_override)

                case _:
                    raise SkillIssue("Im not gonna lie I dont know how you got here.")
        else:
            self.base_path:str = self._get_appdata_path()

        _formatted_name: str = f"{self.app_name}-test" if self.config.is_test else self.app_name
        self.app_directory_path: str = os.path.join(self.base_path, _formatted_name)