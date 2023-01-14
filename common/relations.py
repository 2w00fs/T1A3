
import time
from shared import db, cute
from schemas import Ledger, LedgerSchema, LedgerSum, LedgerSumSchema, LedgerSecond, LedgerSecondSum, LedgerSecondSumSchema
from ledger_entry import LedgerEntry
from pprint import pprint
from sqlalchemy.dialects.postgresql import insert


def parse_date(ca):
    extra_dates = {
        "utc": "DD/MM/YY",
        "fy": 0
    }
    
    if type(ca) == 'str':
        ca = int(ca)
    
    createdat = int(int(ca) / 1000)
    
    extra_dates['utc'] = time.strftime('%d/%m/%Y', time.localtime(createdat))
    month = time.strftime('%m', time.localtime(createdat))
    year = time.strftime('%Y', time.localtime(createdat))
    
    if month >= 7:
        extra_dates['fy'] = year
    elif month < 7:
        extra_dates['fy'] = year - 1
        
    return extra_dates


def get_order():
    oid = '60eaa6f32575430006ee3f39'
    ass_val = cute(db.select(Ledger.asset, Ledger.direction, db.func.sum(Ledger.size)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid))
    for a in ass_val:
        print(a)
    


def ledger_entry(id, order_id, date, acc_type, bizType, symbol, asset, direction, size, fee):
    insert_stmt = insert(Ledger).values(
        id=id,
        order_id=order_id,
        date=date,
        acc_type=acc_type,
        biz_type=bizType,
        symbol=symbol,
        asset=asset,
        direction=direction,
        size=size,
        fee=fee
    )

    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
    cute(do_nothing_stmt)
    
    '''
    v = LedgerSecond(
        id=id,
        order_id=order_id,
        date=date,
        acc_type=acc_type,
        biz_type=bizType,
        symbol=symbol,
        asset=asset,
        direction=direction,
        size=size,
        fee=fee
    )
    
    insert(Ledger).values(
    id=id,
    order_id=order_id,
    date=date,
    acc_type=acc_type,
    biz_type=bizType,
    symbol=symbol,
    asset=asset,
    direction=direction,
    size=size,
    fee=fee
    )
    '''



def commit_entries():
    db.session.commit()


def ledger_test2():
    assets = list(cute(db.select(db.distinct(LedgerSecondSum.asset))).scalars())
    base_assets = list(cute(db.select(db.distinct(LedgerSecondSum.base_asset))).scalars())
    combined_assets = []
    sizes = {}
    
    for a in assets:
        combined_assets.append(a)
        
    for b in base_assets:
        if b not in combined_assets:
            combined_assets.append(b)
    
    for c in combined_assets:
        sizes.update({c:0})
        
    for ab in assets:
        ass_size = cute(db.select(db.func.sum(LedgerSecondSum.asset_size)).group_by(LedgerSecondSum.asset).filter(LedgerSecondSum.asset == ab)).scalars().first()
        sizes[ab] += ass_size
    
    for bb in base_assets:
        if bb != None:
            bass_size = cute(db.select(db.func.sum(LedgerSecondSum.base_asset_size)).group_by(LedgerSecondSum.base_asset).filter(LedgerSecondSum.base_asset == bb)).scalars().first()
            sizes[bb] += bass_size
    
    for i in sizes.keys():
        if sizes[i] > 0.1 or sizes[i] < -0.1:
            print(f'{i} {round(sizes[i],3)}')


def transfers():   
    ass_size = cute(db.select(LedgerSecondSum.asset, db.func.sum(LedgerSecondSum.asset_size)).group_by(LedgerSecondSum.asset)
        .filter(db.or_(
            LedgerSecondSum.biz_type == 'Bank Card Deal',
            LedgerSecondSum.biz_type == 'Deposit',
            LedgerSecondSum.biz_type == 'Distribution',
            LedgerSecondSum.biz_type == 'KuCoin Bonus',
            LedgerSecondSum.biz_type == 'Open red envelope',
            LedgerSecondSum.biz_type == 'Other rewards',
            LedgerSecondSum.biz_type == 'Rewards',
            LedgerSecondSum.biz_type == 'Send red envelope',
            LedgerSecondSum.biz_type == 'Soft Staking Profits',
            LedgerSecondSum.biz_type == 'Sub-account transfer',
            LedgerSecondSum.biz_type == 'Transfer',
            LedgerSecondSum.biz_type == 'Withdrawal'
            )))
    
    print(ass_size)
    
    for i in ass_size:
        print(i)


