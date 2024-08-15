class Ack:
    # El parametro seq indica el numero de secuencia que se esta confirmando
    def __init__(self, seq):
        self.type = "ack"
        self.seq = seq

    def encode(self):
        return self.seq.to_bytes(4, "big")

    @classmethod
    def decode(cls, binary):
        buffer = bytearray(binary)
        seq = int.from_bytes(buffer[0:4], "big")
       
        return cls(seq)
        