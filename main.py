import ordertest
import getprices
import get_ledger
import time
#import json
#import argparse
import names
#1623048348955 1625029200000
def fetch_ledger():
    get_ledger.run_ledger(1622910800000,1623048348955)

def data_ledger(f_name):
    return ordertest.check_ledger_empty(f_name)


if __name__ == "__main__":
    returned_name = names.base_file_name
    fetch_ledger()
    for i in data_ledger(returned_name.ledger):
        if i['items']:
            for x in i['items']:
                ordertest.parse_orders(x)

    ordertest.write_csvs(returned_name)

    getprices.store_prices(returned_name)
