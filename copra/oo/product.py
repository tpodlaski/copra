from decimal import Decimal

class Product():
    def __init__(self, rest_resp, base_currency, quote_currency):
        self.id = rest_resp['id']
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.quote_increment = Decimal(rest_resp['quote_increment'])
        self.max_order_size = Decimal(rest_resp['base_max_size'])
        self.min_order_size = Decimal(rest_resp['base_min_size'])
        self.max_funds = Decimal(rest_resp['max_market_funds'])
        self.min_funds = Decimal(rest_resp['min_market_funds'])