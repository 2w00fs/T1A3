from kucoin_futures.client import Trade, User
import credentials
import time
from shared import db, ma, cute
from schemas import (
                        FuturesTHist, FuturesLedger,
                        FuturesFunding, FuturesOrderId,
                        FuturesTransactionHistory, FuturesLedgerDate, FuturesFundingDate,
                        FuturesOrderIdDate
                    )
from sqlalchemy.dialects.postgresql import insert


futures_client = User(credentials.futures_api_key, credentials.futures_secret, credentials.api_passphrase)


def futures_date_to_integer():
    futuresOrderId = cute(db.select(FuturesOrderId)).scalars().all()
    
    for i in futuresOrderId:
        date = int(int(i.createdAt) / 1000)
        
        
        if i.side == 'buy':
            value = i.dealValue
            size = i.dealSize
            cost = 0 - (i.dealValue / float(i.leverage))
        else:
            value = 0 - i.dealValue
            size = 0 - i.dealSize
            cost = (i.dealValue / float(i.leverage))
        
        
        
        insert_stmt = insert(FuturesOrderIdDate).values(
            id = i.id,
            date = date,
            symbol = i.symbol,
            type = i.type,
            side = i.side,
            value = value,
            size = size,
            cost = cost,
            leverage = float(i.leverage)
        )

        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
        cute(do_nothing_stmt)
    
    db.session.commit()


def futures_date_to_integer__OG():
    #   FuturesTHist, FuturesLedger, FuturesFunding,
    thist = cute(db.select(FuturesTHist)).scalars().all()
    
    for i in thist:
        date = int(int(i.time) / 1000)
        insert_stmt = insert(FuturesTransactionHistory).values(
            date = date,
            type = i.type,
            value = i.amount,
            fee = i.fee,
            accountEquity = i.accountEquity,
            status = i.status,
            remark = i.remark,
            offset = i.offset,
            asset = i.currency
        )

        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['date', 'value'])
        cute(do_nothing_stmt)
    
    db.session.commit()
    
    fills = cute(db.select(FuturesLedger)).scalars().all()
    for v in fills:
        date = int(int(v.date) / 1000)
        if v.direction == 'buy':
            size = v.size
            value = v.value
        else:
            size = 0 - v.size
            value = 0 - v.value
        
        insert_stmt = insert(FuturesLedgerDate).values(
            id = v.id,
            order_id = v.order_id,
            date = date,
            trade_type = v.trade_type,
            symbol = v.symbol,
            direction = v.direction,
            size = size,
            settle_asset = v.settle_asset,
            value = value,
            price = v.price,
            fee_currency = v.fee_currency,
            fee = v.fee,
        )

        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
        cute(do_nothing_stmt)
    
    db.session.commit()
    
    funding = cute(db.select(FuturesFunding)).scalars().all()
    for f in funding:
        date = int(int(f.date) / 1000)
        
        insert_stmt = insert(FuturesFundingDate).values(
            id = f.id,
            symbol = f.symbol,
            date = date,
            fundingRate = f.fundingRate,
            markPrice = f.markPrice,
            positionQty = f.positionQty,
            positionCost = f.positionCost,
            funding = f.funding,
            settle_currency = f.settleCurrency
        )

        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
        cute(do_nothing_stmt)
    
    db.session.commit()
    

def running_sizes():
    asset = 'XBT'
    orders = cute(db.select(FuturesLedgerDate.date, FuturesLedgerDate.size, FuturesLedgerDate.value)
                  .filter(FuturesLedgerDate.settle_asset == asset).order_by(FuturesLedgerDate.date.desc()))
    
    order_no = 1
    order_vals = {}
    running_size = 0
    
    for i in orders:
        if str(order_no) in order_vals.keys():
            order_vals[str(order_no)]['value'] += i.value
        else:
            order_vals.update({str(order_no): 
                { "value"  :i.value,
                  "date" : i.date
                }
                })
        
        running_size += i.size
            
        if running_size == 0:
            order_no += 1
    
    for v in order_vals.values():
        print(f"{v['date']} {v['value']}")
    
        
