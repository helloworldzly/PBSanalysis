from data_utils import *
import time
from collections import OrderedDict
import os
import csv
from utils import hex_to_unicode,hex_to_int
import json
import sys
#import pdb
def preprocess_by_day(date):
    print(f"start preprocessing data in {date}")
    csv.field_size_limit(100000000)

    start_time = time.time()
    base_data_dir = "/data4/zengliyi/all_preprocessed_data/"
        #"/mnt/data1/zhangzihao/preprocessed_data/"

    data_dir = os.path.join(base_data_dir) #date
    # block data
    blocks_path = os.path.join(data_dir,f"blocks_{date}.csv")
    logs_path = os.path.join(data_dir,f"logs_{date}.csv")
    token_transfers_path = os.path.join(data_dir,f"tokens_{date}.csv")
    traces_path = os.path.join(data_dir,f"traces_{date}.csv")
    transactions_path = os.path.join(data_dir,f"transactions_{date}.csv")


    #
    block_dict = dict()
    
    with open(blocks_path,'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        #print("block header: ", header)
        for row in reader:
            row[0] = int(row[0]) # number
            # row[1] timestamp
            # row[2] miner
            try:
                row[3] = hex_to_unicode(row[3]) #  extradata
            except:
                pass
            row[4] = int(row[4]) # gas_limit
            row[5] = int(row[5]) # gas_used
            row[6] = int(row[6]) # transaction_count
            row[7] = int(row[7]) # base_fee_per_gas
            row.append(dict()) # transactions
            #row.append([]) # logs 
            #row.append([]) # token_transfers 
            #row.append([]) # traces
            block_dict[row[0]] = row
            
    
    with open(transactions_path,'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        #print("transaction header: ", header)
        for row in reader:
            row[1] = int(row[1]) # transaction index
            row[4] = int(float(row[4])) # value
            row[5] = int(row[5]) # gas
            row[6] = int(row[6]) # gas_price
            row[7] = int(row[7]) # receipt_gas_used
            row[11] = int(row[11]) # block_number
            try:
                row[12] = int(float(row[12])) # max_fee_per_gas
                row[13] = int(float(row[13])) # max_priority_fee_per_gas
            except:
                row[12] = -1
                row[13] = -1
            
            row[15] = int(row[15]) # receipt_effective_gas_price
            #print(row)

            record = [
                row[0], # transaction hash
                row[1], # transaction_index
                row[2], # from address
                row[3], # to address
                row[4], # value
                row[5], # gas
                row[6], # gas price
                row[7], # receipt_gas_used
                row[8], # receipt_contract_address
                row[9], # receipt_status
                row[12],# max_fee_per gas
                row[13],# max_priority_fee_per_gas
                row[14], # transaction_type
                row[15], # receipt_effective_gas_price
                [], # logs
                [], # token_transfers
                [], # traces
            ]
            #print(record)
            block_dict[row[11]][8][row[0]] = record
    
    
    
    with open(logs_path,'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        #print("log header: ", header)
        for row in reader:
            row[0] = int(row[0])# log index
            
            row[5] = row[5].replace("\n ",",").replace('"',"").replace("'",'"')
            #print("log's topics: ", row[5])
            row[5] = json.loads(row[5]) # topics
            
            block_number = int(row[7])
            transaction_hash = row[1]
            #transaction_index = int(row[2])# transaction_index
            
            log_record = [
                row[0], # log index
                row[3], # address
                row[4], # data
                row[5], # topics
            ]


            

            #print(record)
            block_dict[block_number][8][transaction_hash][14].append(log_record)
            #assert(False)
    
    
    with open(token_transfers_path,'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        #print("token header: ", header)
        for row in reader:
            #print(row)
            row[3] = int(row[3]) # value
            row[5] = int(row[5]) # log_index

            transaction_hash = row[4]
            block_number = int(row[7])
            
            token_transfer_record = [
                row[0], # token_address
                row[1], # from_address
                row[2], # to_address
                row[3], # value
                row[5], # log_index
            ]

            block_dict[block_number][8][transaction_hash][15].append(token_transfer_record)
            #print(token_transfer_record)
    
    
    with open(traces_path,'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        #print("trace header: ", header)
        for row in reader:

            
            block_number = int(row[4])
            transaction_hash = row[0]
            #print(block_number)
            #print(transaction_hash)
            trace_record = [
                row[1], # from address
                row[2], # to address
                int(float(row[3])), # value
            ]
            
            
            block_dict[block_number][8][transaction_hash][16].append(trace_record)
    # 将transaction进行排序
    for block_number,block in block_dict.items():
        # 将transactions转化为列表
        block[8] = list(block[8].values())
        # 根据transactions_index进行排序
        block[8] = sorted(block[8], key=lambda x: x[1]) 


    # save data
    pkl_filename = f"preprocess_data_{date}.pkl"
    pkl_path = os.path.join(data_dir,pkl_filename)
    print("save file: ", pkl_path)

    save_pickle(pkl_path,block_dict)
    

    end_time = time.time()

    print(f"{date} used time: {end_time - start_time}")

    

def preprocess_by_month(month):
    #"""
    # get block files
    blocks_filename = get_files_list_by_month("block",month)
    # load block
    df = load_csv_to_pandas(blocks_filename[0])

    block_dict = OrderedDict(zip(df['number'], df.to_dict('records')))
    del df
    
    for key,value in block_dict.items():
        block_dict[key]["transactions"] = []
        block_dict[key]["token_transfers"] = []
        block_dict[key]["logs"] = []
        block_dict[key]["traces"] = []

    #print(block_dict[15660225])
    
    print("loaded block_data")
    
    """
    # load transaction data
    transaction_filenames =  get_files_list_by_month("transaction",month)
    print("start transactions data")

    
    file_num = 0
    for transaction_filename in transaction_filenames:
        file_num += 1
        start_time = time.time()
        df = load_parquet_to_pandas(transaction_filename)
        transactions_list = df.to_dict('records')
        #end_time = time.time()
        
        #for index, row in df.iterrows():
        for row in transactions_list:
            row["value"] = int(row["value"])
            #print(row['block_timestamp'])
            row['block_timestamp'] = str(row['block_timestamp'])
            #block_dict[row['block_number']]["transactions"].append(row)
            block_dict[row['block_number']]["transactions"].append(row)
        del df
        end_time = time.time()
        print(f"finish {file_num}/{len(transaction_filenames)}, use time {end_time -start_time}")
        #save_json("test.json",block_dict[15660557])
        #assert(0==1)
    """
    
    # load token_transfer data
    token_transfers_filenames =  get_files_list_by_month("token_transfer",month)
    print("start token_transfer data")

    
    file_num = 0
    for token_transfers_filename in token_transfers_filenames:
        print(token_transfers_filename)
        file_num += 1
        start_time = time.time()
        df = load_parquet_to_pandas(token_transfers_filename)
        token_transfers_list = df.to_dict('records')
        #end_time = time.time()
        
        #for index, row in df.iterrows():
        for row in token_transfers_list:
            row['block_timestamp'] = str(row['block_timestamp'])
            #block_dict[row['block_number']]["transactions"].append(row)
            block_dict[row['block_number']]["token_transfers"].append(row)
        del df
        end_time = time.time()
        print(f"finish {file_num}/{len(token_transfers_filenames)}, use time {end_time -start_time}")
        #save_json("test.json",block_dict[15660557])
        #assert(0==1)
    
    # load logs
    logs_filenames =  get_files_list_by_month("token_transfer",month)
    print("start token_transfer data")
    file_num = 0
    for logs_filename in logs_filenames:
        print(logs_filename)
        file_num += 1
        start_time = time.time()
        df = load_parquet_to_pandas(token_transfers_filename)
        token_transfers_list = df.to_dict('records')
        #end_time = time.time()
        
        #for index, row in df.iterrows():
        for row in token_transfers_list:
            row['block_timestamp'] = str(row['block_timestamp'])
            #block_dict[row['block_number']]["transactions"].append(row)
            block_dict[row['block_number']]["token_transfers"].append(row)
        del df
        end_time = time.time()
        print(f"finish {file_num}/{len(token_transfers_filenames)}, use time {end_time -start_time}")



        

def main():
    #pd.set_option("display.precision", 16)
    #preprocess_by_month("2022_10")
    #preprocess_by_day("2022-10-01")
    
    month = str(sys.argv[1])
    
    dates = get_dates_by_month(data_dir="/mnt/data1/zhangzihao/preprocessed_data/",month=month)
    
    #print(dates)
    for date in dates:
        try:
            preprocess_by_day(date)
        except:
            print(f"error in {date}")
    

    """
    start_time = time.time()
    df = load_parquet_to_pandas("/mnt/data1/zhangzihao/transactions/transactions_2023_01_000000000236.parquet.gzip")
    
    time1 = time.time()
    data_dict = df.to_dict('records')

    time2 = time.time()
    save_pickle("test.pkl",data_dict)
    #print(data_dict)
    end_time = time.time()

    print(time1-start_time)
    print(time2 - time1)
    print(end_time - time2)
    """
if __name__ == "__main__":
    main()