from dataclasses import dataclass
from enum import StrEnum
from typing import Optional
import json
import os
from shutil import copy2

import logging

from .exceptions import Error, CustomWarning, FormattedMessage, MissingFileError, MissingDirectoryError, CorruptedFileError

class SupportedFileType(StrEnum):
    """
    These are all of the currently supported file types.
    """
    JSON = ".json"
    DB = ".db"
    LOG = ".log"
    TMP = ".tmp"
    BAK = ".bak"
    CORRUPT = ".corrupt"

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
class _SupportedFile:
    """
    Base class for supported files
    """
    name: str
    directory_path: str
    file_type: SupportedFileType
    directory_provision: bool = False
    encoding: Optional[EncodingMethod] = EncodingMethod.UTF_8

    def __post_init__(self) -> None:
        if self.directory_provision:
            self.provide_directory()

    @property
    def name_with_extension(self) -> str:
        return f"{self.name}{self.file_type}"

    @property
    def file_path(self) -> str:
        return os.path.join(self.directory_path, self.name_with_extension)

    def provide_directory(self) -> None:
        os.makedirs(self.directory_path, exist_ok=True)

    def backup(self, destination_directory: Optional[str] = None, missing_ok: bool = False) -> bool:
        backup_file_name = f"{self.name_with_extension}{SupportedFileType.BAK}"
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

@dataclass
class JsonFile(_SupportedFile):
    """
    Object class for JSON files that handles reading and writing,
    Inherits name, directory_path, and file_path property from SupportedFile
    """
    file_type: SupportedFileType = SupportedFileType.JSON

    @property
    def _temp_file_path(self) -> str:
        return os.path.join(self.directory_path, f"{self.name_with_extension}{SupportedFileType.TMP}")

    def push(self, data: dict | list) -> None:
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

        if not self.directory_provision:
            if not os.path.isdir(self.directory_path):
                raise MissingDirectoryError(self.directory_path)

        try:
            with open(self._temp_file_path, "w", encoding=self.encoding) as file:
                json.dump(data, file, indent=4)
                file.flush()
                os.fsync(file.fileno())

            os.replace(self._temp_file_path, self.file_path)

        except Exception:
            if os.path.exists(self._temp_file_path):
                os.remove(self._temp_file_path)
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

        try:
            with open(self.file_path, "r", encoding = self.encoding) as file:
                return json.load(file)
        except json.JSONDecodeError:
            corrupted_path = os.path.join(self.directory_path, f"{self.name_with_extension}{SupportedFileType.CORRUPT}")
            os.replace(self.file_path, corrupted_path)

            raise CorruptedFileError(self.file_path, notes=f"Saving corrupted version at {corrupted_path}")

#TODO
#Need to add .db and .log file support

@dataclass
class DbFile(_SupportedFile):
    """
    This is just a bridge layer that can be handled by ORMS of your choice

    Support for built-in ORM factory methods will come later
    """
    file_type: SupportedFileType = SupportedFileType.DB
    directory_provision: bool = True
    encoding: Optional[EncodingMethod] = None

    @property
    def connection_uri(self) -> str:
        return f"sqlite:///{self._normalized_file_path}"

    @property
    def _normalized_file_path(self) -> str:
        return os.path.abspath(self.file_path).replace("\\", "/")

        #TODO
        #I do want to add full factory methods for SQL ORMs that would use those ORMs to do everything you would want.
        #I think this could be pretty simple to accomplish but for right now, this is fully decoupled and requires no
        #other prerequisites.

@dataclass
class LogFile(_SupportedFile):
    """
    For now, just a bridge to use with Python's built-in logging module
    """
    file_type: SupportedFileType = SupportedFileType.LOG
    directory_provision: bool = True
        #TODO
        #I will be adding full factory methods for logging using Python's logging module.
        #for now, this will just serve as a bridge between my architecture and said module