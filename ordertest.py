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

def basset(symbol,name,size,side):
    sizeside = float(size) if side == "in" else float(size) * -1
    if (name + "-") in symbol: # if true the asset is main asset being traded        
        direction = "in" if sizeside > 0 else "out"
        #return asset, baseasset, assetsize, baseassetsize, direction
        return (name,None,sizeside,0,direction)
    else: # if condition above is false the asset is the baseasset used to pay for the trade
        direction = "out" if sizeside > 0 else "in"
        return (None,name,0,sizeside,direction)

def loopitems(item):
    if item['bizType'] == 'Cross Margin' or item['bizType'] == 'Exchange':
        context = json.loads(item["context"])
        symbol = context.get('symbol')
        name = item['currency']
        size = item['amount']
        side = item['direction']
        date = int(item['createdAt'])
        dateutc = utc(date)
        orderid = context.get("orderId")
        
        asset, baseasset, assetsize, baseassetsize, direction = basset(symbol,name,size,side)

        if orderid in orders:
            orders[orderid].add(asset=asset, baseasset=baseasset, assetsize=assetsize, baseassetsize=baseassetsize)
            if baseasset != None and orders[orderid].value['basevalue'] == 0:
                orders[orderid].add(basevalue= getprices.feed_me(baseasset, date))
        else:
            orders[orderid] =  Order(orderid, dateutc, item['accountType'], symbol, direction, asset=asset, baseasset=baseasset,assetsize=assetsize, baseassetsize=baseassetsize)
            if baseasset != None:
                orders[orderid].add(basevalue= getprices.feed_me(baseasset, date))

for index in mytestdata.data:
    loopitems(index)

for i in orders.values():
    print(i.value)

getprices.store_prices()

"""
            if orders[orderid].get(basevalue) == 0:
                if name != 'USDT':
                    basevalue = getprices.feedme(name,date)
                else:
                    basevalue = 1
            else:
                    basevalue = 0

"""