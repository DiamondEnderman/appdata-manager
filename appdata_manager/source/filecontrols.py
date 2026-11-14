from dataclasses import dataclass
from enum import StrEnum
from typing import Optional
import json
import os

from .exceptions import MissingFileError, MissingDirectoryError, CorruptedFileError

from shutil import copy2

class SupportedFileType(StrEnum):
    """
    These are all of the currently supported file types.
    """
    JSON = ".json"
    #TODO Uncomment these when they are added
    DB = ".db"
    #LOG = ".log"
    TMP = ".tmp"
    BAK = ".bak"
    CORRUPT = ".corrupt"

@dataclass
class _SupportedFile:
    """
    Base class for supported files
    """
    name: str
    directory_path: str
    file_type: SupportedFileType

    @property
    def file_path(self):
        return os.path.join(self.directory_path, f"{self.name}{self.file_type}")

    def backup(self, destination_directory: Optional[str] = None, missing_ok: bool = False) -> bool:
        backup_file_name = f"{self.name}{SupportedFileType.BAK}"
        backup_file_path = os.path.join(
            self.directory_path if destination_directory is None else destination_directory,
            backup_file_name
        )

        if destination_directory is not None:
            os.makedirs(destination_directory, exist_ok=True)

        if not os.path.exists(self.file_path):
            if missing_ok:
                return False
            
            raise MissingFileError(self.file_path, notes="Backup failed, set missing_ok to True if you want to bypass this exception")

        copy2(self.file_path, backup_file_path)
        return True

class EncodingMethod(StrEnum):
    """
    Common cross-platform text encodings compatible with Python's open().

    UTF-8 is generally the only option that makes sense, but I mean, options amirite?
    """

    UTF_8 = "utf-8"
    UTF_8_SIG = "utf-8-sig"
    UTF_16 = "utf-16"
    UTF_16_LE = "utf-16-le"
    UTF_16_BE = "utf-16-be"
    UTF_32 = "utf-32"
    UTF_7 = "utf-7"

    ASCII = "ascii"

    LATIN_1 = "latin-1"
    ISO_8859_15 = "iso8859-15"
    CP1252 = "cp1252"
    CP437 = "cp437"

    CP1251 = "cp1251"
    SHIFT_JIS = "shift-jis"
    GBK = "gbk"
    EUC_KR = "euc-kr"
    MAC_ROMAN = "mac-roman"

@dataclass
class JsonFile(_SupportedFile):
    """
    Object class for JSON files that handles reading and writing,
    Inherits name, directory_path, and file_path property from SupportedFile
    """
    file_type: SupportedFileType = SupportedFileType.JSON
    encoding: EncodingMethod = EncodingMethod.UTF_8

    def push(self, data: dict | list, directory_provision: bool = False) -> None:
        """
        Pushes given data to disk, writes the data to a temp file before fully
        committing it to the json file. If the writing fails, the temp file is removed from disk.

        if directory_provision is set to true, the directory and all parents will be created
        to house the file.
        """
        if not isinstance(data, dict | list):
            raise TypeError(
                f"Invalid argument type - {type(data).__name__} | "
                "Expected list/dict."
            )

        if not directory_provision:
            if not os.path.isdir(self.directory_path):
                raise MissingDirectoryError(self.directory_path)
        else:
            os.makedirs(self.directory_path, exist_ok=True)

        temp_path = os.path.join(self.directory_path, f"{self.name}{SupportedFileType.TMP}")

        try:
            with open(temp_path, "w", encoding=self.encoding) as file:
                    json.dump(data, file, indent=4)
                    file.flush()
                    os.fsync(file.fileno())

            os.replace(temp_path, self.file_path)

        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def pull(self, default: Optional[dict | list] = None) -> dict | list:
        """
        Returns data loaded from disk.
        defaults must be set if loading from a file that is not verified to exist.

        If the file is corrupted apon load, the return aborts and the file extension is
        changed to corrupt.
        """
        if not os.path.exists(self.file_path):
            if default is None:
                raise MissingFileError(self.file_path, notes="No Default Set.")

            return default

        with open(self.file_path, "r", encoding = self.encoding) as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                corrupted_path = os.path.join(self.directory_path, f"{self.name}{SupportedFileType.CORRUPT}")
                os.replace(self.file_path, corrupted_path)

                raise CorruptedFileError(self.file_path, notes=f"Saving corrupted version at {corrupted_path}")

#TODO
#Need to add .db and .log file support

@dataclass
class DbFile(_SupportedFile):
    file_type: SupportedFileType = SupportedFileType.DB
    directory_provision: bool = True

    def __post_init__(self):
        if self.directory_provision:
            self.provide_directory()
        

    def provide_directory(self):
        os.makedirs(self.directory_path, exist_ok=True)

    