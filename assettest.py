from assetclass import Asset
import mytestdata

assets = {}

def loopitems(item):
    if item['bizType'] == 'Cross Margin' or item['bizType'] == 'Exchange':
        name = item['currency']
        size = item['amount']
        side = item['direction']
        sizeside = float(size) if side == "in" else float(size) * -1
    
        if name in assets:
            assets[name].add(sizeside)
        else:
            assets[name] =  Asset(name,sizeside)

for index in mytestdata.data:
    loopitems(index)

for i in assets.values():
    print(i.value)