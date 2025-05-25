from log_analyze import analysis_logs,cache_init,get_token_name,get_token_decimal,update_token_info
from data_utils import get_token_cache,load_pickle,save_pickle
from pbs_analysis import get_coinbase_transfer_from_transaction
from web3 import Web3
from price_utils import get_daily_prices

def remove_curve(swaps_list):
    new_list = []
    for swap in swaps_list:
        valid = True
        if swap["name"] == 'SWAP_CURVE':
            # 删去curve
            valid = False
        if swap["name"] == 'SWAP_UNISWAP_V2':
            # 删去uniswap v2
            if not (swap["exchange_name"] == 'SushiSwap' or swap["exchange_name"] == 'Uniswap V2'):
                valid = False
        

        if valid:    
            new_list.append(swap)
        
    return new_list

def load_tokens_cache():
    tokens_cache = load_pickle("/home/zengly23/pbs_zly/pbs_analysis/cache/tokens_cache_2023-09-30.pkl")
    return tokens_cache

def compute_transaction_cost(transaction,block):
    builder_address = block[2]
    base_fee_per_gas = block[7]
    receipt_gas_used = transaction[7] 
    receipt_effective_gas_price = transaction[13] 
    
    burnt_fee = receipt_gas_used * base_fee_per_gas
    priorty_fee = receipt_gas_used * (receipt_effective_gas_price - base_fee_per_gas)
    transaction_fee = receipt_gas_used * receipt_effective_gas_price
    coinbase_transfer_amount = get_coinbase_transfer_from_transaction(transaction, builder_address)

    # 总开销: burnt + bribe
    cost_eth = (transaction_fee + coinbase_transfer_amount) /10**18
    
    # burnt
    burnt_eth = burnt_fee / 10**18
    
    # builder净利润
    priorty_fee = priorty_fee / 10**18
    coinbase_transfer_amount = coinbase_transfer_amount / 10**18
    builder_profit_eth = (priorty_fee + coinbase_transfer_amount)

    return cost_eth,burnt_eth,priorty_fee,coinbase_transfer_amount,builder_profit_eth

def compute_mev_by_gains(gains, prices, tokens_cache):
    #print(gains)
    all_price = prices["all"]
    total_revenue = 0
    for token_address,amount in gains.items():
        #这里z只计算
        if token_address in all_price:
            try:
                price = all_price[token_address]
                
                if price < 0.1:
                    total_revenue += 0
                else:
                    decimals = int(tokens_cache[token_address.lower()]["decimals"])
                    revenue = amount / (10**decimals)  * price
                    total_revenue += revenue

                    #print(token_address)
                    #print(price)
                    #print(amount / (10**decimals)  * price)
            except:
                print("invalid_token!")
    return total_revenue




def detect_arbitrage(block,actions_by_block,prices,tokens_cache):
    
    transactions = block[8]
    arbitrage_findings = []
    for transaction, actions_by_transaction in zip(transactions, actions_by_block):
        
        actions_list,swaps_list,liquidations_list,flash_loans_list = actions_by_transaction
        swaps_list = remove_curve(swaps_list)
        findings = detect_arbitrage_by_transaction(swaps_list,transaction,block,prices,tokens_cache)
        
        arbitrage_findings.extend(findings)
    
    return arbitrage_findings

            
        

