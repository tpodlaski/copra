from decimal import Decimal, ROUND_FLOOR

class Account():
    def __init__(self, rest_resp, currency):
        self.id = rest_resp['id']
        self.currency = currency
        self.balance = Decimal(rest_resp['balance'])
        self.hold = Decimal(rest_resp['hold'])
        self.profile_id = rest_resp['profile_id']

     
    @property
    def available(self):
        return (self.balance - self.hold).quantize(self.currency.min_size, rounding=ROUND_FLOOR)

    def formatted(self, value, width):
        l = '{:f}'.format(self.currency.min_size).split('.')
        if len(l) < 2:
            precision = 0
        else:
            precision = len(l[1])
        format_str = '{:' + str(width) + '.' + str(precision) + 'f}'
        return format_str.format(value)  
            
    
    def __eq__(self, other):
        return (self.id == other.id and
                self.currency == other.currency and
                self.balance == other.balance and
                self.available == other.available and
                self.hold == other.hold and
                self.profile_id == other.profile_id)

        
    def __repr__(self):
        rep  = f'Account: {self.currency.id}\tID: {self.id}\n'
        rep += f'-----------------------------------------------------------\n'
        rep += f'Balance\t\tAvailable\tOn Hold\n'
        rep += f'{self.balance:.8f}\t{self.available:.8f}\t{self.hold:.8f}\n'
        rep += f'-----------------------------------------------------------\n'
        return rep