def running_sizes_orderids():
    symbol = 'XBTUSDM'
    orders = cute(db.select(FuturesOrderIdDate.date, FuturesOrderIdDate.size, FuturesOrderIdDate.value)
                  .filter(FuturesOrderIdDate.symbol == symbol).order_by(FuturesOrderIdDate.date.asc()))
    
    order_no = 1
    order_vals = {}
    running_size = 0
    
    for i in orders:
        if str(order_no) in order_vals.keys():
            order_vals[str(order_no)]['value'] += i.value
        else:
            order_vals.update({str(order_no): 
                { "value"  :i.value,
                  "date" : i.date
                }
                })
        
        running_size += i.size
            
        if running_size == 0:
            order_no += 1
    
    for v in order_vals.values():
        print(f"{v['date']} {round(v['value'],4)}")


def futures_balance_at_date(date, date_from):
    print(date)
    # 1593525600    1625061600  1656597600  1688133600
    asset = 'XBT'
    transfers = cute(db.select(db.func.sum(FuturesTransactionHistory.value))
                     .filter(db.and_(FuturesTransactionHistory.asset == asset, FuturesTransactionHistory.date < date, 
                                     FuturesTransactionHistory.type.notlike('RealisedPNL')
                                     ))).scalars().first()
    
    pnl = cute(db.select(db.func.sum(FuturesTransactionHistory.value))
                     .filter(db.and_(FuturesTransactionHistory.asset == asset, FuturesTransactionHistory.date < date, 
                                     FuturesTransactionHistory.type == 'RealisedPNL'
                                     ))).scalars().first()


    contracts = cute(db.select(db.func.sum(FuturesLedgerDate.value))
                     .filter(db.and_(FuturesLedgerDate.settle_asset == asset, FuturesLedgerDate.date < date))).scalars().first()
    
    
    c_size = cute(db.select(db.func.sum(FuturesLedgerDate.size))
                     .filter(db.and_(FuturesLedgerDate.settle_asset == asset, FuturesLedgerDate.date < date))).scalars().first()
    
    
    fees = cute(db.select(db.func.sum(FuturesLedgerDate.fee))
                .filter(db.and_(FuturesLedgerDate.settle_asset == asset, FuturesLedgerDate.date < date))).scalars().first()
    
    
    funding = cute(db.select(db.func.sum(FuturesFundingDate.funding))
                   .filter(db.and_(FuturesFundingDate.settle_currency == asset, FuturesFundingDate.date < date))).scalars().first()


    find_value_size = 0
    find_value = 0
    
    orders = cute(db.select(FuturesLedgerDate.date, FuturesLedgerDate.size, FuturesLedgerDate.value)
                  .filter(db.and_(FuturesLedgerDate.settle_asset == asset, FuturesLedgerDate.date < date)).order_by(FuturesLedgerDate.date.desc()))
    
    for i in orders:
        if find_value_size != c_size:
            find_value += i.value
            find_value_size += i.size
        
        if find_value_size == c_size:
            break
    

    '''
    print(f"transfers {transfers}")
    print(f"contracts {contracts}")
    print(f"c_size {c_size}")
    print(f"fees {fees}")
    print(f"funding {funding}")
    print(f"Realised PNL {pnl}")
    print()
    print(f"PNL: {contracts - fees + funding}")
    print(f"Account Balance: {transfers + contracts - fees + funding}")
    '''
    return  {
                "transfers": transfers,
                "contracts": contracts,
                "c_size": c_size,
                "fees": fees,
                "funding": funding,
                "realised": pnl,
                "pnl": (contracts - fees + funding),
                "find_value": find_value,
                "acc_balance": round((transfers + contracts - fees + funding + abs(find_value)), 4)
            }
    
    
def futures_thist(thist):
    for i in thist['dataList']:
        insert_stmt = insert(FuturesTHist).values(
        time = i['time'],
        type = i['type'],
        amount = i['amount'],
        fee = i['fee'],
        accountEquity = i['accountEquity'],
        status = i['status'],
        remark = i['remark'],
        offset = i['offset'],
        currency = i['currency'],
        )
        
        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['time', 'amount'])
        cute(do_nothing_stmt)
            
    db.session.commit()


