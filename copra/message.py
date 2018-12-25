# -*- coding: utf-8 -*-
"""FIX message class for the Coinbase Pro platform.
"""

from names import TYPES, TAGS, VALUES

class Message:
    """FIX message class.
    
    Provides the basic key/value pairs for every Coinbase FIX message and the 
    funcionality for manipulating and preparing the message for transmission. 
    """
    
    @classmethod
    def from_formatted(cls, msg):
        """Initialize new Message object from a formatted string/binary msg.
        
        :param str msg: str or binary "formatted" representation of a message.
        
        """
        if isinstance(msg, bytes):
            msg = msg.decode('ascii')
        l = [field.split('=', 1) for field in msg.split(chr(1))]
        msg_dict = dict([(int(pair[0]), pair[1]) for pair in l[:-1]])
        
        del msg_dict[9] # len is virtual. checksum will verify it is correct
        checksum = msg_dict.pop(10)
        key  = msg_dict.pop(49)
        seq_num = msg_dict.pop(34)
        msg_type = msg_dict.pop(35)
        
        new_msg = cls(key, seq_num, msg_type, msg_dict)

        if new_msg[10] != checksum:
            raise ValueError('Checksum of the message is incorrect.')
        return new_msg
        

    def __init__(self, key, seq_num, msg_type, fields=None):
        """Initialize the Message object
        
        :param str key: The API key of the client generating the message.
        
        :param int seq_num: The sequence number of the message as tracked by
            the client.
        
        :param str msg_type: The type field of the message. It /should/ be a
            str but since many are ints, it will accept an int and convert it
            to a str.
            
        :param dict fields: (optional) Additional fields (key/value pairs) the 
            message is to be intialized with. The default is None.
        """
        
        self.dict = { 8: 'FIX.4.2',
                     35: str(msg_type),
                     49: str(key),
                     56: 'Coinbase',
                     34: str(seq_num)}
                     
        if fields:
            self.dict.update({int(key): str(value) for key, value in fields.items()})
            
            
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


    def __len__(self):
        return len(chr(1).join(['{}={}'.format(key, self.dict[key]) 
                                for key in self.dict.keys() - {8}])) + 1
        
    
    def __repr__(self):
        keys = [8, 9, 35] + list(self.dict.keys() - {8, 9, 35}) + [10]
        return ''.join(['{}={}{}'.format(key, self[key], chr(1)) for key in keys])
    
    
    def __str__(self):
        str_ = 'FIX Message {} [{}]\n'.format(self[35], TYPES.get(self[35], 'Unknown'))
        keys = [8, 9, 35] + sorted(list(self.dict.keys() - {8, 9, 35})) + [10]
        for key in keys:
            str_ += '\t{} [{}]:  {}'.format(key, TAGS.get(key, 'Unknown'), self[key])
            if key in VALUES:
                str_ += ' <{}>'.format(VALUES[key][str(self[key])])
            str_ += '\n'
        return str_
        
        
    def __bytes__(self):
        return repr(self).encode('ascii')
        
        
    def checksum(self):
        s = ''.join(['{}={}{}'.format(key, self[key], chr(1)) for key in self.dict.keys() | {9}])
        ord_sum = sum([ord(char) for char in s]) % 256
        return str(ord_sum).zfill(3)
