from utils import hex_to_unicode,hex_to_int
from data_utils import load_pickle,save_pickle,get_dates_by_month
import os
import csv


def get_coinbase_transfer_from_transaction(transaction, builder_address):
    coinbase_transfer_amount = 0
    
    traces = transaction[16]
    for trace in traces:
        from_address = trace[0]
        to_address = trace[1]
        value = trace[2]
        if (to_address == builder_address):
            coinbase_transfer_amount += value
    
    return coinbase_transfer_amount







def analysis_pbs(block):

    # builder
    builder_address = block[2] # miner
    builder_name = block[3] # extra_data

    
    if builder_name == "":
        builder_name = builder_address
    
    base_fee_per_gas = block[7]
    transaction_count = block[6]
    transactions = block[8]
    
    total_priority_fee_number = 0
    total_priority_fee = 0
    total_coinbase_transfer = 0
    total_coinbase_transfer_number = 0
    flashbots_payment_value = None
    flashbots_payment_fee = None
    proposer_address = None
    # transactions
    for transaction in transactions:
        
        # 计算fee
        receipt_gas_used = transaction[7] 
        receipt_effective_gas_price = transaction[13] 
        priorty_fee = receipt_gas_used * (receipt_effective_gas_price - base_fee_per_gas)
        #burnt_fee = receipt_gas_used * base_fee_per_gas
        transaction_fee = receipt_gas_used * receipt_effective_gas_price
        # 计算所有的transaction fee
        total_priority_fee += priorty_fee
        total_priority_fee_number += 1
        
        # 计算transaction
        transaction_index = transaction[1]
        from_address = transaction[2]
        if (transaction_index == transaction_count - 1) and (from_address == builder_address):

            flashbots_payment_value = transaction[4] # value
            flashbots_payment_fee = transaction_fee
            proposer_address = transaction[3] # proposer_address = to_address

        # coinbase_transfer builder receive
        coinbase_transfer_amount = get_coinbase_transfer_from_transaction(transaction, builder_address)
        total_coinbase_transfer += coinbase_transfer_amount
        if coinbase_transfer_amount > 0:
            total_coinbase_transfer_number += 1
    
    #print(total_priority_fee)
    #print(total_coinbase_transfer)
    #print(flashbots_payment_value)
    #print(flashbots_payment_fee)
    
    
    if flashbots_payment_value is None:
        # 说明这个是原始的block
        is_pbs_block = False
        
        builder_revenue = 0
        proposer_revenue = total_priority_fee + total_coinbase_transfer
        flashbots_payment_value = 0
        
        proposer_address = builder_address
        proposer_name = builder_name
        builder_address = ""
        builder_name = ""
    else:
        # 说明这个是pbs block
        is_pbs_block = True
        builder_revenue = total_coinbase_transfer + total_priority_fee - flashbots_payment_value - flashbots_payment_fee
        proposer_revenue = flashbots_payment_value

        flashbots_payment_value = flashbots_payment_value
        
        builder_address = builder_address
        builder_name = builder_name
        proposer_address = proposer_address
        proposer_name = ""
    #print(builder_revenue)


    return {
        "is_pbs_block" : is_pbs_block,
        "builder_address" : builder_address,
        "builder_name" : builder_name,
        "proposer_address": proposer_address, #原始区块miner
        "proposer_name" : proposer_name,
        "builder_revenue" : builder_revenue,
        "proposer_revenue" : proposer_revenue,
        "total_priority_fee_number": total_priority_fee_number,
        "total_priority_fee": total_priority_fee,
        "total_coinbase_transfer_number":total_coinbase_transfer_number,
        "total_coinbase_transfer": total_coinbase_transfer,
        "flashbots_payments_value": flashbots_payment_value,
        # add block info
        'timestamp': block[1],
        #'miner': block[2], #builder addr
        #'extra_data': block[3], #builder name
        "gas_limit": block[4],
        "gas_used": block[5],
        "transaction_count": block[6],
        "base_fee_per_gas": block[7]
        #"log_avaliable": log_avaliable,
        #"eth_price": prices["eth"]
    }
            

# analysis block pbs 并写入到date里
def analysis_pbs_into_pickle_by_date(date):
    print(f"start analysis pbs in {date}.")
    base_data_dir = "/data4/zengliyi/final_pre"
    #"/mnt/data1/zhangzihao/preprocessed_data"
    pkl_path = os.path.join(base_data_dir,date) #f"preprocess_data_{date}.pkl"
    block_dict = load_pickle(pkl_path)
    date_real = date.split(".")[0].split("_")[2]
    print ("real date: ", date_real)
    result_path = os.path.join("/data4/zengliyi/analysis2",f"result_v2_{date_real}.pkl")

    data = []
    for block_number,block in block_dict.items():
        block_result = analysis_pbs(block)
        block_result["block_number"] = block_number
        
        data.append(block_result)
    save_pickle(result_path,data)
"""
def analysis_pbs_into_csv_by_date(date):
    base_data_dir = "/mnt/data1/zhangzihao/preprocessed_data"
    pkl_path = os.path.join(base_data_dir,date,f"preprocess_data_{date}.pkl")
    block_dict = load_pickle(pkl_path)
    
    result_path = os.path.join(base_data_dir,date,f"result_v1_{date}.csv")
    f1 = open(result_path, "w", newline="")
    writer = csv.DictWriter(f1,fieldnames=["block_number","is_pbs_block","builder_address","builder_name","proposer_address","proposer_name","builder_revenue", "proposer_revenue","total_priority_fee_number","total_priority_fee","total_coinbase_transfer_number","total_coinbase_transfer","flashbots_payments_value"])


    writer.writeheader()
    for block_number,block in block_dict.items():
        block_result = analysis_block(block)
        block_result["block_number"] = block_number
        
        writer.writerow(block_result)
    
    f1.close()
"""

        

def main():

    #block_dict = load_pickle("/mnt/data1/zhangzihao/preprocessed_data/2023-01-25/preprocess_data_2023-01-25.pkl")
    #block = block_dict[16484956]
    #save_pickle("block_16484956.pkl",block)
    #block = load_pickle("block_16484956.pkl")
    #"2022-03",
    months = ["2022-03","2022-04","2022-05","2022-06","2022-07","2022-08", "2022-09", "2022-10", "2022-11", "2022-12", "2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", "2023-07", "2023-08", "2023-09", ]
    #"2022_11","2022_12","2023_01"]
    for month in months:
        base_data_dir = "/data4/zengliyi/final_pre"
        #"/mnt/data1/zhangzihao/preprocessed_data"
        dates = get_dates_by_month(base_data_dir,month)
        for date in dates:
            analysis_pbs_into_pickle_by_date(date)
            #analysis_block_into_pickle_by_date(date)
            print(f"finish {date}.")
            #break
        #break
    



if __name__ == "__main__":
    main()
    