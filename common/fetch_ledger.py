from shared import db, ma

from relations import (
    unique_orders, get_order,
    ledger_test, date_to_integer,
    balance_at_date, ledger_running_sizes
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
    run_futures_fills,
    futures_test, run_futures_ledger, get_test,
    run_order_by_id, futures_date_to_integer, 
    futures_balance_at_date, running_sizes,
    running_sizes_orderids, orderId as futures_orderid
    )

from fetch_prices import ledger_prices

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
    app1.run_ledger(1626501511842,1673322330000)
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/date_create/")
def f_dates():
    futures_date_to_integer()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"
    

@app.route('/futures/balance')
def f_balance():
    args = request.args
    date = args.get("date", default=1673322330000, type=int)
    date_from = args.get("dateFrom", default=0, type=int)
    #date = request.args
    return futures_balance_at_date(date, date_from)
    

@app.route("/futures/t-history")
def f_run():

    # funding t-history
    run_futures_ledger(1583042312345,1673322330000, 'funding')
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/fills")
def f_fills():
    # 1652659199194 1652831999193 1673322330000
    run_futures_fills(1652701123456,1673322330000)
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/orderids")
def f_orders():
    run_order_by_id()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"
    

@app.route("/futures/id")
def f_id():
    futures_orderid()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route("/futures/run/test")
def f_run_test():
    # 1651291183638 app1.run_ledger(1625097600000,1659139200000) 1590633289000 1672281619
    run_futures_ledger(1590633289000,1672281619000)
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"
    

@app.route("/futures/test")
def f_test():
    get_test()
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route('/ledger/test')
def l_test():
    ledger_test()
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


@app.route('/ledger/prices')
def price_ledger():
    ledger_prices()
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


@app.route('/ledger/running_sizes')
def l_run_sizes():
    ledger_running_sizes()
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


@app.route('/ledger/balance')
def ledger_balance():
    args = request.args
    date = args.get("date", default=1673322330000, type=int)
    date_from = args.get("dateFrom", default=0, type=int)
    return balance_at_date(date, date_from)


if __name__ == "__main__":
    app.run(port="8111")
    
