import time
import credentials
import json
from kucoin.client import User # Ledger data stored accessed through User endpoint in API and its SDK
from names import base_file_name

client = User(credentials.api_key, credentials.api_secret, credentials.api_passphrase) # Create User class called client

data = []

def error_log(error):
    with open(base_file_name.log, 'a') as e_log:
        e_log.write(error)
    e_log.close()

def get_ledger(start,end,page):
    while True:
        try:
            ledger = client.get_account_ledger(startAt=start,endAt=end,pageSize=500,currentPage=page)
        except Exception as e:
            if "Too Many Requests" in str(e.args):
                print(f"Too many requests, paused at {utc(start)} will retry again in 10 seconds")
                for i in range(1,11,1):
                    print(f"Retrying in {i}", end='\r')
                    time.sleep(1)
                print("...RETRYING...")
            else:
                print()
                print(f"FAILED TO FETCH PRICE AT {utc(start)}")
                print(e)
                error_log(str(start))
                error_log(e)
                return 20000
        else:
            data.append(ledger)
            return ledger['totalPage']

def utc(ca):
    createdat = int(ca / 1000)
    local_time = time.strftime('%d/%m/%Y', time.localtime(createdat))
    return local_time

# 1583020800000 1659139200000
# FY 21 22 1625097600000 1656633600000
def run_ledger(startat,endat):
    for day_start_time in range(startat, endat + 86399999, 86399999):
        day_end = day_start_time + 86399998
        print(utc(day_start_time), '\r') # prints date in UTC instead of UNIX
        page = 1
        total_pages = 2
        while page <= total_pages:
            total_pages = get_ledger(day_start_time,day_end,page)
            print(f"Page {page} of {total_pages}", end='\r')
            page += 1
            time.sleep(0.2) # wait for 0.2 seconds

    with open(base_file_name.ledger, "w") as outfile:
        json.dump(data, outfile)
    

"""
    startat = 1583020800000
    dynamicend = startat + 86399999
    endat = 1659139200000
    main(1583020800000,1659139200000)

    if __name__ == "__main__":
    run_ledger(1622910800000,1625029200000)
"""
