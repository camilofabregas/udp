from os import listdir
import signal
import socket
from os.path import getsize
import threading
from queue import Queue
import sys
import copy
from src.commands.list import List, get_list
from src.messages.header import *
from src.messages.data import *
from src.messages.handshake import *
from src.messages.ack import *
from src.messages.fin import *

from src.commands.upload import *
from src.commands.download import *
from src.arqs.utils import *
from src.tools.constants import FIN_TIMEOUTS, FIXED_TIMEOUT, PACKET_SIZE
from src.tools.logger import Logger


class Connection:
    def __init__(self, config, queue, server_socket, socket_lock):
        self.server_socket = server_socket
        self.socket_lock = socket_lock
        self.queue = queue
        self.config = config

    def run(self):
        error = self.handshake_server()
        if error:
            return

        if self.config.command == "download":
            arq = arq_by_side[self.config.arq]["sender"]
            Upload(arq, self.config, self.server_socket, self.socket_lock, self.queue).run()
        if self.config.command == "upload":
            arq = arq_by_side[self.config.arq]["receiver"]
            Download(arq, self.config, self.server_socket, self.socket_lock, self.queue).run()
        if self.config.command == "list":
            arq = arq_by_side[self.config.arq]["sender"]
            List(arq, self.config, self.server_socket, self.socket_lock, self.queue).run()
        # if para el resto de los casos (list)

    def handshake_server(self):
        logger = self.config.logger
        logger.log("=== iniciando el handshake ===", self.config.host, self.config.port)
        client_handshake = self.queue.get()
        logger.log("  <<  HANDSHAKE",  self.config.host, self.config.port)
        self.config.command = client_handshake.command
        self.config.name = client_handshake.filename
        self.config.filesize = client_handshake.filesize

        handshake = Handshake(self.config.command, self.config.filesize, self.config.name,
                                self.config.arq)
        
        if self.config.command == "download":
            path = os.path.join(self.config.storage, self.config.name)
            if os.path.exists(path):
                self.config.filesize = getsize(path)
                handshake.filesize = self.config.filesize
            else:
                logger.log('[ERROR]: El archivo no existe.',  self.config.host, self.config.port, force=True)
                handshake.file_error = True
                self.server_socket.sendto(encode(handshake), (self.config.host, self.config.port))
                return True
        elif self.config.command == "list":
            self.config.filesize = len(get_list(self.config.storage))
            handshake.filesize = self.config.filesize        
       
        while True:
            self.server_socket.sendto(encode(handshake), (self.config.host, self.config.port))
            logger.log('  >>  HANDSHAKE',  self.config.host, self.config.port)
            try:
                msj = self.queue.get(timeout=FIXED_TIMEOUT)
                logger.log(f'  <<  {msj.type.upper()}',  self.config.host, self.config.port)
                if not (msj.type == 'data' or msj.type == 'ack'):
                    continue
                if msj.type == 'data':
                    self.queue.queue.insert(0, msj)
                break
            except:
                continue
        
       

        logger.log(f"",  self.config.host, self.config.port)
        logger.log(f"  client:         {self.config.host}, {self.config.port}",  self.config.host, self.config.port)
        logger.log(f"  command:        {self.config.command}",  self.config.host, self.config.port)
        logger.log(f"  architecture:   {self.config.arq}",  self.config.host, self.config.port)
        logger.log(f"  filename:       {self.config.name}",  self.config.host, self.config.port)
        logger.log(f"  filesize:       {self.config.filesize}",  self.config.host, self.config.port)
        logger.log(f"=== handshake finalizado ===\n", self.config.host, self.config.port)
        
        return False


class Server:
    def __init__(self, config):
        self.config = config
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.config.host, self.config.port))
        self.socket_lock = threading.Lock()
        self.clients = {}

        signal.signal(signal.SIGINT, self.handle_sigint)

        self.config.logger.log("El servidor esta listo para recibir")

    def connection_thread(self, client_address, queue):
        client_config = copy.copy(self.config)
        client_config.host = client_address[0]
        client_config.port = client_address[1]
        client_config.command = None
        connection = Connection(client_config, queue, self.server_socket, self.socket_lock)
        connection.run()

    def run(self):
        while True:
            response, client_address = self.server_socket.recvfrom(PACKET_SIZE)
            response_payload = decode(response)

            # si ya tenemos una conexion con ese address, y sigue alive se le manda
            if client_address in self.clients:
                client_thread, client_queue = self.clients[client_address]
                if client_thread.is_alive():
                    client_queue.put(response_payload)
                    continue

            # caso contrario, si es un handshake se crea una nueva connection en su thread
            if response_payload.type == 'handshake':
                client_queue = Queue()
                client_queue.put(response_payload)
                client_thread = threading.Thread(target=self.connection_thread, args=(client_address, client_queue))
                client_thread.daemon = True
                client_thread.start()
                self.clients[client_address] = (client_thread, client_queue)

    def close_server(self):
        self.server_socket.close()

    def handle_sigint(self, signal, frame):
        self.close_server()
        for client_thread, client_queue in self.clients.values():
            client_thread.join()
        self.config.logger.log("\nServidor desconectado con éxito.")
        sys.exit(0)
