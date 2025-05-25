
from key_address import *
from web3 import Web3


# token cache的key是lower
def update_token_info(token_address,tokens_cache,w3):
    
    try:
        token_contract = w3.eth.contract(address=token_address, abi=[{"constant":True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"}])
        token_name = token_contract.functions.name().call()
    except:
        try:
            token_contract = w3.eth.contract(address=token_address, abi=[{"name": "name", "outputs": [{"type": "bytes32", "name": "out"}], "inputs": [], "constant": True, "payable": False, "type": "function", "gas": 1623}])
            token_name = token_contract.functions.name().call().decode("utf-8").replace(u"\u0000", "")
        except:
            token_name = token_address
    
    try:
        token_contract = w3.eth.contract(address=token_address, abi=[{"constant":True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"}])
        decimals = token_contract.functions.decimals().call()
    except:
        decimals = 0
    
    tokens_cache[token_address.lower()]= {'symbol': '', 'name': token_name, 'decimals': decimals}


def get_token_name(token_address,tokens_cache,w3):
    name = ""
    if token_address.lower() not in tokens_cache:
        update_token_info(token_address,tokens_cache,w3)
    
    name = tokens_cache[token_address.lower()]["name"]

    name = name.replace(".", " ").replace("$", "")
    
    return name

def get_token_decimal(token_address,tokens_cache,w3):
    decimal = 0

    if token_address.lower() not in tokens_cache:
        update_token_info(token_address,tokens_cache,w3)
    
    decimals = tokens_cache[token_address.lower()]["decimals"]

    return decimals
def toSigned256(n):
    n = n & 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    return (n ^ 0x8000000000000000000000000000000000000000000000000000000000000000) - 0x8000000000000000000000000000000000000000000000000000000000000000


# cache data
# 这里用于记录所有的cache

# cache data结构
# 最外层对应每个操作
# UniswapV2 input 地址 return _token0,_token1,_name

def cache_init():
    cache = {}
    cache["uniswap_v2_swap"] = {}
    cache["uniswap_v3_swap"] = {}
    cache["curve_swap"] = {}
    cache["dydx_flashloan"] = {}

    return cache


def get_uniswap_v2_swap_contract_detail(log_address,cache,w3):
    uniswap_cache = cache["uniswap_v2_swap"]
    address = Web3.toChecksumAddress(log_address)
    #print(address)
    
    if not (address in uniswap_cache):
        exchange_contract = w3.eth.contract(address=address,abi=[
                        {
                            "constant":True,
                            "inputs":[],
                            "name":"name",
                            "outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,
                            "stateMutability":"view",
                            "type":"function"
                            },
                        {
                            "inputs":[],
                            "name":"token0",
                            "outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view",
                            "type":"function"
                            },
                        {
                            "inputs":[],
                            "name":"token1",
                            "outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view",
                            "type":"function"
                            }
                ])
        _token0 = exchange_contract.functions.token0().call()
        _token1 = exchange_contract.functions.token1().call()
        _name = exchange_contract.functions.name().call()
        uniswap_cache[address] = (_token0,_token1,_name)
    #print(uniswap_cache[address])
    return uniswap_cache[address]

def get_uniswap_v3_swap_contract_detail(log_address,cache,w3):
    uniswap_cache = cache["uniswap_v3_swap"]
    address = Web3.toChecksumAddress(log_address)
    if not (address in uniswap_cache):
        exchange_contract = w3.eth.contract(address=address, abi=[
                    {"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
                    {"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
                ])
        _token0 = exchange_contract.functions.token0().call()
        _token1 = exchange_contract.functions.token1().call()
        uniswap_cache[address] = (_token0,_token1)
    
    return uniswap_cache[address]


def get_curve_swap_contract_detail(log_address,_sold_id,_bought_id,cache,w3):
    curve_cache = cache["curve_swap"]
    address = Web3.toChecksumAddress(log_address)
    key = address +str(_sold_id) + "_"+ str(_bought_id)
    if not (key in curve_cache):
        try:
            curve_contract = w3.eth.contract(address=address, abi=[{"name":"underlying_coins","outputs":[{"type":"address","name":"out"}],"inputs":[{"type":"int128","name":"arg0"}],"constant":True,"payable":False,"type":"function","gas":2190}])
            in_token = curve_contract.functions.underlying_coins(_sold_id).call()
            out_token = curve_contract.functions.underlying_coins(_bought_id).call()
        except:
            try:
                curve_contract = w3.eth.contract(address=address, abi=[{"name":"underlying_coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":"arg0"}],"stateMutability":"view","type":"function","gas":2340}])
                in_token = curve_contract.functions.underlying_coins(_sold_id).call()
                out_token = curve_contract.functions.underlying_coins(_bought_id).call()
            except:
                try:
                    curve_contract = w3.eth.contract(address=address, abi=[{"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"int128","name":"arg0"}],"constant":True,"payable":False,"type":"function","gas":2310}])
                    in_token = curve_contract.functions.coins(min(1, _sold_id)).call()
                    out_token = curve_contract.functions.coins(min(1, _bought_id)).call()
                except:
                    curve_contract = w3.eth.contract(address=address, abi=[{"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":"arg0"}],"stateMutability":"view","type":"function","gas":2250}])
                    in_token = curve_contract.functions.coins(min(1, _sold_id)).call()
                    out_token = curve_contract.functions.coins(min(1, _bought_id)).call()
        curve_cache[key] =  (in_token,out_token)
    
    return curve_cache[key]

def get_dydx_flashloan_detail(log_address,_market_id,cache,w3):
    dydx_cache = cache["dydx_flashloan"]
    address = Web3.toChecksumAddress(log_address)
    key = address + str(_market_id)
    if not (key in dydx_cache):
        dydx_contract = w3.eth.contract(address=address, abi=[{"constant":True,"inputs":[{"name":"marketId","type":"uint256"}],"name":"getMarketTokenAddress","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"}])
        _market = dydx_contract.functions.getMarketTokenAddress(_market_id).call()

        dydx_cache[key] = _market
    
    return dydx_cache[key]





    






def analysis_logs(transaction,cache,tokens_cache,w3):  
    #print(f"hash : {transaction[0]}")
    actions_list = [] # 记录所有的actions
    swaps_list = []# 记录所有的swap
    liquidations_list = []#记录所有的liquidation
    flash_loans_list = []

    dydx_flashloan_market_dict = {}
    logs = transaction[14]
    
    for log in logs:

        log_index = log[0]
        log_address = log[1]
        log_data = log[2].replace("0x", "")
        log_topics = log[3]


        
        if SWAP_UNISWAP_V2 in log_topics: # 已经检查
            #try:
            _amount0In  = int(log_data[0:64], 16)
            _amount1In  = int(log_data[64:128], 16)
            _amount0Out = int(log_data[128:192], 16)
            _amount1Out = int(log_data[192:256], 16)
            """
            exchange_contract = get_contract(address=log_address,abi=[
                    {
                        "constant":True,
                        "inputs":[],
                        "name":"name",
                        "outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,
                        "stateMutability":"view",
                        "type":"function"
                        },
                    {
                        "inputs":[],
                        "name":"token0",
                        "outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view",
                        "type":"function"
                        },
                    {
                        "inputs":[],
                        "name":"token1",
                        "outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view",
                        "type":"function"
                        }
            ])
            
            # get in_token / out_token address
            _token0 = exchange_contract.functions.token0().call()
            _token1 = exchange_contract.functions.token1().call()
            _name = exchange_contract.functions.name().call()
            """
            _token0,_token1,_name= get_uniswap_v2_swap_contract_detail(log_address,cache,w3)
            
            if _name.startswith("SushiSwap"):
                _name = "SushiSwap"
            if _amount0In == 0 and _amount1Out == 0:
                amount_in  = _amount1In
                amount_out = _amount0Out
                in_token = _token1
                out_token = _token0
            elif _amount1In == 0 and _amount0Out == 0:
                amount_in  = _amount0In
                amount_out = _amount1Out
                in_token = _token0
                out_token = _token1
            else:
                continue

            in_token_name = get_token_name(in_token,tokens_cache,w3)
            out_token_name = get_token_name(out_token,tokens_cache,w3)
        
            event = {
                "action": "SWAP",
                "name": "SWAP_UNISWAP_V2",
                "log_index":log_index,
                "in_token": in_token,
                "out_token": out_token,
                "in_token_name": in_token_name,
                "out_token_name": out_token_name,
                "in_amount": amount_in, 
                "out_amount": amount_out,
                "exchange": log_address,
                "exchange_name": _name,
            }

            actions_list.append(event)
            swaps_list.append(event)
            #except:
            #    print("unrecognize uniswap v2!")
            #    pass
        
        if SWAP_UNISWAP_V3 in log_topics: #已经检查
            #try:
            _amount0   = toSigned256(int(log_data[0:64], 16))
            _amount1   = toSigned256(int(log_data[64:128], 16))
            """
            exchange_contract = get_contract(address=log_address, abi=[
                {"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
                {"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
            ])
            _token0 = exchange_contract.functions.token0().call()
            _token1 = exchange_contract.functions.token1().call()
            """
            _token0,_token1 = get_uniswap_v3_swap_contract_detail(log_address,cache,w3)
            
            if _amount0 < 0:
                amount_in = _amount1
                amount_out = abs(_amount0)
                in_token = _token1
                out_token = _token0
            else:
                amount_in = _amount0
                amount_out = abs(_amount1)
                in_token = _token0
                out_token = _token1
            
            #get token name

            in_token_name = get_token_name(in_token,tokens_cache,w3)
            out_token_name = get_token_name(out_token,tokens_cache,w3)
            
            event = {
                "action": "SWAP",
                "name": "SWAP_UNISWAP_V3",
                "log_index":log_index,
                "in_token": in_token,
                "out_token": out_token,
                "in_token_name": in_token_name,
                "out_token_name": out_token_name,
                "in_amount": amount_in, 
                "out_amount": amount_out,
                "exchange": log_address,
                "exchange_name": "uniswapv3",
            }

            actions_list.append(event)
            swaps_list.append(event)

        
        
            #print("uniswap v3 swap!")
            #except:
            #    print("unrecognize uniswap v3!")
            #    pass
        if BALANCER in log_topics:
            # BALANCER V2
            #try:
                
            _tokenIn        = Web3.toChecksumAddress("0x"+log_topics[2].replace("0x", "")[24:64])
            _tokenOut       = Web3.toChecksumAddress("0x"+log_topics[3].replace("0x", "")[24:64])
            #_tokenIn        = Web3.toChecksumAddress("0x"+event["topics"][2].hex().replace("0x", "")[24:64])
            #_tokenOut       = Web3.toChecksumAddress("0x"+event["topics"][3].hex().replace("0x", "")[24:64])
            _tokenAmountIn  = int(log_data[0:64], 16)
            _tokenAmountOut = int(log_data[64:128], 16)
            
            in_token_name = get_token_name(_tokenIn,tokens_cache,w3)
            out_token_name = get_token_name(_tokenOut,tokens_cache,w3)
            
            
            
            event = {
                "action": "SWAP",
                "name": "SWAP_BALANCER",
                "log_index":log_index,
                "in_token": _tokenIn,
                "out_token": _tokenOut,
                "in_token_name": in_token_name,
                "out_token_name": out_token_name,
                "in_amount": _tokenAmountIn, 
                "out_amount": _tokenAmountOut,
                "exchange": log_address,
                "exchange_name": "balancer",
            }

            actions_list.append(event)
            swaps_list.append(event)
            #print("balancer swap!")
            #except:
            #    print("unrcognize balancer!")
            #    pass
            
        if (CURVE_1 in log_topics) or (CURVE_2 in log_topics):
            #try:
            _sold_id       = int(log_data[0*64:0*64+64], 16)
            _tokens_sold   = int(log_data[1*64:1*64+64], 16)
            _bought_id     = int(log_data[2*64:2*64+64], 16)
            _tokens_bought = int(log_data[3*64:3*64+64], 16)
            """
            try:
                curve_contract = get_contract(address=log_address, abi=[{"name":"underlying_coins","outputs":[{"type":"address","name":"out"}],"inputs":[{"type":"int128","name":"arg0"}],"constant":True,"payable":False,"type":"function","gas":2190}])
                in_token = curve_contract.functions.underlying_coins(_sold_id).call()
                out_token = curve_contract.functions.underlying_coins(_bought_id).call()
            except:
                try:
                    curve_contract = get_contract(address=log_address, abi=[{"name":"underlying_coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":"arg0"}],"stateMutability":"view","type":"function","gas":2340}])
                    in_token = curve_contract.functions.underlying_coins(_sold_id).call()
                    out_token = curve_contract.functions.underlying_coins(_bought_id).call()
                except:
                    try:
                        curve_contract = get_contract(address=log_address, abi=[{"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"int128","name":"arg0"}],"constant":True,"payable":False,"type":"function","gas":2310}])
                        in_token = curve_contract.functions.coins(min(1, _sold_id)).call()
                        out_token = curve_contract.functions.coins(min(1, _bought_id)).call()
                    except:
                        curve_contract = get_contract(address=log_address, abi=[{"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":"arg0"}],"stateMutability":"view","type":"function","gas":2250}])
                        in_token = curve_contract.functions.coins(min(1, _sold_id)).call()
                        out_token = curve_contract.functions.coins(min(1, _bought_id)).call()
            """
            in_token,out_token = get_curve_swap_contract_detail(log_address,_sold_id,_bought_id,cache,w3)
            
            in_token_name = get_token_name(in_token,tokens_cache,w3)
            out_token_name = get_token_name(out_token,tokens_cache,w3)
            
            event = {
                "action": "SWAP",
                "name": "SWAP_CURVE",
                "log_index":log_index,
                "in_token": in_token,
                "out_token": out_token,
                "in_token_name": in_token_name,
                "out_token_name": out_token_name,
                "in_amount": _tokens_sold, 
                "out_amount": _tokens_bought,
                "exchange": log_address,
                "exchange_name": "curve",
            }

            actions_list.append(event)
            swaps_list.append(event)
            #print("curve swap!")
            #except:
            #    print("unrcognize curve swap")
            #    pass
        if (BANCOR in log_topics):
            #try:
            #_fromToken = Web3.toChecksumAddress("0x"+event["topics"][1].hex().replace("0x", "")[24:64])
            #_toToken = Web3.toChecksumAddress("0x"+event["topics"][2].hex().replace("0x", "")[24:64])
            _fromToken = Web3.toChecksumAddress("0x"+log_topics[1].replace("0x", "")[24:64])
            _toToken = Web3.toChecksumAddress("0x"+log_topics[2].replace("0x", "")[24:64])
            _amount = int(log_data[0*64:0*64+64], 16)
            _return = int(log_data[1*64:1*64+64], 16)

            in_token_name = get_token_name(_fromToken,tokens_cache,w3)
            out_token_name = get_token_name(_toToken,tokens_cache,w3)
            if in_token_name.lower() == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE".lower():
                in_token_name = "Ether"
            if out_token_name.lower() == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE".lower():
                out_token_name = "Ether"
            
            event = {
                "action": "SWAP",
                "name": "SWAP_BANCOR",
                "log_index":log_index,
                "in_token": _fromToken,
                "out_token": _toToken,
                "in_token_name": in_token_name,
                "out_token_name": out_token_name,
                "in_amount": _amount, 
                "out_amount": _return,
                "exchange": log_address,
                "exchange_name": "bancor",
            }

            actions_list.append(event)
            swaps_list.append(event)
            
            #print("bancor swap!")
            #except:
            #    print("unrcognize bancor swap!")
            #    pass
        if (ZERO_EX_1 in log_topics) or (ZERO_EX_2 in log_topics) or (ZERO_EX_3 in log_topics):
            # 0x
            #try:
            if (ZERO_EX_1 in log_topics):
                index = int(log_data[0*64:0*64+64], 16) * 2 + 96
                _makerAssetData = Web3.toChecksumAddress("0x"+log_data[index:index+40])
                index = int(log_data[1*64:1*64+64], 16) * 2 + 96
                _takerAssetData = Web3.toChecksumAddress("0x"+log_data[index:index+40])
                _makerAssetFilledAmount = int(log_data[6*64:6*64+64], 16)
                _takerAssetFilledAmount = int(log_data[7*64:7*64+64], 16)
            elif (ZERO_EX_2 in log_topics):
                _makerAssetData = Web3.toChecksumAddress("0x"+log_data[4*64+24:4*64+64])
                _takerAssetData = Web3.toChecksumAddress("0x"+log_data[5*64+24:5*64+64])
                _takerAssetFilledAmount = int(log_data[6*64:6*64+64], 16)
                _makerAssetFilledAmount = int(log_data[7*64:7*64+64], 16)
            else:
                _makerAssetData = Web3.toChecksumAddress("0x"+log_data[3*64+24:3*64+64])
                _takerAssetData = Web3.toChecksumAddress("0x"+log_data[4*64+24:4*64+64])
                _takerAssetFilledAmount = int(log_data[5*64:5*64+64], 16)
                _makerAssetFilledAmount = int(log_data[6*64:6*64+64], 16)
            
            in_token_name = get_token_name(_takerAssetData,tokens_cache,w3)
            out_token_name = get_token_name(_makerAssetData,tokens_cache,w3)
            event = {
                "action": "SWAP",
                "name": "SWAP_0x",
                "log_index":log_index,
                "in_token": _takerAssetData,
                "out_token": _makerAssetData,
                "in_token_name": in_token_name,
                "out_token_name": out_token_name,
                "in_amount": _takerAssetFilledAmount, 
                "out_amount": _makerAssetFilledAmount,
                "exchange": log_address,
                "exchange_name": "0x",
            }

            actions_list.append(event)
            swaps_list.append(event)
            #print("0x swap!")
            #except:
                #print("unrcognize 0x swap!")
                #pass
        
        if AAVE_FLASH_LOAN in log_topics:
            #try:
            #_reserve  = Web3.toChecksumAddress("0x"+event["topics"][2].hex().replace("0x", "")[24:64])
            _reserve  = Web3.toChecksumAddress("0x"+log_topics[2].replace("0x", "")[24:64])
            _amount   = int(log_data[0:64], 16)
            _totalFee = int(log_data[64:128], 16)

            token_name = get_token_name(_reserv,tokens_cache,w3)
            token_decimals = get_token_decimal(_reserve,tokens_cache,w3)
            
            event = {
                "action": "FLASHLOAN",
                "name": "FLASHLOAN_AAVE",
                "token_name": token_name,
                "token_decimals": token_decimals, 
                "amount": _amount, 
                "fee": _totalFee,
                "exchange": log_address,
                "exchange_name": "aave",
            }
            actions_list.append(event)
            flash_loans_list.append(event)
            
            #flash_loans[event["transactionIndex"]][_reserve] = {"token_name": token_name, "token_decimals": token_decimals, "amount": _amount, "fee": _totalFee, "platform": "Aave"}
            #print("aave flashloan!")
            #except:
            #    print("unrcognize AAVE flashloan!")
            #    pass
        """
        if DYDX_WITHDRAW in log_topics:
            try:
                _market_id = int(log_data[1*64:1*64+64], 16)
                _amount = int(log_data[3*64:3*64+64], 16)
                
                _market = get_dydx_flashloan_detail(log_address,_market_id,cache,w3)
                
                
                token_name = get_token_name(_market,tokens_cache,w3)
                token_decimals = get_token_decimal(_market,tokens_cache,w3)
                
                
                dydx_event = {
                    "action": "FLASHLOAN",
                    "name": "FLASHLOAN_DYDX",
                    "token_name": token_name, 
                    "token_decimals": token_decimals, 
                    "amount": _amount,
                    "fee": None,
                    "exchange": log_address,
                    "exchange_name": "dydx",
                }
                
                if _market in dydx_flashloan_market_dict:
                    # 代表还款交易在其中
                    _fee = dydx_flashloan_market_dict[_market]["amount"] - _amount
                    dydx_event["fee"] = _fee
                    actions_list.append(dydx_event)
                    flash_loans_list.append(dydx_event)
                else:
                    dydx_flashloan_market_dict[_market] = dydx_event

                
                

            except:
                pass

        if DYDX_DEPOSIT in log_topics:
            try:
                _market_id = int(log_data[1*64:1*64+64], 16)
                _amount = int(log_data[3*64:3*64+64], 16)

                
                _market = get_dydx_flashloan_detail(log_address,_market_id,cache,w3)

                token_name = get_token_name(_market,tokens_cache,w3)
                token_decimals = get_token_decimal(_market,tokens_cache,w3)
                
                if _market in dydx_flashloan_market_dict:
                    # 代表借款交易在其中
                    _fee = _amount - dydx_flashloan_market_dict[_market]["amount"]
                    # 添加event
                    dydx_event = dydx_flashloan_market_dict[_market]
                    dydx_event["fee"] = _fee
                    
                    actions_list.append(dydx_event)
                    flash_loans_list.append(dydx_event)
                    
                    
                else:
                    dydx_flashloan_market_dict[_market] = {
                        "action": "FLASHLOAN",
                        "name": "FLASHLOAN_DYDX",
                        "token_name": token_name, 
                        "token_decimals": token_decimals, 
                        "amount": _amount,
                        "fee": None,
                        "exchange": log_address,
                        "exchange_name": "dydx",
                    }

                
            
            except:
                pass
        """
        if (AAVE_V1 in log_topics): 
            #try:
            #received_token_address = Web3.toChecksumAddress("0x"+event["topics"][1].hex().replace("0x", "")[24:64]) # _collateral
            #debt_token_address     = Web3.toChecksumAddress("0x"+event["topics"][2].hex().replace("0x", "")[24:64]) # _reserve
            #liquidated_user        = Web3.toChecksumAddress("0x"+event["topics"][3].hex().replace("0x", "")[24:64]) # _user
            received_token_address = Web3.toChecksumAddress("0x"+log_topics[1].replace("0x", "")[24:64]) # _collateral
            debt_token_address     = Web3.toChecksumAddress("0x"+log_topics[2].replace("0x", "")[24:64]) # _reserve
            liquidated_user        = Web3.toChecksumAddress("0x"+log_topics[3].replace("0x", "")[24:64]) # _user
            debt_token_amount      = int(log_data[0:64], 16) # _purchaseAmount
            received_token_amount  = int(log_data[64:128], 16) # _liquidatedCollateralAmount
            liquidator             = Web3.toChecksumAddress("0x"+log_data[216:256]) # _liquidator
            
            debt_token_name = get_token_name(debt_token_address,tokens_cache,w3)
            debt_token_decimals = get_token_decimal(debt_token_address,tokens_cache,w3)
            received_token_name = get_token_name(received_token_address,tokens_cache,w3)
            received_token_decimals = get_token_decimal(received_token_address,tokens_cache,w3)
            
            event ={
                "action": "LIQUIDATION",
                "name" : "AAVE_V1_LIQUIDATION",
                "liquidator": liquidator,
                "liquidated_user": liquidated_user,
                "debt_token_address": debt_token_address,
                "debt_token_amount": debt_token_amount,
                "debt_token_name": debt_token_name,
                "debt_token_decimals": debt_token_decimals,
                "debt_token_to_eth_price": None,
                "received_token_address": received_token_address,
                "received_token_amount": received_token_amount,
                "received_token_name": received_token_name,
                "received_token_decimals": received_token_decimals,
                "received_token_to_eth_price": None,
                "protocol_address": log_address,
                "protocol_name": "Aave V1"
            }

            actions_list.append(event)
            liquidations_list.append(event)
            #print("aave v1!")
            #except:
            #    print("unrcognize AAVE_V1!")
            #    pass
        if (AAVE_V2 in log_topics): 
            #try:
            #received_token_address = Web3.toChecksumAddress("0x"+event["topics"][1].hex().replace("0x", "")[24:64]) # collateralAsset
            #debt_token_address     = Web3.toChecksumAddress("0x"+event["topics"][2].hex().replace("0x", "")[24:64]) # debtAsset
            #liquidated_user        = Web3.toChecksumAddress("0x"+event["topics"][3].hex().replace("0x", "")[24:64]) # user
            received_token_address = Web3.toChecksumAddress("0x"+log_topics[1].replace("0x", "")[24:64]) # collateralAsset
            debt_token_address     = Web3.toChecksumAddress("0x"+log_topics[2].replace("0x", "")[24:64]) # debtAsset
            liquidated_user        = Web3.toChecksumAddress("0x"+log_topics[3].replace("0x", "")[24:64]) # user
            
            debt_token_amount      = int(log_data[0:64], 16) # debtToCover
            received_token_amount  = int(log_data[64:128], 16) # liquidatedCollateralAmount
            liquidator             = Web3.toChecksumAddress("0x"+log_data[152:192]) # liquidator
            
            debt_token_name = get_token_name(debt_token_address,tokens_cache,w3)
            debt_token_decimals = get_token_decimal(debt_token_address,tokens_cache,w3)
            received_token_name = get_token_name(received_token_address,tokens_cache,w3)
            received_token_decimals = get_token_decimal(received_token_address,tokens_cache,w3)
            
            event ={
                "action": "LIQUIDATION",
                "name" : "AAVE_V2_LIQUIDATION",
                "liquidator": liquidator,
                "liquidated_user": liquidated_user,
                "debt_token_address": debt_token_address,
                "debt_token_amount": debt_token_amount,
                "debt_token_name": debt_token_name,
                "debt_token_decimals": debt_token_decimals,
                "debt_token_to_eth_price": None,
                "received_token_address": received_token_address,
                "received_token_amount": received_token_amount,
                "received_token_name": received_token_name,
                "received_token_decimals": received_token_decimals,
                "received_token_to_eth_price": None,
                "protocol_address": log_address,
                "protocol_name": "Aave V2"
            }

            actions_list.append(event)
            liquidations_list.append(event)
            #print("aave v2 liquidation")
            #except:
            #    print("unrcognize AAVE_V2!")
            #    pass
        """
        if COMPOUND_V2 in log_topics:
            try:
                liquidator             = Web3.toChecksumAddress("0x"+log_data[24:64]) # liquidator
                liquidated_user        = Web3.toChecksumAddress("0x"+log_data[88:128]) # borrower
                debt_token_amount      = int(log_data, 16) # repayAmount
                received_token_address = Web3.toChecksumAddress("0x"+log_data[216:256]) # cTokenCollateral
                received_token_amount  = int(log_data[256:320], 16)
                
                received_token_name = get_token_name(received_token_address,tokens_cache)
                received_token_decimals = get_token_decimal(received_token_address,tokens_cache)

                event ={
                    "action": "LIQUIDATION",
                    "name" : "COMPOUND_V2_LIQUIDATION"
                    "liquidator": liquidator,
                    "liquidated_user": liquidated_user,
                    "debt_token_address": "",
                    "debt_token_amount": debt_token_amount,
                    "debt_token_name": "",
                    "debt_token_decimals": 0,
                    "debt_token_to_eth_price": None,
                    "received_token_address": received_token_address,
                    "received_token_amount": received_token_amount,
                    "received_token_name": received_token_name,
                    "received_token_decimals": received_token_decimals,
                    "received_token_to_eth_price": None,
                    "protocol_address": log_address,
                    "protocol_name": "Compound V2"
                }

                actions_list.append(event)
                liquidations_list.append(event)
            
            except:
                pass
        """

    return actions_list,swaps_list,liquidations_list,flash_loans_list
        
            








from utils import json_parse


def main():
    block  = json_parse("out/test2.json")
    transactions = block[8]
    for transaction in transactions:
        analysis_logs(transaction)



if __name__ == "__main__":
    main()

                
            
    
