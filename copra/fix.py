# -*- coding: utf-8 -*-
"""Asynchronous FIX client for the Coinbase Pro platform.
"""

import asyncio
import os
import ssl


URL = 'fix.pro.coinbase.com:4198'
SANDBOX_URL = 'fix-public.sandbox.pro.coinbase.com'

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
        keys = [8, 9, 35] + list(self.dict.keys() - {8, 9, 25} | {10})
        return ''.join(['{}={}{}'.format(key, self[key], chr(1)) for key in keys])


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
        
        
class Client(asyncio.Protocol):
    """Asynchronous FIX client for Coinbase Pro"""
    
    def __init__(self, loop, key, secret, passphrase, url=URL,
                 cert_file=CERT_FILE, auto_connect=True):
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
            
        :param bool auto_connect: (optional) If True, the Client will 
            automatically add itself to its event loop (ie., open a connection 
            if the loop is running or as soon as it starts). If False, 
            add_as_task_to_loop() needs to be explicitly called to add the 
            client to the loop. The default is True.
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
        
        
    async def connect(self):
        """Open a connection with FIX server.
        """
        host, port = self.url.split(':')
        await self.loop.create_connection(self, host, int(port), 
                                          ssl=self.ssl_context)
