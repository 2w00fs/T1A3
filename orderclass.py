class Order:
    def __init__(self, orderid, date, accounttype, direction=None, asset=None, baseasset=None, assetsize=0, baseassetsize=0):
        self.value = (orderid, date, accounttype, direction, asset, baseasset, assetsize, baseassetsize)
    
    @property
    def value(self):
        return {\
            "orderid": self.__orderid,\
            "date": self.__date,\
            "accounttype": self.__accounttype,\
            "direction": self.__direction,\
            "asset": self.__asset,\
            "baseasset": self.__baseasset,\
            "assetsize": self.__assetsize,\
            "baseassetsize": self.__baseassetsize\
            }

    @value.setter
    def value(self, value_set):
        orderid, date, accounttype, direction, asset, baseasset, assetsize, baseassetsize = value_set
        self.__orderid = orderid
        self.__date = date
        self.__accounttype = accounttype
        self.__asset = asset
        self.__baseasset = baseasset
        self.__direction = direction
        self.__assetsize = assetsize
        self.__baseassetsize = baseassetsize
    
    def add(self, asset=None,baseasset=None,assetsize=0,baseassetsize=0):
        self.__asset = self.__asset if asset == None else asset 
        self.__baseasset = self.__baseasset if baseasset == None else baseasset
        self.__assetsize += assetsize
        self.__baseassetsize += baseassetsize
