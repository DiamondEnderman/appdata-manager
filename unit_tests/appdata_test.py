import test_common_lib as common
from typing import Final
import os

def test_appdata():
    TEST_PATH_OVERRIDE: Final[str] = common.PackagePaths.TEMP
    IS_TEST_BOOL: Final[bool] = True
    DO_PROVISION: Final[bool] = True
    TEST_SUBFOLDERS: Final[list[str | list[str] | tuple[str, ...]]] = [ #gnarliest type hint ever btw
        "parentless_child1",
        "parentless_child2",
        ("grandparent", "parent", "child"),
        ["grandparent", "parent2"]
    ]
    CREATED_FOLDER: Final[tuple[str, ...]] = ("grandparent", "created_folder") #type hinting is cool we should do it more

    test_config = common.APPDATA_M.StorageConfig(
        base_path_override = TEST_PATH_OVERRIDE,
        is_test = IS_TEST_BOOL,
        subfolders = TEST_SUBFOLDERS
    )

    test_appdata = common.APPDATA_M.AppData(
        app_name = "example",
        config = test_config,
        provision = DO_PROVISION
    )

    test_appdata.create_folder(*CREATED_FOLDER)

    _ASSERTION_PATHS: Final[list[str]] = [
        test_appdata.app_directory_path,
        os.path.join(test_appdata.app_directory_path, *CREATED_FOLDER)
    ]

    for fset in TEST_SUBFOLDERS:
        if isinstance(fset, list | tuple):
            _ASSERTION_PATHS.append(os.path.join(test_appdata.app_directory_path, *fset))
        else:
            _ASSERTION_PATHS.append(os.path.join(test_appdata.app_directory_path, fset))

    for path in _ASSERTION_PATHS:
        assert os.path.isdir(path), f"{path} not found!"

if __name__ == "__main__":
    test_appdata()