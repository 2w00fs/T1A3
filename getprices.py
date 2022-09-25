import time
import json
import credentials
from kucoin.client import Market
from names import base_file_name

def error_log(error):
    with open(base_file_name.log, 'a') as e_log:
        e_log.write(error)
    e_log.close()


def check_json_not_empty(f_name):
    try:
        jfile = open(f_name, 'r')
    except:
        jfile = open(f_name, 'w')
        jfile.close()
        return {}
    else:
        read_start = jfile.read(1)
        if not read_start:
            print("empty")
            jfile.close()
            return {}
        
        jfile.close()
        with open(f_name, 'r') as file:
            contents = json.load(file)
        file.close()
        return contents

prices = check_json_not_empty(base_file_name.prices)

client = Market(
    credentials.api_key,
    credentials.api_secret,
    credentials.api_passphrase,
    is_sandbox=False,
    url='https://api.kucoin.com'
    )

"""
The ticker data date goes up in increments of 60
A date we supply to it from our order will likely fall somewhere between each 60 second increment
The following code changes the inputed value to be a multiple of 60, allowing us to search existing data before
making a call to the api (which has a very strict rate limit for ticker data, slowing the program dramatically)
"""
def sixty(n):
    modulo = n % 60
    if modulo == 0:
        return n
    
    remainder = modulo / 60
    amount_to_add = round((1 - remainder) * 60) #used round because int effectively rounds down
    final = amount_to_add + n
    return final

def store_prices(f_name):
    with open(f_name.prices, "w") as outfile:
        json.dump(prices, outfile)

def parse_prices(api_data, start, name):
    ohlc_to_return = 0
    for i in api_data:
        ohlc = round((float(i[1]) + float(i[2]) + float(i[3]) + float(i[4])) / 4,4)
        date = int(i[0])
        prices[name][str(date)] = ohlc # adds fetched values to stored data
        if date == start:
            ohlc_to_return = ohlc
    
    if ohlc_to_return != 0:
        return ohlc_to_return

    print(f"Prices for {name} were returned however a price for {date} was not found")
    error_log.write(f"{name} {date} no price found, substituted with 1.001001001\n\n")
    return 1.001001001

def get_data(symbol,start,end,name):
    while True:
        try:
            api_data = client.get_kline(symbol=symbol,kline_type="1min",startAt=start,endAt=end)
        except Exception as e:
            if "Too Many Requests" in str(e.args):
                print(f"Too many requests, data for {name} {start} will retry again in 20 seconds")
                for i in range(1,21,1):
                    print(f"retrying in...{i}", end='\r')
                    time.sleep(1)
                print("RETRYING...")
            else:
                print()
                print(f"FAILED TO FETCH PRICE...{name}...{start}")
                error_log(f"FAILED TO FETCH PRICE FOR {name}...{start}, substituded with 1.010101\n")
                error_log(f"{e}\n\n")
                print(e)
                return 1.010101
        else:
            time.sleep(1)
            return parse_prices(api_data, start, name)

def find_price(name,date):
    symbol = f"{name}-USDT"
    if name in prices.keys():
        if str(date) in prices[name]:
            return prices[name][str(date)]

        print(f"finding {name} price for date: {date}")
        end_at = date + (60 * 60 * 24)
        return get_data(symbol,date,end_at,name)
    
    prices[name] = {}
    print(f"finding {name} price for date: {date}")
    end_at = date + (60 * 60 * 24)
    return get_data(symbol,date,end_at,name)

def run_me(name,date):
    ignored_assets = ("USDT", "USD", "PAX","UST","AUD")
    if name not in ignored_assets:
        date = sixty(int(date / 1000))
        price = find_price(name,date)
        print(f"Price for: {name} :: {price}")
        return price
    
    return 1
