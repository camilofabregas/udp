import sys
from src.tools.tools import print_error, print_help


class Interfaz:
    def __init__(self, command):
        self.argumentos = {
            "verbose": False,
            "quiet": False,
            "host": None,
            "port": None,
            "name": None,
            "src": None,
            "dst": None,
            "storage": None,
            "arq": None}
        self.command = command
        self.parsear_args(sys.argv[1:])

    # Intenta setear el valor ingresado a su respectivo argumento (sino, lo deja en None).
    def setear_arg(self, args):
        try:
            return args.pop(0)
        except:
            return None

    # Chequea si se ingresaron los argumentos obligatorios para cada command.
    def chequear_args_obligatorios(self, command):
        if self.argumentos["verbose"] and self.argumentos["quiet"]:
            print_error("ERROR: los argumentos '-q' y '-v' no se pueden usar juntos.")

        if command == 'upload' and None in (self.argumentos["host"], self.argumentos["src"]):
            print_error("ERROR: faltan argumentos obligatorios para el command 'upload' (-H, y -s).")

        if command == 'download' and None in (
                self.argumentos["host"], self.argumentos["name"]):
            print_error("ERROR: faltan argumentos obligatorios para el command 'download' (-H y -n).")

        if command == 'server' and None in (
                self.argumentos["host"], self.argumentos["storage"]):
            print_error("ERROR: faltan argumentos obligatorios para el command 'server' (-H y -s).")

    # Parsea los argumentos ingresados por el usuario, que puede ser un cliente ('upload' | 'download') o un 'server'.
    def parsear_args(self, args):

        while args:
            arg = args.pop(0)
            if arg in ['-h', '--help']:
                print_help(self.command)
            elif arg in ['-v', '--verbose']:
                self.argumentos["verbose"] = True
            elif arg in ['-q', '--quiet']:
                self.argumentos["quiet"] = True
            elif arg in ['-H', '--host']:
                self.argumentos["host"] = self.setear_arg(args)
            elif arg in ['-p', '--port']:
                self.argumentos["port"] = self.setear_arg(args)
            elif arg in ['-n', '--name']:
                self.argumentos["name"] = self.setear_arg(args)
            elif arg in ['-s', '--src'] and self.command == 'upload':
                self.argumentos["src"] = self.setear_arg(args)
            elif arg in ['-s', '--storage'] and self.command == 'server':
                self.argumentos["storage"] = self.setear_arg(args)
            elif arg in ['-a', '--arq'] and self.command == 'server':
                self.argumentos["arq"] = self.setear_arg(args)
            elif arg in ['-d', '--dst'] and self.command == 'download':
                self.argumentos["dst"] = self.setear_arg(args)
            else:
                print_error("ERROR: el argumento '" + arg + "' no existe para el command '" + self.command + "'.")

        self.chequear_args_obligatorios(self.command)