def ledger_test():
    #transfers()
    ass_size = cute(db.select(LedgerSecondSum.asset, db.func.sum(LedgerSecondSum.asset_size)).group_by(LedgerSecondSum.asset))
    for i in ass_size:
        print(i)
    
    print()
    
    bass_size = cute(db.select(LedgerSecondSum.base_asset, db.func.sum(LedgerSecondSum.base_asset_size)).group_by(LedgerSecondSum.base_asset))
    for v in bass_size:
        print(v)
    
def ledger_test3():
    ass_size = cute(db.select(LedgerSecondSum.asset, db.func.sum(LedgerSecondSum.asset_size)).group_by(LedgerSecondSum.asset))
    ass = {}
    for i in ass_size:
        ass.update({i.asset: i.sum})
    
    b_ass_size = cute(db.select(LedgerSecondSum.base_asset, db.func.sum(LedgerSecondSum.base_asset_size)).group_by(LedgerSecondSum.base_asset))
    for b in b_ass_size:
        try:
            ass[b.base_asset] += b.sum
        except:
            ass.update({b.base_asset: b.sum})

    kcs_fee_size = cute(db.select(db.func.sum(LedgerSecondSum.fee_kcs))).scalars().first()
    ass['KCS'] += kcs_fee_size
    
    for v in ass:
        if ass[v] > 0.1 or ass[v] < -0.1:
            print(f'{v}  {ass[v]}')
    
    print()
    print(f'KCS fee size {kcs_fee_size}')

    '''
    for i in sizes.keys():
        if sizes[i] > 0.1 or sizes[i] < -0.1:
            print(f'{i} {round(sizes[i],3)}')
    '''

def count(order_id, clmn):
    # complicated query that counts the number of each bizType in an order, and returns the most used one
    # need this value when collating the orders so that entries such as 'Refunded Fee' don't determine the biztype
    # when it should be 'Exchange' etc.
    #print(clmn)
    #print(order_id)
    def s(c):
        #stmnt = cute(db.select(c, db.func.count(c)).group_by(c)
        #     .filter(Ledger.order_id == order_id)).scalars().all()
        stmnt = cute(db.select(c, db.func.count(c)).group_by(c)
             .filter(Ledger.order_id == order_id).order_by(db.func.count(c).desc())).scalars().first()

        return stmnt

    match clmn:
        case 'bizType':
            return s(Ledger.biz_type)
        case 'acc_type':
            return s(Ledger.acc_type)
        case 'symbol':
            return s(Ledger.symbol)


