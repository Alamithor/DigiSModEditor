import collections
import json
import logging
import os
import re
import zipfile
from pathlib import Path
from os import PathLike
from typing import Union, Tuple, Dict, List, Generator

import speedcopy

from . import constants as const
from . import errors as err
from . import decorators as deco

log = logging.getLogger(const.LogName.MAIN)


def get_asset_related_files(asset_name, files_text) -> Dict:
    """
    Given an asset name and a text containing all files in a directory, returns a dictionary
    containing related files for the asset. The returned dictionary will have the following structure:
    {
        'asset_name': {
            'Name': [<asset_name>],
            'Geometry': [<asset_name>.geom],
            'Skeleton': [<asset_name>.skel],
            'Animation': [sorted list of <asset_name>_<number>.anim]
        }
    }
    :param asset_name: The name of the asset
    :param files_text: A text containing all files in the directory
    :return: A dictionary containing related files for the asset
    """
    file_name, ext = os.path.splitext(asset_name)
    # r_geo = f'({file_name})' + const.Pattern.GEO
    # r_skel = f'({file_name})' + const.Pattern.SKEL
    r_anim = f'({file_name})' + const.Pattern.ANIM

    result_data = {
        file_name: {}
    }
    name_file = asset_name
    geo_file = f'{file_name}.geom'
    skel_file = f'{file_name}.skel'
    # geo_files = [f'{o_name}.{o_ext}' for (o_name, o_ext) in re.findall(r_geo, files_text)]
    # skel_files = [f'{o_name}.{o_ext}' for (o_name, o_ext) in re.findall(r_skel, files_text)]
    anim_files = [f'{o_name}{o_mid}.{o_ext}' for (o_name, o_mid, o_ext) in re.findall(r_anim, files_text)]

    result_data[file_name]['Name'] = [name_file]
    result_data[file_name]['Geometry'] = [geo_file]
    result_data[file_name]['Skeleton'] = [skel_file]
    result_data[file_name]['Animation'] = sorted(anim_files)

    return result_data


def create_project_mods_structure(project_name: str, dir_path: Union[PathLike, Path]) -> Path:
    """
    Creates a directory structure for a project mods.

    Given a project name and a directory path, creates a directory structure for the project
    mods. The directory structure will be the following:
    - Project directory
        - modfiles (directory)

    :param project_name: The name of the project
    :param dir_path: The directory path where the project directory will be created
    :return: The path of the project directory
    :raises ValueError: If the project name is empty
    """
    if not project_name:
        raise ValueError('Project name cannot be empty')
    project_dir = dir_path / project_name
    mods_dir = project_dir / 'modfiles'
    mods_dir.mkdir(parents = True, exist_ok = True)

    return project_dir


def write_metadata_mods(title: str, author: str, version: Tuple[int, int], category: str, project_dir: Union[PathLike, Path]):
    """
    Writes the metadata of a project mods to a file.

    Given a project name, author, version, category, and a directory path, writes the metadata
    of the project mods to a file. The file will be a JSON file with the name 'METADATA.json'
    and will be located in the project directory.

    The JSON file will contain the following information:
    {
        'name': <project name>,
        'author': <author>,
        'version': <version tuple>,
        'category': <category>
    }

    :param title: The name of the project
    :param author: The author of the project
    :param version: The version of the project
    :param category: The category of the project
    :param project_dir: The directory path where the project directory is located
    """
    metadata_dict = {
        'name': title,
        'author': author,
        'version': version,
        'category': category
    }
    metadata_file = project_dir / 'METADATA.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata_dict, f)