def detect_arbitrage_by_transaction(swaps_list,transaction,block,prices,tokens_cache):   
    # 探测arbitrage
    if len(swaps_list) >=2:
        #arbtirage至少需要两条交换交易
        
        #print(swaps_list)

        if swaps_list[0]["in_token"] != "" and swaps_list[-1]["out_token"] != ""  \
        and (swaps_list[0]["in_token"] == swaps_list[-1]["out_token"] or  \
        (swaps_list[0]["in_token"] in ["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"] \
        and swaps_list[-1]["out_token"] in ["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"])):
            # 需要让整体形成一个环
            valid = True
            gains = dict() # 需要保证交易中涉及到的每种货币都是正数
            intermediary_swaps = list()
            intermediary_swaps.append(swaps_list[0])
            for i in range(1, len(swaps_list)):
                previous_swap = swaps_list[i-1]
                current_swap = swaps_list[i]
                #记录中间环
                intermediary_swaps.append(current_swap)

                if previous_swap["out_token"] != current_swap["in_token"]:
                    valid = False
                if (swaps_list[0]["in_token"] == current_swap["out_token"] or \
                (swaps_list[0]["in_token"] in ["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"] \
                and current_swap["out_token"] in ["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"])) \
                and valid:
                    # 找到了一个环
                    #print("Detected an arbitrage.")

                    # 将环中内容添加到gain中
                    for swap in intermediary_swaps:
                        if not swap["in_token"] in gains:
                            gains[swap["in_token"]] = 0
                        gains[swap["in_token"]] -= int(swap["in_amount"])
                        if not swap["out_token"] in gains:
                            gains[swap["out_token"]] = 0
                        gains[swap["out_token"]] += int(swap["out_amount"])
                    intermediary_swaps = []


            if valid:
                # 计算收入
                pure_mev_usd = compute_mev_by_gains(gains, prices, tokens_cache)
                
                pure_mev_eth = pure_mev_usd / prices["eth"]
                
                # 计算开销
                cost_eth,burnt_eth,priorty_fee_eth,coinbase_transfer_amount,builder_profit_eth = compute_transaction_cost(transaction,block)

                
                # searcher净利润
                searcher_profit_eth = pure_mev_eth - cost_eth  
                
                # 去除burnt之后的 builder +searcher总利润
                total_profit_eth = searcher_profit_eth + builder_profit_eth  
                
                
                
                transaction_hash = transaction[0]
                from_address = transaction[2]
                to_address = transaction[3]
                
                finding = {
                    "mev_type": "arbitrage",
                    "sender":from_address,
                    "MEV bot": to_address,
                    "transaction_hash": transaction_hash,
                    "eth_prices": prices["eth"],
                    "pure_mev_eth": float(pure_mev_eth),
                    "pure_mev_usd": float(pure_mev_eth * prices["eth"]),
                    "cost_eth": float(cost_eth),
                    "cost_usd": float(cost_eth* prices["eth"]),
                    "builder_profit_eth": float(builder_profit_eth),
                    "builder_profit_usd": float(builder_profit_eth * prices["eth"]),
                    "searcher_profit_eth": float(searcher_profit_eth),
                    "searcher_profit_usd": float(searcher_profit_eth * prices["eth"]),
                    "priorty_fee_eth": float(priorty_fee_eth),
                    "priorty_fee_usd": float(priorty_fee_eth * prices["eth"]),
                    "coinbase_transfer_eth": float(coinbase_transfer_amount),
                    "coinbase_transfer_usd": float(coinbase_transfer_amount * prices["eth"]),
                    "burnt_eth": float(burnt_eth),
                    "burnt_usd": float(burnt_eth * prices["eth"]),
                    "total_profit_eth":float(total_profit_eth),
                    "total_profit_usd":float(total_profit_eth * prices["eth"]),
                }
            
            
            
                return [finding]
            
    return []



def detect_liquidation(block,actions_by_block,prices,tokens_cache):
    transactions = block[8]
    arbitrage_findings = []
    for transaction, actions_by_transaction in zip(transactions, actions_by_block):
        
        
        
        findings = detect_liquidation_by_transaction(actions_by_transaction,transaction,block,prices,tokens_cache)
        
        arbitrage_findings.extend(findings)
    
    return arbitrage_findings


