from shared import db, ma, cute
from kucoin.client import User # Ledger data stored accessed through User endpoint in API and its SDK
import time
import credentials
from ledger_entry import LedgerEntry
from relations import (
                        ledger_entry, commit_entries
                        )
from schemas import (
                        Ledger, LedgerSchema, FuturesTHist, FuturesTHistSchema
                    )

class FetchLedger:
    def __init__(self):
        self.file_name = "test_001"
        self.client = User(credentials.api_key, credentials.api_secret, credentials.api_passphrase) # Create User class called client
        self.data = []
        self.futures_client = User(credentials.futures_api_key, credentials.futures_secret, credentials.api_passphrase)


    def utc(self, ca):
        createdat = int(ca / 1000)
        local_time = time.strftime('%d/%m/%Y', time.localtime(createdat))
        return local_time


    def error_log(self, error):
        with open(self.file_name.log, 'w') as e_log:
            e_log.write(error)
        e_log.close()


    def get_ledger(self, start,end,page):
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
                        if i['currency'] != 'KCANDY':
                            parse_entry = LedgerEntry(i)
                            id, order_id, date, acc_type, bizType, symbol, asset, direction, size, fee = parse_entry.data.values()
                            ledger_entry(id, order_id, date, acc_type, bizType, symbol, asset, direction, size, fee)

                db.session.commit()
                return ledger['totalPage']


       
    def get_ledger_test(self, start,end,page):
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
                        f = open("demofile2.txt", "a")
                        f.write(f'{i}\n')
                        f.close()
                        #parse_entry = LedgerEntry(i)
                        #id, order_id, date, acc_type, bizType, symbol, asset, direction, size, fee = parse_entry.data.values()
                        #ledger_entry(id, order_id, date, acc_type, bizType, symbol, asset, direction, size, fee)

                #db.session.commit()
                return ledger['totalPage']

    # 1625141419556 1625441419556
    # 1583020800000 1659139200000
    # FY 21 22 1625097600000 1656633600000
    def run_ledger(self, startat,endat):
        for day_start_time in range(startat, endat + 86399999, 86399999):
            day_end = day_start_time + 86399999
            print(f'{self.utc(day_start_time)}  {day_start_time}', '\r') # prints date in UTC instead of UNIX
            page = 1
            total_pages = 2
            while page <= total_pages:
                total_pages = self.get_ledger(day_start_time,day_end,page)
                print(f"Page {page} of {total_pages}")
                # print(f"Page {page} of {total_pages}", end='\r')
                page += 1
                time.sleep(0.2) # wait for 0.2 seconds

            # with open(self.file_name.ledger, "w") as outfile:
            #     json.dump(self.data, outfile)


    def save_to_db(self, page):
        for i in page:
            (id, order_id, date, acc_type, symbol, direction, asset, size) = i
            ledger_entry(id, order_id, date, acc_type, symbol, direction, asset, size)

        commit_entries()
    
    
    def get_futures_ledger(self,start,end,page):
        while True:
            try:
                ledger = self.futures_client.get_transaction_history(startAt=start, endAt=end,currentPage=page)
            except Exception as e:
                if "Too Many Requests" in str(e.args):
                    print(f"Too many requests")
                    for i in range(1,11,1):
                        print(f"Retrying in {i}", end='\r')
                        time.sleep(1)
                    print("...RETRYING...")
                else:
                    print()
                    print(f"FAILED TO FETCH PRICE")
                    print(e)
                    return 20000
            else:
                for i in ledger['dataList']:
                    e = FuturesTHist(
                    time = str(i['time']),
                    type = i['type'],
                    amount = i['amount'],
                    fee = i['fee'],
                    accountEquity = i['accountEquity'],
                    status = i['status'],
                    remark = i['remark'],
                    offset = i['offset'],
                    currency = i['currency'],
                    )
                    db.session.add(e)

                db.session.commit()
                return ledger['hasMore']
    
    
    def run_futures_ledger(self,startat,endat):
        for day_start_time in range(startat, endat + 8639999, 86399999):
            day_end = day_start_time + 86399999
            page = 1
            has_more = True
            while has_more == True:
                has_more = self.get_futures_ledger(day_start_time,day_end,page)
                print(f"Page {page}", end='\r')
                page += 1
                time.sleep(0.2) # wait for 0.2 seconds
        