from kucoin.client import Market
import time
import credentials
from orderclass import Order

from kucoin.client import User # Ledger data stored accessed through User endpoint in API and its SDK
client = User(credentials.api_key, credentials.api_secret, credentials.api_passphrase) # Create User class called client

def getledger(start,end,page):
    try:
        ledger = client.get_account_ledger(startAt=start,endAt=end,pageSize=500,currentPage=page)
    except:
        return -1
    else:
        #print(ledger)
        return ledger['totalPage']



startat = 1603745599999
dynamicend = startat + 86399999
endat = 1610075199810


while dynamicend <= endat: # doesnt use a for loop because i want it to be able to repeat in case of error
    pagenumber = 1

    ledger = getledger(startat,dynamicend,pagenumber)
    print(ledger)
    
    if ledger >= 0:
        if ledger > 1:
            while pagenumber <= ledger:
                ledger = getledger(startat,dynamicend,pagenumber)
                if ledger >= 0:
                    pagenumber += 1
                    time.sleep(0.2) # wait for 0.2 seconds
                else:
                    time.sleep(1) # wait for 1 second
        
        startat = dynamicend
        dynamicend = startat + 86399999
        time.sleep(0.2) # wait for 0.2 seconds
    else:
        time.sleep(1) # wait for 1 second
    

