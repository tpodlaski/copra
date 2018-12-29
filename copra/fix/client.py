# -*- coding: utf-8 -*-
"""Asynchronous FIX client for the Coinbase Pro platform.
"""

import asyncio
import base64
import hashlib
import hmac
import logging
import os
import re
import ssl
import time

from copra.fix.message import Message
from copra.fix.names import VALUES
from copra.fix.order import Order

logger = logging.getLogger(__name__)

URL = 'fix.pro.coinbase.com:4198'
SANDBOX_URL = 'fix-public.sandbox.pro.coinbase.com:4198'

CERT_FILE = os.path.join(os.path.dirname(__file__), 'certs', 
                                                    'fix.pro.coinbase.com.pem')
SANDBOX_CERT_FILE = os.path.join(os.path.dirname(__file__), 'certs', 
                                      'fix-public.sandbox.pro.coinbase.com.pem')
                                      
class Client:

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
        
        self.orders = {}


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
        
        if self.is_closing:
            logger.info("connection to {}:{} closed".format(self.host, 
                                                                     self.port))
        else:
            logger.warning("connection to {}:{} unexpectedly closed".format(
                                                          self.host, self.port))
            if self.reconnect:
                self.loop.create_task(self.connect())
        
        
    def data_received(self, data):
        """Callback called when data is received from the FIX server.
        
        :param bytes data: ascii-encoded byte string of key=value pairs
            representing the fix message.
        """
        for f_msg in re.split(r'8=FIX\.4\.2.', data.decode('ascii'))[1:]:
            
            msg = Message.from_formatted(f_msg)
    
            logger.debug(msg)
    
            if msg[35] == '8':              # execution report
            
                try:
                    order_id = msg[11]      # new or rejected order - use client_oid
                except KeyError:
                    order_id = msg[37]      # not a new or rejected order - use oid 
                
                try:
                    
                    order = self.orders[order_id]
                    
                    if msg[150] == '0' or msg[150] == '8':     # ExcecType new or rejected
                        del self.orders[order_id]
                        self.orders[msg[37]] = order
                        
                    order.fix_update(msg)
                    
                    logging.info('\n{}\n'.format(order))
                    
                except KeyError:
                    # log error message here
                    pass
                    
            elif msg[35] == '0':            #heartbeat
                pass
            
            elif msg[35] == '1':            #test
                self.heartbeat(msg[112])
            
            elif msg[35] == 'A':            #login
                self.logged_in.set()
                self.logged_out.clear()
                logger.info(f"logged in to {self.host}:{self.port}")
            
            elif msg[35] == '5':            #logout
                self.logged_out.set()
                self.logged_in.clear()
                logger.info(f"logged out of {self.host}:{self.port}")
                
            elif msg[35] == '9':            #cancel order reject
                logger.warning("Order {} cancel failed.".format(msg[37]))
            
            elif msg[35] == '3':            #reject
                reason = ''
                if 58 in msg:
                    reasson = ' ' + msg[38] + '.'
                logger.warning("Message rejected.{}".format(reason))
            
            else:
                logger.warning("Uncaught message:\n{}".format(msg))
            
        
    def send(self, msg):
        """Send a message to the FIX server.
        
        :param Message msg: The message to send.
        """
        self.transport.write(bytes(msg))


    async def connect(self):
        """Open a connection with FIX server.
        
        Connects to the FIX server, logs in, starts the keep alive task.
        """
        
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
                logger.warning("Connection to {} timed out.".format(self.url))
                attempts += 1
                continue
                
            logger.info("connection made to {}".format(self.url))
            break
        
        else:
            logger.error("connection to {} failed.".format(self.url))
            return

        await self.login()
        
        self.keep_alive_task = self.loop.create_task(self.keep_alive())
            
            
    async def close(self):
        """Close the connection with the FIX server.
        """
        
        self.is_closing = True
        self.transport.close()
        await self.disconnected.wait()
        

    async def login(self, send_time=None):
        """Log in to the FIX server.
        
        :param str send_time: For testing purposes only
        """
        self.seq_num += 1

        fields = {}
        fields[52] = send_time or time.time()      #SendingTime, Time of message transmission
        fields[98] = 0                             #EncryptMethod, 0 = None/other
        fields[108] = 30                           #HeartBtInt, Heartbeat interval in seconds
        fields[554] = self.passphrase              #Password, Client API passphrase
        fields[8013] = 'S'                         #CancelOrdersOnDisconnect, 
                                                   #  Y: Cancel all open orders for the 
                                                   #     current profile
                                                   #  S: Cancel open orders placed during 
                                                   #     session

        login_msg = Message(self.key, self.seq_num, 'A', fields)

        #message signature
        keys = [52, 35, 34, 49, 56]
        s = chr(1).join([str(login_msg[key]) for key in keys] + [self.passphrase]).encode('utf-8')
        hmac_key  = base64.b64decode(self.secret)
        signature = hmac.new(hmac_key, s, hashlib.sha256)
        sign_b64  = base64.b64encode(signature.digest()).decode()
        login_msg[96] = sign_b64
        
        self.send(login_msg)
        await self.logged_in.wait()
        

    async def logout(self):
        """Log out of the FIX server.
        """
        self.seq_num += 1
        
        self.send(Message(self.key, self.seq_num, '5'))
        await self.logged_out.wait()
        
        
    async def heartbeat(self, test_req_id=None):
        """Send a heartbeat message
        
        :param str test_req_id: (optional) The test request id if there was one 
            to initiate the heartbeat.
        """
        self.seq_num += 1
        self.send(Message(self.key, self.seq_num, '0', 
                                   {112: test_req_id} if test_req_id else None))
                                
                                
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


    async def limit_order(self, side, product_id, size, price, 
                                          time_in_force='GTC', stop_price=None):
        """Place a limit order or a stop entry/loss limit order.
        
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
            
        :raises ValueError:
        
            * The side is not either "buy" or "sell".
            * The time_in_force is not GTC, IOC, FOK, or PO.
            * A stop_order has post_only set to True
        """

        self.seq_num += 1
        
        order, msg = Order.limit_order(self.key, self.seq_num, side, product_id,
                                         size, price, time_in_force, stop_price)
                                         
        self.orders[order.client_oid] = order
        self.send(msg)
       
        await order.received.wait()
        
        return order
        
                
    async def market_order(self, side, product_id, size=None, funds=None,
                                                              stop_price=None):
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
            
        :raises ValueError:
        
            * The side is not either "buy" or "sell".
            * Neither size nor funds is set.
            * Both size and funds are set
        """
        
        self.seq_num += 1
             
        order, msg = Order.market_order(self.key, self.seq_num, side, product_id, size, funds, stop_price)
        self.orders[order.client_oid] = order
        self.send(msg)
       
        await order.received.wait()
        
        return order
        
        
    async def cancel(self, order_id=None, client_oid=None):
        """Cancel a previously placed order.

        :param str order_id: The id of the order to cancel.
            
        :raises KeyError: If the order with order_id is not being managed 
            by the current session.
        """

        self.seq_num += 1
        
        order = self.orders[order_id]
        self.send(Message(self.key, self.seq_num, 'F', {37: order.id}))
        
        await order.done.wait()