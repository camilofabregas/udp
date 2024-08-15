commands = {
    'download': 1,
    'upload': 2,
    'list': 3,
}

command_as_strings = list(commands.keys())
command_as_numbers = list(commands.values())

arqs = {
    None: 1,
    "stop&wait": 2,
    "selectiveRepeat": 3,
}
arq_as_strings = list(arqs.keys())
arq_as_numbers = list(arqs.values())


class Handshake:
    # El parametro command indica que tipo de accion se quiere realizar, esta puede ser download, upload o list
    # EL parametro filename indica el nombre del archivo sobre el que se quiere operar
    def __init__(self, command, filesize, filename, arq, file_error=False):
        self.type = "handshake"
        self.command = command
        self.filesize = filesize
        self.filename = filename if filename else ''
        self.arq = arq
        self.file_error = file_error
        if self.filesize is None:
            self.filesize = 0

    def encode(self):
        return commands[self.command].to_bytes(1, "big") + arqs[self.arq].to_bytes(1, "big") + self.file_error.to_bytes(1, "big") + self.filesize.to_bytes(
            4, "big") + self.filename.encode()
       
    @classmethod
    def decode(cls, binary):
        buffer = bytearray(binary)
        command_number = buffer[0]
        arq_number = buffer[1]
        file_error = buffer[2] == 1
        filesize = int.from_bytes(buffer[3:7], "big")
        filename = buffer[7:].decode()
        
        command = command_as_strings[command_as_numbers.index(command_number)]
        arq = arq_as_strings[arq_as_numbers.index(arq_number)]

        return cls(command, filesize, filename, arq, file_error)
