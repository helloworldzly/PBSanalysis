from data_split_merge import data_split
from functools import partial
import glob
import multiprocessing
import time
from utils import chunk_list


def get_filepaths(data_type):
    #data_dir = "/data4/zengliyi/pbs_dataset_first"
    data_dir = "/data4/zengliyi/pbs_dataset"
    pattern = f"{data_type}_info_*.parquet.gzip"
    #pattern = f"{data_type}_first_*.parquet.gzip"  # Change this to match the desired pattern
    # Get a list of all file names in the directory that match the pattern
    filepaths = glob.glob(data_dir + "/" + pattern)
    filepaths.sort()
    return filepaths
    #/data4/zengliyi/pbs_dataset
    # Set the directory path and the regular expression pattern
"""
    if data_type == 'block':
        pattern = f"{data_type}s_*.csv"
        filepaths = glob.glob(data_dir+ "/" + pattern)
        filepaths.sort()
    elif data_type == "token_transfer":
        pattern = f"{data_type}_info_000*.parquet.gzip"  # Change this to match the desired pattern

        # Get a list of all file names in the directory that match the pattern
        filepaths = glob.glob(data_dir+ "/" + pattern)
        filepaths.sort()
    else:
"""


def split_data_batch(file_paths,data_type):
    for file_path in file_paths:
        print("split_data_batch",file_path)
        data_split(filepath= file_path,data_type=data_type)








def main():
    # block
    #filepaths =get_filepaths("log")
    #print(filepaths)
    #split_data_batch([filepaths[0]],"log")


    # other
    
    n_workers = 8
    
    
    pool = multiprocessing.Pool(processes=n_workers)
    
    
    for data_type in ["token_transfer"]:
            #first ["blocks","logs","token","transactions","traces"]:
            #origin ["blocks","logs"," token_transfer","transactions","traces"]:
    
        file_paths = get_filepaths(data_type)
        print(file_paths)
        print("file num", len(file_paths))
        chunk_lists = chunk_list(file_paths, n_workers)
        pfunc = partial(split_data_batch,data_type=data_type)
        pool.map(pfunc,chunk_lists)
    
    pool.close()
    pool.join()
    
    #split_data_batch(filepaths,data_type)
if __name__ == "__main__":
    main()