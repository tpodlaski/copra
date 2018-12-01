========
Examples
========

Market Order
------------

The following example places a market order for the minimum amount of BTC-USD possible and then follows up by placing a stop loss market order at a stop price that is $300 less than the original order price.

This is a contrived example that makes some assumptions and does not count for every contingency, but it does use several ``copra.rest.Client`` methods. The steps that is follows are:

    1. Check to see what the minimum BTC-USD order size is. (:meth:`products() <copra.rest.Client.products>`)
    2. Check to see what the available USD balance is. (:meth:`accounts() <copra.rest.Client.accounts>`)
    3. Check for the price of the last BTC-USD trade. (:meth:`ticker() <copra.rest.Client.ticker>`)
    4. Place a market order. (:meth:`market_order() <copra.rest.Client.market_order>`)
    5. Check the order status. (:meth:`get_order() <copra.rest.Client.get_order>`)
    6. Place a stop loss market order. (:meth:`market_order() <copra.rest.Client.market_order>`)
    
 