def detect_liquidation_by_transaction(actions_by_transaction,transaction,block,prices,tokens_cache): 
    
    actions_list,swaps_list,liquidations_list,flash_loans_list = actions_by_transaction
    swaps_list = remove_curve(swaps_list)
    valid = False
    findings = []
    if len(liquidations_list) >= 1:
        valid = True
        gains = {}

        for liquidation in liquidations_list:

            # 还款token
            debt_token_address = liquidation["debt_token_address"]
            debt_token_name = liquidation["debt_token_name"]
            debt_token_amount = liquidation["debt_token_amount"] #/ 10**int(liquidation["debt_token_decimals"])
            
            # 抵押物token
            received_token_address = liquidation["received_token_address"]
            received_token_name = liquidation["received_token_name"]
            received_token_amount = liquidation["received_token_amount"] #/10**int(liquidation["received_token_decimals"])

            # 套利者
            liquidator = liquidation["liquidator"]
            protocol_name = liquidation["protocol_name"]

            
            if debt_token_address not in gains:
                gains[debt_token_address] = 0
            if received_token_address not in gains:
                gains[received_token_address] = 0
            gains[debt_token_address]  -= int(debt_token_amount)
            gains[received_token_address] += int(received_token_amount)

        for swap in swaps_list:
            if not swap["in_token"] in gains:
                gains[swap["in_token"]] = 0
            gains[swap["in_token"]] -= int(swap["in_amount"])
            if not swap["out_token"] in gains:
                gains[swap["out_token"]] = 0
            gains[swap["out_token"]] += int(swap["out_amount"])
        
        # 计算收益
        pure_mev_usd = compute_mev_by_gains(gains, prices, tokens_cache)
        pure_mev_eth = pure_mev_usd / prices["eth"]

         
        # 计算开销
        cost_eth,burnt_eth,priorty_fee_eth,coinbase_transfer_amount,builder_profit_eth = compute_transaction_cost(transaction,block)

        
        # searcher净利润
        searcher_profit_eth = pure_mev_eth - cost_eth  
        
        # 去除burnt之后的 builder +searcher总利润
        total_profit_eth = searcher_profit_eth + builder_profit_eth  


        transaction_hash = transaction[0]
        from_address = transaction[2]
        to_address = transaction[3]

        finding = {
                    "mev_type": "liquidation",
                    "sender":from_address,
                    "MEV bot": to_address,
                    "transaction_hash": transaction_hash,
                    "eth_prices": prices["eth"],
                    "pure_mev_eth": float(pure_mev_eth),
                    "pure_mev_usd": float(pure_mev_eth * prices["eth"]),
                    "cost_eth": float(cost_eth),
                    "cost_usd": float(cost_eth* prices["eth"]),
                    "builder_profit_eth": float(builder_profit_eth),
                    "builder_profit_usd": float(builder_profit_eth * prices["eth"]),
                    "searcher_profit_eth": float(searcher_profit_eth),
                    "searcher_profit_usd": float(searcher_profit_eth * prices["eth"]),
                    "priorty_fee_eth": float(priorty_fee_eth),
                    "priorty_fee_usd": float(priorty_fee_eth * prices["eth"]),
                    "coinbase_transfer_eth": float(coinbase_transfer_amount),
                    "coinbase_transfer_usd": float(coinbase_transfer_amount * prices["eth"]),
                    "burnt_eth": float(burnt_eth),
                    "burnt_usd": float(burnt_eth * prices["eth"]),
                    "total_profit_eth":float(total_profit_eth),
                    "total_profit_usd":float(total_profit_eth * prices["eth"]),
                }

        
        findings.append(finding)
    return findings







def detect_sandwich(block,actions_by_block,prices,tokens_cache):
    # 我们首先检测有没有两个接近的tran
    transactions = block[8]
    
    from_address_dict = dict()
    to_address_dict = dict()
    possible_pair = set() # 需要被检测的pair
    
    for i,transaction in enumerate(transactions):
        from_address = transaction[2]
        to_address = transaction[3]
        if from_address not in from_address_dict:
            from_address_dict[from_address] = [i]
        else:
            # 如果之前已经有交易了
            last_index = from_address_dict[from_address][-1]
            if (i - last_index >= 2) and  (i - last_index <= 2):
                possible_pair.add((last_index, i))
            from_address_dict[from_address].append(i)
        
        if to_address not in to_address_dict:
            to_address_dict[to_address] = [i]
        else:
            # 如果之前已经有交易了
            last_index = to_address_dict[to_address][-1]
            if (i - last_index >= 2) and  (i - last_index <= 2):
                possible_pair.add((last_index, i))
            to_address_dict[to_address].append(i)
    
    sandwich_finding = []
    for pair in possible_pair:
        start,end = pair
        finding =  detect_sandwich_by_start_end(block,actions_by_block,prices,tokens_cache,start,end)
        
        sandwich_finding.extend(finding)
    
        
    return sandwich_finding
    
        
            
        
