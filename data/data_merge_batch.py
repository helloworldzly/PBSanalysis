from data_split_merge import data_merge
from data_utils import get_dates_by_month
from functools import partial
import glob
import multiprocessing
import time
from utils import chunk_list

def data_merge_batch(date):
    print(f"merge {date}")
    data_merge("blocks",date) #first
    data_merge("log",date) #logs
    data_merge("token_transfer",date)#token
    data_merge("trace",date) #traces
    data_merge("transaction", date) #transactions

def main():
    # 示例
    n_workers = 8
    BASE_DATA_DIR = "/data4/zengliyi/preprocessed_data"
        #"/data4/zengliyi/preprocessed_data_first"
    #"/mnt/data1/zhangzihao/preprocessed_data"
    # 获得日期
    dates = []
    #"2023-03"
    for month in ["2023-05", "2023-06", "2023-07", "2023-08", "2023-09"]:
            
        dates.extend(get_dates_by_month(BASE_DATA_DIR,month))

    pool = multiprocessing.Pool(processes=n_workers)
    pool.map(data_merge_batch,dates)
    
    pool.close()
    pool.join()
   
if __name__ == "__main__":
    main()


#transactions
#hash,transaction_index,from_address,to_address,value,gas,gas_price,receipt_gas_used,receipt_contract_address,receipt_status,block_timestamp,block_number,max_fee_per_gas,max_priority_fee_per_gas,transaction_type,receipt_effective_gas_price

#traces
#transaction_hash,from_address,to_address,value,block_number,block_timestamp

#token
#token_address,from_address,to_address,value,transaction_hash,log_index,block_timestamp,block_number

#log
#log_index,transaction_hash,transaction_index,address,data,topics,block_timestamp,block_number,block_hash

#block
#number,timestamp,miner,extra_data,gas_limit,gas_used,transaction_count,base_fee_per_gas

