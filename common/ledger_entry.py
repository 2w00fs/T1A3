import json


class LedgerEntry:
    def __init__(self, data):
        self.data = self.parse_data(data)


    def parse_symbol(self, context, biz, cur):
        dw = ('Bank Card Deal', 'Deposit', 'Withdrawal')
        if 'symbol' in context.keys():
            return context['symbol']

        if biz in dw:
            return f"{cur}-USD"
        
        return f"{cur}-{cur}"
            

    def parse_orderid(self, context, id):
        if 'orderId' in context.keys():
            return context['orderId']
        if 'loanRepayOrderNo' in context.keys():
            return context['loanRepayOrderNo']
        if 'loanBorrowOrderNo' in context.keys():
            return context['loanBorrowOrderNo']

        return id


    def parse_data(self, d):
        id = d['id']
        createdAt = d['createdAt']
        accountType = d['accountType']
        bizType = d['bizType']
        currency = d['currency']
        direction = d['direction']
        amount = float(d['amount'])
        fee = float(d['fee'])
        n = d['context']
        try:
            context = json.loads(n)
        except:
            print(f'No Context {n}')
            context = {"no_data" : "no_data"} 
        
        symbol = self.parse_symbol(context, bizType, currency)            
        orderId = self.parse_orderid(context, id)
    
        return {
            'id': id,
            'order_id': orderId,
            'date': createdAt,
            'acc_type': accountType,
            'bizType': bizType,
            'symbol': symbol,
            'asset': currency,
            'direction': direction,
            'size': amount,
            'fee': fee
            }
