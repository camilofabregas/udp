class Fin:
    # El parametro seq indica el numero de secuencia del paquete enviado
    # EL parametro data contiene los datos en si enviados
    def __init__(self):
        self.type = "fin"

    def encode(self):
        return b''

    @classmethod
    def decode(cls, binary):
        return cls()
        