import os
import re
import timeit
from pathlib import Path


def benchmark_regex(root_dir):
    r_name = re.compile(r'(\w+)\.(name)')
    name_list = []
    for root, dirs, files in os.walk(root_dir):
        files_text = ';'.join(files)
        name_list.extend(r_name.findall(files_text))
    return name_list


def benchmark_endswith(root_dir):
    name_list = []
    for root, dirs, files in os.walk(root_dir):
        for o in files:
            if o.endswith('.name'):
                name_list.append(o)
    return name_list


def benchmark_rglob(root_dir):
    name_list = []
    for o in root_dir.rglob('*.name'):
        name_list.append(o)
    return name_list


def collect_name(root_dir: Path):
    name_list = []
    files_text = ''
    for o in root_dir.iterdir():
        if o.suffix == '.name':
            name_list.append(o)
        if o.is_file():
            if files_text:
                files_text += f';{o.name}'
            else:
                files_text += f'{o.name}'
    return name_list, files_text


def benchmark_collect_rglob(root_dir: Path):
    result = {}
    related_suffix = ['.geom', '.skel', '.anim', '.img']
    name_list, files_text = collect_name(root_dir)
    counter = 2
    for o in name_list:
        if counter < 1:
            break
        if not o.stem.startswith('chr'):
            continue
        temp = {}
        for x in related_suffix:
            temp[x] = [i for i in root_dir.rglob(f'{o.stem}*{x}')]
            # temp[x] = root_dir.rglob(f'{o.stem}*{x}')
        result[o.stem] = temp
        counter -= 1
    return name_list, result


def benchmark_collect_regex(root_dir: Path):
    result = {}
    related_suffix = [r'\.(geom)', r'\.(skel)', r'(\_\w{2}\d{2}|)\.(anim)', r'(\w+)\.(img)']
    name_list, files_text = collect_name(root_dir)
    _, img_files_text = collect_name(root_dir / 'images')

    files_text += f';{img_files_text}'

    for o in name_list:
        if not o.stem.startswith('chr'):
            continue
        temp = {}
        for x in related_suffix:
            r_txt = f'({o.stem}){x}'
            re_found = re.findall(r_txt, files_text)
            if x == related_suffix[2] or x == related_suffix[3]:
                temp[x] = [f'{o_name}{o_mid}.{o_ext}' for (o_name, o_mid, o_ext) in re_found]
            else:
                temp[x] = [f'{o_name}.{o_ext}' for (o_name, o_ext) in re_found]
        result[o.stem] = temp
    return name_list, result


def benchmark_collect_iter_endswith(root_dir: Path):
    result = {}
    name_list = [o for o in root_dir.iterdir() if o.suffix == '.name']
    geo_skel = ['.geom', '.skel']
    for o in name_list:
        if not o.stem.startswith('chr'):
            continue
        temp_dict = {
            'geom': [],
            'skel': [],
            'anim': [],
            'img': [],
        }
        geom_file = root_dir / f'{o.stem}.geom'
        if geom_file.exists():
            temp_dict['geom'].append(geom_file)
        skel_file = root_dir / f'{o.stem}.skel'
        if skel_file.exists():
            temp_dict['skel'].append(skel_file)

        for i in root_dir.iterdir():
            if not i.stem.startswith('chr') or not i.suffix == '.anim':
                continue
            i_name = i.name
            if i_name.startswith(o.stem) and i_name.endswith('.anim'):
                temp_dict['anim'].append(i)
        for x in (root_dir / 'images').iterdir():
            x_name = x.name
            if x_name.startswith(o.stem):
                temp_dict['img'].append(x)

        result[o.stem] = temp_dict
    return name_list, result


if __name__ == '__main__':
    dir_path = Path(r'D:\IDrive\Project\2024\DigimonStory\original-content\DSDB')
    # Benchmark os.walk
    start = timeit.default_timer()
    num_files_walk = benchmark_regex(dir_path)
    end = timeit.default_timer()
    print(f"regex files processed {len(num_files_walk)} files in {end - start} seconds")

    # Benchmark endswith
    start = timeit.default_timer()
    num_files_endswith = benchmark_endswith(dir_path)
    end = timeit.default_timer()
    print(f"loop and endswith processed {len(num_files_endswith)} files in {end - start} seconds")

    # Benchmark pathlib.Path.rglob
    start = timeit.default_timer()
    num_files_rglob = benchmark_rglob(dir_path)
    end = timeit.default_timer()
    print(f"pathlib.Path.rglob processed {len(num_files_rglob)} files in {end - start} seconds")

    # Benchmark collect rglob
    # start = timeit.default_timer()
    # name_l_rglob, collected_rglob = benchmark_collect_rglob(dir_path)
    # end = timeit.default_timer()
    # print(f"Collect rglob processed {len(name_l_rglob)}, "
    #       f"files in {end - start} seconds")
    # print(collected_rglob)

    # Benchmark collect regex
    start = timeit.default_timer()
    name_l_regex, collected_regex = benchmark_collect_regex(dir_path)
    end = timeit.default_timer()
    print(f"Collect regex processed {len(name_l_regex)}, "
          f"files in {end - start} seconds")
    # print(collected_regex)

    # Benchmark collect iter endswith
    start = timeit.default_timer()
    name_l_iter, collected_iter = benchmark_collect_iter_endswith(dir_path)
    end = timeit.default_timer()
    print(f"Collect iter endswith processed {len(name_l_iter)}, "
          f"files in {end - start} seconds")
    print(collected_iter)

