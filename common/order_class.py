class Order:
    def __init__(self, orderid, date, accounttype, symbol, direction=None, asset=None, baseasset=None, assetsize=0, baseassetsize=0, basevalue=0):
        self.value = (orderid, date, accounttype, symbol, direction, asset, baseasset, assetsize, baseassetsize,basevalue)
    
    @property
    def value(self):
        return {
            "orderid": self.__orderid,
            "date": self.__date,
            "acctype": self.__accounttype,
            "symbol": self.__symbol,
            "side": self.__direction,
            "asset": self.__asset,
            "base": self.__baseasset,
            "asize": self.__assetsize,
            "basesize": self.__baseassetsize,
            "basevalue": self.__basevalue,
            "baseworth": self.baseworth()
            }

    @value.setter
    def value(self, value_set):
        orderid, date, accounttype, symbol, direction, asset, baseasset, assetsize, baseassetsize, basevalue = value_set
        self.__orderid = orderid
        self.__date = date
        self.__accounttype = accounttype
        self.__symbol = symbol
        self.__asset = asset
        self.__baseasset = baseasset
        self.__direction = direction
        self.__assetsize = assetsize
        self.__baseassetsize = baseassetsize
        self.__basevalue = basevalue
    
    def add(self, asset=None,baseasset=None,assetsize=0,baseassetsize=0,basevalue=0):
        self.__asset = self.__asset if asset is None else asset 
        self.__baseasset = self.__baseasset if baseasset is None else baseasset
        self.__assetsize += assetsize
        self.__baseassetsize += baseassetsize
        self.__basevalue += basevalue

    def baseworth(self):
        return self.__basevalue * self.__baseassetsize
