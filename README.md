# Introducción a los Sistemas Distribuidos (75.43) - TP N◦1: File Transfer

## Grupo B4 - Integrantes:

| Alumno                                                      | Padrón |
| ----------------------------------------------------------- | ------ |
| [Camila Fernández Marchitelli](https://github.com/camifezz) | 102515 |
| [Lucas Aldazabal](https://github.com/LucasAlda)             | 107705 |
| [Bautista Boselli](https://github.com/BautistaBoselli)      | 107490 |
| [Alejo Fábregas](https://github.com/alejofabregas)          | 106160 |
| [Camilo Fábregas](https://github.com/camilofabregas)        | 103740 |

## Resumen

En este trabajo práctico se implementó una aplicación de File Transfer en Python, con protocolos de Reliable Data Transfer (RDT) basados en UDP.
El servidor ofrece dos protocolos RDT para comunicarse con los clientes: una versión Stop & Wait y otra Selective Repeat.

## Servidor: iniciar

```
> python start-server -h

usage : server [-H ADDR] [-s DIRPATH]

mandatory arguments:
-H, --host : service IP address
-s, --storage : storage dir path

optional arguments:
-h, --help : show this help message and exit
-v, --verbose : increase output verbosity
-q, --quiet : decrease output verbosity
-p, --port : service port
-a, --arq : ARQ type (sw = Stop&Wait | sr = Selective Repeat)""")
```

Por defecto, se utilizará:

- --port : 3000
- --arq : Stop & Wait

## Cliente: subir archivo

```
> python upload -h

usage: upload [-H ADDR] [-s FILEPATH]

mandatory arguments:
-H, --host : server IP address
-s, --src : source file path

optional arguments:
-h, --help : show this help message and exit
-v, --verbose : increase output verbosity
-q, --quiet : decrease output verbosity
-p, --port : server port
-n, --name : file name
```

Por defecto, se utilizará:

- --port : 3000

## Cliente: descargar archivo

```
> python download -h

usage: download [-H ADDR] [-d FILEPATH]

mandatory arguments:
-H, --host : server IP address
-d, --dst : destination file path

optional arguments:
-h, --help : show this help message and exit
-v, --verbose : increase output verbosity
-q, --quiet : decrease output verbosity
-p, --port : server port
-n, --name : file name
```

Por defecto, se utilizará:

- --port : 3000

## Cliente: listar archivos

```
> python list -h

usage : list [-H ADDR]

mandatory arguments:
-H, --host : server IP address

optional arguments:
-h, --help : show this help message and exit
-p, --port : server port
```

Por defecto, se utilizará:

- --port : 3000

## Wireshark plugin

Para poder visualizar los paquetes enviados y recibidos por el cliente y el servidor, se desarrolló un plugin para Wireshark. Para instalarlo, se debe copiar el archivo `b4.lua` en la carpeta de plugins de Wireshark (se puede encontrar en la seccion `Help > About Wireshark > Forders > Personal Lua Plugins`).
