# -*- coding: utf-8 -*-
"""Asynchronous FIX client for the Coinbase Pro platform.
"""

import asyncio
import base64
import hashlib
import hmac
import os
import ssl
import time


URL = 'fix.pro.coinbase.com:4198'
SANDBOX_URL = 'fix-public.sandbox.pro.coinbase.com:4198'

CERT_FILE = os.path.join(os.path.dirname(__file__), 'certs', 
                                                    'fix.pro.coinbase.com.pem')
SANDBOX_CERT_FILE = os.path.join(os.path.dirname(__file__), 'certs', 
                                      'fix-public.sandbox.pro.coinbase.com.pem')


class Message():
    """Base class for FIX messages.
    """

    def __init__(self, key, seq_num, msg_type):
        """Initialize the Message object
        
        :param str key: The API key of the client generating the message.
        
        :param int seq_num: The sequence number of the message as tracked by
            the client.
        
        :param str msg_type: The type field of the message. It /should/ be a
            str but since many are ints, it will accept an int and convert it
            to a str.
        """
        
        self.dict = { 8: 'FIX.4.2',
             35: str(msg_type),
             49: key,
             56: 'Coinbase',
             34: seq_num }


    def __len__(self):
        len_ = 0
        for key in self.dict.keys() - {8}:
            len_ += len('{}={}'.format(key, self.dict[key])) + 1
        return len_


    def __repr__(self):
        keys = [8, 9, 35] + list(self.dict.keys() - {8, 9, 35}) + [10]
        rep = ''.join(['{}={}{}'.format(key, self[key], chr(1)) for key in keys])
        return rep


    def __bytes__(self):
        return self.__repr__().encode('ascii')
        

    def checksum(self):
        s = ''.join(['{}={}{}'.format(key, self[key], chr(1)) for key in self.dict.keys() | {9}])
        ord_sum = sum([ord(char) for char in s]) % 256
        return str(ord_sum).zfill(3)    
 
    
    def __getitem__(self, key):
        if key == 9:
            return len(self)
        if key == 10:
            return self.checksum()
        return self.dict[key]

        
    def __setitem__(self, key, value):
        if key in (9, 10):
            raise KeyError('Key {} may not be manually set.'.format(key))
        self.dict[key] = value
        
    
    def __delitem__(self, key):
        del(self.dict[key])

    
    def __contains__(self, item):
        if item in (9, 10):
            return True
        return item in self.dict
        
        
    def __eq__(self, other):
        return self.dict == other.dict
        
        
class LoginMessage(Message):
    """FIX login message.
    """
    
    def __init__(self, key, secret, passphrase, seq_num, send_time=None):
        """ Initialize the login message.
        
        :param str key: The API key of the client generating the message.
        
        :param str secret: The API key secret.
        
        :param str passphrase: The API key passphrase.
        
        :param int seq_num: The sequence number of the message as tracked by
            the client.
        
        :param str send_time: For testing purposes only
        
        """
        super().__init__(key, seq_num, 'A')
        
        if not send_time:
            send_time = time.time()
        
        self[52] = send_time       #SendingTime, Time of message transmission
        self[98] = 0               #EncryptMethod, 0 = None/other
        self[108] = 30             #HeartBtInt, Heartbeat interval in seconds
        self[554] = passphrase     #Password, Client API passphrase
        self[8013] = 'S'           #CancelOrdersOnDisconnect, 
                                   #  Y: Cancel all open orders for the 
                                   #     current profile
                                   #  S: Cancel open orders placed during 
                                   #     session
                                   
        #message signature
        keys = [52, 35, 34, 49, 56]
        s = chr(1).join([str(self[key]) for key in keys] + [passphrase]).encode('utf-8')
        hmac_key  = base64.b64decode(secret)
        signature = hmac.new(hmac_key, s, hashlib.sha256)
        sign_b64  = base64.b64encode(signature.digest()).decode()
        self[96] = sign_b64    


class LogoutMessage(Message):
    """FIX logout message.
    """
    
    def __init__(self, key, seq_num):
        """Initialize the LogoutMessage object
        
        :param str key: The API key of the client generating the message.
        
        :param int seq_num: The sequence number of the message as tracked by
            the client.
        """
        
        super().__init__(key, seq_num, '5')
    

class HeartbeatMessage(Message):
    """A simple heartbeat message.
    """
    
    def __init__(self, key, seq_num, test_req_id=None):
        """Initialize the heartbeat message.
        
        :param str key: The API key of the client generating the message.
        
        :param int seq_num: The sequence number of the message as tracked by
            the client.
        
        :param str test_req_id: (optional) The test request id if there was one 
            to initiate the heartbeat.
        """
        
        super().__init__(key, seq_num, '0')
        
        if test_req_id:
            self[112] = test_req_id
            
            