def detect_sandwich_by_start_end(block,actions_by_block,prices,tokens_cache,start,end):
    #assert((end -start) == 2)
    t1 = actions_by_block[start]
    t2 = actions_by_block[end]
    tv = actions_by_block[start+1]
    
    swaps_t1 = t1[1]
    swaps_t2 = t2[1]
    swaps_tv = tv[1]
    
    swaps_t1 = remove_curve(swaps_t1)
    swaps_t2 = remove_curve(swaps_t2)
    swaps_tv = remove_curve(swaps_tv)
    
    valid = False
    
    exchange_dict = {}
    
    for swap in swaps_t1:
        if swap["exchange"] not in exchange_dict:
            exchange_dict[swap["exchange"]] = {"t1":{"in_token":swap["in_token"],
                                                     "in_amount":swap["in_amount"],
                                                     "out_token":swap["out_token"],
                                                     "out_amount":swap["out_amount"],
                                                    }
                                              }

    for swap in swaps_t2:
        if swap["exchange"] in exchange_dict:
            exchange_dict[swap["exchange"]]["t2"] = {"in_token":swap["in_token"],
                                                     "in_amount":swap["in_amount"],
                                                     "out_token":swap["out_token"],
                                                     "out_amount":swap["out_amount"],
                                                    }
    
    for swap in swaps_tv:
        
        if swap["exchange"] in exchange_dict:
            
            exchange_dict[swap["exchange"]]["tv"] ={"in_token":swap["in_token"],
                                                     "in_amount":swap["in_amount"],
                                                     "out_token":swap["out_token"],
                                                     "out_amount":swap["out_amount"],
                                                    }
    
    for exchange in exchange_dict.keys():
        if ("t1" not in exchange_dict[exchange]) or ("t2" not in exchange_dict[exchange]) or ("tv" not in exchange_dict[exchange]):
            continue
        t1_swap = exchange_dict[exchange]["t1"]
        t2_swap = exchange_dict[exchange]["t2"]
        tv_swap = exchange_dict[exchange]["tv"]
        if (t1_swap["in_token"] == tv_swap["in_token"]) and (t1_swap["out_token"] == tv_swap["out_token"]) \
        and (t1_swap["in_token"] == t2_swap["out_token"]) and (t1_swap["out_token"] == t2_swap["in_token"]): 
            
            ratio = t1_swap["out_amount"] / t2_swap["in_amount"]
            if ratio > 0.9 and ratio < 1.1:
                valid = True
    
    if valid:

        gains = {}
        swaps = swaps_t1 + swaps_t2
        for swap in swaps:
            in_token = swap["in_token"]
            out_token = swap["out_token"]
            # 统一eth token
            if in_token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE": 
                in_token = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            if out_token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE": 
                out_token = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            
            if not in_token in gains:
                gains[in_token] = 0
            gains[in_token] -= swap["in_amount"]
            if not out_token in gains:
                gains[out_token] = 0
            gains[out_token] += swap["out_amount"]
            
            
        #print(gains)
        
    
    
    if valid:
        # 计算t1和t2的gain
        
        pure_mev_usd = compute_mev_by_gains(gains,prices,tokens_cache)
        pure_mev_eth = pure_mev_usd / prices["eth"]
        
        
        transaction_t1 = block[8][start]
        transaction_t2 = block[8][end]
        
        
        cost_eth_t1,burnt_eth_t1,priorty_fee_t1,coinbase_transfer_amount_t1,_ = compute_transaction_cost(transaction_t1,block)
        cost_eth_t2,burnt_eth_t2,priorty_fee_t2,coinbase_transfer_amount_t2,_ = compute_transaction_cost(transaction_t2,block)
        
        
        cost_eth = (cost_eth_t1 + cost_eth_t2) 
        
        burnt_eth = (burnt_eth_t1 + burnt_eth_t2)
        
        priorty_fee_eth = (priorty_fee_t1 + priorty_fee_t2)

        coinbase_transfer_amount_eth = (coinbase_transfer_amount_t1 + coinbase_transfer_amount_t2)
        
        builder_profit_eth =  priorty_fee_eth + coinbase_transfer_amount_eth
        
        searcher_profit_eth = pure_mev_eth - cost_eth  
        
        # 去除burnt之后的 builder +searcher总利润
        total_profit_eth = searcher_profit_eth + builder_profit_eth
        
        
        from_address_t1 = transaction_t1[2]
        to_address_t1 = transaction_t1[3]
        
        from_address_t2 = transaction_t2[2]
        to_address_t2 = transaction_t2[3]
        
        transaction_hash_t1 = transaction_t1[0]
        transaction_hash_t2 = transaction_t2[0]
        finding ={
                    "type":"sandwich",
                    "from_address_t1": from_address_t1,
                    "to_address_t1": to_address_t1,
                    "transaction_hash_t1": transaction_hash_t1,
                    "from_address_t2": from_address_t2,
                    "to_address_t2": to_address_t2,
                    "transaction_hash_t2": transaction_hash_t2,
                    "eth_prices": prices["eth"],
                    "pure_mev_eth": float(pure_mev_eth),
                    "pure_mev_usd": float(pure_mev_eth * prices["eth"]),
                    "cost_eth": float(cost_eth),
                    "cost_usd": float(cost_eth* prices["eth"]),
                    "builder_profit_eth": float(builder_profit_eth),
                    "builder_profit_usd": float(builder_profit_eth * prices["eth"]),
                    "searcher_profit_eth": float(searcher_profit_eth),
                    "searcher_profit_usd": float(searcher_profit_eth * prices["eth"]),
                    "priorty_fee_eth": float(priorty_fee_eth),
                    "priorty_fee_usd": float(priorty_fee_eth * prices["eth"]),
                    "coinbase_transfer_eth": float(coinbase_transfer_amount_eth),
                    "coinbase_transfer_usd": float(coinbase_transfer_amount_eth * prices["eth"]),
                    "burnt_eth": float(burnt_eth),
                    "burnt_usd": float(burnt_eth * prices["eth"]),
                    "total_profit_eth":float(total_profit_eth),
                    "total_profit_usd":float(total_profit_eth * prices["eth"]),
        }
    
        return [finding]
    return []

        

