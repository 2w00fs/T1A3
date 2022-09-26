from common.parse_orders import Orders
from common.fetch_ledger import Ledger
import argparse
from common.names import Name
#1623048348955 1625029200000

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ledger", "--ledgername", dest = "ledgername", default = None, help="Exisitng Ledger Name")
    parser.add_argument("-prices", "--pricelist", dest = "pricelist", default = None, help="Existing Price List Name")
    args = parser.parse_args()
    change_list = []
    if args.ledgername:
        change_list.append(["ledger",f"{args.ledgername}"])
    if args.pricelist:
        change_list.append(["prices",f"{args.pricelist}"])
    
    file_names = Name(change=change_list)
    _ledger = Ledger(file_names)
    _orders = Orders(file_names)
    _ledger.run_ledger(1622910800000,1623048348955)

    for i in _orders.check_ledger_empty():
        if i['items']:
            for x in i['items']:
                _orders.parse_orders(x)

    _orders.write_csvs()