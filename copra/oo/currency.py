from decimal import Decimal 

class Currency():
    
    def __init__(self, rest_resp):
        self.id = rest_resp['id']
        self.name = rest_resp['name']
        self.type = rest_resp['details']['type']
        min_size = rest_resp['min_size'].rstrip('0')
        if min_size.endswith('.'):
            min_size = min_size[:-1]
        self.min_size = Decimal(min_size)

    def __str__(self):
        name_id = '{} [{}]'.format(self.name, self.id)
        return '{:<28}\tType: {}\tMin size: {:f}'.format(name_id, self.type, self.min_size)