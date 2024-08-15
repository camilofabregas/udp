import os
from math import ceil
from time import time

class Download:
    def __init__(self, arq, config, socket, socket_lock, queue):
        self.arq = arq
        self.config = config
        self.socket = socket
        self.socket_lock = socket_lock
        self.queue = queue
        self.chunk_size = 1400


    def run(self):
        download_start = time()
        chunks = self.arq( self.config, self.socket, self.socket_lock, self.queue).run()
        duration_ms = (time() - download_start) * 1000
        if self.config.command == 'download':
            #esto es de parte del cliente
            if self.config.dst:
                path = os.path.join(self.config.dst)
            else:
                #esto es de parte del server
                path = os.path.join(self.config.name)
        else:
            path = os.path.join(self.config.storage, self.config.name)
        
        throughput = (self.config.filesize / 1024) / (duration_ms / 1000)
        
        action = 'DESCARGA' if self.config.side == 'client' else 'SUBIDA'
        self.config.logger.log(f'{action} {path} en {(duration_ms):.3f}ms ({(throughput):.3f}KB/s)', self.config.host, self.config.port, True)
        
        if os.path.exists(path):
            os.remove(path)
        file = open(path, "ab")
        for chunk in chunks:
            file.write(chunk)
