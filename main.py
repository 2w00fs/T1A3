import ordertest
import getprices
import get_ledger
import argparse
import names
#1623048348955 1625029200000

def fetch_ledger():
    get_ledger.run_ledger(1622910800000,1623048348955)

def data_ledger(f_name):
    return ordertest.check_ledger_empty(f_name)



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

    file_names = names.Name(change=change_list)
    _ledger = get_ledger.Ledger(file_names)
    _prices = getprices.Prices(file_names)
    _orders = ordertest.Orders(file_names)
    _ledger.run_ledger(1622910800000,1623048348955)

    for i in _orders.check_ledger_empty():
        if i['items']:
            for x in i['items']:
                _orders.parse_orders(x)

    _orders.write_csvs()