import time
import json
import credentials
from kucoin.client import Market
from shared import db, cute
from schemas import Prices, PricesSchema, Ledger, LedgerSchema, LedgerSecondSum, LedgerSecondSumSchema, LedgerPrices, LedgerPricesSchema
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
        #symbol = f"{name}-USDT"
        symbol = "LUNA-USDT"
        # check if price data already in database
        # if no data found proceed to fetch it
        search = cute(db.select(Prices).filter(db.and_(Prices.date == date, Prices.asset == name))).scalars().first()
        if search == None:
            api_data = self.get_data(symbol,date,name)
            ohlc = self.parse_prices(api_data, date, name)
            return ohlc        
        else:
            return search.price


    def run_me(self, name, date):
        ignored_assets = ("USDT", "USD", "PAX","UST","AUD", "ZIL", "CS", "WAX","GAS")
        #if name == "LUNA":
        #    name == "LUNC"

        if name not in ignored_assets:
            sixty_date = self.sixty(int(int(date) / 1000))
            price = self.find_price(name,sixty_date)
            #print(f"Price for: {name} :: {price} :: {sixty_date}")
            return price


def prices_test1():
    asset_date = cute(db.select(LedgerSecondSum.asset, LedgerSecondSum.date).filter(LedgerSecondSum.asset == "LUNA").group_by(LedgerSecondSum.asset, LedgerSecondSum.date)).all()
    base_asset_date = cute(db.select(LedgerSecondSum.base_asset, LedgerSecondSum.date).filter(LedgerSecondSum.base_asset == "LUNA").group_by(LedgerSecondSum.base_asset, LedgerSecondSum.date)).all()
    #base_asset_date = cute(db.select(LedgerSecondSum.base_asset, LedgerSecondSum.date).filter(LedgerSecondSum.base_asset.notlike('USDT'), LedgerSecondSum.biz_type == 'Deposit').group_by(LedgerSecondSum.base_asset, LedgerSecondSum.date)).all()
    
    fetch_prices = FetchPrices()
    for i in base_asset_date:
        sixty_date = fetch_prices.sixty(int(int(i.date) / 1000))
        #print(f"{i.asset} {sixty_date}")
        fetch_prices.run_me(i.base_asset, i.date)
    
    for v in asset_date:
        sixty_date = fetch_prices.sixty(int(int(i.date) / 1000))
        #print(f"{i.asset} {sixty_date}")
        fetch_prices.run_me(v.asset, v.date)


def prices_test():
   
    orders = cute(db.select(LedgerPrices)).scalars().all()
    
    
    def usd(o):
        val = 0
        for i in o:
            if i.base_asset == "USD":
                val += i.asset_size * i.base_price
        
        return val


    def ords(o):
        val = 0
        for i in o:
            if i.symbol == f"{i.asset}-{i.asset}":
                if i.biz_type == 'Debt Repayment' or i.biz_type == 'Borrowings':
                    val += i.asset_size * i.base_price
            #else:
            #    val += i.base_asset_size * i.base_price

        return val
    
    
    #print(usd(orders))
    print(ords(orders))


def utc(ca):
        createdat = int(int(ca) / 1000)
        local_time = time.strftime('%d/%m/%Y', time.localtime(createdat))
        return local_time
    

def month(ca):
        createdat = int(int(ca) / 1000)
        local_time = time.strftime('%m', time.localtime(createdat))
        return int(local_time)


def year(ca):
        createdat = int(int(ca) / 1000)
        local_time = time.strftime('%Y', time.localtime(createdat))
        return int(local_time)
    

def ledger_prices():
    fetch_prices = FetchPrices()
    orders = cute(db.select(LedgerSecondSum)).scalars().all()
    for i in orders:
        price_date = fetch_prices.sixty(int(int(i.date) / 1000))
        if i.base_asset == 'USDT':
            price = 1
        elif i.base_asset == 'USD':
            price = cute(db.select(Prices.price)
                           .filter(db.and_(Prices.asset == i.asset, Prices.date == price_date))).scalars().first()
        else:
            price = cute(db.select(Prices.price)
                           .filter(db.and_(Prices.asset == i.base_asset, Prices.date == price_date))).scalars().first()
        
        if price == 'None':
            price = 0

        ass_size = round(i.asset_size,4)
        bass_size = round(i.base_asset_size, 4)
        utc_ = utc(i.date)
        month_ = month(i.date)
        
        if month_ >= 7:
            fy= int(year(i.date))
        elif month_ < 7:
            fy = int(year(i.date)) - 1


        insert_stmt = insert(LedgerPrices).values(
                                                    order_id = i.order_id,
                                                    date = i.date,
                                                    date_utc = utc_,
                                                    acc_type = i.acc_type,
                                                    biz_type = i.biz_type,
                                                    symbol = i.symbol,
                                                    asset = i.asset,
                                                    base_asset = i.base_asset,
                                                    direction = i.direction,
                                                    asset_size = ass_size,
                                                    base_asset_size = bass_size,
                                                    fee = i.fee,
                                                    fee_asset = i.fee_asset,
                                                    fee_kcs = i.fee_kcs,
                                                    base_price = price,
                                                    fy = fy
                                                )

        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['order_id'])
        cute(do_nothing_stmt)
        
    db.session.commit()