def read_metadata_mods(metadata_file: Union[PathLike, Path]) -> Dict:
    """
    Reads the metadata of a project mods from a file.

    Given a file path of a 'METADATA.json' file, reads the metadata of the project mods
    from the file and returns it as a dictionary. The returned dictionary will contain
    the following information:
    {
        'name': <project name>,
        'author': <author>,
        'version': <version tuple>,
        'category': <category>
    }

    :param metadata_file: The file path of the 'METADATA.json' file
    :return: A dictionary containing the metadata of the project mods
    :raises FileNotFoundError: If the file does not exist
    """
    if not metadata_file.exists():
        raise FileNotFoundError(f'Metadata file does not exist: {metadata_file}')
    with open(metadata_file, 'r') as f:
        metadata_dict = json.load(f)
    metadata_dict['version'] = tuple(metadata_dict['version'])
    return metadata_dict


def write_description_mods(desc: str, project_dir: Union[PathLike, Path]):
    """
    Writes a description of a project mods to a file.

    Given a string and a project directory path, writes the string
    to a file named 'DESCRIPTION.html' in the project directory.

    :param desc: The description of the project mods
    :param project_dir: The directory path of the project mods directory
    """
    description_file = project_dir / 'DESCRIPTION.html'
    with open(description_file, 'w') as f:
        f.write(desc)


def read_description_mods(desc_file: Union[PathLike, Path]) -> str:
    """
    Reads a description of a project mods from a file.

    Given a file path of a 'DESCRIPTION.html' file, reads the description of the project mods
    from the file and returns it as a string.

    :param desc_file: The file path of the 'DESCRIPTION.html' file
    :return: A string containing the description of the project mods
    :raises FileNotFoundError: If the file does not exist
    """
    if not desc_file.exists():
        raise FileNotFoundError(f'Description file does not exist: {desc_file}')
    with open(desc_file, 'r') as f:
        return f.read()


@deco.validate_directory
def create_project_mods(
        dir_path: Union[PathLike, Path],
        project_name: str,
        author: str,
        version: Tuple[int, int],
        category: str,
        description: str
) -> None:
    """
    Creates a project mods directory.

    Given a directory path, a project name, an author, a version, a category, and a description,
    creates a project mods directory with the given name in the specified directory.
    The directory will contain a METADATA.json file with the given information and a DESCRIPTION.html
    file with the given description.

    :param dir_path: The directory path where the project mods directory will be created
    :param project_name: The name of the project
    :param author: The author of the project
    :param version: The version of the project as a tuple of two integers
    :param category: The category of the project
    :param description: The description of the project as a string
    """
    if not dir_path.exists():
        raise err.InvalidDirectoryPath(f'Directory does not exist: {dir_path}')

    project_dir = create_project_mods_structure(project_name, dir_path)
    log.info(f'Project mods folder created: {project_dir}')

    write_metadata_mods(project_name, author, version, category, project_dir)
    write_description_mods(description, project_dir)


@deco.validate_directory
def is_project_mods_directory(dir_path: Union[PathLike, Path]) -> bool:
    """
    Checks if a given directory path is a valid project mods directory.

    A project mods directory should contain a 'modfiles' subdirectory and two files:
    'METADATA.json' and 'DESCRIPTION.html'. If the directory does not exist, does not
    contain the 'modfiles' subdirectory, or does not contain the 'METADATA.json' and
    'DESCRIPTION.html' files, this function will return False.

    :param dir_path: The directory path to check
    :return: True if the directory path is a valid project mods directory, False otherwise
    """
    if not dir_path.exists():
        raise err.InvalidDirectoryPath(f'Directory does not exist: {dir_path}')
    # check modfiles subdirectory
    mod_dir = dir_path / 'modfiles'
    # check METADATA.json and DESCRIPTION.html files
    metadata_file = dir_path / 'METADATA.json'
    desc_file = dir_path / 'DESCRIPTION.html'
    return mod_dir.exists() and metadata_file.exists() and desc_file.exists()


