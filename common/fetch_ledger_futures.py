import time
import credentials
import json
from shared import db, ma, cute
from kucoin.client import User # Ledger data stored accessed through User endpoint in API and its SDK
from relations import ledger_entry, commit_entries, order_sum, unique_orders, count, get_order
from ledger_entry import LedgerEntry
from schemas import Ledger, LedgerSchema

from flask import Flask

from settings import (
    db_name,
    db_address,
    db_user,
    db_pass,
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_address}:5432/{db_name}'


db.init_app(app)
ma.init_app(app)


class FetchLedger:
    def __init__(self):
        self.file_name = "test_001"
        self.client = User(credentials.api_key, credentials.api_secret, credentials.api_passphrase) # Create User class called client
        self.data = []


    def utc(self, ca):
        createdat = int(ca / 1000)
        local_time = time.strftime('%d/%m/%Y', time.localtime(createdat))
        return local_time


    def error_log(self, error):
        with open(self.file_name.log, 'w') as e_log:
            e_log.write(error)
        e_log.close()


    def get_ledger(self, start,end,page):
        tracking_items = ("Cross Margin", "KCS Pay Fees", "Rewards", "Refunded Fees", "Transfer", "Exchange", "Deposit", "Withdrawal", "Isolated Margin")
        while True:
            try:
                ledger = self.client.get_account_ledger(startAt=start,endAt=end,pageSize=500,currentPage=page)
            except Exception as e:
                if "Too Many Requests" in str(e.args):
                    print(f"Too many requests, paused at {self.utc(start)} will retry again in 10 seconds")
                    for i in range(1,11,1):
                        print(f"Retrying in {i}", end='\r')
                        time.sleep(1)
                    print("...RETRYING...")
                else:
                    print()
                    print(f"FAILED TO FETCH PRICE AT {self.utc(start)}")
                    print(e)
                    self.error_log(str(start))
                    self.error_log(e)
                    return 20000
            else:
                 
                for i in ledger['items']:
                    if len(i) > 0:
                        if i['bizType'] in tracking_items:
                            parse_entry = LedgerEntry(i)
                            id, order_id, date, acc_type, bizType, symbol, asset, direction, size, fee = parse_entry.data.values()
                            ledger_entry(id, order_id, date, acc_type, bizType, symbol, asset, direction, size, fee)

                db.session.commit()
                return ledger['totalPage']


    # 1583020800000 1659139200000
    # FY 21 22 1625097600000 1656633600000
    def run_ledger(self, startat,endat):
        for day_start_time in range(startat, endat + 86399999, 86399999):
            day_end = day_start_time + 86399998
            print(self.utc(day_start_time), '\r') # prints date in UTC instead of UNIX
            page = 1
            total_pages = 2
            while page <= total_pages:
                total_pages = self.get_ledger(day_start_time,day_end,page)
                print(f"Page {page} of {total_pages}", end='\r')
                page += 1
                time.sleep(0.2) # wait for 0.2 seconds

            # with open(self.file_name.ledger, "w") as outfile:
            #     json.dump(self.data, outfile)


    def save_to_db(self, page):
        for i in page:
            (id, order_id, date, acc_type, symbol, direction, asset, size) = i
            ledger_entry(id, order_id, date, acc_type, symbol, direction, asset, size)

        commit_entries()

app1 = FetchLedger()

@app.route("/")
def welcome():
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route('/create_all/')
def create_db_all():
    db.create_all()
    # db.session.add_all(jb_seed)
    db.session.commit()
    print("All Done")
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route("/run")
def run():
    # 1651291183638 app1.run_ledger(1625097600000,1659139200000)
    app1.run_ledger(1651291183638,1659139200000)
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"
    

@app.route('/sum/')
def sum():
    #order_sum()
    orders = unique_orders()
    for i in orders.scalars():
        ls = order_sum(i)
        db.session.add(ls)
    
    db.session.commit()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/count/')
def count_():
    print(count('60e01eb438ec0100066673c4'))
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/get_order/')
def getorder():
    order_sum('60e01eb438ec0100066673c4')
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


if __name__ == "__main__":
    app.run(port="8111")
    

"""
        startat = 1583020800000
        dynamicend = startat + 86399999
        endat = 1659139200000
        main(1583020800000,1659139200000)

        if __name__ == "__main__":
        run_ledger(1622910800000,1625029200000)
        

######### TO DO

Save ledger data using returned values
Account for different data structure according to transaction type

    - Context
        -- Order ID
    
    - Account Type
        -- Symbol
"""


