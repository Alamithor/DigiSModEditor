import json
import os
import re
from pathlib import Path
from os import PathLike
from typing import Union, Generator, Tuple, Dict, List


def traverse_asset_files(dir_path: Union[PathLike, Path]) -> Tuple[str, Dict[str, List[str]]]:
    """
    Traverses the directory tree from `dir_path` and finds asset files.

    :param dir_path: The path to the root directory.
    :return: A generator that yields tuples containing the asset name and its corresponding children data.
    """
    pattern_geo = r'\.(geom)'
    pattern_skel = r'\.(skel)'
    pattern_anim = r'(\_\w{2}\d{2}|)\.(anim)'
    for root, dirs, files in os.walk(dir_path):
        files_text = ';'.join(files)
        name_list = [o for o in files if o.endswith('.name')]

        for name in name_list:
            file_name, ext = os.path.splitext(name)
            if file_name.startswith('cam_'):
                continue

            r_geo = f'({file_name})' + pattern_geo
            r_skel = f'({file_name})' + pattern_skel
            r_anim = f'({file_name})' + pattern_anim

            children_data = {}
            geo_files = [f'{o_name}.{o_ext}' for (o_name, o_ext) in re.findall(r_geo, files_text)]
            skel_files = [f'{o_name}.{o_ext}' for (o_name, o_ext) in re.findall(r_skel, files_text)]
            anim_files = [f'{o_name}{o_mid}.{o_ext}' for (o_name, o_mid, o_ext) in re.findall(r_anim, files_text)]
            children_data['Geometry'] = geo_files
            children_data['Skeleton'] = skel_files
            children_data['Animation'] = sorted(anim_files)

            yield name, children_data


def create_project_structure(project_name: str, dir_path: Union[PathLike, Path]) -> Path:
    if not project_name:
        raise ValueError('Project name cannot be empty')
    project_dir = dir_path / project_name
    if not project_dir.exists():
        project_dir.mkdir()
    mod_dir = project_dir / 'modfiles'
    if not mod_dir.exists():
        mod_dir.mkdir()

    return project_dir


def write_metadata_mod(author: str, version: Tuple[int, int], category: str, project_dir: Union[PathLike, Path]):
    metadata_dict = {
        'author': author,
        'version': version,
        'category': category
    }
    metadata_file = project_dir / 'METADATA.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata_dict, f)


def read_metadata_mod(metadata_file: Union[PathLike, Path]) -> Dict:
    if not metadata_file.exists():
        raise FileNotFoundError('Metadata file does not exist')
    with open(metadata_file, 'r') as f:
        metadata_dict = json.load(f)
    metadata_dict['version'] = tuple(metadata_dict['version'])
    return metadata_dict


def write_description_mod(desc: str, project_dir: Union[PathLike, Path]):
    description_file = project_dir / 'DESCRIPTION.html'
    with open(description_file, 'w') as f:
        f.write(desc)


def read_description_mod(desc_file: Union[PathLike, Path]) -> str:
    if not desc_file.exists():
        raise FileNotFoundError('Description file does not exist')
    with open(desc_file, 'r') as f:
        return f.read()


def create_project_mod(
        project_name: str,
        dir_path: Union[PathLike, Path],
        author: str,
        version: Tuple[int, int],
        category: str,
        description: str
) -> None:
    if not dir_path.exists():
        raise FileNotFoundError('Directory does not exist')

    project_dir = create_project_structure(project_name, dir_path)
    write_metadata_mod(author, version, category, project_dir)
    write_description_mod(description, project_dir)


def is_project_mod_directory(dir_path: Union[PathLike, Path]) -> bool:
    if not dir_path.exists():
        raise FileNotFoundError('Directory does not exist')
    # check modfiles subdirectory
    mod_dir = dir_path / 'modfiles'
    # check METADATA.json and DESCRIPTION.html files
    metadata_file = dir_path / 'METADATA.json'
    desc_file = dir_path / 'DESCRIPTION.html'
    return mod_dir.exists() and metadata_file.exists() and desc_file.exists()


def is_dsdb_directory(dir_path: Union[PathLike, Path]) -> bool:
    if not dir_path.exists():
        raise FileNotFoundError('Directory does not exist')
    # check any .name files
    found_counter = 0
    for o in dir_path.glob('*.name'):
        found_counter += 1
        if found_counter > 2:
            return True
    return False

