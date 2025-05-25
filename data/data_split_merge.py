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
    df = load_parquet_to_pandas(filepath)

    
    file_id = re.search(f'{data_type}_info_(.*).parquet.gzip$',filename).group(1)

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


def main():

    data_type = str(sys.argv[1])
    month = str(sys.argv[2])

    data_split(data_type,month)
    data_merge(data_type,month)


if __name__ == "__main__":
    main()

