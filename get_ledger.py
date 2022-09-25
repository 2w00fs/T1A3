import time
import credentials
import json
from kucoin.client import User # Ledger data stored accessed through User endpoint in API and its SDK

class Ledger:
    def __init__(self, file_name):
        self.file_name = file_name
        self.client = User(credentials.api_key, credentials.api_secret, credentials.api_passphrase) # Create User class called client
        self.data = []

    def check_json_not_empty(self):
        try:
            jfile = open(self.file_name.ledger, 'r')
        except:
            return None
        else:
            read_start = jfile.read(1)
            if not read_start:
                print("File is empty")
                jfile.close()
                return None
        
            jfile.close()
            with open(self.file_name.ledger, 'r') as file:
                contents = json.load(file)
            file.close()
            return contents

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
                self.data.append(ledger)
                return ledger['totalPage']



    # 1583020800000 1659139200000
    # FY 21 22 1625097600000 1656633600000
    def run_ledger(self, startat,endat):
        supplied_ledger = self.check_json_not_empty()
        if not supplied_ledger:
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

            with open(self.file_name.ledger, "w") as outfile:
                json.dump(self.data, outfile)

        return supplied_ledger

    """
        startat = 1583020800000
        dynamicend = startat + 86399999
        endat = 1659139200000
        main(1583020800000,1659139200000)

        if __name__ == "__main__":
        run_ledger(1622910800000,1625029200000)
    """
