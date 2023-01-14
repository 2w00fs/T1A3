from shared import db, ma

from relations import (
    unique_orders, count, get_order,
    ledger_test, order_collate, date_to_integer
    )

from schemas import (
    Ledger, LedgerSchema, FuturesTHist,
    FuturesTHistSchema, Ledger,
    LedgerSchema, Prices, PricesSchema,
    LedgerPrices, LedgerPricesSchema, FuturesOrderId,
    FuturesOrderIdSchema, FuturesLedgerDate, FuturesLedgerDateSchema,
    FuturesFundingDate, FuturesFundingDateSchema, FuturesTransactionHistory,
    FuturesTransactionHistorySchema, FuturesOrderIdDate, FuturesOrderIdDateSchema
    )

from futures import (
    futures_transfer_value, run_futures_fills,
    futures_test, unique_futures_orders,
    unique_futures_symbol, run_futures_ledger,
    futures_value, futures_funding_value, futures_order_collate,
    get_test, run_order_by_id, futures_date_to_integer, balance_at_date,
    running_sizes, running_sizes_orderids
    )

from fetch_prices import prices_test

from fetch_ledger_class import FetchLedger


from flask import Flask, request

from settings import (
    db_name,
    db_address,
    db_user,
    db_pass,
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_address}:5432/{db_name}'


db.init_app(app)
ma.init_app(app)


app1 = FetchLedger()

@app.route("/")
def welcome():
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route('/create_all/')
def create_db_all():
    db.create_all()
    # db.session.add_all(jb_seed)
    db.session.commit()
    print("All Done")
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route("/run")
def run():
    # 1651291183638 app1.run_ledger(1625097600000,1659139200000)
    # 1583020800000 1659139200000
    # 1621428488935 1625441419556 1673322330000
    app1.run_ledger(1656039200000,1673322330000)
    # app1.run_ledger(1622601288630,1622860488627)
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"



@app.route("/futures/date_create/")
def f_dates():
    futures_date_to_integer()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"
    

@app.route('/futures/balance/<date>')
def f_balance(date):
    #date = request.args
    print(date)
    return balance_at_date(date)
    

@app.route("/futures/t-history")
def f_run():
    # 1651291183638 app1.run_ledger(1625097600000,1659139200000) 1590633289000 1672281619
    # 1583020800000 1659139200000
    # 1585883199909 1590883199909
    # 1673322330000
    #run_futures_fills(1590883199909,1672281619000)
    run_futures_ledger(1672812200000,1673322330000, 't-history')
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/fills")
def f_fills():
    # MORE THAN 1 PAGE
    # 1652659199194
    # run_futures_fills(1583020800000,1673322330000)
    # 1652659199194 1652831999193
    run_futures_fills(1652659199194,1652831999193)
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/funding")
def f_funding():
    unique_futures_symbol(1672812200000, 1673322330000)
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/orderids")
def f_orders():
    run_order_by_id()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/run/test")
def f_run_test():
    # 1651291183638 app1.run_ledger(1625097600000,1659139200000) 1590633289000 1672281619
    run_futures_ledger(1590633289000,1672281619000)
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"
    

@app.route("/futures/sum")
def f_sum():
    # 1651291183638 app1.run_ledger(1625097600000,1659139200000) 1590633289000 1672281619
    unique_futures_orders()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"
    

@app.route("/futures/value2")
def f_value2():
    fv = futures_value()    
    ffv = futures_funding_value()
    ftv = futures_transfer_value()
    
    print(fv)
    print(ffv)
    print(ftv)
    
    for i in ffv:
        fv[i] += ffv[i]
    
    for v in ffv:
        fv[v] += ftv[v]
        
    print(fv)

    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/value")
def f_value():
    #futures_transfer_value()
    futures_value()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"



@app.route("/futures/symbol")
def f_symbol():
    unique_futures_symbol()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/test")
def f_test():
    # 1651291183638 app1.run_ledger(1625097600000,1659139200000)
    #futures_test('60e2fa1f1f8b450006c89814')
    # futures_order_collate()
    get_test()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route('/ledger/collate/')
def sum():
    #order_sum()
    unique_orders()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/ledger/test')
def l_test():
    ledger_test()
    #second_items()
    #order_collate_test()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/ledger/collate/test')
def collate_test():
    order_collate('61b7e836fd0c3c0001e39171')
    #second_items()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/count/')
def count_():
    print(count('60e01eb438ec0100066673c4'))
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/get_order/')
def getorder():
    get_order()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/test_save/')
def test_save():
    e = FuturesTHist(
        time = '1652150076000',
        type = 'TransferIn',
        amount = 0.05031108,
        fee = 0.0,
        accountEquity = 0.05031108,
        status = 'Completed',
        remark = 'Transferred from Trading Account',
        offset = 13813169,
        currency = 'XBT',
                    )
                    
    db.session.add(e)

    db.session.commit()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/prices/test')
def test_prices():
    prices_test()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/change_date')
def change_date():
    date_to_integer()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/running_sizes')
def f_run_sizes():
    running_sizes_orderids()
    #running_sizes()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'




if __name__ == "__main__":
    app.run(port="8111")
    

"""
        startat = 1583020800000
        dynamicend = startat + 86399999
        endat = 1659139200000
        main(1583020800000,1659139200000)

        if __name__ == "__main__":
        run_ledger(1622910800000,1625029200000)
        

######### TO DO

Save ledger data using returned values
Account for different data structure according to transaction type

    - Context
        -- Order ID
    
    - Account Type
        -- Symbol
"""


