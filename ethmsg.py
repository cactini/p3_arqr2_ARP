#!/usr/bin/env python3

import sys
import signal
from ethernet import *
import threading
import time
from datetime import datetime, timezone, timedelta

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


def process_ethMsg_frame(us: ctypes.c_void_p, header: pcap_pkthdr, data: bytes, srcMac: bytes) -> None:
    '''
        Nombre: process_EthMsg_frame
        Descripción: Esta función procesa las tramas mensajes sobre ethernet.
            Se ejecutará por cada trama Ethenet que se reciba con Ethertype ETHTYPE (si ha sido registrada en initEth).
                - Imprimir el contenido de los datos indicando la direccion MAC del remitente así como el tiempo de recepcion del mensaje, según el siguiente formato:
                    [<segundos.microsegundos>] <MAC>: <mensaje>
                - En caso de que no exista retornar

        Argumentos:
            -us: Datos de usuario pasados desde la llamada de pcap_loop. En nuestro caso será None
            -header: cabecera pcap_pktheader
            -data: array de bytes con el contenido de la trama ethMsg. Los dos primeros bytes tienen la longitud del mensaje en orden de red. El resto de bytes son el mensaje en sí mismo.
            -srcMac: MAC origen de la trama Ethernet que se ha recibido
        Retorno: Ninguno
    '''
    # *******************************
    # PRACTICA: Procesar aquí el mensaje recibido DONE
    # *******************************
    global canal
    # Leemos el frame según el diagrama del enunciado:
    tiempo = data[0:20].decode()
    canal_recibido = data[20:30]
    remitente = data[30:40]
    tamano = data[40:44]
    tamano = int.from_bytes(tamano, "big")
    mensaje = data[44:]

    # print(f"\nTiempo = {tiempo} \ncanal = {canal_recibido} \nremitente = {remitente} \ntamaño = {tamano} \nmensaje = {mensaje}")

    canal_recibido = canal_recibido.rstrip(b"\x00")
    remitente = remitente.rstrip(b"\x00")

    if canal_recibido.decode() != canal:
        print("\n--Mensaje de otro canal recibido--")
        return

    # Aquí termina la implementación del alumno

    print("\n--- Mensaje recibido ---")
    print("MAC remitente:", ':'.join(f"{b:02x}" for b in srcMac))
    print("Remitente:", remitente.decode())
    print("Tamaño:", tamano)
    print("Tiempo:", tiempo)

    try:
        texto = mensaje[:tamano].decode()
        print("Mensaje:", texto)
    except:
        print("Mensaje (binario):", mensaje[:tamano])

    print("-------------------------")



def unix_to_ddmmyyyy(unixtime: int) -> str:
    tz = timezone(timedelta(hours=2))  # Spain current offset (CEST)
    fecha = datetime.fromtimestamp(unixtime, tz)

    return fecha.strftime("%d:%m:%Y_%H:%M:%S_")

def enviar(interfaz, ip, mensaje):

    canal = "mensajes"
    usuario = str(ip % 256)
    macdestino = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

    cadena_bytes = mensaje.encode()
    longitud_camposiguiente = len(cadena_bytes)

    tiempo = time.time()
    tiempo_b = unix_to_ddmmyyyy(tiempo).encode()
    canal_b = canal.encode().ljust(10, b'\x00')
    user_b = usuario.encode().ljust(10, b'\x00')
    len_b = len(cadena_bytes)
    len_b = len_b.to_bytes(4, byteorder="big")
    trama_chat = tiempo_b + canal_b + user_b + len_b + cadena_bytes

    longitud_camposiguiente = len(trama_chat)

    # Termina nuestra implementación
    enviado = sendEthernetFrame(trama_chat, longitud_camposiguiente, TYPE2, macdestino)

    if enviado == -1:
        print("Error enviando trama")


def init_recibir(interfaz):
    global canal
    canal = "mensajes"

    registerEthCallback(process_ethMsg_frame, TYPE2)
    signal.signal(signal.SIGINT, fn_signal)
