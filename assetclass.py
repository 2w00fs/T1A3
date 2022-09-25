class Asset:
    def __init__(self, asset, size, usdvalue):
        self.value = (asset,size, usdvalue)
    
    @property
    def value(self):
        return {
        "asset": self.__asset,
        "size": self.__size,
        "usdvalue": self.__usdvalue
        }
    
    @value.setter
    def value(self, value_dict):
        asset, size, usdvalue = value_dict
        self.__asset = asset
        self.__size = round(size,5)
        self.__usdvalue = round(usdvalue,2)

    def add(self, size, usdvalue):
        self.__size += round(size,5)
        self.__usdvalue += round(usdvalue,2)