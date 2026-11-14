from typing import Optional, ClassVar
from enum import StrEnum

class SeverityLevel(StrEnum):
    ERROR = "[ERROR]: "
    WARNING = "[WARNING]: "
    INFO = "[INFO]: "
    DEBUG = "[DEBUG]: "

#NOTE All custom exceptions will require a formatted message
#This is absolutely not of any sort of python standard, but this
#definitely was super fun to work out, and makes working with the
#warnings module for my formatted warnings a bit easier


#also imo this is one of the coolest things I have personally made,
#even if it is the most "Nobody codes like this" thing ever

class FormattedMessage(str):
    """
    Creates a formatted string object,
    This is specifically formatted for logging purposes.

    All custom exceptions will require a Formatted message,
    with or without notes
    """
    def __new__(cls, message: str, notes: Optional[str] = None):
        message_object = super().__new__(cls, cls._format_message(message, notes))
        return message_object

    @staticmethod
    def _format_notes(notes: str) -> str:
        formatted_notes: str = f"Notes: {notes}"
        return formatted_notes

    @classmethod
    def _format_message(cls, message: str, notes: Optional[str] = None) -> str:
        if notes is not None:
            return f"{message} {cls._format_notes(notes)}"
        return message

    @classmethod
    def with_severity(cls, severity_level: SeverityLevel, formatted_message: "FormattedMessage") -> "FormattedMessage":
        """
        This is a factory method that returns a new FormattedMessage object
        with the severity level appended to the beginning.
        """
        message_object = super().__new__(cls, f"{severity_level}{formatted_message}")
        return message_object

#EXCEPTIONS
class Error(Exception):
    def __init__(self, formatted_message: FormattedMessage) -> None:
        """
        These ones crash the program
        """
        super().__init__(FormattedMessage.with_severity(SeverityLevel.ERROR, formatted_message))

class MissingDirectoryError(Error):
    def __init__(self, directory_path: str, notes: Optional[str] = None) -> None:
        message = FormattedMessage(f"Directory Not Found at path: {directory_path}.", notes)
        super().__init__(message)

class MissingFileError(Error):
    def __init__(self, file_path: str, notes: Optional[str] = None) -> None:
        message = FormattedMessage(f"File Not Found at path: {file_path}.", notes)
        super().__init__(message)

class MissingEnvironmentVariable(Error):
    def __init__(self, environment_variable: str, notes: Optional[str] = None) -> None:
        message = FormattedMessage(f"Missing environment variable: {environment_variable}", notes)
        super().__init__(message)

class IncompatibleOSError(Error):
    def __init__(self, environment_variable: str, notes: Optional[str] = None) -> None:
        message = FormattedMessage(f"Path envelope is incompatible with the current operating system: {environment_variable}", notes)
        super().__init__(message)

class CorruptedFileError(Error):
    def __init__(self, file_path: str, notes: Optional[str] = None) -> None:
        message = FormattedMessage(f"File corrupted at: {file_path}.", notes)
        super().__init__(message)

class InvalidNameError(Error):
    def __init__(self, name: str, notes: Optional[str] = None) -> None:
        message = FormattedMessage(f"Invalid Application name: {name}.", notes)
        super().__init__(message)

class InvalidPathError(Error):
    def __init__(self, path: str, notes: Optional[str] = None) -> None:
        message = FormattedMessage(f"Invalid path: {path}.", notes)
        super().__init__(message)

class UnsupportedOS(Error):
    def __init__(self, operating_system: str) -> None:
        message = FormattedMessage(f"Unsupported Operating System: {operating_system}")
        super().__init__(message)

class SkillIssue(Error):
    def __init__(self, notes: Optional[str] = None) -> None:
        message = FormattedMessage("Did pylance not warn you plenty?", notes)
        super().__init__(message)

#WARNINGS
class CustomWarning(Warning):
    severity_level: ClassVar[SeverityLevel] = SeverityLevel.WARNING 
    """
    All subclasses default to severity level warning.
    """

    def __init__(self, formatted_message: FormattedMessage) -> None:
        """
        These ones do not crash the program
        """
        super().__init__(FormattedMessage.with_severity(self.severity_level, formatted_message))

class WrongOSPathOverrideWarning(CustomWarning):
    def __init__(self, notes: Optional[str] = None) -> None:
        message = FormattedMessage("Path override is not standard for this operating system.", notes)
        super().__init__(message)

class ManualOverrideWarning(CustomWarning):
    def __init__(self, notes: Optional[str] = None) -> None:
        message = FormattedMessage("Base path manual override.", notes)
        super().__init__(message)