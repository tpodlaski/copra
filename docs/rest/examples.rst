========
Examples
========

Market Order
------------

The following example places a market order for the minimum amount of BTC-USD possible and then follows up by placing a stop loss market order at a stop price that is $300 less than the original order price.

This is a contrived example that makes some assumptions and does not count for every contingency, but it does use several ``copra.rest.Client`` methods. The steps that is follows are:

    1. Check to see what the minimum BTC-USD order size is. :meth:`products() <copra.rest.Client.products>`
    2. Check to see what the available USD balance is. :meth:`accounts() <copra.rest.Client.accounts>`
    3. Check for the price of the last BTC-USD trade. :meth:`ticker() <copra.rest.Client.ticker>`
    4. Place a market order. :meth:`market_order() <copra.rest.Client.market_order>`
    5. Check the order status. :meth:`get_order() <copra.rest.Client.get_order>`
    6. Place a stop loss market order. :meth:`market_order() <copra.rest.Client.market_order>`
    
.. code:: python

# rest_example.py

import asyncio

from copra.rest import APIRequestError, Client

KEY = YOUR_KEY
SECRET = YOUR_SECRET
PASSPHRASE = YOUR_PASSPHRASE

loop = asyncio.get_event_loop()
    

async def run():
    
    async with Client(loop, auth=True, key=KEY, secret=SECRET, 
                      passphrase=PASSPHRASE) as client:
        
        # Determine the smallest size order of BTC-USD possible.
        products = await client.products()
        for product in products:
            if product['id'] == 'BTC-USD':
                min_btc_size = float(product['base_min_size'])
                break
            
        print('\nMinimum BTC-USD order size: {}\n'.format(min_btc_size))
                
        
        # Get the amount of USD you have available. This assumes you don't 
        # know the account id of your Coinbase Pro USD account. If you did,
        # you could just call client.account(account_id) to retrieve the 
        # amount of USD available.
        accounts = await client.accounts()
        for account in accounts:
            if account['currency'] == 'USD':
                usd_available = float(account['available'])
                
        print('USD available: ${}\n'.format(usd_available))
        
        
        # Get the last price of BTC-USD
        btc_usd_ticker = await client.ticker('BTC-USD')
        btc_usd_price = float(btc_usd_ticker['price'])
        
        print("Last BTC-USD price: ${}\n".format(btc_usd_price))
        
        
        # Verify you have enough USD to place the minimum BTC-USD order
        usd_needed = btc_usd_price * min_btc_size
        if usd_available < usd_needed:
            print('Sorry, you need ${} to place the minimum BTC order'.format(
                                                                    usd_needed))
            return
        
        
        # Place a market order for the minimum amount of BTC
        try:
            order = await client.market_order('buy', 'BTC-USD', 
                                              size=min_btc_size)
            order_id = order['id']
            
            print('Market order placed.')
            print('\tOrder id: {}'.format(order_id))
            print('\tSize: {}\n'.format(order['size']))
            
        except APIRequestError as e:
            print(e)
            return
        
        
        # Wait a few seconds just to make sure the order completes.
        await asyncio.sleep(5)
        
        
        # Check the order status
        order = await client.get_order(order_id)
        
        
        # Assume the order is done and not rejected.
        order_size = float(order['filled_size'])
        order_executed_value = float(order['executed_value'])
        
        # We could check the fills to get the price(s) the order was
        # executed at, but we'll just use the average price.
        order_price = order_size * order_executed_value
        
        print('{} BTC bought at ${:.2f} for ${:.2f}\n'.format(order_size,
                                                          order_price, 
                                                          order_executed_value))
                                             
        
        # Place a stop loss market order at $300 below the order price.
        stop_price = '{:.2f}'.format(6680.55 - 300)
        sl_order = await client.market_order('sell', 'BTC-USD', order_size, 
                                             stop='loss', stop_price=stop_price)
                                 
        print('Stop loss order placed.') 
        print('\tOrder id: {}'.format(sl_order['id']))
        print('\tSize: {}'.format(sl_order['size']))
        print('\tStop price: ${:.2f}\n'.format(float(sl_order['stop_price'])))
        
        await client.cancel_all(stop=True)

loop.run_until_complete(run())

loop.close()