class LimitOrderMessage(Message):
    """A limit/stop limit order message.
    """
    
    def __init__(self, key, seq_num, side, product_id, price, size,
                 time_in_force='GTC', stop_price=None, client_oid=None):
        """Initialize the limit order message.
        
        :param str key: The API key of the client generating the message.
    
        :param int seq_num: The sequence number of the message as tracked by
            the client.
    
        :param str side: Either buy or sell
    
        :param str product_id: The product id to be bought or sold.
        
        :param float price: The price the order is to be executed at. This 
            paramater may also be a string to avoid floating point issues.
        
        :param float size: The quantity of the cryptocurrency to buy or sell. 
            This parameter may also be a string.
            
        :param str time_in_force: (optional) Time in force policies provide 
            guarantees about the lifetime of an order. There are four 
            policies: GTC (good till canceled), IOC (immediate or cancel), 
            FOK (fill or kill), PO (post only). The default is GTC.
            
        :param float stop_price: (optional) The trigger price for stop orders. 
            This may also be a string. The default is None.
            
        :param str client_oid: (optional) A self generated UUID to identify the 
            order. The default is None.
        """
        
        super().__init__(key, seq_num, 'D')
         
        self[22] = 1                            #22  HandlInst, Must be 1
        self[54] = 1 if side == 'sell' else 2   #54  Side, 1 to buy or 2 to sell
        self[55] = product_id                   #55  Symbol, E.g. BTC-USD
        self[44] = price                        #44  Price, Limit price
        self[38] = size                         #38  OrderQty, Order size in base units
        self[59] = {'GTC': 1, 'IOC': 3, 'FOK': 4, 'PO': 'P'}[time_in_force] #59  TimeInForce
        if stop_price:
            self[40] = 4                        #40  OrdType, 4 for stop limit
            self[99] = stop_price               #99  StopPx, Stop price for order.
        else:
            self[40] = 2                        #40  OrdType, 2 for limit
        if client_oid:
            self[11] = client_oid               #11  ClOrdID, UUID selected by client to identify the order


class MarketOrderMessage(Message):
    """A market/stop market order message.
    """
    
    def __init__(self, key, seq_num, side, product_id, size=None, funds=None,
                                           stop_price=None, client_oid=None):
        """Initialize the market order message.
        
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
            This may also be a string. The default is None.
            
        :param str client_oid: (optional) A self generated UUID to identify the 
            order. The default is None.
        """
 
        super().__init__(key, seq_num, 'D')
         
        self[22] = 1                            #22  HandlInst, Must be 1
        self[54] = 1 if side == 'sell' else 2   #54  Side, 1 to buy or 2 to sell
        self[55] = product_id                   #55  Symbol, E.g. BTC-USD
        
        if size:
            self[38] = size                     #38  OrderQty, Order size in base units
            
        if funds:
            self[152] = funds                   #152 CashOrderQty, Order size in quote units
             
        if stop_price:
            self[40] = 3                        #40  OrdType, 3 for stop market
            self[99] = stop_price               #99  StopPx, Stop price for order
        else:
            self[40] = 1                        #40  OrdType, 1 for market
       
        if client_oid:
            self[11] = client_oid               #11  ClOrdID, UUID selected by client to identify the order


class CancelMessage(Message):
    """Message to cancel a single order.
    """
    
    def __init__(self, key, seq_num, order_id=None, client_oid=None):
        """Initialize a cancel message.
        
        :param str key: The API key of the client generating the message.
    
        :param int seq_num: The sequence number of the message as tracked by
            the client.
        
        :param str order_id: (optional) The final id of the order as assigned
            by Coinbase. Either this or client_oid must be provided.
            
        :param str client_oid: (optional) The user generated id for the order 
            when it was placed. Either this or the order_id must be provided.
            
        .. note:: Use of the client_oid is not available after reconnecting or 
            starting a new session. You should use the order_id obtained via the 
            execution report once available.
        """
        
        super().__init__(key, seq_num, 'F')
        
        if client_oid:
            self[11] = client_oid               #11	ClOrdID	UUID selected by client for the order
        else:
            self[37] = order_id                 #37  OrderID, OrderID from the ExecutionReport with OrdStatus=New (39=0)
            
     
