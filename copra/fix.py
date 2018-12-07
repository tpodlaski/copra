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
            
            
class Client(asyncio.Protocol):
    """Asynchronous FIX client for Coinbase Pro"""
    
    def __init__(self, loop, key, secret, passphrase, url=URL,
                                                      cert_file=CERT_FILE):
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
        """
        self.loop = loop
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.url = url
        
        self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        self.ssl_context.load_verify_locations(cert_file)
        
        self.seq_num = 0
        
        self.connected = asyncio.Event()
        self.disconnected = asyncio.Event()
        self.disconnected.set()
        
        self.logged_in = asyncio.Event()
        self.logged_out = asyncio.Event()
        self.logged_out.set()


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
        
        self.connected.clear()
        self.disconnected.set()
        print(f"connection to {self.host}:{self.port} closed")


    def data_received(self, data):
        """Callback called when data is received from the FIX server.
        
        :param bytes data: ascii-encoded byte string of key=value pairs
            representing the fix message.
        """
        data = data.decode()
        l = [field.split('=') for field in data.split(chr(1))]
        msg = dict([(int(pair[0]), pair[1]) for pair in l[:-1]])
        
        if msg[35] == 'A':            #login
            self.logged_in.set()
            self.logged_out.clear()
            print(f"logged in to {self.host}:{self.port}")
        
        elif msg[35] == '5':            #logout
            self.logged_out.set()
            self.logged_in.clear()
            print(f"logged out of {self.host}:{self.port}")    

    
    async def connect(self, login=True):
        """Open a connection with FIX server.
        
        :param bool login: (optional) Automatically log in after the 
            connection has been established. The default is True.
            
        """
        
        (self.transport, _) = await self.loop.create_connection(self, self.host, 
                                                self.port, ssl=self.ssl_context)
        self.connected.set()
        self.disconnected.clear()
        print(f"connection made to {self.url}")
    

    async def close(self):
        """Close the connection with the FIX server.
        """
        
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
        