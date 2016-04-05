import socket, time, thread

# Variable que comparten todos los hilos
log = open("log.csv", "w")  # Donde se va a guardar la bitacora del programa
log.write("Metodo,Estampilla de tiempo,Servidor,Refiere,URL,Datos\n")

server_port = 2080  # Puerto de escucha del servidor


# ---- Funciones del servidor ----
def Get(data):
    print("Entre a GET")


def Post(data):
    print("Entre a POST")


def Head(data):
    print("Entre a HEAD")


def ProcessData(thread_number, data):
    print("Soy el hilo {}".format(thread_number))
    print(data)
    # Obtiene identifica el tipo de operacion y la ejecuta
    operation = data.split('\n')[0].split(' ')[0]
    if (operation == "GET"):
        Get(data)
    elif (operation == "POST"):
        Post(data)
    elif (operation == "HEAD"):
        Head(data)


def OpenServer():
    # --------------Conexion entrante-----------------
    # Creando el socket TCP/IP
    sock_input = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Enlace de socket y puerto conexion entrante
    server_address = ('localhost', server_port)
    sock_input.bind(server_address)

    # Escuchando conexiones entrantes
    sock_input.listen(10)
    input_connection, client_address = sock_input.accept()

    data_buffer = {}
    data_size = 10000
    thread_number = 1
    while len(data_buffer) < data_size <= 10000:

        # TODO: hacer los hilos
        try:
            data = input_connection.recv(1000).decode()
            # Revisa que tenga datos
            if data:
                thread.start_new_thread(ProcessData, (thread_number, data))
                thread_number += 1
        except:
            print("ERROR: no se pudo establecer conexion con el socket")
            break

    sock_input.close()


# ----- Programa (main)-----

OpenServer()
