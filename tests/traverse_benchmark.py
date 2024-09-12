import os
import timeit
from pathlib import Path

# Define the directory path here
dir_path = Path(r'D:\IDrive\Project\2024\DigimonStory\original-content\DSDB')


def benchmark_os_walk():
    num_files = 0
    for root, dirs, files in os.walk(dir_path):
        num_files += len(dirs)
        num_files += len(files)
    return num_files


def benchmark_pathlib_rglob():
    num_files = len(list(dir_path.rglob('*')))
    return num_files


if __name__ == '__main__':
    # Benchmark os.walk
    start = timeit.default_timer()
    num_files_walk = benchmark_os_walk()
    end = timeit.default_timer()
    print(f"os.walk processed {num_files_walk} files in {end - start} seconds")

    # Benchmark pathlib.Path.rglob
    start = timeit.default_timer()
    num_files_rglob = benchmark_pathlib_rglob()
    end = timeit.default_timer()
    print(f"pathlib.Path.rglob processed {num_files_rglob} files in {end - start} seconds")