def order_collate(oid):
    assets = list(cute(db.select(db.distinct(Ledger.asset)).filter(Ledger.order_id == oid)).scalars())
    bizType = cute(db.select(db.distinct(Ledger.biz_type)).filter(Ledger.order_id == oid)).scalars()
    
    fee_size = cute(db.select(Ledger.asset, db.func.sum(Ledger.fee)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid).order_by(db.func.sum(Ledger.fee).desc())).first()

    sizes = {}
    fees = {}
    
    
    
    for ast in assets:
        sizes.update({ast: 0})
        fees.update({ast: 0})

    # subtract the fee
    sizes[fee_size[0]] -= fee_size[1]
    fees[fee_size[0]] -= fee_size[1]
    
    # get static information
    real_b_type = count(oid, 'bizType')
    real_acc_type = count(oid, 'acc_type')
    symbol = count(oid, 'symbol')
    
    # assign default values used in an entry to the DB
    ls_order_id = oid
    ls_date = cute(db.select(Ledger.date).filter(Ledger.order_id == oid)).scalars().first()
    ls_biz_type = real_b_type
    ls_acc_type = real_acc_type
    ls_symbol = symbol
    ls_asset_size = 0
    ls_fee = 0 # not assigned fee value incase value needs to be updated with refunded amount
    ls_fee_kcs = 0
    ls_direction = ''
    ls_asset = ''
    ls_asset_size = 0
    ls_base_asset = '' # not all orders have a base asset or base asset size
    ls_base_asset_size = 0
    ls_fee_asset = ''
    ls_fee_kcs = 0
      

    # Iterates through unique bizTypes and sums up their size by Asset and Direction
    # ('ENQ', 'out', 22697.192200000005)
    # ('USDT', 'in', 1960.1792662700002)
    for i in bizType:
        ass_size = cute(db.select(Ledger.asset, Ledger.direction, db.func.sum(Ledger.size)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid, Ledger.biz_type == i))
        for v in ass_size:
            print(fees[fee_size[0]])
            ass = v[0]
            dir = v[1]
            sz = v[2]
            if i == 'Refunded Fees':
                fees[ass] += sz
                sizes[ass] += sz
            if i == 'KCS Pay Fees':
                ls_fee_kcs -= sz
            
            if dir == 'in':
                sizes[ass] += sz
            elif dir == 'out':
                sizes[ass] -= sz
            else:
                print('oh no')

    
    for a in assets:
        if f'{a}-' in symbol:
            ls_asset=a
            ls_asset_size = sizes[a]
            ls_direction = cute(db.select(Ledger.direction).filter(Ledger.order_id == oid, Ledger.symbol == symbol, Ledger.asset == a)).scalar()
            if fees[a] != 0:
                ls_fee -= fees[a]
                ls_fee_asset = a
        elif f'-{a}' in symbol:
            ls_base_asset=a
            ls_base_asset_size=sizes[a]
            if fees[a] != 0:
                ls_fee -= fees[a]
                ls_fee_asset = a
        else:
            ls_fee_kcs = sizes[a]
    
    insert_stmt = insert(LedgerSecondSum).values(
        order_id=ls_order_id,
        date=ls_date,
        acc_type=ls_acc_type,
        biz_type=ls_biz_type,
        symbol=ls_symbol,
        asset=ls_asset,
        base_asset = ls_base_asset,
        direction=ls_direction,
        asset_size=ls_asset_size,
        base_asset_size = ls_base_asset_size,
        fee=ls_fee,
        fee_asset = ls_fee_asset,
        fee_kcs = ls_fee_kcs
    )

    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['order_id'])
    cute(do_nothing_stmt)
    #db.session.add(ls)
    db.session.commit()


