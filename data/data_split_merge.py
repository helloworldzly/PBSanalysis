import pandas as pd
from data_utils import *
import time
import os
import sys
import re
import gc

#import pdb

BASE_DATA_DIR = "/data4/zengliyi/preprocessed_data"
#"/data4/zengliyi/preprocessed_data_first"

# 将每个文件按照日期进行分割
def data_split(filepath,data_type):
    #BASE_DATA_DIR ="/mnt/data1/zhangzihao/preprocessed_data"
    print("data_split",filepath)
    filename = os.path.basename(filepath)
    
    #if data_type == "block":
    #    df = load_csv_to_pandas(filepath)
    #else:
    df = load_parquet_to_pandas(filepath)

    
    
    #if data_type == "blocks":
        #pdb.set_trace()
        #df['timestamp'] = df['timestamp'].str.slice(stop=-4)
        #df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')

        #grouped = df.groupby(df['timestamp'].dt.strftime('%Y-%m-%d'))
        #print(grouped)
        #for date, group in grouped:

            #date_dir = os.path.join(BASE_DATA_DIR, date)
            #if not os.path.exists(date_dir):
            #    os.mkdir(date_dir)
            

            # 将分组数据存储到文件中
            #filename = os.path.join(date_dir,f"{data_type}_{date}.csv")
            #group.to_csv(filename, index=False)

    
    #else:
    
    
    file_id = re.search(f'{data_type}_info_(.*).parquet.gzip$',filename).group(1)
    #re.search(f'{data_type}_first_(.*).parquet.gzip$',filename).group(1)
    

        # 将时间戳列转换为 Pandas 的日期时间类型
        #df['block_timestamp'] = pd.to_datetime(df['block_timestamp'])

    # 使用 strftime 方法将时间戳按天分组
    if data_type == "blocks":
        #pdb.set_trace()
        #df['timestamp'] = df['timestamp'].str.slice(stop=-4)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')

        grouped = df.groupby(df['timestamp'].dt.strftime('%Y-%m-%d'))
    else:
        grouped = df.groupby(df['block_timestamp'].dt.strftime('%Y-%m-%d'))

        # 遍历每个日期分组，将其数据存储到单独的文件中
    for date, group in grouped:

        date_dir = os.path.join(BASE_DATA_DIR, date)
        if not os.path.exists(date_dir):
            os.mkdir(date_dir)
            
        data_dir = os.path.join(BASE_DATA_DIR, date, data_type)
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        # 将分组数据存储到文件中
        filename = os.path.join(data_dir,f"{data_type}_{date}_{file_id}.csv")
        group.to_csv(filename, index=False)
    
    del df
        


# 已经作废
# 将每个子文件，按照日期分割成多个子文件
"""
def data_split_by_month(data_type,month):
    
    filepaths = get_files_list_by_month(data_type,month)
    
    for filepath in filepaths:
        
        
        filename = os.path.basename(filepath)
        if data_type == "trace":
            file_id = re.search(f'trace_filtered_{month}_(.*).parquet.gzip$',filename).group(1)
        else:
            file_id = re.search(f'{data_type}s_{month}_(.*).parquet.gzip$',filename).group(1)
        print(filepath)
        #print(file_id)
        # 读文件 block暂时不支持
        if data_type == "block":
            raise ValueError("block not support")
            
        df = load_parquet_to_pandas(filepath)
        
        # 将时间戳列转换为 Pandas 的日期时间类型
        #df['block_timestamp'] = pd.to_datetime(df['block_timestamp'])

        # 使用 strftime 方法将时间戳按天分组
        grouped = df.groupby(df['block_timestamp'].dt.strftime('%Y-%m-%d'))

        # 遍历每个日期分组，将其数据存储到单独的文件中
        for date, group in grouped:
            data_dir = os.path.join(BASE_DATA_DIR, date, data_type)

            if not os.path.exists(data_dir):
                os.mkdir(data_dir)
            # 将分组数据存储到文件中
            filename = os.path.join(data_dir,f"{data_type}_{date}_{file_id}.csv")
            group.to_csv(filename, index=False)
        
        del df
"""

def data_merge(data_type,date):
    BASE_DATA_DIR ="/data4/zengliyi/preprocessed_data"
        #"/data4/zengliyi/preprocessed_data_first"
        #"/mnt/data1/zhangzihao/preprocessed_data"
    print(f"start merging, {data_type} in {date} ")
    data_dir = os.path.join(BASE_DATA_DIR,date,data_type)
    file_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    #print(file_paths)
    df_list = []
    for filepath in file_paths:
        #读文件
        df = load_csv_to_pandas(filepath)
        df_list.append(df)
    # 合并为一个文件
    df = pd.concat(df_list)
    del df_list
    # 保存
    filename = os.path.join(BASE_DATA_DIR,date,f"{data_type}_{date}.csv")
    #print(filename)
    df.to_csv(filename, index=False)
    del df




"""
# 已经作废
def data_merge_by_month(data_type,month):
    print("start merging data")

    # 合并数据
    dates = [ d for d in os.listdir(BASE_DATA_DIR) if os.path.isdir(os.path.join(BASE_DATA_DIR, d))]
    dates = [date for date in dates if ((date[0:4] == month[0:4]) and (date[5:7] == month[5:7]))]
    
    dates.sort()

    for date in dates:
        
    
        data_dir = os.path.join(BASE_DATA_DIR,date,data_type)
        file_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
        print(file_paths)
        df_list = []
        for filepath in file_paths:
            #读文件
            # 读文件 block暂时不支持
            
            df = load_csv_to_pandas(filepath)
            
            
            df_list.append(df)

        # 合并为一个文件
        df = pd.concat(df_list)
        del df_list
        # 保存
        filename = os.path.join(BASE_DATA_DIR,date,f"{data_type}_{date}.csv")
        print(filename)
        df.to_csv(filename, index=False)
        del df
"""






"""
    start_time = time.time()
    df = pd.concat(df_list)
    print(df["block_timestamp"])
    

    # 将时间戳列转换为 Pandas 的日期时间类型
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 使用 strftime 方法将时间戳按天分组
    grouped = df.groupby(df['timestamp'].dt.strftime('%Y-%m-%d'))

    # 遍历每个日期分组，将其数据存储到单独的文件中
    for date, group in grouped:
        data_dir = os.path.join(BASE_DATA_DIR, date)
            

        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        # 将分组数据存储到文件中
        filename = os.path.join(data_dir,f"{data_type}_{date}")
        #assert(False)
        group.to_csv(filename, index=False)

    end_time = time.time()
    print(f"use time {end_time -start_time}.")
"""
def main():

    data_type = str(sys.argv[1])
    month = str(sys.argv[2])

    data_split(data_type,month)
    data_merge(data_type,month)


if __name__ == "__main__":
    main()

