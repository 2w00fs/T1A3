import re

class InvalidNameError(Exception):
    def __init__(self,chars):
        super().__init__(f"Illegal character in file name,{self.vals(chars)} pls try a different one, spaces are not allowed")
    
    def vals(self, chars):
        for i in chars:
            i = "[space]" if i == " " else i
            print(f"Illegal Character: {i}")
        return ""

class Name:
    def __init__(self, change=None):
        self.the_name = self.set_name(change)
        self.log = self.the_name['log']
        self.ledger = self.the_name['ledger']
        self.prices = self.the_name['prices']
        self.orders = self.the_name['orders']
        self.assets = self.the_name['assets']

    def check_name(self, text):
        illegal = "[\#\<\$\^\+%\>\!\`\&\*\'\|\{\?\"\=\}\/\:\\\ \@\;]"
        check_text = re.findall(illegal, text)
        if len(check_text):
            raise InvalidNameError(check_text)

        return text

    def set_name(self,change=None):
        while True:
            try:
                fn = input("Filename for Output Files pls: ")
                self.check_name(fn)
            except InvalidNameError as e:
                print(e)
            else:
                
                names = {"log": f"{fn}LOG.txt", "ledger": f"{fn}_Ledger.json", "prices": f"{fn}_Prices.json", "orders": f"{fn}_Orders.csv", "assets": f"{fn}_Assets.csv"}
                if change is not None:
                    for i in change:
                        names[i[0]] = f"{i[1]}.json"

                return names
    
    def update(self, type, new_name):
        self[type] = new_name