def detect_mev_by_block(block,actions_by_block,prices,tokens_cache):
    
    transactions_map = {} # 每个transaction只能出现在
    
    sandwich_findings = detect_sandwich(block,actions_by_block,prices,tokens_cache)
    
    for finding in sandwich_findings:
        transactions_map[finding["transaction_hash_t1"]] = 1
        transactions_map[finding["transaction_hash_t2"]] = 1


    temp_liquidation_findings = detect_liquidation(block,actions_by_block,prices,tokens_cache)
    liquidation_findings = []
    for finding in temp_liquidation_findings:
        if finding["transaction_hash"] not in transactions_map:
            # 仅将之前没出现过的transaction加入
            transactions_map[finding["transaction_hash"]] = 1
            liquidation_findings.append(finding)

    
    temp_arbitrage_findings = detect_arbitrage(block,actions_by_block,prices,tokens_cache)
    arbitrage_findings = []
    for finding in temp_arbitrage_findings:
        if finding["transaction_hash"] not in transactions_map:
            # 仅将之前没出现过的transaction加入
            transactions_map[finding["transaction_hash"]] = 1
            arbitrage_findings.append(finding)
    

    return sandwich_findings,arbitrage_findings,liquidation_findings
    

def stat_user_perference(block,actions_by_block,sandwich_findings,arbitrage_findings,liquidation_findings):

    # 统计MEV bot
    mev_user_stat = {}
    mev_bot_stat = {}
    for finding in sandwich_findings:
        if finding['from_address_t1'] == finding['from_address_t2']:
            if finding['from_address_t1'] not in mev_user_stat:
                mev_user_stat[finding['from_address_t1']] = 0
            mev_user_stat[finding['from_address_t1']] += 1
        
        if finding['to_address_t1'] == finding['to_address_t2']:
            if finding['to_address_t1'] not in mev_bot_stat:
                mev_bot_stat[finding['to_address_t1']] = 0

            mev_bot_stat[finding['to_address_t1']] += 1

    for finding in arbitrage_findings:
        
        if finding['sender'] not in mev_user_stat:
            mev_user_stat[finding['sender']] = 0
        mev_user_stat[finding['sender']] += 1
        
        if finding['MEV bot'] not in mev_bot_stat:
            mev_bot_stat[finding['MEV bot']] = 0
        mev_bot_stat[finding['MEV bot']] += 1

    for finding in liquidation_findings:
        
        if finding['sender'] not in mev_user_stat:
            mev_user_stat[finding['sender']] = 0
        mev_user_stat[finding['sender']] += 1
        
        if finding['MEV bot'] not in mev_bot_stat:
            mev_bot_stat[finding['MEV bot']] = 0
        mev_bot_stat[finding['MEV bot']] += 1


    user_stat = {}
    trader_stat = {}

    transactions = block[8]

    for actions, transaction in zip(actions_by_block,transactions):
        actions_list = actions[0]
        user_address = transaction[2] # from address
        if len(actions_list) > 0:
            
            # trader
            if user_address not in trader_stat:
                trader_stat[user_address] = 0
            trader_stat[user_address] += 1
        else:
            # user 
            if user_address not in user_stat:
                user_stat[user_address] = 0
            user_stat[user_address] += 1

    return mev_user_stat,mev_bot_stat,trader_stat,user_stat

    


