import socket
from os.path import getsize
import threading
import sys
from queue import Queue
from src.commands.list import PrintList

from src.messages.header import *
from src.messages.data import *
from src.messages.handshake import *
from src.messages.ack import *
from src.messages.fin import *

from src.commands.upload import *
from src.commands.download import *
from src.arqs.utils import *
from src.tools.constants import FIXED_TIMEOUT, PACKET_SIZE


class Client:
    def __init__(self, config):
        self.socket_lock = threading.Lock()
        self.config = config
        self.queue = Queue()
        self.thread = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handshake(self):
        logger = self.config.logger
        logger.log("=== iniciando el handshake ===")

        handshake = Handshake(self.config.command, self.config.filesize, self.config.name,
                              self.config.arq)

        while True:
            self.client_socket.sendto(encode(handshake), (self.config.host, self.config.port))
            logger.log('  >>  HANDSHAKE')
            try:
                handshake_server = self.queue.get(timeout=FIXED_TIMEOUT)
                logger.log(f'  <<  {handshake_server.type.upper()}')
                if handshake_server.type == 'handshake':
                    if not handshake_server.file_error:
                        self.config.arq = handshake_server.arq
                        self.config.filesize = handshake_server.filesize
                        break
                    
                    logger.log(f'[ERROR]: El archivo que se quiere descargar no existe', force=True)
                    return True
            except:
                continue

        if self.config.command == "download" or self.config.command == "list":
            ack = Ack(2 ** 16 - 1)
            while True:
                self.client_socket.sendto(encode(ack), (self.config.host, self.config.port))
                logger.log('  >>  ACK')
                try:
                    response = self.queue.get(timeout=FIXED_TIMEOUT)
                    if response.type == 'data':
                        self.queue.queue.insert(0, response)  # vuelvo a poner el data asi lo lee la estrategia
                        break
                    logger.log(f'  <<  {response.type.upper()}')
                except:
                    continue

        logger.log(f"\n  command:        {self.config.command}")
        logger.log(f"  architecture:   {self.config.arq}")
        logger.log(f"  filename:       {self.config.name}")
        logger.log(f"  filesize:       {self.config.filesize}")
        logger.log(f"=== handshake finalizado ===\n")
        
        return False

    def start_command(self):
        if self.config.command == "upload":
            arq = arq_by_side[self.config.arq]["sender"]
            upload = Upload(arq, self.config, self.client_socket, self.socket_lock, self.queue)
            upload.run()
        if self.config.command == "download":
            arq = arq_by_side[self.config.arq]["receiver"]
            upload = Download(arq, self.config, self.client_socket, self.socket_lock, self.queue)
            upload.run()
        if self.config.command == "list":
            arq = arq_by_side[self.config.arq]["receiver"]
            upload = PrintList(arq, self.config, self.client_socket, self.socket_lock, self.queue)
            upload.run()

    def connection_thread(self):
        error = self.handshake()
        if error:
            self.close_connection()
            sys.exit()
        self.start_command()

    def run(self):
        self.thread = threading.Thread(target=self.connection_thread)
        self.thread.start()

        self.client_socket.settimeout(FIXED_TIMEOUT)
        while self.thread.is_alive():
            try:
                response, server_socket = self.client_socket.recvfrom(PACKET_SIZE)
                response_payload = decode(response)
                self.queue.put(response_payload)
            except:
                continue

    def close_connection(self):
        self.client_socket.close()