@deco.validate_directory
def is_dsdb_directory(dir_path: Union[PathLike, Path]) -> bool:
    """
    Checks if a given directory path is a valid DSDB directory.

    A DSDB directory should contain at least 2 '.name' files. If the directory does not exist,
    does not contain any '.name' files, or does not contain at least 2 '.name' files, this
    function will return False.

    :param dir_path: The directory path to check
    :return: True if the directory path is a valid DSDB directory, False otherwise
    """
    if not dir_path.exists():
        raise err.InvalidDirectoryPath(f'Directory does not exist: {dir_path}')
    # check any .name files
    found_counter = 0
    for o in dir_path.glob('*.name'):
        found_counter += 1
        if found_counter > 2:
            return True
    return False


CopyResult = collections.namedtuple(
    'CopyResult',
    (
        'success',
        'source',
        'destination',
        'message'
    )
)


def copy_asset_file(
        src_dir: Union[PathLike, Path],
        dest_dir: Union[PathLike, Path],
        file: str,
        replace: bool = True
) -> CopyResult:
    """
    Copies a file from a source directory to a destination directory.

    If the destination file already exists, the `replace` parameter determines
    whether to overwrite the destination file or not. If `replace` is True,
    the existing destination file is renamed by appending ".old" to the end
    of the filename. If `replace` is False, a `CopyResult` with a success of
    False is returned with a message indicating that the destination file
    already exists.

    If the destination directory does not exist, it is created with parents.

    :param src_dir: The source directory containing the file to copy
    :param dest_dir: The destination directory to copy the file to
    :param file: The name of the file to copy
    :param replace: Whether to overwrite the destination file if it already exists
    :return: A `CopyResult` indicating the success and details of the copy operation
    """
    src_path = src_dir / file
    dest_path = dest_dir / file
    dest_old = dest_path.with_name(f'{dest_path.name}.old')

    if not src_path.exists():
        return CopyResult(False, src_path, dest_path, f'Source file {src_path} does not exist')

    if dest_path.exists():
        if replace:
            os.rename(dest_path, dest_old)
        else:
            return CopyResult(
                False,
                src_path,
                dest_path,
                f'Destination file {dest_path} already exists. Use the replace option to overwrite.'
            )

    if not dest_dir.exists():
        dest_dir.mkdir(parents = True)
    result = speedcopy.copyfile(str(src_path), str(dest_path))
    if result:
        if dest_old.exists():
            os.remove(dest_old)

        return CopyResult(True, src_path, dest_path, f'Successfully copied {src_path} to {dest_path}.')
    else:
        if dest_old.exists():
            os.rename(dest_old, dest_path)

        return CopyResult(False, src_path, dest_path, f'Failed to copy {src_path} to {dest_path}.')


def copy_asset(
        src_files: List[Union[PathLike, Path]],
        dest_dir: Union[PathLike, Path],
        replace: bool = True
) -> Generator[CopyResult, None, None]:
    """
    Copies all files in the given list from their respective source directories to a single destination directory.

    This is a convenience function that simply calls `copy_asset_file` for each file in the list.
    """
    for src_file in src_files:
        src_dir = src_file.parent
        file_name = src_file.name
        yield copy_asset_file(src_dir, dest_dir, file_name, replace = replace)


def pack_project_mods(project_mods_dir: Union[PathLike, Path], dest_dir: Union[PathLike, Path], zip_file_name: str):
    """
    Packs all files in the given project mods directory into a ZIP file.

    This function creates a ZIP file at the given destination directory with the given name.
    The contents of the project mods directory are recursively added to the ZIP file,
    maintaining their relative directory structure.

    :param project_mods_dir: The project mods directory to pack
    :param dest_dir: The destination directory to create the ZIP file in
    :param zip_file_name: The name of the ZIP file to create
    :raises InvalidProjectModsDirectory: If `project_mods_dir` is not a valid project mods directory
    """
    if not is_project_mods_directory(project_mods_dir):
        raise err.InvalidProjectModsDirectory(f'Directory is not project mods directory: {project_mods_dir}')
    zip_file_path = dest_dir / zip_file_name

    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        for o in project_mods_dir.rglob('*'):
            if not o.is_dir():
                relative_path = o.relative_to(project_mods_dir)
                zip_file.write(o, relative_path)


