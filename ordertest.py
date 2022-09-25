import time
import json
import getprices
import exchangerates
import assettest
from orderclass import Order

#order_data_file_name = "ledger_as_json"
#order_data_file_name = "FULL_LEDGER"
order_data_file_name = "mytestdata"

csv_name = input("Filename for CSV Output pls: ")
def check_json_notempty(fname):
    try:
        jfile = open(f"{fname}.json", 'r')
    except:
        print("FILE DOES NOT EXIST")
    else:
        read_start = jfile.read(1)
        if not read_start:
            print("NO DATA IN FILE")
            jfile.close()
        else:
            jfile.close()
            file = open(f"{fname}.json", 'r')
            contents = json.load(file)
            file.close()
            return contents

raw_data = check_json_notempty(order_data_file_name)

orders = {}
"""
    the 36000000 is to add 10 hours to match AEST
    may remove later because localtime should work off the OS time, Docker has it set wrong methinks
    created_at format is in milliseconds since unix epoch
"""
def utc(ca):
    createdat = int((ca + 36000000) / 1000) # turning from milliseconds to seconds
    local_time = time.strftime('%d/%m/%Y', time.localtime(createdat))
    return local_time

def basset(asset_or_base,name,size,date,biz_type):
    if biz_type not in ("Deposit", "Withdrawal"):
        if asset_or_base: # True means it is a Main Asset we are dealing with
            return (name,None,size,0,0)  # asset, baseasset, assetsize, baseassetsize, basevalue     
        
        basevalue = getprices.feed_me(name, date) # If condition above is False we have a Base Asset and need to find its USD Value
        return (None,name,0,size,basevalue)
    
    basevalue = getprices.feed_me(name, date) 
    basesize = size * basevalue
    if asset_or_base:
        return (name,"USD",size,basesize,basevalue) # returns if a Deposit or Withdrawal uses Asset
       
    return ("USD",name,basesize,size,basevalue) # returns if a Deposit or Withdrawal uses Base Asset

def is_asset(symbol, name):
    var = bool(f"{name}-" in symbol)
    return var

def order_direction(account_type, direction, a_or_b):
    if account_type != "MAIN" and a_or_b is False: # WORKS OUT IF THE ASSET IS A BASE ASSET FROM A MARGIN OR EXCHANGE ORDER
        return "in" if direction == "out" else "out" # SIDE REFERS TO THE DIRECTION OF THE ORDER THIS DATA ITEM IS A PART OF
    
    return direction

def parse_orders(item):
    _, name, size, _, _, account_type, biz_type, direction, date, context = item.values()
    def symside(btype, name):
        if btype == "Deposit":
            return f"{name}-USD"
          
        return f"USD-{name}"

    if biz_type in ('Cross Margin', 'Exchange', 'Deposit', 'Withdrawal'):
        sizeside = float(size) if direction == "in" else float(size) * -1
        dateint = int(date)
        datestr = str(date)
        dateutc = utc(dateint)

        if biz_type in ('Deposit', 'Withdrawal'):
            try:
                orderid, _ = json.loads(context).values()
            except:
                orderid = f"DW{datestr}"
                symbol = symside(biz_type, name)
            else:
                symbol = symside(biz_type, name)
        else:
            symbol, orderid, _ = json.loads(context).values()
        
        a_or_b = is_asset(symbol, name)
        side = order_direction(account_type, direction, a_or_b)
        asset, baseasset, assetsize, baseassetsize, basevalue = basset(a_or_b,name,sizeside,dateint,biz_type)
        assettest.parse_assets(name, sizeside)

        if orderid in orders:
            orders[orderid].add(asset=asset, baseasset=baseasset, assetsize=assetsize, baseassetsize=baseassetsize)
            if orders[orderid].value['basevalue'] == 0:
                orders[orderid].add(basevalue=basevalue)
        else:
            orders[orderid] =  Order(orderid, dateutc, account_type, symbol, side, asset=asset, baseasset=baseasset,assetsize=assetsize, baseassetsize=baseassetsize,basevalue=basevalue)

for i in raw_data:
    if i['items']:
        for x in i['items']:
            parse_orders(x)

csv_orders = open(f"{csv_name}_ORDERS.csv",'a')
csv_orders.write("Order ID, Date, Account Type, Symbol, Side, Asset, Base Asset, Size, Base Asset Size, Base Value, Base Worth (USD)\n")
for i in orders.values():
        orderid,date,acctype,symbol,side,asset,base,size,basesize,basevalue,baseworth = i.value.values()
        csv_orders.write(f"{orderid},{date},{acctype},{symbol},{side},{asset},{base},{size},{basesize},{basevalue},{baseworth}\n")

csv_orders.close()

csv_assets = open(f"{csv_name}_ASSETS.csv",'a')
csv_assets.write("Asset, Size, USD Value\n")
for i in assettest.assets.values():
    asset,size,usdvalue = i.value.values()
    csv_assets.write(f"{asset},{size},{usdvalue}\n")

csv_assets.close()

getprices.store_prices()

# 1625097600000

#1656633600000
