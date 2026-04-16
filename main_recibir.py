#!/usr/bin/env python3

import sys
import signal
from ethernet import *
from datetime import datetime
import argparse

TYPE1 = 0x4444
TYPE2 = 0xAAAA

parar = 0
canal = ""


def fn_signal(signum, frame):
    global parar

    finalizar = stopEthernetLevel()

    if finalizar == -1:
        print("\nError finalizando")
        sys.exit(1)
    else:
        print("\nFinalizacion correcta")
        sys.exit(0)

    parar = 1


# Funcion de recepcion de mensajes
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

def main():

    global canal
    global parar

    timeout = 1000

    # LECTURA DE PARAMETROS DE ENTRADA
    parser = argparse.ArgumentParser( description="Main recibir tramas ethernet")
    parser.add_argument("-i", type=str, required=True, metavar="INTERFAZ", help="interfaz de red")
    parser.add_argument("-c", type=str, required=True, metavar="CANAL", help="canal")
    args = parser.parse_args()

    canal = args.c
    interfaz = args.i

    resultado = startEthernetLevel(interfaz)
    registerEthCallback(process_ethMsg_frame, TYPE2)

    if resultado == -1:
        print("Error inicializando Ethernet")
        return -1

    signal.signal(signal.SIGINT, fn_signal)

    while parar == 0:
        pass  # Bucle infinito NO modificar

    finalizado = stopEthernetLevel()

    if finalizado == -1:
        print("\nError finalizando")
        return 1
    else:
        print("\nFinalizacion correcta")
        return 0


if __name__ == "__main__":
    main()
