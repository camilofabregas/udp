import sys


# Imprime el mensaje 'msg' recibido y sale del programa.
def print_error(msg):
    print(msg)
    sys.exit(0)


# Imprime el mensaje de ayuda, dependiendo si fue un command 'upload', 'download' o 'server'.
def print_help(command):
    if command == "upload":
        print("""usage: upload [-H ADDR] [-s FILEPATH]
mandatory arguments:
-H, --host : server IP address
-s, --src : source file path
optional arguments :
-h, --help : show this help message and exit
-v, --verbose : increase output verbosity
-q, --quiet : decrease output verbosity
-p, --port : server port
-n, --name : file name""")

    elif command == "download":
        print("""usage: download [-H ADDR] [-d FILEPATH]
mandatory arguments:
-H, --host : server IP address
-d, --dst : destination file path
optional arguments :
-h, --help : show this help message and exit
-v, --verbose : increase output verbosity
-q, --quiet : decrease output verbosity
-p, --port : server port
-n, --name : file name""")

    elif command == 'server':
        print("""usage : server [-H ADDR] [-s DIRPATH])
mandatory arguments:
-H, --host : service IP address
-s, --storage : storage dir path
optional arguments :
-h, --help : show this help message and exit
-v, --verbose : increase output verbosity
-q, --quiet : decrease output verbosity
-p, --port : service port
-a, --arq : ARQ type (sw = Stop&Wait | sr = Selective Repeat)""")
        
    elif command == 'list':
        print("""usage : list [-H ADDR]
mandatory arguments:
-H, --host : server IP address
optional arguments :
-h, --help : show this help message and exit
-p, --port : server port""")

    sys.exit(0)
