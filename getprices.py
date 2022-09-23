import time
import json
import credentials
from kucoin.client import Market

json_file_name = "sample_test"

def check_json_notempty(fname):
    try:
        jfile = open(f"{fname}.json", 'r')
    except:
        jfile = open(f"{fname}.json", 'w')
        jfile.close()
        return {}
    else:
        read_start = jfile.read(1)
        if not read_start:
            print("empty")
            jfile.close()
            return {}
        else:
            jfile.close()
            file = open('sample.json', 'r')
            contents = json.load(file)
            file.close()
            return contents

prices = check_json_notempty(json_file_name)

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
    else:
        remainder = modulo / 60
        amount_to_add = round((1 - remainder) * 60) #used round because int effectively rounds down
        final = amount_to_add + n
        return final

def store_prices():
    with open(f"{json_file_name}.json", "w") as outfile:
        json.dump(prices, outfile)

def parse_prices(api_data, start, name):
    for i in api_data:
        try:
            ohlc = round((float(i[1]) + float(i[2]) + float(i[3]) + float(i[4])) / 4,4)
        except:
            print(F"PARSE_PRICES FAILED: {i}")
        else:
            date = int(i[0])
            prices[name][str(date)] = ohlc # adds fetched values to stored data
            if date == start:
                return_price = ohlc
    return return_price

def get_data(symbol,start,end,name):
    try:
        api_data = client.get_kline(symbol=symbol,kline_type="1min",startAt=start,endAt=end)
    except:
        for i in range(1,15,1):
            print(f"retrying in...{i}")
            time.sleep(1)
        data = client.get_kline(symbol=symbol,kline_type="1min",startAt=start,endAt=end)
        return parse_prices(data, start, name)
    else:
        time.sleep(1)
        return parse_prices(api_data, start, name)

def find_price(name,date):
    symbol = name + "-USDT"
    if name in prices.keys():
        if str(date) in prices[name]:
            return prices[name][str(date)]
        else:
            print(f"finding {name} price for date: {date}")
            end_at = date + (60 * 60 * 24)
            return get_data(symbol,date,end_at,name)
    else:
        prices[name] = {}
        print(f"finding {name} price for date: {date}")
        end_at = date + (60 * 60 * 24)
        return get_data(symbol,date,end_at,name)

def feed_me(name,date):
    if name != 'USDT':
        date = sixty(int(date / 1000))
        price = find_price(name,date)
        print(f"feed me: {name} :: {price}")
        return price
    else:
        return 1
        #data = get_data(symbol,start_at,end_at)

# 1607520235369 1607520240