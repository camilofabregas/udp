import os
from math import ceil
from time import time

from src.tools.constants import CHUNK_SIZE

def get_list(dir):
    return '\n'.join(os.listdir(dir)).encode()

class List:
    def __init__(self, arq, config, socket, socket_lock, queue):
        self.arq = arq
        self.config = config
        self.socket = socket
        self.socket_lock = socket_lock
        self.queue = queue

    def run(self):
        buffer = get_list(self.config.storage)
        chunks = [buffer[i:i + CHUNK_SIZE] for i in range(0, len(buffer), CHUNK_SIZE)] 
        self.arq(chunks, self.config, self.socket, self.socket_lock, self.queue).run()
        self.config.logger.log(f'LISTAR', self.config.host, self.config.port, True)
        


class PrintList:
    def __init__(self, arq, config, socket, socket_lock, queue):
        self.arq = arq
        self.config = config
        self.socket = socket
        self.socket_lock = socket_lock
        self.queue = queue
        self.chunk_size = 1400


    def run(self):        
        chunks = self.arq( self.config, self.socket, self.socket_lock, self.queue).run()
        self.config.logger.log(f'', self.config.host, self.config.port, True)
        self.config.logger.log(f'ARCHIVOS EN EL SERVIDOR', self.config.host, self.config.port, True)
        
        lines = ''
        for chunk in chunks:
            lines += chunk.decode()
        lines = lines.split('\n')
        
        for line in lines:
            self.config.logger.log(f' - {line}', self.config.host, self.config.port, True)

