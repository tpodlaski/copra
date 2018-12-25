# -*- coding: utf-8 -*-
"""Order class for the Coinbase Pro platform.
"""

import asyncio
from decimal import Decimal
import uuid

from copra.message import Message

class Order:
    """Base order class.
    """
    
    @classmethod
    def _create(cls, key, seq_num, side, product_id):
        """Factory to create the base of an order and FIX message.
        
        Creates an order and FIX message with the attributes and fields
        that are common to both limit and market orders.
        
        :param str key: The API key of the client generating the message.
        
        :param int seq_num: The sequence number of the message as tracked by
            the client.

        :param str side: Either buy or sell
        
        :param str product_id: The product id to be bought or sold.
        
        
        returns: A tuple consisting of the Order object and the FIX message
            object to place the order.
            
        :raises ValueError:
        
            * The side is not either "buy" or "sell".
        """
        if side not in ('buy', 'sell'):
            raise ValueError("Invalid side: {}. Must be either buy or sell".format(side))       

        order = cls()
        msg = Message(key, seq_num, 'D', {22: '1'})
        
        order.client_oid = str(uuid.uuid4())
        msg[11] = order.client_oid
        
        order.side = side
        msg[54] = '1' if side == 'sell' else '2'
        
        order.product_id = product_id
        msg[55] = product_id
        
        order.received = asyncio.Event()
        
        return order, msg

    
    @classmethod
    def limit_order(cls, key, seq_num, side, product_id, size, price, 
                                          time_in_force='GTC', stop_price=None):
        """
        Factory method to create a new limit order.
        
        Returns a new limit order and the FIX message to place it.

        :param str key: The API key of the client generating the message.
        
        :param int seq_num: The sequence number of the message as tracked by
            the client.

        :param str side: Either buy or sell
        
        :param str product_id: The product id to be bought or sold.

        :param float size: The quantity of the cryptocurrency to buy or sell. 
            This parameter may also be a string.
            
        :param float price: The price the order is to be executed at. This 
            paramater may also be a string to avoid floating point issues.
            
        :param str time_in_force: (optional) Time in force policies provide 
            guarantees about the lifetime of an order. There are four 
            policies: GTC (good till canceled), IOC (immediate or cancel), 
            FOK (fill or kill), PO (post only). The default is GTC.
        
        :param float stop_price: (optional) The trigger price for stop orders. 
            This may also be a string. The default is None.

        :returns: A tuple consisting of the Order object and the FIX message
            object to place the order.
            
        :raises ValueError:
        
            * The side is not either "buy" or "sell".
            * The time_in_force is not GTC, IOC, FOK, or PO.
            * A stop_order has post_only set to True
        """

        if time_in_force not in ('GTC', 'IOC', 'FOK', 'PO'):
            raise ValueError('time_in_force must be GTC, IOC, FOK, or PO.')
            
        if stop_price and time_in_force == 'PO':
            raise ValueError('Stop orders cannot be Post Only.')
            
        order, msg = cls._create(key, seq_num, side, product_id)

        if stop_price:
            order.type = 'stop limit'
            msg[40] = '4'
            order.stop_price = Decimal(str(stop_price))
            msg[99] = str(order.stop_price)
            
        else:
            order.type = 'limit'
            msg[40] = '2'
            
        order.size = Decimal(str(size))
        msg[38] = str(order.size)
        
        order.price = Decimal(str(price))
        msg[44] = str(order.price)

        order.time_in_force = time_in_force
        msg[59] = {'GTC': '1', 'IOC': '3', 'FOK': '4', 'PO': 'P'}[order.time_in_force]
              
        return (order, msg)

       
    @classmethod
    def market_order(cls, key, seq_num, side, product_id, size=None, funds=None, 
                                                               stop_price=None):
        """Factory method to create a new market order.
        
        Returns a new market order and the FIX message to place it.

        :param str key: The API key of the client generating the message.
        
        :param int seq_num: The sequence number of the message as tracked by
            the client.

        :param str side: Either buy or sell
        
        :param str product_id: The product id to be bought or sold.

        :param float size: The quantity of the cryptocurrency to buy or sell. 
            Either size or funds must be set for a market order but not both.  
            This may also be a string. The default is None. 

        :param float funds: This is the amount of quote currency to be used for 
            a purchase (buy) or the amount to be obtained from a sale (sell). 
            Either size or funds must be set for a market order but not both. 
            This may also be a string. The default is None.

        :param float stop_price: (optional) The trigger price for stop orders. 
            Required if stop is set. This may also be a string. The default is 
            None.
            
        :returns: A tuple consisting of the Order object and the FIX message
            object to place the order.
            
        :raises ValueError:
        
            * The side is not either "buy" or "sell".
            * Neither size nor funds is set.
            * Both size and funds are set
        """
            
        if not (size or funds):
                raise ValueError('Market orders must have size or funds set.')
                
        if size and funds:
                raise ValueError("Market orders can't have both size and funds set.")
                
        order, msg = cls._create(key, seq_num, side, product_id)

        if stop_price:
            order.type = 'stop market'
            msg[40] = '3'
            order.stop_price = Decimal(str(stop_price))
            msg[99] = str(order.stop_price)
            
        else:
            order.type = 'market'
            msg[40] = '1'
        
        if size:
            order.size = Decimal(str(size))
            msg[38] = str(order.size)
            
        if funds:
            order.funds = Decimal(str(funds))
            msg[152] = str(order.funds)
            
        return (order, msg)
    
    def fix_update(self,  msg):
        pass
        
    #     if msg[150] == '0':         #ExcecType new
    #         self.received.set()