def order_collate_two(oid):
    # changed the way fees are deducted
    assets = list(cute(db.select(db.distinct(Ledger.asset)).filter(Ledger.order_id == oid)).scalars())
    bizType = cute(db.select(db.distinct(Ledger.biz_type)).filter(Ledger.order_id == oid)).scalars()
    
    fee_size = cute(db.select(Ledger.asset, db.func.sum(Ledger.fee)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid).order_by(db.func.sum(Ledger.fee).desc())).first()

    sizes = {}
    fees = {}
    
    
    
    for ast in assets:
        sizes.update({ast: 0})
        fees.update({ast: 0})

    # subtract the fee
    sizes[fee_size[0]] -= fee_size[1]
    fees[fee_size[0]] -= fee_size[1]
    
    # get static information
    real_b_type = count(oid, 'bizType')
    real_acc_type = count(oid, 'acc_type')
    symbol = count(oid, 'symbol')
    
    # assign default values used in an entry to the DB
    ls_order_id = oid
    ls_date = cute(db.select(Ledger.date).filter(Ledger.order_id == oid)).scalars().first()
    ls_biz_type = real_b_type
    ls_acc_type = real_acc_type
    ls_symbol = symbol
    ls_asset_size = 0
    ls_fee = 0 # not assigned fee value incase value needs to be updated with refunded amount
    ls_fee_kcs = 0
    ls_direction = ''
    ls_asset = ''
    ls_asset_size = 0
    ls_base_asset = '' # not all orders have a base asset or base asset size
    ls_base_asset_size = 0
    ls_fee_asset = ''
    ls_fee_kcs = 0
      

    # Iterates through unique bizTypes and sums up their size by Asset and Direction
    # ('ENQ', 'out', 22697.192200000005)
    # ('USDT', 'in', 1960.1792662700002)
    for i in bizType:
        ass_size = cute(db.select(Ledger.asset, Ledger.direction, db.func.sum(Ledger.size)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid, Ledger.biz_type == i))
        for v in ass_size:
            print(fees[fee_size[0]])
            ass = v[0]
            dir = v[1]
            sz = v[2]
            if i == 'Refunded Fees':
                fees[ass] += sz
                sizes[ass] += sz
            if i == 'KCS Pay Fees':
                ls_fee_kcs -= sz
            
            if dir == 'in':
                sizes[ass] += sz
            elif dir == 'out':
                sizes[ass] -= sz
            else:
                print('oh no')

    
    for a in assets:
        if f'{a}-' in symbol:
            ls_asset=a
            ls_asset_size = sizes[a]
            ls_direction = cute(db.select(Ledger.direction).filter(Ledger.order_id == oid, Ledger.symbol == symbol, Ledger.asset == a)).scalar()
            if fees[a] != 0:
                ls_fee -= fees[a]
                ls_fee_asset = a
        elif f'-{a}' in symbol:
            ls_base_asset=a
            ls_base_asset_size=sizes[a]
            if fees[a] != 0:
                ls_fee -= fees[a]
                ls_fee_asset = a
        else:
            ls_fee_kcs = sizes[a]
    
    insert_stmt = insert(LedgerSecondSum).values(
        order_id=ls_order_id,
        date=ls_date,
        acc_type=ls_acc_type,
        biz_type=ls_biz_type,
        symbol=ls_symbol,
        asset=ls_asset,
        base_asset = ls_base_asset,
        direction=ls_direction,
        asset_size=ls_asset_size,
        base_asset_size = ls_base_asset_size,
        fee=ls_fee,
        fee_asset = ls_fee_asset,
        fee_kcs = ls_fee_kcs
    )

    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['order_id'])
    cute(do_nothing_stmt)
    #db.session.add(ls)
    db.session.commit()
    

