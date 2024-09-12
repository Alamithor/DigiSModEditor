import os
import re
from pathlib import Path
from os import PathLike
from typing import Union


def traverse_asset_files(dir_path: Union[PathLike, Path]):
    pattern_geo = r'\.(geom)'
    pattern_skel = r'\.(skel)'
    pattern_anim = r'(\_\w{2}\d{2}|)\.(anim)'
    # name_list = []
    # file_list = []
    asset_data = {}
    for root, dirs, files in os.walk(dir_path):
        # file_list.extend(files)
        # name_list.extend([o for o in files if o.endswith('.name')])

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
