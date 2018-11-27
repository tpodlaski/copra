========
Examples
========

Ticker
------

The following code, saved as ``ticker.py``, when run from the command line
prints a running ticker for the product ID supplied as an argument to the
script.

.. code:: python

    #!/usr/bin/env python3
    
    import asyncio
    from datetime import datetime
    import sys
    
    from copra.websocket import Channel, Client
    
    class Tick:
       
        def __init__(self, tick_dict):
            self.product_id = tick_dict['product_id']
            self.best_bid = float(tick_dict['best_bid'])
            self.best_ask = float(tick_dict['best_ask'])
            self.price = float(tick_dict['price'])
            self.side = tick_dict['side']
            self.size = float(tick_dict['last_size'])
            self.time = datetime.strptime(tick_dict['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            
        @property
        def spread(self):
            return self.best_ask - self.best_bid
    
        def __repr__(self):
            
            rep  = "{}\t\t\t\t   {}\n".format(self.product_id, self.time)
            rep += "=============================================================\n"
            rep += "   Price: ${:.2f}\t    Size: {:.8f}\t  Side: {: >5}\n".format(self.price, self.size, self.side)
            rep += "Best ask: ${:.2f}\tBest bid: ${:.2f}\tSpread: ${:.2f}\n".format(self.best_ask, self.best_bid, self.spread)
            rep += "=============================================================\n"
            return rep
            
    
    class Ticker(Client):
        
        def on_message(self, message):
            if message['type'] == 'ticker' and 'time' in message:
                tick = Tick(message)
                print(tick, "\n\n")
    
    product_id = sys.argv[1]
    
    loop = asyncio.get_event_loop()
    
    channel = Channel('ticker', product_id)
    
    ticker = Ticker(loop, channel)
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ticker.close())
        loop.close()
        
Streaming a ticker for LTC-USD:

.. code:: bash

    $ ./ticker.py LTC-USD
    
    LTC-USD                            2018-07-12 21:40:38.501000
    =============================================================
       Price: $75.73            Size: 0.22134981      Side:   buy
    Best ask: $75.73        Best bid: $75.67        Spread: $0.06
    =============================================================
     
    
    
    LTC-USD                            2018-07-12 21:40:38.501000
    =============================================================
       Price: $75.74            Size: 0.29362708      Side:   buy
    Best ask: $75.74        Best bid: $75.67        Spread: $0.07
    =============================================================
     
    
    
    LTC-USD                            2018-07-12 21:40:41.202000
    =============================================================
       Price: $75.68            Size: 0.19211000      Side:  sell
    Best ask: $75.74        Best bid: $75.68        Spread: $0.06
    =============================================================
     
    
    
    LTC-USD                            2018-07-12 21:41:09.452000
    =============================================================
       Price: $75.71            Size: 0.63097536      Side:   buy
    Best ask: $75.71        Best bid: $75.68        Spread: $0.03
    =============================================================
     
    ^C
    $
