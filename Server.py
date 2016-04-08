# Universidad de Costa Rica
# Escuela de Ciencias de la Computacion e Informatica
# CI-2413: Desarrollo de Aplicaciones Web
# - Carlos Mata Guzman
# - Fabian Rodriguez Obando
# Tarea 1: Mini servidor web
# I Semestre 2016

import socket, time, thread

# Variable que comparten todos los hilos
log = open("log.csv", "w")  # Donde se va a guardar la bitacora del programa
log.write("Metodo, Estampilla de tiempo, Servidor, Refiere, URL, Datos\n")
log.close()
log_lock = thread.allocate_lock()


# ---- Funciones del servidor ----

def WriteLog(new_data):
    log_lock.acquire()
    log = open("log.csv", "a")
    log.write(new_data)
    log.close()
    log_lock.release()


def Get(data, input_conection):
    print("Entre a GET")
    lines = data.split('\n')
    method = lines[0].split(' ')[0]
    timestamp = time.strftime("%c")
    server = lines[1].split(' ')[1]
    WriteLog(method + ", " + timestamp + ", " + server + '\n')

    # TODO: seguir el flowchart para revisar si todo cumple y retornar el codigo de respuesta
    return_code = 200  # Esto hay que cambiarlo dependiendo de si hubo error o no.
    data_return = "HTTP/1.1 "
    if return_code == 200:
        data_return += str(return_code)
        data_return += " OK\r\n\r\n"
        data_return = "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>User information</title></head><body><h1>Bienvenido</h1><h4>Mini servidor hecho en python</h4><hr/><p>A continuacion puede ingresar sus datos al sistema:</p><form method=\"post\"><label for=\"input_name\">Nombre:</label><br/><input type=\"text\" id=\"input_name\"><br/><label for=\"input_lastname\">Apellidos</label><br/><input type=\"text\" id=\"input_lastname\"><br/><label for=\"input_mail\">Correo:</label><br/><input type=\"email\" id=\"input_mail\"><br/><label for=\"input_date\">Fecha de nacimiento: </label><input type=\"date\" id=\"input_date\"><br/><input type=\"submit\" id=\"btn_submit\" value=\"Enviar datos\"></form><hr/></body></html>"
    elif return_code == 404:
        print("Error 404")
    elif return_code == 406:
        print("Error 406")

    return (data_return)


def Post(data, input_conection):
    print("Entre a POST")


def Head(data, input_conection):
    print("Entre a HEAD")


def ProcessData(thread_number, data, input_conection):
    print("Soy el hilo {}".format(thread_number))
    print(data)
    data_return = ""
    # Obtiene identifica el tipo de operacion y la ejecuta
    operation = data.split('\n')[0].split(' ')[0]
    if (operation == "GET"):
        data_return = Get(data, input_conection)
    elif (operation == "POST"):
        data_return = Post(data, input_conection)
    elif (operation == "HEAD"):
        data_return = Head(data, input_conection)
    input_conection.send(data_return)
    input_conection.close()


def OpenServer():
    server_port = 2080  # Puerto de escucha del servidor

    # --------------Conexion entrante-----------------
    # Creando el socket TCP/IP
    sock_input = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Enlace de socket y puerto conexion entrante
    server_address = ('localhost', server_port)
    sock_input.bind(server_address)

    # Escuchando conexiones entrantes
    sock_input.listen(10)
    thread_number = 1
    while True:
        try:
            input_connection, client_address = sock_input.accept()
            data = input_connection.recv(1024).decode()
            # Revisa que tenga datos
            if data:
                try:
                    thread.start_new_thread(ProcessData,
                                            (thread_number, data,
                                             input_connection))  # Crea el hilo para responder la solicitud
                    thread_number += 1
                except:
                    print("No se pudo crear el hilo")
        except:
            print("ERROR: no se pudo establecer conexion con el socket")
        sock_input.close()


# ----- Programa principal-----

OpenServer()
