#!/usr/bin/python3

import re
import language

#grab just the nick
pattern = re.compile(r'^:*!')

class Message():
    """Message class to handle parsing of messages"""
    def __init__(self, msg_parts):
        match = re.search(pattern, msg_parts[0])
        if match:
            sender = macth.expand()
        for msg in msg_parts:
            if msg.startswith(':'):
                i = msg_parts.index(msg)
                message = ' '.join(msg_parts[i:])[1:]
                for msg in msg_parts[2:i]:
                    if msg == 'PupBot':
                        #message for us
                        self.parse_msg(message)
    
    def parse_msg(self, message):
        pass