def order_collate_test(oid):
    #oid = '5f3cd0b3b6401500072ba719' # kcs-usdt
    #oid = '62aae683501cb3000102d95c' # bank card
    # oid = '6034a8ebb616180006616a78'
    # oid = '60eaa6f32575430006ee3f39'
    # changed the way fees are deducted
    #assets = list(cute(db.select(db.distinct(Ledger.asset)).filter(Ledger.order_id == oid)).scalars())
    bizType = list(cute(db.select(db.distinct(Ledger.biz_type)).filter(Ledger.order_id == oid)).scalars())
    
    fee_size = cute(db.select(Ledger.asset, db.func.sum(Ledger.fee)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid).order_by(db.func.sum(Ledger.fee).desc())).first()

    fee_asset = fee_size[0]
    fee_total = fee_size[1]
    fee_kcs = 0
    
    if 'Refunded Fees' in bizType:
        refunded_fees = cute(db.select(db.func.sum(Ledger.size))
             .filter(Ledger.order_id == oid, Ledger.biz_type == 'Refunded Fees')).scalars().first()
        
        fee_total -= refunded_fees
        
    if 'KCS Pay Fees' in bizType:
        kcs_pay_fees = cute(db.select(db.func.sum(Ledger.size))
             .filter(Ledger.order_id == oid, Ledger.biz_type == 'KCS Pay Fees')).scalars().first()
        
        fee_kcs -= kcs_pay_fees
    
  
    # get static information
    real_b_type = count(oid, 'bizType')
    real_acc_type = count(oid, 'acc_type')
    symbol = count(oid, 'symbol')
    
    
    ass_size = cute(db.select(Ledger.asset, Ledger.direction, db.func.sum(Ledger.size)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid, Ledger.biz_type == real_b_type))
    
    asset = ''
    base_asset = ''
    direction = ''
    asset_size = 0
    base_asset_size = 0
    
    for a in ass_size:
        asset_, direction_, size_ = a
        ### adds any fee to the asset size where orders are XXXX-USD, probs only Deposit and Withdrawal transactions
        ### they dont have a fee anyway though 
        if f'{asset_}-USD' in symbol and f'{asset_}-USDT' not in symbol:
            #print(f'{asset_}-USD in symbol')
            asset_size += fee_total
            base_asset = 'USD'

        if f'{asset_}-' in symbol:
            #print(f'{asset_}- in symbol')
            asset = asset_
            direction = direction_
            asset_size += size_
            if direction == 'out':
                asset_size = 0 - asset_size

        if f'-{asset_}' in symbol and f'{asset_}-' not in symbol:
            #print(f'-{asset_} in symbol and {asset_}- not in symbol')
            base_asset = asset_
            base_asset_size = size_ + fee_total
            if direction_ == 'out':
                base_asset_size = 0 - base_asset_size
                
        if f'{asset_}-{asset_}' in symbol:
            #print(f'{asset_}-{asset_} in symbol')
            base_asset = asset_
            base_asset_size = 0
                
    print(f'{asset} {asset_size}    {base_asset} {base_asset_size}')
    print()

    date = cute(db.select(Ledger.date).filter(Ledger.order_id == oid)).scalars().first()
    '''
    # assign default values used in an entry to the DB
    ls_order_id = oid
    ls_date = cute(db.select(Ledger.date).filter(Ledger.order_id == oid)).scalars().first()
    ls_biz_type = real_b_type
    ls_acc_type = real_acc_type
    ls_symbol = symbol
    ls_asset_size = 0
    ls_fee = 0 # not assigned fee value incase value needs to be updated with refunded amount
    ls_fee_kcs = 0
    ls_direction = ''
    ls_asset = ''
    ls_asset_size = 0
    ls_base_asset = '' # not all orders have a base asset or base asset size
    ls_base_asset_size = 0
    ls_fee_asset = fee_asset
    ls_fee_kcs = 0
      

    # Iterates through unique bizTypes and sums up their size by Asset and Direction
    # ('ENQ', 'out', 22697.192200000005)
    # ('USDT', 'in', 1960.1792662700002)
    for i in bizType:
        ass_size = cute(db.select(Ledger.asset, Ledger.direction, db.func.sum(Ledger.size)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid, Ledger.biz_type == i))
        for v in ass_size:
            ass = v[0]
            dir = v[1]
            sz = v[2]
            if i == 'KCS Pay Fees':
                ls_fee_kcs -= sz
            
            if dir == 'in':
                sizes[ass] += sz
            elif dir == 'out':
                sizes[ass] -= sz
            else:
                print('oh no')

    
    for a in assets:
        if f'{a}-' in symbol:
            ls_asset=a
            ls_asset_size = sizes[a]
            ls_direction = cute(db.select(Ledger.direction).filter(Ledger.order_id == oid, Ledger.symbol == symbol, Ledger.asset == a)).scalar()
        elif f'-{a}' in symbol:
            ls_base_asset=a
            ls_base_asset_size=sizes[a]
        else:
            ls_fee_kcs = sizes[a]
    
    '''
    insert_stmt = insert(LedgerSecondSum).values(
        order_id=oid,
        date=date,
        acc_type=real_acc_type,
        biz_type=real_b_type,
        symbol=symbol,
        asset=asset,
        base_asset = base_asset,
        direction=direction,
        asset_size=asset_size,
        base_asset_size = base_asset_size,
        fee=fee_total,
        fee_asset = fee_asset,
        fee_kcs = fee_kcs
    )

    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['order_id'])
    cute(do_nothing_stmt)
    db.session.commit()



