from dataclasses import dataclass
import os
import os.path as op
from typing import Final, Optional

from appdata_manager.source import appdata as APPDATA_M

#Set this to true if you want to auto build temp on import of test_common_lib
        #the option is there, not entirely recommended but hey some people are lazy
_AUTO_BUILD_TEMP = False

class PackagePaths:
    _PARENT_WORKSPACE: Final[str] = op.abspath(op.join(op.dirname(__file__), ".."))
    _PARENT_PACKAGE: Final[str] = op.join(_PARENT_WORKSPACE, "appdata_manager")

    UNIT_TESTS: Final[str] = op.join(_PARENT_WORKSPACE, "unit_tests")
    TEMP: Final[str] = op.join(_PARENT_WORKSPACE, "temp")

    SOURCE: Final[str] = op.join(_PARENT_PACKAGE, "source")
    DEPRECATED: Final[str] = op.join(_PARENT_PACKAGE, "deprecated")

def build_temp_folder():
    os.makedirs(PackagePaths.TEMP, exist_ok=True)

if _AUTO_BUILD_TEMP:
    build_temp_folder()

class SkillIssue(Exception):
    def __init__(self, message: str = "Did pylance not warn you plenty? Like, this is a unit test and you managed to get this exception.") -> None:
        super().__init__(message)