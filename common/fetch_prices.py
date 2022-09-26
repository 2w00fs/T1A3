import time
import json
import credentials
from kucoin.client import Market

class Prices:
    def __init__(self, file_name):
        self.file_name = file_name
        self.prices = self.check_json_not_empty()
        self.client = Market(credentials.api_key,credentials.api_secret,credentials.api_passphrase,is_sandbox=False,url='https://api.kucoin.com')

    def error_log(self, error):
        with open(self.file_name.log, 'a') as e_log:
            e_log.write(error)
        e_log.close()

    def check_json_not_empty(self):
        try:
            jfile = open(self.file_name.prices, 'r')
        except:
            jfile = open(self.file_name.prices, 'w')
            jfile.close()
            return {}
        else:
            read_start = jfile.read(1)
            if not read_start:
                print("empty")
                jfile.close()
                return {}

            jfile.close()
            with open(self.file_name.prices, 'r') as file:
                contents = json.load(file)
            file.close()
            return contents

    """
    The ticker data date goes up in increments of 60
    A date we supply to it from our order will likely fall somewhere between each 60 second increment
    The following code changes the inputed value to be a multiple of 60, allowing us to search existing data before
    making a call to the api (which has a very strict rate limit for ticker data, slowing the program dramatically)
    """
    def sixty(self,n):
        modulo = n % 60
        if modulo == 0:
            return n

        remainder = modulo / 60
        amount_to_add = round((1 - remainder) * 60) #used round because int effectively rounds down
        final = amount_to_add + n
        return final

    def store_prices(self):
        with open(self.file_name.prices, "w") as outfile:
            json.dump(self.prices, outfile)

    def parse_prices(self, api_data, start, name):
        ohlc_to_return = 0
        for i in api_data:
            ohlc = round((float(i[1]) + float(i[2]) + float(i[3]) + float(i[4])) / 4,4)
            date = int(i[0])
            self.prices[name][str(date)] = ohlc # adds fetched values to stored data
            if date == start:
                ohlc_to_return = ohlc

        if ohlc_to_return != 0:
            return ohlc_to_return

        print(f"Prices for {name} were returned however a price for {date} was not found")
        self.error_log(f"{name} {date} no price found, substituted with 1.001001001\n\n")
        return 1.001001001

    def get_data(self, symbol, start, end, name):
        while True:
            try:
                api_data = self.client.get_kline(symbol=symbol,kline_type="1min",startAt=start,endAt=end)
            except Exception as e:
                if "Too Many Requests" in str(e.args):
                    print(f"Too many requests, data for {name} {start} will retry again in 20 seconds")
                    for i in range(1,21,1):
                        print(f"retrying after 20 seconds...{i}", end='\r')
                        time.sleep(1)
                    print("RETRYING...")
                else:
                    print()
                    print(f"FAILED TO FETCH PRICE...{name}...{start}")
                    self.error_log(f"FAILED TO FETCH PRICE FOR {name}...{start}, substituded with 1.010101\n")
                    self.error_log(f"{e}\n\n")
                    print(e)
                    return 1.010101
            else:
                time.sleep(2)
                return self.parse_prices(api_data, start, name)

    def find_price(self, name, date):
        symbol = f"{name}-USDT"
        end_at = date + (60 * 60 * 24)
        if name in self.prices.keys():
            if str(date) in self.prices[name]:
                return self.prices[name][str(date)]

            print(f"finding {name} price for date: {date}")
            return self.get_data(symbol,date,end_at,name)

        self.prices[name] = {}
        print(f"finding {name} price for date: {date}")
        return self.get_data(symbol,date,end_at,name)

    def run_me(self, name, date):
        ignored_assets = ("USDT", "USD", "PAX","UST","AUD")
        if name not in ignored_assets:
            date = self.sixty(int(date / 1000))
            price = self.find_price(name,date)
            print(f"Price for: {name} :: {price}")
            return price

        return 1
