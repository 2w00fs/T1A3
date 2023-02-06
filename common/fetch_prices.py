import time
import json
import credentials
from kucoin.client import Market
from shared import db, cute
from schemas import Prices, Ledger, LedgerSchema, LedgerPrices
from sqlalchemy.dialects.postgresql import insert

class FetchPrices:
    def __init__(self):
        self.client = Market(credentials.api_key,credentials.api_secret,credentials.api_passphrase,is_sandbox=False,url='https://api.kucoin.com')

    def error_log(self, error):
        with open('fetch-prices.log', 'a') as e_log:
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


    def parse_prices(self, api_data, start, name):
        ohlc_to_return = 0
        try:
            for i in api_data:
                ohlc = round((float(i[1]) + float(i[2]) + float(i[3]) + float(i[4])) / 4,4)
                date = int(i[0])
                # OLD self.prices[name][str(date)] = ohlc # adds fetched values to stored data
                insert_stmt = insert(Prices).values(
                                                        date=date,
                                                        asset=name,
                                                        price=ohlc
                                                    )

                do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['date', 'asset'])
                cute(do_nothing_stmt)

                if date == start:
                    ohlc_to_return = ohlc

            db.session.commit()

            if ohlc_to_return != 0:
                return ohlc_to_return

            print(f"Prices for {name} were returned however a price for {date} was not found")
            self.error_log(f"{name} {date} no price found, substituted with 1.001001001\n\n")

            return 1.001001001

        except ValueError:
            print("NO DATA RETURNED")


    def get_data(self, symbol, start, name):
        date = start - 82800# start the search an hour before
        print(start)
        end = date + 86400 # seconds in a day (60 * 60 * 24)for date: {date}")
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
                return api_data


    def find_price(self, name, date):
        ignored_assets = ("USDT", "USD", "PAX","UST","AUD", "ZIL", "CS", "WAX","GAS", "PMGT")
        if name not in ignored_assets:
            symbol = f"{name}-USDT"
            # check if price data already in database
            # if no data found proceed to fetch it
            search = cute(db.select(Prices).filter(db.and_(Prices.date == date, Prices.asset == name))).scalars().first()
            if search == None:
                api_data = self.get_data(symbol,date,name)
                ohlc = self.parse_prices(api_data, date, name)
                return ohlc        
            else:
                return search.price
        
        return 0


    def run_me(self, name, date):
        sixty_date = self.sixty(int(int(date) / 1000))
        price = self.find_price(name,sixty_date)
        #print(f"Price for: {name} :: {price} :: {sixty_date}")
        return price


def prices_test1():
    asset_date = cute(db.select(Ledger.asset, Ledger.date).filter(Ledger.asset == "LUNA").group_by(Ledger.asset, Ledger.date)).all()
    
    fetch_prices = FetchPrices()
   
    for v in asset_date:
        sixty_date = fetch_prices.sixty(v.date)
        #print(f"{i.asset} {sixty_date}")
        fetch_prices.run_me(v.asset, v.date)


def prices_test():
   pass


def unix_length(ca):
    if isinstance(ca, str):
        int_ca = int(ca)
    else:
        int_ca = ca
    
    if int_ca > 9999999999:
        int_ca = int(int_ca / 1000)
    
    return int_ca
        
def parse_date(ca):
    extra_dates = {
        "utc": "DD/MM/YY",
        "fy": 0
    }
    
    int_ca = unix_length(ca)
    
    extra_dates['utc'] = time.strftime('%d/%m/%Y', time.localtime(int_ca))
    month = time.strftime('%m', time.localtime(int_ca))
    year = time.strftime('%Y', time.localtime(int_ca))
    
    if int(month) >= 7:
        extra_dates['fy'] = int(year)
    elif int(month) < 7:
        extra_dates['fy'] = int(year) - 1
        
    return extra_dates
    

def ledger_prices():
    fetch_prices = FetchPrices()
    orders = cute(db.select(Ledger)).scalars().all()
    for i in orders:
        price = 0
        price_date = fetch_prices.sixty(unix_length(i.date))
        
        if f'{i.asset}-' in i.symbol and f'{i.asset}-{i.asset}' not in i.symbol:
            asset_type = 'main'
        else:
            asset_type = 'base'


        if asset_type == 'base' and i.asset == 'USDT':
            price = 1
        elif asset_type == 'base' and i.asset != 'USDT':
            price = fetch_prices.find_price(i.asset, price_date)
        elif asset_type == 'main' and '-USD' in i.symbol and '-USDT' not in i.symbol:
            price = fetch_prices.find_price(i.asset, price_date)
        
        if i.direction == 'in':
            fee = i.fee
        elif i.direction == 'out':
            fee = 0 - i.fee

        ass_size = round(i.size, 4)
        dates = parse_date(i.date)
        
        try:
            insert_stmt = insert(LedgerPrices).values(
                                                    id = i.id,
                                                    order_id = i.order_id,
                                                    date = i.date,
                                                    date_utc = dates['utc'],
                                                    acc_type = i.acc_type,
                                                    biz_type = i.biz_type,
                                                    symbol = i.symbol,
                                                    asset = i.asset,
                                                    asset_type = asset_type,
                                                    direction = i.direction,
                                                    size = ass_size,
                                                    fee = fee,
                                                    price_usdt = price,
                                                    value_usdt = price * ass_size,
                                                    fee_usdt = price * fee,
                                                    fy = dates['fy']
                                                )
        except:
            print(f'id = {i.id}')
            print(f'price = {price}')
            print(f'size = {ass_size}')
            print(f'fee = {fee}')
        else:
            do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
            cute(do_nothing_stmt)
        
    db.session.commit()

# price = cute(db.select(Prices.price)
#                           .filter(db.and_(Prices.asset == i.asset, Prices.date == price_date))).scalars().first()