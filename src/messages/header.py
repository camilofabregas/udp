from .ack import *
from .data import *
from .fin import *
from .handshake import *

types = {
    "handshake" : 1,
    "data" : 2,
    "ack" : 3,
    "fin" : 4,
}

type_as_strings = list(types.keys())
type_as_numbers = list(types.values())
    
def encode(message):
        #el checksum no es necesario ya que UDP dropea el segmento
        message_buffer = message.encode()
        type_as_number = types[message.type].to_bytes(1, "big")
        length  = len(message_buffer).to_bytes(2, "big")
        return type_as_number + length + message_buffer

def decode(binary):
        buffer = bytearray(binary)
        type_number = buffer[0]
        #Esto es O(1)
        type = type_as_strings[type_as_numbers.index(type_number)]
        len = int.from_bytes(buffer[1:3], "big")
        
        if type == 'data':
            return Data.decode(buffer[3:])
        elif type == "handshake":
            return Handshake.decode(buffer[3:])
        elif type == 'ack':
            return Ack.decode(buffer[3:])
        elif type == 'fin':
            return Fin.decode(buffer[3:])
  
    