def second_items():
    # complete = cute(db.select(Ledger).filter(Ledger.order_id == order_id)).scalars()
    # clist = LedgerSchema(many=True).dump(complete)
    #complete = cute(db.select(db.distinct(Ledger.biz_type))).scalars().all()
    #      sqlalchemy.schema.Column.notlike(other, escape=None)
    c = cute(db.select(db.distinct(Ledger.order_id)).filter(Ledger.biz_type.notlike('Exchange'))
                                      .filter(Ledger.biz_type.notlike('Cross Margin'))
                                      .filter(Ledger.biz_type.notlike('KCS Pay Fees'))
                                      .filter(Ledger.biz_type.notlike('Rewards'))
                                      .filter(Ledger.biz_type.notlike('Refunded Fees'))
                                      .filter(Ledger.biz_type.notlike('Transfer'))
                                      .filter(Ledger.biz_type.notlike('Deposit'))
                                      .filter(Ledger.biz_type.notlike('Withdrawal'))
                                      .filter(Ledger.biz_type.notlike('Isolated Margin'))
                                      ).scalars()
    for i in c:
        order_collate(i)


def date_to_integer():
    s = cute(db.select(Ledger)).scalars().all()
    
    for i in s:
        date = int(int(i.date) / 1000)
        if i.direction == 'in':
            size = i.size
        else:
            size = 0 - i.size
        
        insert_stmt = insert(LedgerSecond).values(
        id=i.id,
        order_id=i.order_id,
        date=date,
        acc_type=i.acc_type,
        biz_type=i.biz_type,
        symbol=i.symbol,
        asset=i.asset,
        direction=i.direction,
        size=size,
        fee=i.fee
        )

        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
        cute(do_nothing_stmt)
    
    db.session.commit()   
    
    
'''
order_sum
    merge fills to single order
        params
        - order_id

calls ledger table in database, finds unique asset names, sums up their size, assigns asset as main (mAsset) or base (bAsset)
    db calls
        - unique assets (should return 2 values, some may be 1 value for Refund transactions)
        - uniqe symbol (should return 1 value)
        - sum function

select asset, sum(asset_size)
from ledger_second_sum
where biz_type
like 
'Bank Card Deal'
'Deposit'
'Distribution'
'KuCoin Bonus'
'Open red envelope'
'Other rewards'
'Rewards'
'Send red envelope'
'Soft Staking Profits'
'Sub-account transfer'
'Transfer'
'Withdrawal'
'''
'''
def order_sum_old(order_id):
    
    assets = cute(db.select(db.distinct(Ledger.asset)).filter(Ledger.order_id == order_id)).scalars()
    symbol=count(order_id, 'symbol')
    acc_type=count(order_id, 'acc_type')
    bizType=count(order_id, 'bizType')
    size = get_size(order_id)
    
    l = cute(db.select(Ledger).filter(Ledger.order_id == order_id)).first()
    ls = LedgerSum()
    
    date = l[0].date
    
    
    ls.order_id=order_id
    ls.acc_type=acc_type
    ls.date=date
    ls.bizType=bizType
    ls.symbol=symbol

    for i in assets.all():
        # osum = cute(db.select(Ledger.order_id, db.func.sum(Ledger.size)).group_by(Ledger.order_id).filter(Ledger.order_id == order_id).filter(Ledger.asset == i)).first()
        if f'{i}-' in symbol:
            ls.asset=i
            ls.asset_size= size[i]
            ls.direction = cute(db.select(Ledger.direction).filter(Ledger.order_id == order_id, Ledger.symbol == symbol, Ledger.acc_type == acc_type)).scalar()
        elif f'-{i}' in symbol:
            ls.base_asset=i
            ls.base_asset_size=size[i]
        else:
            ls.fee_asset = i
            ls.fee = size[i]

    print(order_id)
    return ls
'''

