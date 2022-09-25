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
        self.log = f"{self.the_name['log']}_LOG.txt"
        self.ledger = f"{self.the_name['ledger']}_Ledger.json"
        self.prices = f"{self.the_name['prices']}_Prices.json"
        self.orders = f"{self.the_name['orders']}_Orders.csv"
        self.assets = f"{self.the_name['assets']}_Assets.csv"

    def check_name(self, text):
        illegal = "[\#\<\$\^\+%\>\!\`\&\*\'\|\{\?\"\=\}\/\:\\\ \@\;]"
        check_text = re.findall(illegal, text)
        if len(check_text):
            raise InvalidNameError(check_text)

        return text

    def set_name(self,change=None):
        print(change)
        while True:
            try:
                file_name = input("Filename for Output Files pls: ")
                self.check_name(file_name)
            except InvalidNameError as e:
                print(e)
            else:
                names = {"log": file_name, "ledger": file_name, "prices": file_name, "orders": file_name, "assets": file_name}
                if change != None:
                    for i in change:
                        names[i[0]] = i[1]

                return names

    def update(self, type, new_name):
        self[type] = new_name