def futures_order_id(orderIdLedger):
    insert_stmt = insert(FuturesOrderId).values(
        id = orderIdLedger['id'],
        symbol = orderIdLedger['symbol'],
        type = orderIdLedger['type'],
        side = orderIdLedger['side'],
        price = orderIdLedger['price'],
        size = orderIdLedger['size'],
        value = orderIdLedger['value'],
        dealValue = orderIdLedger['dealValue'],
        dealSize = orderIdLedger['dealSize'],
        stp = orderIdLedger['stp'],
        stop = orderIdLedger['stop'],
        stopPriceType = orderIdLedger['stopPriceType'],
        stopTriggered = orderIdLedger['stopTriggered'],
        stopPrice = orderIdLedger['stopPrice'],
        timeInForce = orderIdLedger['timeInForce'],
        postOnly = orderIdLedger['postOnly'],
        hidden = orderIdLedger['hidden'],
        iceberg = orderIdLedger['iceberg'],
        leverage = orderIdLedger['leverage'],
        forceHold = orderIdLedger['forceHold'],
        closeOrder = orderIdLedger['closeOrder'],
        visibleSize = orderIdLedger['visibleSize'],
        clientOid = orderIdLedger['clientOid'],
        remark = orderIdLedger['remark'],
        tags = orderIdLedger['tags'],
        isActive = orderIdLedger['isActive'],
        cancelExist = orderIdLedger['cancelExist'],
        createdAt = orderIdLedger['createdAt'],
        updatedAt = orderIdLedger['updatedAt'],
        endAt = str(orderIdLedger['endAt']),
        orderTime = str(orderIdLedger['orderTime']),
        settleCurrency = orderIdLedger['settleCurrency'],
        status = orderIdLedger['status'],
        filledSize = orderIdLedger['filledSize'],
        filledValue = orderIdLedger['filledValue'],
        reduceOnly = orderIdLedger['reduceOnly']
    )
        
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
    cute(do_nothing_stmt)
            
    db.session.commit()


def futures_funding(v):
    for i in v:
        print(i)
        insert_stmt = insert(FuturesFunding).values(
        id = str(i['id']),
        symbol = i['symbol'],
        date = str(i['timePoint']),
        fundingRate = i['fundingRate'],
        markPrice = i['markPrice'],
        positionQty = i['positionQty'],
        positionCost = i['positionCost'],
        funding = i['funding'],
        settleCurrency = i['settleCurrency']
        )
        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
        cute(do_nothing_stmt)
    
    db.session.commit()


def get_futures_ledger(start,end,page,ledger_type,symbol=None):
    while True:
        try:
            if ledger_type == 't-history':
                ledger = futures_client.get_transaction_history(startAt=start, endAt=end,maxCount=500)
            elif ledger_type == 'funding':
                ledger = futures_client.get_funding_history(symbol=symbol, startAt=start, endAt=end,currentPage=page, maxCount=500)
        except Exception as e:
            if "Too Many Requests" in str(e.args):
                print(f"Too many requests")
                for i in range(1,11,1):
                    print(f"Retrying in {i}", end='\r')
                    time.sleep(1)
                print("...RETRYING...")
            else:
                print()
                print(f"FAILED TO FETCH PRICE")
                print(e)
                return 20000
        else:
            if len(ledger['dataList']) > 0:
                if ledger_type == 't-history':
                    futures_thist(ledger)
                elif ledger_type == 'funding':
                    futures_funding(ledger['dataList'])
            
            more = ledger['hasMore']
            length = len(ledger['dataList'])
            return {'more':more, 'length':length}


def run_order_by_id():                       
    orders = cute(db.select(db.distinct(FuturesLedger.order_id)).filter(FuturesLedger.trade_type == 'trade')).scalars().all()
    
    for i in orders:       
        while True:
            try:
                ledger = futures_client.get_order_by_id(i)
            except Exception as e:
                if "Too Many Requests" in str(e.args):
                    print(f"Too many requests")
                    for i in range(1,11,1):
                        print(f"Retrying in {i}", end='\r')
                        time.sleep(1)
                    print("...RETRYING...")
                else:
                    return print(f"order id {i} is invalid")
            else:
                futures_order_id(ledger)
                time.sleep(0.5)