def unique_orders():
    orders = cute(db.select(db.distinct(Ledger.order_id))).scalars()
    for i in orders:
        order_collate_test(i)


'''
Need to count number of items per acc_type and bizType,
Use the one with the most values
    or
if equal use most common values
'''

'''
GET UNIQUE VALUES
    Using SQLAlchemy Method
        osum = cute(db.select(Ledger.asset).filter(Ledger.order_id == "62d8971f0eac7e00018012af")).scalars()
        print(osum.unique().all())
    
    Using Postgres DISTINCT
        osum = cute(db.select(db.distinct(Ledger.asset)).filter(Ledger.order_id == "62d8971f0eac7e00018012af")).scalars()
        print(osum.all())
'''

'''
def get_job_by_id(id):
    # uses a JOIN query to select a customers data when their id is assigned to a job
    job_cust_info = cute(db.select(Customer.business_name, Customer.branch_name, Customer.contact_name,
                                   Customer.location, Jobcard.issue, Jobcard.comments, Jobcard.job_id)
                         .join_from(Customer, Jobcard).filter_by(job_id=id)).first()
    # deconstructs customer and job info returned from query
    bname, branch, cname, location, issue, comments, jid = job_cust_info

    # another JOIN query is made to get details about the equipment that is listed on the job card
    job_equip_info = cute(db.select(Equipment.serial_number, Equipment.make, Equipment.model,
                                    Equipment.manufacture_year, Equipment.cycle_count)
                          .join_from(Equipment, Jobcard).filter_by(job_id=id)).first()
    # deconstructs equipment info returned from query
    sn, make, model, mfy, cc = job_equip_info
    # pass all returned values in to very basic html to be displayed
    return update_card(jid, bname, branch, cname, make, mfy, sn, model, cc, issue)


def update_job(job_id, comments):
    print(comments)
    j = cute(db.select(Jobcard).filter(Jobcard.job_id == job_id)).scalar()
    print(j.issue)
    j.comments = comments
    j.completed = True
    db.session.commit()
    return f'<html style="background-color:black"><h1 style="color:white">Job Card Submitted!</h1> \
            {index_list()}</html>'


def new_card(cust_id, issue, machine, technician):
    tech = cute(db.select(Staff).filter(Staff.staff_id == technician)).scalar()
    cust = cute(db.select(Customer).filter(Customer.customer_id == cust_id)).scalar()
    equip = cute(db.select(Customer).filter(Equipment.serial_number == machine)).scalar()

    new_job = Jobcard(job_id=secrets.token_hex(3), issue=issue)

    tech.job_staff.extend([new_job])
    cust.job_customer.extend([new_job])
    equip.job_equipment.extend([new_job])
    db.session.commit()
    return f'<html style="background-color:black"><h1 style="color:white">Job Created</h1> \
            {index_list()}</html>'
            
            
bcrypt==4.0.1
certifi==2022.9.24
cffi==1.15.1
charset-normalizer==2.1.1
click==8.1.3
cryptography==38.0.3
Flask==2.2.2
Flask-Bcrypt==1.0.1
Flask-Dance==6.2.0
Flask-JWT-Extended==4.4.4
Flask-Login==0.6.2
flask-marshmallow==0.14.0
Flask-SQLAlchemy==3.0.2
greenlet==2.0.1
idna==3.4
itsdangerous==2.1.2
Jinja2==3.1.2
jsonify==0.5
MarkupSafe==2.1.1
marshmallow==3.18.0
marshmallow-sqlalchemy==0.28.1
oauthlib==3.2.2
packaging==21.3
psycopg2-binary==2.9.5
    pycparser==2.21
    PyJWT==2.6.0
    pyOpenSSL==22.1.0
    pyparsing==3.0.9
    python-dotenv==0.21.0
    requests==2.28.1
    requests-oauthlib==1.3.1
    six==1.16.0
SQLAlchemy==1.4.43
    - urllib3==1.26.12
    - URLObject==2.4.3
Werkzeug==2.2.2

'''