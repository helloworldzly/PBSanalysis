

from log_analyze import analysis_logs
from data_utils import load_pickle,save_pickle,get_all_dates
from web3 import Web3
import os
import time
quicknode_provider = 'https://compatible-red-gadget.quiknode.pro/35ab5eaabb4231d8ab9ade04d779acbd179266d4/'
alchemy_provider ="https://eth-mainnet.g.alchemy.com/v2/YKv-d7WfRZ_uamnrtGoSfoNJ0jIQEvpf"
#w3 = Web3(Web3.HTTPProvider(quick_provider))
w3 = Web3(Web3.HTTPProvider(quicknode_provider))

tokens_cache = load_pickle("/home/zengly23/pbs_zly/pbs_analysis/cache/tokens_cache_2023-09-30.pkl")
cache = load_pickle("/home/zengly23/pbs_zly/pbs_analysis/cache/contracts_cache_2023-09-30.pkl")
#



# load data
#data_path = "/mnt/data1/zhangzihao/preprocessed_data/2022-03-01/preprocess_data_2022-03-01.pkl"
def run_log_analysis_by_date(date):
    print(f"start log_analysis in {date}.")
    data_dir = "/data4/zengliyi/final_pre"
    preprocess_data_path = os.path.join(data_dir,f"preprocess_data_{date}.pkl")
    preprocess_data = load_pickle(preprocess_data_path)
    #print("loaded data!")

    result_dict = {}
    error_block_list = []
    for block_number,block in preprocess_data.items():
        transactions = block[8]
        
        try:
            block_result_list = []
            for i,transaction in enumerate(transactions):
                actions_list,swaps_list,liquidations_list,flash_loans_list = analysis_logs(transaction,cache,tokens_cache,w3)
                block_result_list.append([actions_list,swaps_list,liquidations_list,flash_loans_list])
            result_dict[block_number] = block_result_list
            
                
        except:
            error_block_list.append(block_number)
    output_dir = "/data4/zengliyi/log_results"
    transaction_actions_dir = os.path.join(output_dir,f"transaction_actions")
    contracts_cache_dir = os.path.join(output_dir,f"contracts_cache")
    tokens_cache_dir = os.path.join(output_dir,f"tokens_cache")
    error_block_log_analysis_dir = os.path.join(output_dir,f"error_block_log_analysis")
    if not os.path.exists(transaction_actions_dir):
        os.makedirs(transaction_actions_dir)
    if not os.path.exists(contracts_cache_dir):
        os.makedirs(contracts_cache_dir)
    if not os.path.exists(tokens_cache_dir):
        os.makedirs(tokens_cache_dir)
    if not os.path.exists(error_block_log_analysis_dir):
        os.makedirs(error_block_log_analysis_dir)
    #save_pickle(os.path.join(data_dir,f"transaction_actions_{date}.pkl"),result_dict)
    #save_pickle(os.path.join(data_dir,f"contracts_cache_{date}.pkl"),cache)
    #save_pickle(os.path.join(data_dir,f"tokens_cache_{date}.pkl"),tokens_cache)
    #save_pickle(os.path.join(data_dir,f"error_block_log_analysis_{date}_list.pkl"),error_block_list)
    save_pickle(os.path.join(transaction_actions_dir,f"transaction_actions_{date}.pkl"),result_dict)
    save_pickle(os.path.join(contracts_cache_dir,f"contracts_cache_{date}.pkl"),cache)
    save_pickle(os.path.join(tokens_cache_dir,f"tokens_cache_{date}.pkl"),tokens_cache)
    save_pickle(os.path.join(error_block_log_analysis_dir,f"error_block_log_analysis_{date}_list.pkl"),error_block_list)
    del preprocess_data
    del result_dict

def get_dates_in_final_pre(data_dir):

    # 合并数据
    dates = [ d[-14:-4] for d in os.listdir(data_dir)]
    dates.sort()
    return dates

def main():
    print(w3.is_connected())
    base_data_dir = "/data4/zengliyi/final_pre"
    dates = get_dates_in_final_pre(base_data_dir)
    #dates = [date for date in dates if date >= "2023-03-01"] #why? fc version: 2022-03-01 - 2023-04-30
    print(dates)
    for date in dates:
        run_log_analysis_by_date(date)
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