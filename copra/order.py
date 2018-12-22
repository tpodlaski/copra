# -*- coding: utf-8 -*-
"""FIX message class for the Coinbase Pro platform.
"""

import uuid

class Order:
    
    def __init__(self):
        self.client_oid = str(uuid.uuid4())