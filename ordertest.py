import time
import json
import exchangerates
from orderclass import Order
import mytestdata

orders = {}

def utc(ca):
    createdat = int((ca + 36000000) / 1000) 
    utc = time.strftime('%d/%m/%Y', time.localtime(createdat))
    return utc


def sizeside(size,side):
    floatsize = float(size)
    return floatsize if side == "in" else floatsize * -1

def basset(symbol,name,size,side):
    ss = sizeside(size,side)
    if (name + "-") in symbol: # if true the asset is main asset being traded        
        direction = "in" if ss > 0 else "out"
        #return asset, baseasset, assetsize, baseassetsize, direction
        return (name,None,sizeside(size,side),0,direction)
    else: # if condition above is false the asset is the baseasset used to pay for the trade
        direction = "out" if ss > 0 else "in"
        return (None,name,0,sizeside(size,side),direction)

def decidedirection(assettype, size):
    if assettype == 'asset':
        if size > 0:
            direction = "in"
        else:
            direction = "out"
    if assettype == 'baseasset':
        if size > 0:
            direction = "out"
        else:
            direction = "in"

def loopitems(item):
    if item['bizType'] == 'Cross Margin' or item['bizType'] == 'Exchange':
        context = json.loads(item["context"])
        symbol = context.get('symbol')
        name = item['currency']
        size = item['amount']
        side = item['direction']
        orderid = context.get("orderId")

        asset, baseasset, assetsize, baseassetsize, direction = basset(symbol,name,size,side)

        if orderid in orders:
            orders[orderid].add(asset=asset, baseasset=baseasset, assetsize=assetsize, baseassetsize=baseassetsize)
        else:
            orders[orderid] =  Order(orderid, item['createdAt'], item['accountType'], direction, asset=asset, baseasset=baseasset,assetsize=assetsize, baseassetsize=baseassetsize)

for index in mytestdata.data:
    loopitems(index)
    #print(index)
        

for i in orders.values():
    print(i.value)

