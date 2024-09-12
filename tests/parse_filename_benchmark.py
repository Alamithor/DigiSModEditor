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


if __name__ == '__main__':
    root_dir = Path(r'D:\IDrive\Project\2024\DigimonStory\original-content\DSDB')
    # Benchmark os.walk
    start = timeit.default_timer()
    num_files_walk = benchmark_regex(root_dir)
    end = timeit.default_timer()
    print(f"regex files processed {len(num_files_walk)} files in {end - start} seconds")

    # Benchmark pathlib.Path.rglob
    start = timeit.default_timer()
    num_files_rglob = benchmark_endswith(root_dir)
    end = timeit.default_timer()
    print(f"loop and endswith processed {len(num_files_rglob)} files in {end - start} seconds")