def run_mev_analysis(date):
    print(f"start analysis {date} ...")
    data_path = f"/data4/zengliyi/final_pre/preprocess_data_{date}.pkl"
    block_data = load_pickle(data_path)
    # token_cache
    tokens_cache = load_pickle("/home/zengly23/pbs_zly/pbs_analysis/cache/tokens_cache_2023-09-30.pkl")
    tokens_cache["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE".lower()] = {'symbol': 'ETH', 'name': 'Ether', 'decimals': 18}

    # prices
    prices = get_daily_prices(date)
    actions_by_block_dict = load_pickle(f"/data4/zengliyi/log_results/transaction_actions/transaction_actions_{date}.pkl")
    # 额外添加
    tokens_cache["0x0763fdCCF1aE541A5961815C0872A8c5Bc6DE4d7"] = {'symbol': '', 'name': 'suku', 'decimals': 18}
    
    block_stat_dict = {} 

    for block_number in block_data.keys():
        log_avaliable = True
        block = block_data[block_number]
        if block_number in actions_by_block_dict:
            actions_by_block = actions_by_block_dict[block_number]
        else:
            transaction_count = block[6]
            log_avaliable = False
            actions_by_block = [[[],[],[],[]] for i in range(transaction_count)]

        # mev analysis
        sandwich_findings,arbitrage_findings,liquidation_findings = detect_mev_by_block(block,actions_by_block,prices,tokens_cache)

        block_mev_stat = {
            "sandwich_findings":sandwich_findings,
            "arbitrage_findings": arbitrage_findings,
            "liquidation_findings": liquidation_findings,
        }
        # eth_price
        finding_list = sandwich_findings + arbitrage_findings + liquidation_findings
        # user perference analysis
        mev_user_stat,mev_bot_stat,trader_stat,user_stat = stat_user_perference(block,actions_by_block,sandwich_findings,arbitrage_findings,liquidation_findings)

        block_user_stat = {
            "mev_user_stat": mev_user_stat,
            "mev_bot_stat": mev_bot_stat,
            "trader_stat" : trader_stat,
            "user_stat" : user_stat,
        }

        # block_info 
        block_stat = { 
            "block_number": block[0],
            'timestamp': block[1],
            'miner': block[2],
            'extra_data' : block[3],
            "gas_limit" : block[4],
            "gas_used" : block[5],
            "transaction_count" : block[6],
            "base_fee_per_gas" : block[7],
            "log_avaliable": log_avaliable,
            "eth_price": prices["eth"]
        }

        block_stat.update(block_mev_stat)
        block_stat.update(block_user_stat)

        block_stat_dict[block_number] = block_stat

    
    result_path = f"/data4/zengliyi/mev_results/block_stat_v4_{date}.pkl"
    save_pickle(result_path,block_stat_dict)


def main():
    run_mev_analysis("2022-03-01")
if __name__ == "__main__":
    main()



                

