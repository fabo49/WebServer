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
log.write("Metodo,Estampilla de tiempo,Servidor,Refiere,URL,Datos\n")
log.close()
log_lock = thread.allocate_lock()


# ---- Funciones del servidor ----

# Crea un diccionario con los datos del encabezado (key) y sus datos (value),
# esto para facilitar la busqueda y operaciones de los mismos
def DicData(data):
    list_headers = data.split('\n')
    dict = {} # Crea el diccionario vacio
    for header in list_headers:
        if header != '\r' and header != '':
            if header.find(' ') == -1:
                # Si es un POST, en la ultima hilera lo que viene son los parametros
                dict["Params:"] = header
            else:
                line = header.split(' ', 1)
                dict[line[0]] = line[1]
    return dict


def WriteLog(new_data):
    log_lock.acquire()
    log = open("log.csv", "a")
    log.write(new_data)
    log.close()
    log_lock.release()


def Get(dic_headers):
    print "--- Entre a GET"

    # El [:-1] es para quitarle el "\r" ya que molesta para la bitacora
    server = dic_headers["Host:"][:-1] if "Host:" in dic_headers else " "
    referer = dic_headers["Referer:"][:-1] if "Referer:" in dic_headers else " "
    timestamp = time.strftime("%c")
    data_url = dic_headers["GET"].split(" ")[0]
    url = data_url.split("?")[0]
    data = data_url.split("?")[1] if len(data_url.split("?")) > 1 else " "
    WriteLog("GET" + ',' + timestamp + ',' + server + ',' + referer + ',' + url + ',' + data + '\n')
    data_return = "HTTP/1.1 200 OK\r\n\r\n"

    entity_body = open("index.html", 'r')
    data_return += str(entity_body.read())
    entity_body.close()

    print "--- Salgo del GET"
    return data_return


def Post(dic_headers):
    print "--- Entro al POST"

    server = dic_headers["Host:"][:-1] if "Host:" in dic_headers else " "
    referer = dic_headers["Referer:"][:-1] if "Referer:" in dic_headers else " "
    timestamp = time.strftime("%c")
    data_url = dic_headers["POST"].split(" ")[0]
    url = data_url.split("?")[0]
    # Esto es solo si se ocupan sacar tambien las variables de la URL:
    # data += dic_headers.split("?")[1] if len(data_url.split("?")) > 1 else " "
    data = dic_headers["Params:"]
    WriteLog("POST" + ',' + timestamp + ',' + server + ',' + referer + ',' + url + ',' + data + '\n')
    data_return = "HTTP/1.1 200 OK\r\n\r\n"

    user_info = data.replace('+', ' ').split('&')
    user_name = str(user_info[0].split('=')[1] + " " + user_info[1].split('=')[1])
    fin = open("user_welcome.html", 'r')
    data_return += str(fin.read())%(user_name)
    fin.close()

    print "--- Salgo del POST"
    return data_return




def Head(data):
    print "--- Entro al HEAD"

    print "--- Salgo del HEAD"


def ProcessData(thread_number, data, input_conection):
    print "----- Soy el hilo {} -----".format(thread_number)
    print "Datos del header:"
    print data

    # Identifica el tipo de operacion y la ejecuta
    operation = data.split('\n')[0].split(' ')[0]
    dic_headers = DicData(data)

    # TODO: buscar si hay error 404 o 406

    data_return = ""
    if (operation == "GET"):
        data_return = Get(dic_headers)
    elif (operation == "POST"):
        data_return = Post(dic_headers)
    elif (operation == "HEAD"):
        data_return = Head(dic_headers)

    # Le envia la info al navegador
    input_conection.send(data_return)
    input_conection.close()


def OpenServer():
    server_port = 1080  # Puerto de escucha del servidor

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
            #print("ERROR: no se pudo establecer conexion con el socket")
            pass
    sock_input.close()


# ----- Programa principal-----

OpenServer()
