class Asset:
    def __init__(self, asset, size):
        self.value = (asset,size)
    
    @property
    def value(self):
        return {"asset": self.__asset, "size": self.__size}
    
    @value.setter
    def value(self, value_dict):
        asset, size = value_dict
        self.__asset = asset
        self.__size = size

    def add(self, size):
        self.__size += size