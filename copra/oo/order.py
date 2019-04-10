# -*- coding: utf-8 -*-
"""Order class for the Coinbase Pro platform.
"""

import asyncio
from decimal import Decimal, ROUND_CEILING
import uuid

from copra.fix.message import Message
from copra.fix.names import VALUES

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
        msg[54] = '2' if side == 'sell' else '1'
        
        order.product_id = product_id
        msg[55] = product_id
        
        order.id = None
        order.status = None
        order.filled_size = Decimal('0')
        order._executed_value = Decimal('0')
        order.last_fill = Decimal('0')
        order.fill_callback = lambda x, y: None
        order.done_callback = lambda x, y: None
        order.received = asyncio.Event()
        order.done = asyncio.Event()
        
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
            order.stop_price = None
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
            order.stop_price = None
            msg[40] = '1'
        
        if size:
            order.size = Decimal(str(size))
            order.funds = None
            msg[38] = str(order.size)
            
        if funds:
            order.funds = Decimal(str(funds))
            order.size = None
            msg[152] = str(order.funds)
            
        return (order, msg)


    @property
    def executed_value(self):
        return self._executed_value.quantize(Decimal('0.01'), rounding=ROUND_CEILING)


    @property
    def remaining(self):
        if (self.type == 'market' or self.type == 'stop market') and self.funds:
            return self.funds - self.executed_value
        return self.size - self.filled_size
    
        
    @property
    def avg_price(self):
        if not self.filled_size:
            avg = Decimal('0')
        else:
            avg = self.executed_value / self.filled_size
        return avg.quantize(Decimal('0.01'), rounding=ROUND_CEILING)

    
    def __str__(self):
        if self.type == 'market' or self.type == 'stop market':
            if self.size:
                size_price = '{} {}'.format(self.size, self.product_id)
            else:
                size_price = '${} {}'.format(self.funds, self.product_id)
        else:
            size_price = '{} {} @ ${:.2f}'.format(self.size, self.product_id, self.price )

        str_ = '{} {} {}'.format(self.type.upper(), self.side.upper(), size_price)
        if self.type == 'limit' or self.type == 'stop limit':
            str_ += ' ({})'.format(self.time_in_force)
        if self.stop_price:
            str_ += ' <stop: ${}>'.format(self.stop_price)
        
        str_ = '{:<76} [{}]\n'.format(str_, self.status[0].upper() if self.status else 'None')
        
        if not (self.status == 'new' or self.status == 'stopped' or self.status == 'rejected'):
            str_ += '-' * 80 + '\n'
            str_ += '     Filled: {:<11.8}\tRemaining: {:<11.8}\tLast: {:<11.8}\n'.format(
                   self.filled_size, self.remaining.normalize(), self.last_fill)
            str_ += ' Exec Value: ${:<10}\tAvg Price: ${}\n'.format(
                                            self.executed_value, self.avg_price)
        if self.status == 'rejected':
            str_ += '-' * 80 + '\n'
            str_ += 'Reject Reason: {}\n'.format(self.reject_reason)
            
        str_ += '-' * 80 + '\n'
        if self.id:
            str_ += '{:>80}'.format('ID: ' + self.id)
        else:
            str_ += '{:>80}'.format('Client OID: ' + self.client_oid)
        
        return str_
        
   
    def fix_update(self, msg):
        
        self.status = VALUES[39][msg[39]]
        
        if msg[150] == '0' or msg[150] == '7': # ExecType new or stopped
            self.id = msg[37]
            self.received.set()
            
        elif msg[150] == '8':       # ExecType rejected 
            self.id = msg[37]
            self.reject_reason = msg[58]
            self.received.set()
            self.done.set()
            
        elif msg[150] == '1':       # ExecType fill
            size = Decimal(msg[32])
            price = Decimal(msg[31])  
            self.filled_size += size
            self._executed_value += size * price
            self.last_fill = size
            self.fill_callback(size, price)
            
        elif msg[150] == '3':       # ExecType done
            self.done.set()
            self.done_callback(self.filled_size, self.executed_value)
            
        elif msg[150] == '4':       # ExecType canceled
            self.done.set()
            self.done_callback(self.filled_size, self.executed_value)
            