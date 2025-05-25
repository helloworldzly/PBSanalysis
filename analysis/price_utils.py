
import json
import datetime

def time_convert(timestamp):
    

    #timestamp = 1618228800  # 时间戳，表示2021年4月12日 00:00:00

    # 将时间戳转换为UTC datetime对象
    dt_object = datetime.datetime.utcfromtimestamp(timestamp)

    # 格式化日期和时间
    formatted_date = dt_object.strftime('%Y-%m-%d')

    #print(formatted_date)
    return formatted_date
def get_prices_dict():

    btc_daily_price = {}
    eth_daily_price = {}
    all_daily_price = {}
    
    
    with open('price/btc_prices.json') as f:
        temp = json.load(f)#['prices']
        for timestamp, price in temp:
            btc_daily_price[time_convert(timestamp/1000)] = price
        
    with open('price/eth_prices.json') as f:
        temp = json.load(f)#['prices']
        for timestamp, price in temp:
            eth_daily_price[time_convert(timestamp/1000)] = price

    with open('price/coin_prices3.json') as f:
        all_daily_price = {}
        temp = json.load(f)

        for token_address, record in temp.items():
            for timestamp, price in record:
                date = time_convert(timestamp/1000)
                if date not in all_daily_price:
                    all_daily_price[date] = {}
                    
                all_daily_price[date][token_address] = price

    return eth_daily_price,btc_daily_price,all_daily_price



# 千万记得用这个
def get_daily_prices(date):
    eth_daily_price,btc_daily_price,all_daily_price = get_prices_dict()
    try:
        eth_price = eth_daily_price[date]
        btc_price = btc_daily_price[date]
        all_price = all_daily_price[date]
        all_price["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"] = eth_price
        prices = {"eth": eth_price, "btc": btc_price, "all":all_price}
        return prices
    except:
        raise ValueError("Invalid Date")
    
    

      
        




def main():
    prices = get_daily_prices("2023-09-15")
    print(prices)
    print(prices["eth"])
    print(prices["btc"])
    #time_convert(0)
if __name__ == "__main__":
    main()    