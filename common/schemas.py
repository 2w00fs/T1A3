from shared import db, ma


class Ledger(db.Model):
    __tablename__ = 'ledger'

    id = db.Column(db.String, primary_key=True)
    order_id = db.Column(db.String)
    date = db.Column(db.String)
    acc_type = db.Column(db.String)
    biz_type = db.Column(db.String)
    symbol = db.Column(db.String)
    asset = db.Column(db.String)
    direction = db.Column(db.String)
    size = db.Column(db.Float)
    fee = db.Column(db.Float)


class LedgerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'order_id', 'date', 'acc_type', 'biz_type', 'symbol', 'asset', 'direction', 'size', 'fee')


class FuturesTransactionHistory(db.Model):
    __tablename__ = 'futures_transaction_history'

    date = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    value = db.Column(db.Float, primary_key=True)
    fee = db.Column(db.Float)
    accountEquity = db.Column(db.Float)
    status = db.Column(db.String)
    remark = db.Column(db.String)
    offset = db.Column(db.Integer)
    asset = db.Column(db.String)


class FuturesTransactionHistorySchema(ma.Schema):
    class Meta:
        fields = ('date', 'type', 'value', 'fee', 'accountEquity', 'status',
                  'remark', 'offset', 'asset')


class FuturesLedgerDate(db.Model):
    __tablename__ = 'futures_ledger_date'
    
    id = db.Column(db.String, primary_key=True,)
    order_id = db.Column(db.String)
    date = db.Column(db.Integer)
    trade_type = db.Column(db.String)
    symbol = db.Column(db.String)
    direction = db.Column(db.String)
    size = db.Column(db.Integer)
    settle_asset = db.Column(db.String)
    value = db.Column(db.Float)
    price = db.Column(db.Float)
    fee_currency = db.Column(db.String)
    fee = db.Column(db.Float)


class FuturesLedgerDateSchema(ma.Schema):
    class Meta:
        fields = ('id', 'order_id', 'date', 'trade_type', 'symbol', 'direction', 'size',
                  'settle_asset', 'value', 'price', 'fee_currency', 'fee')


class FuturesFundingDate(db.Model):
    __tablename__ = 'futures_funding_date'
    
    id = db.Column(db.String, primary_key=True)
    symbol = db.Column(db.String)
    date = db.Column(db.Integer)
    fundingRate = db.Column(db.Float)
    markPrice = db.Column(db.Float)
    positionQty = db.Column(db.Integer)
    positionCost = db.Column(db.Float)
    funding = db.Column(db.Float)
    settle_currency = db.Column(db.String)


class FuturesFundingDateSchema(ma.Schema):
    class Meta:
        fields = ('id', 'symbol', 'date', 'fundingRate', 'markPrice', 'positionQty',
                  'positionCost', 'funding', 'settle_currency')


class FuturesOrderIdDate(db.Model):
    __tablename__ = 'futures_order_id_date'
    
    id = db.Column(db.String, primary_key=True)
    date = db.Column(db.Integer)
    symbol = db.Column(db.String)
    type = db.Column(db.String)
    side = db.Column(db.String)
    value = db.Column(db.Float)
    size = db.Column(db.Float)
    leverage = db.Column(db.Integer)
    cost = db.Column(db.Float)


class FuturesOrderIdDateSchema(ma.Schema):
    class Meta:
        fields = (
                    'id', 'date', 'symbol', 'type', 'side', 'value',
                    'size', 'cost', 'leverage'
                )


class FuturesLedger(db.Model):
    __tablename__ = 'futures_ledger'
    
    id = db.Column(db.String, primary_key=True,)
    order_id = db.Column(db.String)
    date = db.Column(db.String)
    trade_type = db.Column(db.String)
    symbol = db.Column(db.String)
    direction = db.Column(db.String)
    size = db.Column(db.Integer)
    settle_asset = db.Column(db.String)
    value = db.Column(db.Float)
    price = db.Column(db.Float)
    fee_currency = db.Column(db.String)
    fee = db.Column(db.Float)


class FuturesLedgerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'order_id', 'date', 'trade_type', 'symbol', 'direction', 'size',
                  'settle_asset', 'value', 'price', 'fee_currency', 'fee')


class FuturesFunding(db.Model):
    __tablename__ = 'futures_funding'
    
    id = db.Column(db.String, primary_key=True)
    symbol = db.Column(db.String)
    date = db.Column(db.String)
    fundingRate = db.Column(db.Float)
    markPrice = db.Column(db.Float)
    positionQty = db.Column(db.Integer)
    positionCost = db.Column(db.Float)
    funding = db.Column(db.Float)
    settleCurrency = db.Column(db.String)


class FuturesFundingSchema(ma.Schema):
    class Meta:
        fields = ('id', 'symbol', 'date', 'fundingRate', 'markPrice', 'positionQty',
                  'positionCost', 'funding', 'settleCurrency')


