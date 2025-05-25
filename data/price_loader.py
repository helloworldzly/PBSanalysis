import os
import time
import json
import requests

import web3
from web3 import Web3

def get_coin_list():
    print("Getting list of coins from CoinGecko.com...")
    response = requests.get("https://api.coingecko.com/api/v3/coins/list?include_platform=true").json()
    coin_list = dict()
    for coin in response:
        if "ethereum" in coin["platforms"] and coin["platforms"]["ethereum"]:
            coin_list[Web3.to_checksum_address(coin["platforms"]["ethereum"].lower())] = coin["id"]
    return coin_list

coin_list = get_coin_list()

from_timestamp = str(1640995200) # 2022年1月1日SaturdayAM12点00分
to_timestamp = str(1698796800) # 2023年11月1日WednesdayAM12点00分

with open("coin_prices.json", "r") as f:
    latest_prices = json.load(f)

api_key ="..."

prices = latest_prices
index = 0
for address in coin_list.keys():
    index += 1
    if address not in latest_prices:
        market_id = coin_list[address]
        #print(address, market_id)
        try:
            reponse = requests.get("https://api.coingecko.com/api/v3/coins/"+market_id+"/market_chart/range?vs_currency=eth&from="+from_timestamp+"&to="+to_timestamp+"&x_cg_demo_api_key="+api_key)
            prices[address] = reponse.json()["prices"]
            time.sleep(2)
            
        except Exception as e:
            print(reponse.text)
    if index % 100 == 0:
        with open("coin_prices2.json", "w") as f:
            json.dump(prices,f)
        print(index)