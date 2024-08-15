import ipaddress
import os
from os.path import getsize

from src.client import Client
from src.server import Server
from src.tools.constants import FILE_MAX_SIZE
from src.tools.logger import Logger
from src.tools.tools import print_error


class Config:
    def __init__(self, interfaz):
        """
        Constructor de la clase Config.
        """
        self.command = interfaz.command
        self.verbose = False
        self.host = None
        self.port = 3000
        self.name = None
        self.src = None
        self.dst = None
        self.storage = None
        self.arq = None
        self.filesize = None
        self.side = None
        self.logger = None
        if self.command == "server":
            self.arq = 'stop&wait'  # acá tiene que haber una instancia por default de SelectiveRepeat o StopAndWait
            self.side = "server"
        else:
            self.side = "client"

        self.validar_argumentos(interfaz.argumentos)

        self.logger = Logger(self.side, self.verbose)

    def validar_host(self, address):
        if address == "localhost":
            self.host = address
        else:
            try:
                ipaddress.ip_address(address)
                self.host = address
            except ValueError:
                print_error("ERROR: ingresar una direccion IP valida (-H).")

    def validar_port(self, port):
        if port.isdigit() and 1025 <= int(port) <= 65535:
            self.port = int(port)
        else:
            print_error("ERROR: ingresar un puerto valido (-p).")

    def validar_src(self, path, name):
        if os.path.exists(path):
            self.src = path
            if not name:
                self.name = path.split("/")[-1]
        else:
            print_error("ERROR: ingresar una ruta valida (--src).")

    def validar_dst(self, path, new_name):
        if not new_name:
            print_error("ERROR: ingresar una ruta valida (--dst).")
        if not os.path.exists(path):
            os.makedirs(path)
        full_path = os.path.join(path, new_name)
        self.dst = full_path
        # print_error("ERROR: ingresar una ruta valida (--dst).")

    def validar_storage(self, path):
        if os.path.exists(path):
            self.storage = path
        else:
            os.makedirs(path)
            self.storage = path

    def validar_arq(self, arq):
        if arq == "sw":
            self.arq = "stop&wait"  # acá instanciamos a la clase StopWait
        elif arq == "sr":
            self.arq = "selectiveRepeat"  # aca instanciamos a la clase SelectiveRepeat
        else:
            print_error("ERROR: ingresar un tipo de ARQ valido (-a) (sw = Stop&Wait | sr = Selective Repeat).")

    def validar_file_size_maximo(self):
        file_to_upload = getsize(self.src)
        # Verificar si el tamaño del archivo es menor o igual al tamaño máximo
        if file_to_upload <= FILE_MAX_SIZE:
            self.filesize = file_to_upload
        else:
            print_error("ERROR: ingresar un archivo que tenga como máximo un tamaño de 4GB")

    def validar_argumentos(self, argumentos):

        self.validar_host(argumentos["host"])
        if argumentos["port"]:
            self.validar_port(argumentos["port"])
        if argumentos["src"]:
            self.validar_src(argumentos["src"], argumentos["name"])
            self.validar_file_size_maximo()
        if argumentos["dst"]:
            splitted = argumentos["dst"].split("/")
            if len(splitted) > 1:
                path = "/".join(splitted[:-1])
            else:
                path = "."
            new_name = splitted[-1]
            self.validar_dst(path, new_name)
        if argumentos["storage"]:
            self.validar_storage(argumentos["storage"])
        if argumentos["arq"]:
            self.validar_arq(argumentos["arq"])
        if argumentos["name"]:
            self.name = argumentos["name"]
        if argumentos["verbose"]:
            self.verbose = True

    def identificar_tipo_config(self):
        if self.side == "client":
            return Client(self)
        else:
            return Server(self)