class FuturesTHist(db.Model):
    __tablename__ = 'futures_thist'

    #id = db.Column(db.String, primary_key=True, server_default='gen_random_uuid()')
    time = db.Column(db.String, primary_key=True)
    type = db.Column(db.String)
    amount = db.Column(db.Float, primary_key=True)
    fee = db.Column(db.Float)
    accountEquity = db.Column(db.Float)
    status = db.Column(db.String)
    remark = db.Column(db.String)
    offset = db.Column(db.Integer)
    currency = db.Column(db.String)


class FuturesTHistSchema(ma.Schema):
    class Meta:
        fields = ('time', 'type', 'amount', 'fee', 'accountEquity', 'status',
                  'remark', 'offset', 'currency')


class LedgerSecond(db.Model):
    __tablename__ = 'ledger_second'

    id = db.Column(db.String, primary_key=True)
    order_id = db.Column(db.String)
    date = db.Column(db.Integer)
    acc_type = db.Column(db.String)
    biz_type = db.Column(db.String)
    symbol = db.Column(db.String)
    asset = db.Column(db.String)
    direction = db.Column(db.String)
    size = db.Column(db.Float)
    fee = db.Column(db.Float)


class LedgerSecondSchema(ma.Schema):
    class Meta:
        fields = ('id', 'order_id', 'date', 'acc_type', 'biz_type', 'symbol', 'asset', 'direction', 'size', 'fee')
        

class Prices(db.Model):
    __tablename__ = 'prices'

    date = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String, primary_key=True)
    price = db.Column(db.Float)


class PricesSchema(ma.Schema):
    class Meta:
        fields = ('date', 'asset', 'price')


class LedgerPrices(db.Model):
    __tablename__ = 'ledger_prices'

    id = db.Column(db.String, primary_key=True)
    order_id = db.Column(db.String)
    date = db.Column(db.Integer)
    date_utc = db.Column(db.String)
    acc_type = db.Column(db.String)
    biz_type = db.Column(db.String)
    symbol = db.Column(db.String)
    asset = db.Column(db.String)
    asset_type = db.Column(db.String)
    direction = db.Column(db.String)
    size = db.Column(db.Float)
    fee = db.Column(db.Float)
    price_usdt = db.Column(db.Float)
    value_usdt = db.Column(db.Float)
    fee_usdt = db.Column(db.Float)
    fy = db.Column(db.Integer)


class LedgerPricesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'order_id', 'date', 'date_utc', 'acc_type', 'biz_type', 'symbol', 'asset',
                  'asset_type', 'direction', 'size', 'fee', 'price_usdt', 'value_usdt', 'fee_usdt', 'fy')
        

class FuturesOrderId(db.Model):
    __tablename__ = 'futures_order_id'
    
    id = db.Column(db.String, primary_key=True)
    symbol = db.Column(db.String)
    type = db.Column(db.String)
    side = db.Column(db.String)
    price = db.Column(db.Float)
    size = db.Column(db.String)
    value = db.Column(db.String)
    dealValue = db.Column(db.String)
    dealSize = db.Column(db.String)
    stp = db.Column(db.String)
    stop = db.Column(db.String)
    stopPriceType = db.Column(db.String)
    stopTriggered = db.Column(db.Boolean)
    stopPrice = db.Column(db.Float)
    timeInForce = db.Column(db.String)
    postOnly = db.Column(db.Boolean)
    hidden = db.Column(db.Boolean)
    iceberg = db.Column(db.Boolean)
    leverage = db.Column(db.String)
    forceHold = db.Column(db.Boolean)
    closeOrder = db.Column(db.Boolean)
    visibleSize = db.Column(db.String)
    clientOid = db.Column(db.String)
    remark = db.Column(db.String)
    tags = db.Column(db.String)
    isActive = db.Column(db.Boolean)
    cancelExist = db.Column(db.Boolean)
    createdAt = db.Column(db.String)
    updatedAt = db.Column(db.String)
    endAt = db.Column(db.String)
    orderTime = db.Column(db.String)
    settleCurrency = db.Column(db.String)
    status = db.Column(db.String)
    filledSize = db.Column(db.String)
    filledValue = db.Column(db.String)
    reduceOnly = db.Column(db.Boolean)


class FuturesOrderIdSchema(ma.Schema):
    class Meta:
        fields = (
                    'id', 'symbol', 'type', 'side', 'price', 'size',
                    'value', 'dealValue', 'dealSize', 'stp', 'stop',
                    'stopPriceType', 'stopTriggered', 'stopPrice',
                    'timeInForce', 'postOnly', 'hidden', 'iceberg',
                    'leverage', 'forceHold', 'closeOrder', 'visibleSize', 
                    'clientOid', 'remark', 'tags', 'isActive', 'cancelExist', 
                    'createdAt', 'updatedAt', 'endAt', 'orderTime', 'settleCurrency',  
                    'status',  'filledSize', 'filledValue', 'reduceOnly'
                )


'''
    id = db.Column(db.String, primary_key=True)
    order_id = db.Column(db.String, db.ForeignKey('customer.customer_id'))
    date = db.Column(db.Integer, db.ForeignKey('staff.staff_id'))
    acc_type = db.Column(db.String, db.ForeignKey('equipment.serial_number'))
'''