def get_test():
    # ledger = futures_client.get_futures_fills(startAt=1652659199194,endAt=1652831999193,currentPage=1)
    #items = ledger['items']
    #length = len(items) - 1
    #print(length)
    #print(items[length])
    
    # 1652831999192
    # date < 1643337729 and date > 1643263543;
    #day_end = 1652831999193
    day_end = 1643337729000
    page = 1
    total_pages = 2
    while page <= total_pages:
        # ledger = futures_client.get_futures_fills(startAt=1652659199194,endAt=day_end,currentPage=page)
        ledger = futures_client.get_futures_fills(startAt=1643263543000,endAt=day_end,currentPage=page)
        total_pages = ledger['totalPage']
        print(f"Page {page} of {total_pages}")
        page += 1
        for i in ledger['items']:
            print(i['orderId'])
        
        print("#########################################")
        time.sleep(5) # wait for 0.2 seconds


def run_futures_ledger(startat, endat, ledger_type, symbol=None):
    if ledger_type == 't-history':
        day_length = 86400000
    elif ledger_type == 'funding':
        day_length = + 86400000 * 60

    has_all = 0

    for day_start_time in range(startat, endat + 86400000, day_length):
        day_end = day_start_time + day_length
        page = 1
        has_more = {'more':True,'length':0}
        while has_more['more'] == True:
            if ledger_type == 't-history':
                has_more_again = get_futures_ledger(day_start_time,day_end,page,ledger_type)
            elif ledger_type == 'funding':
                has_more_again = get_futures_ledger(day_start_time,day_end,page,ledger_type,symbol)
            
            has_all += has_more_again['length']
            print(f"Page {page}  {has_more_again['length']}  {day_start_time}  {has_more_again['more']}")
            has_more['more'] = has_more_again['more']
            page += 1
            time.sleep(0.5) # wait for 0.2 seconds
        
    return f"finished {symbol}"

# FILLS IS THE LEDGER
def get_futures_fills(start,end,page):
    while True:
        try:
            ledger = futures_client.get_futures_fills(startAt=start,endAt=end,currentPage=page)
        except Exception as e:
            if "Too Many Requests" in str(e.args):
                print(f"Too many requests")
                for i in range(1,31,1):
                    print(f"Retrying in {i}", end='\r')
                    time.sleep(1)
                print("...RETRYING...")
            else:
                print()
                print(f"Too Many Requests")
                for i in range(1,20,1):
                    print(f"Retrying in {i}", end='\r')
                    time.sleep(1)
                print("...RETRYING...")
        else:
            if 'items' in ledger.keys():
                for i in ledger['items']:
                    date_int = int(i['tradeTime'] / 1000000)
                    
                    insert_stmt = insert(FuturesLedger).values(
                    id = i['tradeId'],
                    order_id = i['orderId'],
                    date = str(date_int),
                    trade_type = i['tradeType'],
                    symbol = i['symbol'],
                    direction = i['side'],
                    size = i['size'],
                    settle_asset = i['settleCurrency'],
                    value = i['value'],
                    price = i['price'],
                    fee_currency = i['feeCurrency'],
                    fee = i['fee']
                    )
                    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
                    cute(do_nothing_stmt)
                
                db.session.commit()
                
                return ledger['totalPage']
            else:
                time.sleep(1)
                return page - 1


def run_futures_fills(startat,endat):
    for day_start_time in range(startat, endat, 86399999):
        day_end = day_start_time + 86399999
        page = 1
        total_pages = 2
        while page <= total_pages:
            total_pages = get_futures_fills(day_start_time,day_end,page)
            print(f"Page {page} of {total_pages} {day_start_time}")
            if total_pages > 1:
                print("#####################")
                print("# MORE THAN 1 PAGE! #")
                print("#####################")
            page += 1
            time.sleep(1) # wait for 0.2 seconds


def futures_test():
    pass


def futures_value():
    pass


def unique_futures_symbol(start, end):
    symbols = cute(db.select(db.distinct(FuturesLedger.symbol))).scalars()
    for i in symbols:
        do_it = run_futures_ledger(start, end, 'funding', i)
        print(do_it)


def unique_futures_orders():
    pass


def orderId():
    ledger = futures_client.get_order_by_id('60ffc1b82b34400006785eb9')
    print(ledger)