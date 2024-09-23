import collections
import json
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


def get_asset_related_files(asset_name, files_text) -> Dict:
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
    if not project_name:
        raise ValueError('Project name cannot be empty')
    project_dir = dir_path / project_name
    mods_dir = project_dir / 'modfiles'
    mods_dir.mkdir(parents = True, exist_ok = True)

    return project_dir


def write_metadata_mods(author: str, version: Tuple[int, int], category: str, project_dir: Union[PathLike, Path]):
    metadata_dict = {
        'author': author,
        'version': version,
        'category': category
    }
    metadata_file = project_dir / 'METADATA.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata_dict, f)


def read_metadata_mods(metadata_file: Union[PathLike, Path]) -> Dict:
    if not metadata_file.exists():
        raise FileNotFoundError(f'Metadata file does not exist: {metadata_file}')
    with open(metadata_file, 'r') as f:
        metadata_dict = json.load(f)
    metadata_dict['version'] = tuple(metadata_dict['version'])
    return metadata_dict


def write_description_mods(desc: str, project_dir: Union[PathLike, Path]):
    description_file = project_dir / 'DESCRIPTION.html'
    with open(description_file, 'w') as f:
        f.write(desc)


def read_description_mods(desc_file: Union[PathLike, Path]) -> str:
    if not desc_file.exists():
        raise FileNotFoundError(f'Description file does not exist: {desc_file}')
    with open(desc_file, 'r') as f:
        return f.read()


@deco.validate_directory
def create_project_mods(
        project_name: str,
        dir_path: Union[PathLike, Path],
        author: str,
        version: Tuple[int, int],
        category: str,
        description: str
) -> None:
    if not dir_path.exists():
        raise err.InvalidDirectoryPath(f'Directory does not exist: {dir_path}')

    project_dir = create_project_mods_structure(project_name, dir_path)
    write_metadata_mods(author, version, category, project_dir)
    write_description_mods(description, project_dir)


@deco.validate_directory
def is_project_mods_directory(dir_path: Union[PathLike, Path]) -> bool:
    if not dir_path.exists():
        raise err.InvalidDirectoryPath(f'Directory does not exist: {dir_path}')
    # check modfiles subdirectory
    mod_dir = dir_path / 'modfiles'
    # check METADATA.json and DESCRIPTION.html files
    metadata_file = dir_path / 'METADATA.json'
    desc_file = dir_path / 'DESCRIPTION.html'
    return mod_dir.exists() and metadata_file.exists() and desc_file.exists()


def is_dsdb_directory(dir_path: Union[PathLike, Path]) -> bool:
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
    for src_file in src_files:
        src_dir = src_file.parent
        file_name = src_file.name
        yield copy_asset_file(src_dir, dest_dir, file_name, replace = replace)


def pack_project_mods(project_mods_dir: Union[PathLike, Path], dest_dir: Union[PathLike, Path], zip_file_name: str):
    if not is_project_mods_directory(project_mods_dir):
        raise err.InvalidProjectModsDirectory(f'Directory is not project mods directory: {project_mods_dir}')
    zip_file_path = dest_dir / zip_file_name

    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        for o in project_mods_dir.rglob('*'):
            if not o.is_dir():
                relative_path = o.relative_to(project_mods_dir)
                zip_file.write(o, relative_path)


