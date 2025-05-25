import os
import re
import pyarrow.parquet as pq
import pandas as pd
import csv
import _pickle as cPickle
import json
#DATA_PATH = "/mnt/data1/zhangzihao"


def save_json(filename,data):
    json_str = json.dumps(data)

    # 将JSON格式的字符串存储到文件中
    with open(filename, 'w') as f:
        f.write(json_str)

def load_json(filename):
    # 打开文件
    with open(filename, 'r') as f:
        # 读取文件内容并解析为JSON对象
        data = json.load(f)

    return data
    
def load_pickle(filename):
    with open(filename, 'rb') as f:
        data_loaded = cPickle.load(f)
    return data_loaded

def save_pickle(filename,data):
    #print(filename)
    with open(filename, 'wb') as f:
        cPickle.dump(data, f)
    

def load_csv_to_pandas(filename):
    df = pd.read_csv(filename,low_memory=False)
    return df

def load_parquet_to_pandas(parquet_file):
    #parquet_file = 'path/to/file.parquet.gzip'
    #print(parquet_file)
    table = pq.read_table(parquet_file)
    df = table.to_pandas()

    return df





def get_files_list_by_month(data_type, month):
    
    files_list = []
    if data_type == "log":
        data_dir = os.path.join(DATA_PATH,f'logs/logs_{month}')
        pattern = re.compile(f'logs_{month}.*\.parquet\.gzip')
    elif data_type == "block":
        data_dir = os.path.join(DATA_PATH,'blocks')
        pattern = re.compile(f'blocks_{month}.csv')
    elif data_type == "token_transfer":
        data_dir = os.path.join(DATA_PATH,f'token_transfers')
        pattern = re.compile(f'token_transfers_{month}.*\.parquet\.gzip')
    elif data_type == "trace":
        data_dir = os.path.join(DATA_PATH,f'trace_filtered')
        pattern = re.compile(f'trace_filtered_{month}.*\.parquet\.gzip')
    elif data_type == "transaction":
        data_dir = os.path.join(DATA_PATH,f'transactions')
        pattern = re.compile(f'transactions_{month}.*\.parquet\.gzip')
    else:
        raise ValueError("invalid data type.")
    files = os.listdir(data_dir)
    #print(files)
    matched_files = [os.path.join(data_dir,filename) for filename in files if pattern.match(filename)]
    #matched_files = matched_files.sort()
    matched_files.sort()
    #print(matched_files)
    return matched_files

def get_dates_by_month(data_dir,month):

    # 合并数据
    #print (os.listdir(data_dir))
    #print (os.path.join(data_dir, 'preprocess_data_2023-05-21.pkl'))
    dates = [ d for d in os.listdir(data_dir) if os.path.exists(os.path.join(data_dir, d))]#isdir
    #change since d is preprocess_data_2023-02-20.pkl year=[16:20] month=[21:23]
    #print (dates[0][16:20], dates[0][21:23], month, month[0:4], month[5:7])
    dates = [date for date in dates if ((date[16:20] == month[0:4]) and (date[21:23] == month[5:7]))]
    #print (dates[0][0:4], dates[0][5:7], month, month[0:4], month[5:7])

    dates.sort()
    return dates

def get_all_dates(data_dir):

    # 合并数据
    dates = [ d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    dates.sort()
    return dates


def get_token_cache():
    token_dict = {}
    with open('/mnt/data1/zhangzihao/tokens.csv', newline='',encoding='utf-8') as csvfile:
        # 使用csv模块读取CSV文件
        reader = csv.DictReader(csvfile)
        # 遍历CSV文件中的每一行
        for row in reader:
            # 输出每一行的数据字典
            token_dict[row['address']] = {"symbol":row["symbol"],"name":row["name"],"decimals":row["decimals"]}
    # 输出转换后的字典
    return token_dict



def main():
    #pass
    base_data_dir =  "/mnt/data1/zhangzihao/preprocessed_data"
    dates = get_all_dates(base_data_dir)
    print(dates)
if __name__ == "__main__":
    main()
    
