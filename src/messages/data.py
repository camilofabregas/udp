from .header import *

class Data:
    # El parametro seq indica el numero de secuencia del paquete enviado
    # EL parametro data contiene los datos en si enviados
    def __init__(self, seq, data):
        self.type = "data"
        self.seq = seq
        self.data = data

    def encode(self):
        return self.seq.to_bytes(4, "big") + self.data

    @classmethod
    def decode(cls, binary):
        buffer = bytearray(binary)
        seq = int.from_bytes(buffer[0:4], "big")
        data = buffer[4:]
       
        return cls(seq, data)
        