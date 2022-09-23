import time
import json
import getprices
import exchangerates
from orderclass import Order
import mytestdata
#import basebtcdata
orders = {}

def utc(ca):
    # the 36000000 is to add 10 hours to match AEST
    # may remove later because localtime should work off the OS time, Docker has it set wrong methinks
    createdat = int((ca + 36000000) / 1000) 
    utc = time.strftime('%d/%m/%Y', time.localtime(createdat))
    return utc

def basset(symbol,name,sizeside,date):
    fname = name + "-"
    print(fname)
    if (name + "-") in symbol: # if true the asset is main asset being traded        
        direction = "in" if sizeside > 0 else "out"
        #return asset, baseasset, assetsize, baseassetsize, direction
        print(f"Symbol: {symbol}, Asset: {name}")
        time.sleep(0.25)
        return (name,None,sizeside,0,direction,0)
    else: # if condition above is false the asset is the baseasset used to pay for the trade
        direction = "out" if sizeside > 0 else "in"
        #basevalue = getprices.feed_me(name, date)
        basevalue = 0
        print(f"Symbol: {symbol}, Base Asset: {name}")
        time.sleep(0.25)
        return (None,name,0,sizeside,direction,basevalue)

def loop_items(item):
    if item['bizType'] == 'Cross Margin' or item['bizType'] == 'Exchange':
        id, currency, amount, fee, accountType, bizType, direction, createdAt, context = item.values()
        sizeside = float(amount) if direction == "in" else float(amount) * -1
        dateutc = utc(int(createdAt))
        symbol, orderid = json.loads(context).values()
        return (symbol, currency, float(amount), direction, sizeside, int(createdAt), dateutc, orderid)
        
def parse_orders():
    for item in mytestdata.data:
        symbol, name, size, side, sizeside, date, dateutc, orderid = loop_items(item)
        asset, baseasset, assetsize, baseassetsize, direction, basevalue = basset(symbol,name,sizeside, date)

        if orderid in orders:
            orders[orderid].add(asset=asset, baseasset=baseasset, assetsize=assetsize, baseassetsize=baseassetsize)
            if orders[orderid].value['basevalue'] == 0:
                orders[orderid].add(basevalue=basevalue)
        else:
            orders[orderid] =  Order(orderid, dateutc, item['accountType'], symbol, direction, asset=asset, baseasset=baseasset,assetsize=assetsize, baseassetsize=baseassetsize,basevalue=basevalue)

parse_orders()
for i in orders.values():
    print(i.value)

getprices.store_prices()

"""

context, symbol, name, size, side, date, orderid = item

        context = json.loads(item["context"])
        symbol = context.get('symbol')
        name = item['currency']
        size = item['amount']
        side = item['direction']
        sizeside = float(size) if side == "in" else float(size) * -1
        date = int(item['createdAt'])
        dateutc = utc(date)
        orderid = context.get("orderId")

id, currency, amount, fee, accountType, bizType, direction, createdAt, context
"""