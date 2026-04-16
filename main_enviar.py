#!/usr/bin/env python3

import sys
import signal
from ethernet import *
import threading
import argparse
import time
from datetime import datetime
from zoneinfo import ZoneInfo

TYPE1 = 0x4444
TYPE2 = 0xAAAA

def fn_signal(signum, frame):
    finalizar = stopEthernetLevel()

    if finalizar == -1:
        print("\nError finalizando")
        sys.exit(1)
    else:
        print("\nFinalizacion correcta")
        sys.exit(0)


def unix_to_ddmmyyyy(unixtime: int) -> str:
    '''
        Nombre: unix_to_ddmmyyyy()
        Definición: Pasa el tiempo de formato unix (segundos desde 1/1/1970) a formato dd:mm:yyyy HH:MM:SS.
        Argumentos: unixtime, que es el tiempo en formato unix.
        Retorno: un string con el tiempo en formato dd:mm:yyyy HH:MM:SS.
    '''
    tz = ZoneInfo("Europe/Madrid")
    fecha = datetime.fromtimestamp(unixtime, tz)

    return fecha.strftime("%d:%m:%Y_%H:%M:%S_")

    '''
    Implementación que no voy a usar porque es lenta de cojones :thumbsup:
    dias_meses = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    dias_total = int(unixtime/(3600*24))

    ano = 1970
    dias = dias_total + 1
    while (dias > 365):
        if (ano % 400 == 0 or (ano % 4 == 0 and ano % 100 != 0)):
            if dias == 366:
                break
            dias -= 366
        else:
            dias -= 365
        ano += 1

    if (ano % 400 == 0 or (ano % 4 == 0 and ano % 100 != 0)):
        dias_meses[1] += 1

    for mes in range(0, 12):
        if dias <= dias_meses[mes]:
            break
        dias -= dias_meses[mes]
    mes += 1

    segundos_restantes = int(unixtime-dias_total*3600*24)
    horas = int(segundos_restantes/3600)
    minutos = int((segundos_restantes-horas*3600)/60)
    segundos = segundos_restantes-horas*3600-minutos*60

    tiempo = f"{dias:02d}:{mes:02d}:{ano} {horas:02d}:{minutos:02d}:{segundos:02d}"
    return tiempo
    '''


def main():

    canal = ""
    usuario = ""

    tipos = [0, 0]

    macdestino = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    timeout = 1000

    trama_chat = bytearray(1498)
    incremento = 0

    parser = argparse.ArgumentParser(description="Main enviar tramas ethernet")
    parser.add_argument("-i", type=str, required=True, metavar="INTERFAZ", help="interfaz de red")
    parser.add_argument("-c", type=str, required=True, metavar="CANAL", help="canal")
    parser.add_argument("-u", type=str, required=True, metavar="USUARIO", help="usuarios")
    args = parser.parse_args()

    canal = args.c
    interfaz = args.i
    usuario = args.u

    resultado = startEthernetLevel(interfaz)
    if resultado == -1:
        print(f"Error al IniciarNivel eTH, resultado = {resultado}")
        return -1

    # *******************************
    # PRACTICA: Chequear canal y usuario DONE
    # *******************************

    if (len(canal) > 10):
        print(f"\nEl nombre del canal \"{canal}\" es demasaido largo. MAX 10 caracteres.")
        return -1
    if (len(usuario) > 10):
        print(f"\nEl nombre del usuario \"{usuario}\" es demasaido largo. MAX 10 caracteres.")
        return -1

    if (len(canal) < 10):
        canal = (canal.encode() + (b"\x00" * (10-len(canal)))).decode()
    if (len(usuario) < 10):
        usuario = (usuario.encode() + (b"\x00" * (10-len(usuario)))).decode()

    # Termina nuestra implementación

    print(f"\nCanal: {canal}\nUser: {usuario}")

    signal.signal(signal.SIGINT, fn_signal)

    while True:
        try:
            cadena = input("\nIntroduce Mensaje a enviar: ")
        except EOFError:
            break

        cadena_bytes = cadena.encode()
        longitud_camposiguiente = len(cadena_bytes)

        # *******************************
        # PRACTICA: Construir aquí la trama DONE
        # *******************************

        tiempo = time.time()
        tiempo_b = unix_to_ddmmyyyy(tiempo).encode()
        canal_b = canal.encode()
        user_b = usuario.encode()
        len_b = len(cadena_bytes)
        len_b = len_b.to_bytes(4, byteorder="big")
        trama_chat = tiempo_b + canal_b + user_b + len_b + cadena_bytes

        longitud_camposiguiente = len(trama_chat)

        # Termina nuestra implementación
        enviado = sendEthernetFrame(trama_chat, longitud_camposiguiente, TYPE2, macdestino)

        if enviado == -1:
            print("Error enviando trama")

        incremento = 0

    finalizar = stopEthernetLevel()

    if finalizar == -1:
        print("\nError finalizando")
        return 1
    else:
        print("\nFinalizacion correcta")
        return 0


if __name__ == "__main__":
    main()