class Client(asyncio.Protocol):
    """Asynchronous FIX client for Coinbase Pro"""
    
    def __init__(self, loop, key, secret, passphrase, url=URL, 
                cert_file=CERT_FILE, max_connect_attempts=5, connect_timeout=10,
                reconnect=True):
        """FIX client initialization.
        
        :param loop: The asyncio loop that the client runs in.
        :type loop: asyncio loop
 
        :param str key: The API key to use for authentication. 

        :param str secret: The secret string for the API key used for
            authenticaiton.
            
        :param str passphrase: The passphrase for the API key used for 
            authentication.
            
        :param str url: (optional) The url of the FIX server. This should 
            include the port but not the protocol.
            
        :param str cert_file: (optional) The path to the ssl certificate for
            the Coinbase Pro FIX server. The default is
            './certs/fix.pro.coinbase.com.pem'. Certificates for both the live
            server and sandbox server are already installed in the `certs` 
            directory.
            
        :param int max_connect_attempts: (optional) The number of time to 
            attempt connecting to the FIX server before giving up. The default
            is 5.
            
        :param int connect_timeout: (optional) The time in seconds to wait while
            connecting to the FIX server before timing out. The default is 10.
        
        :param bool reconnect: (optional) Reconnect to the FIX server if the
            connection is lost but not explicitly closed by the client. The
            default is True.
        """
        self.loop = loop
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.url = url
        
        self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        self.ssl_context.load_verify_locations(cert_file)
        
        self.max_connect_attempts = max_connect_attempts
        self.connect_timeout = connect_timeout
        self.reconnect = reconnect
        
        self.seq_num = 0
        
        self.connected = asyncio.Event()
        self.disconnected = asyncio.Event()
        self.disconnected.set()
        
        self.logged_in = asyncio.Event()
        self.logged_out = asyncio.Event()
        self.logged_out.set()
        
        self.is_closing = False

        self.keep_alive_task = None


    @property
    def host(self):
        return self.url.split(':')[0]

        
    @property
    def port(self):
        return int(self.url.split(':')[1])


    def __call__(self):
        return self        

 
    def connection_made(self, transport):
        """Callback after connection to the server has been made.
        """
        pass

    def connection_lost(self, exc=None):
        """Callback after connection to the server was closed/lost.
        """
        if self.keep_alive_task:
            self.keep_alive_task.cancel()
        self.connected.clear()
        self.logged_in.clear()
        self.disconnected.set()
        self.logged_out.set()
        print(f"connection to {self.host}:{self.port} closed")


    def data_received(self, data):
        """Callback called when data is received from the FIX server.
        
        :param bytes data: ascii-encoded byte string of key=value pairs
            representing the fix message.
        """
        data = data.decode()
        l = [field.split('=') for field in data.split(chr(1))]
        msg = dict([(int(pair[0]), pair[1]) for pair in l[:-1]])
        
        if msg[35] == '0':              #heartbeat
            pass
        
        elif msg[35] == '1':            #test
            self.heartbeat(msg[112])
        
        elif msg[35] == 'A':            #login
            self.logged_in.set()
            self.logged_out.clear()
            print(f"logged in to {self.host}:{self.port}")
        
        elif msg[35] == '5':            #logout
            self.logged_out.set()
            self.logged_in.clear()
            print(f"logged out of {self.host}:{self.port}")    


    async def connect(self):
        """Open a connection with FIX server.
        
        Connects to the FIX server, logs in, starts the keep alive task, and
        waits for the client to be disconnected.
        """
        
        while True:
        
            self.is_closing = False
            
            attempts = 0
            
            while attempts < self.max_connect_attempts:
                try: 
                    (self.transport, _) = await asyncio.wait_for(
                                self.loop.create_connection(self, self.host, self.port,
                                           ssl=self.ssl_context), self.connect_timeout)
                                           
                    self.connected.set()
                    self.disconnected.clear()
                
                except asyncio.TimeoutError:
                    print("Connection to {} timed out.".format(self.url))
                    attempts += 1
                    continue
                    
                print("connection made to {}".format(self.url))
                break
            
            else:
                print("connection to {} failed.".format(self.url))
                return
    
            await self.login()
            
            self.keep_alive_task = self.loop.create_task(self.keep_alive())
            
            await self.disconnected.wait()
        
            if self.is_closing or not self.reconnect:
                break

    async def close(self):
        """Close the connection with the FIX server.
        """
        
        self.is_closing = True
        self.transport.close()
        await self.disconnected.wait()
        
        
    async def send(self, msg):
        """Send a message to the FIX server.
        
        :param Message msg: The message (subclass of Message) to send.
        """
        self.transport.write(bytes(msg))
        
    
    async def login(self, send_time=None):
        """Log in to the FIX server.
        
        :param str send_time: For testing purposes only
        """
        self.seq_num += 1
        await self.send(LoginMessage(self.key, self.secret, self.passphrase, 
                                                       self.seq_num, send_time))
        await self.logged_in.wait()
        
        
    async def logout(self):
        """Log out of the FIX server.
        """
        self.seq_num += 1
        await self.send(LogoutMessage(self.key, self.seq_num))
        await self.logged_out.wait()
        
        
    async def heartbeat(self, test_req_id=None):
        """Send a heartbeat message
        
        :param str test_req_id: (optional) The test request id if there was one 
            to initiate the heartbeat.
        """
        self.seq_num += 1
        await self.send(HeartbeatMessage(self.key, self.seq_num, test_req_id))
        
        
    async def keep_alive(self, interval=30):
        """Keep the connection alive.
        
        Send a heartbeat message at a predefined interval. Runs as long as the 
        client is logged in or until it is proactively cancelled.
        
        :param int interval: (optional) The interval in sec for the heartbeat.
            The default is 30.
        """
        
        while self.logged_in.is_set():
            try:
                await asyncio.wait_for(self.logged_out.wait(), interval)
            except asyncio.TimeoutError:
                await self.heartbeat()
                
    
    async def market_order(self, side, product_id, size=None, funds=None,
                                              stop_price=None, client_oid=None):
        """Place a market order or a stop entry/loss market order.
        
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
            
        :param str client_oid: (optional) A self generated UUID to identify the 
            order. The default is None.

        :raises ValueError:
        
            * The side is not either "buy" or "sell".
            * Neither size nor funds is set.
            * Both size and funds are set
        """

        if side not in ('buy', 'sell'):
            raise ValueError("Invalid side: {}. Must be either buy or sell".format(side))

        if not (size or funds):
                raise ValueError('Market orders must have size or funds set.')
                
        if size and funds:
                raise ValueError("Market orders can't have both size and funds set.")
                
        self.seq_num += 1
        
        msg = MarketOrderMessage(self.key, self.seq_num, side, product_id, size,
                                                  funds, stop_price, client_oid)
        await self.send(msg)


    async def limit_order(self, side, product_id, price, size, 
                          time_in_force='GTC', stop_price=None, client_oid=None):
        """Place a limit order or a stop entry/loss limit order.
        
        :param str side: Either buy or sell
        
        :param str product_id: The product id to be bought or sold.
            
        :param float price: The price the order is to be executed at. This 
            paramater may also be a string to avoid floating point issues.
            
        :param float size: The quantity of the cryptocurrency to buy or sell. 
            This parameter may also be a string.
            
        :param str time_in_force: (optional) Time in force policies provide 
            guarantees about the lifetime of an order. There are four 
            policies: GTC (good till canceled), IOC (immediate or cancel), 
            FOK (fill or kill), PO (post only). The default is GTC.
        
        :param float stop_price: (optional) The trigger price for stop orders. 
            This may also be a string. The default is None.
            
        :param str client_oid: (optional) A self generated UUID to identify the 
            order. The default is None.
            
        :raises ValueError:
        
            * The side is not either "buy" or "sell".
            * The time_in_force is not GTC, IOC, FOK, or PO.
            * A stop_order has post_only set to True
        """

        if side not in ('buy', 'sell'):
            raise ValueError("Invalid side: {}. Must be either buy or sell".format(side))
            
        if time_in_force not in ('GTC', 'IOC', 'FOK', 'PO'):
            raise ValueError('time_in_force must be GTC, IOC, FOK, or PO.')
        
        if stop_price and time_in_force == 'PO':
            raise ValueError('Stop orders cannot be Post Only.')
            
        self.seq_num += 1
        
        msg = LimitOrderMessage(self.key, self.seq_num, side, product_id, price,
                                size, time_in_force, stop_price, client_oid)
        await self.send(msg)
        
        
    async def cancel(self, order_id=None, client_oid=None):
        """Cancel a previously placed order.

        :param str order_id: (optional) The final id of the order as assigned
            by Coinbase. Either this or client_oid must be provided.
            
        :param str client_oid: (optional) The user generated id for the order 
            when it was placed. Either this or the order_id must be provided.
            
        .. note:: Use of the client_oid is not available after reconnecting or 
            starting a new session. You should use the order_id obtained via the 
            execution report once available.
            
        :raises ValueError:
        
            * Neither order_id nor client_oid are provided.
            * Both order_id and client_oid are provided.
        """
        
        if not (order_id or client_oid):
            raise ValueError("Either order_id or client_oid must be provided.")
            
        if order_id and client_oid:
            raise ValueError("Both order_id and client_oid cannot be set.")
            
        self.seq_num += 1
        
        msg = CancelMessage(self.key, self.seq_num, order_id, client_oid)
        
        await self.send(msg)
