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
    def __init__(self):
        self.the_name = self.name()
        self.log = f"{self.the_name}_LOG.txt"
        self.ledger = f"{self.the_name}_Ledger.json"
        self.prices = f"{self.the_name}_Prices.json"
        self.orders = f"{self.the_name}_Orders.csv"
        self.assets = f"{self.the_name}_Assets.csv"

    def check_name(self, text):
        illegal = "[\#\<\$\^\+%\>\!\`\&\*\'\|\{\?\"\=\}\/\:\\\ \@\;]"
        check_text = re.findall(illegal, text)
        if len(check_text):
            raise InvalidNameError(check_text)

        return text


    def name(self):
        while True:
            try:
                file_name = input("Filename for Output Files pls: ")
                self.check_name(file_name)
            except InvalidNameError as e:
                print(e)
            else:
                return file_name

base_file_name = Name()