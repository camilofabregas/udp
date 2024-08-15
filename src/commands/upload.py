import os
from time import time

from src.tools.constants import CHUNK_SIZE
class Upload:
    def __init__(self, arq, config, socket, socket_lock, queue):
        self.arq = arq
        self.config = config
        self.socket = socket
        self.socket_lock = socket_lock
        self.queue = queue

    def run(self):
        # TODO: esto debería ir al config
        if self.config.command == 'upload':
            #esto es de parte del cliente
            path = os.path.join(self.config.src)
        else:
            #esto es de parte del server
            path = os.path.join(self.config.storage, self.config.name)
        
        # manejar que pasa si no existe el archivo
        file = open(path, "rb")
        buffer = file.read()
        chunks = [buffer[i:i + CHUNK_SIZE] for i in range(0, len(buffer), CHUNK_SIZE)]
        
        download_start = time()
        self.arq(chunks, self.config, self.socket, self.socket_lock, self.queue).run()
        duration_ms = (time() - download_start) * 1000
        
        throughput = (self.config.filesize / 1024) / (duration_ms / 1000)
        action = 'SUBIDA' if self.config.side == 'client' else 'DESCARGA'
        self.config.logger.log(f'{action} {path} en {(duration_ms):.3f}ms ({(throughput):.3f}KB/s)', self.config.host, self.config.port, True)
        

