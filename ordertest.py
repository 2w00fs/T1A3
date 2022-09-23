import time
import json
import getprices
import exchangerates
import assettest
from orderclass import Order

order_data_file_name = "ledger_as_json"

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

def utc(ca):
    # the 36000000 is to add 10 hours to match AEST
    # may remove later because localtime should work off the OS time, Docker has it set wrong methinks
    createdat = int((ca + 36000000) / 1000) 
    utc = time.strftime('%d/%m/%Y', time.localtime(createdat))
    return utc

def basset(ab,name,size,date,account_type):
    if account_type != "MAIN":
        # asset, baseasset, assetsize, baseassetsize, basevalue
        if ab:
            return (name,None,size,0,0)
        else:
            basevalue = getprices.feed_me(name, date)
            return (None,name,0,size,basevalue)
    else: # THIS EXISTS BECAUSE I AM TREATING DEPOSITS AND WITHDRAWALS AS A BUY/SELL TRANSACTION
        basevalue = getprices.feed_me(name, date) 
        basesize = size * basevalue
        if ab:
            return (name,"USD",size,basesize,basevalue)
        else:
            return ("USD",name,basesize,size,basevalue)

def loop_items(item):
        id, currency, amount, fee, account_type, bizType, direction, createdAt, context = item.values()
        sizeside = float(amount) if direction == "in" else float(amount) * -1
        dateutc = utc(int(createdAt))
        symbol, orderid, txid = json.loads(context).values()

        return (symbol, currency, float(amount), direction, sizeside, int(createdAt), dateutc, orderid,account_type)

def is_asset(symbol, name):
    if (f"{name}-") in symbol:
        return True
    else:
        return False

def order_direction(account_type, direction, size,is_asset):
    if account_type != "MAIN" and is_asset == False:
        side = "in" if direction == "out" else "out"
    else:
        side = direction
    
    sizeside = float(size) if direction == "in" else float(size) * -1
    return direction, sizeside

def parse_orders(item):
    def symside(btype, name):
            if btype == "Deposit":
                sym = f"{name}-USD"
            else:
                sym = f"USD-{name}"
            return sym
            
    if item['bizType'] == 'Cross Margin' or item['bizType'] == 'Exchange' or item['bizType'] == 'Deposit' or item['bizType'] == 'Withdrawal':
        id, name, size, fee, balance, account_type, biz_type, direction, date, context = item.values()
        #sizeside = float(size) if direction == "in" else float(size) * -1
        dateutc = utc(int(date))

        if biz_type == 'Deposit' or biz_type == 'Withdrawal':
            try:
                orderid, txid = json.loads(context).values()
            except:
                orderid = f"DW{date}"
                symbol = symside(biz_type, name)
            else:
                symbol = symside(biz_type, name)
        elif biz_type == 'Cross Margin' or biz_type == 'Exchange':
            symbol, orderid, txid = json.loads(context).values()
        
        a_or_b = is_asset(symbol, name)
        direction, sizeside = order_direction(account_type, direction, size, a_or_b)
        asset, baseasset, assetsize, baseassetsize, basevalue = basset(a_or_b,name,sizeside,date,account_type)
        assettest.parse_assets(name, sizeside)

        if orderid in orders:
            orders[orderid].add(asset=asset, baseasset=baseasset, assetsize=assetsize, baseassetsize=baseassetsize)
            if orders[orderid].value['basevalue'] == 0:
                orders[orderid].add(basevalue=basevalue)
        else:
            orders[orderid] =  Order(orderid, dateutc, account_type, symbol, direction, asset=asset, baseasset=baseasset,assetsize=assetsize, baseassetsize=baseassetsize,basevalue=basevalue)

for i in raw_data:
    if i['items']:
        for x in i['items']:
            #print(x)
            parse_orders(x)

for i in orders.values():
    print(i.value)

for i in assettest.assets.values():
    print(i.value)



getprices.store_prices()

# 1625097600000

#1656633600000

"""
for i in raw_data:
    if i['items']:
        for x in i['items']:
            #print(x)
            parse_orders(x)
"""