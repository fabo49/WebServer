import socket, time, thread, os

# Universidad de Costa Rica
# Escuela de Ciencias de la Computacion e Informatica
# CI-2413: Desarrollo de Aplicaciones Web
# - Carlos Mata Guzman
# - Fabian Rodriguez Obando
# Tarea 1: Mini servidor web http
# I Semestre 2016

# Variable que comparten todos los hilos
log = open("log.csv", "w")  # Donde se va a guardar la bitacora del programa
log.write("Metodo,Estampilla de tiempo,Servidor,Refiere,URL,Datos\n")
log.close()
log_lock = thread.allocate_lock()


# ---- Funciones del servidor ----

# @definition: Crea un diccionario con los datos del encabezado (key) y sus datos (value).
# @param: String con los encabezados a como los envia el navegador.
# @return: El diccionario recien creado.
def DicData(data):
    list_headers = data.split('\n')
    dict = {}  # Crea el diccionario vacio
    for header in list_headers:
        if header != '\r' and header != '':
            if header.find(' ') == -1:
                # Si es un POST, en la ultima hilera lo que viene son los parametros
                dict["Params:"] = header
            else:
                line = header.split(' ', 1)
                dict[line[0]] = line[1]
    return dict


# @definition: Retorna el MIME Type al que pertenece la extension, acepta los siguientes tipos: html, png, xml, jpg, jpeg y pdf
# @param: String donde viene el campo URL que se muestra en la bitacora
# @return: String con el MIME Type del archivo
def GetMimeType(url):
    my_types = {'html': 'text/html', 'png': 'image/png', 'jpeg': 'image/jpeg', 'jpg': 'image/jpeg', 'xml': 'text/xml',
                'pdf': 'application/pdf', 'csv': 'text/csv'}
    return my_types['html'] if url == '/' else my_types[url.split('.')[1]]


# @definition: Metodo que crea el encabezado que va a retornar el servidor
# @param: "first_header" en donde viene el codigo que se le va a retornar el cliente
# @param: "url" donde viene el nombre del archivo que solicito el cliente
# @return: String con el encabezado
def CreaterHeaderReturn(first_header, url):
    header = first_header
    header += "Server: mApache\r\n"
    header += "Date: " + time.strftime("%c") + "\r\n"
    header += "Content-Length: "
    header += str(os.path.getsize(url[1:])) if url != '/' else str(os.path.getsize("index.html"))
    header += "\r\n"
    header += "Content-Type: " + GetMimeType(url) + "\r\n\r\n"
    return header


# @definition: Metodo auxiliar que escribe en la bitacora, al ser un recurso compartido, se encarga de bloquearlo para que solo haya un hilo escribiendo en ella a la vez.
# @param: String con la informacion que se quiere escribir en la bitacora.
def WriteLog(new_data):
    log_lock.acquire()
    log = open("log.csv", "a")
    log.write(new_data)
    log.close()
    log_lock.release()


# @definition: Metodo que revisa si el archivo solicitado se encuentra en el servidor.
# @param: La ruta del archivo a buscar.
# @return: False si no hay error 404, True si si hay error.
def Check404Error(path):
    if os.path.isfile(path):
        return False
    return True


# @definition: Metodo que revisa si el tipo solicitado esta dentro de los MIME Types del servidor.
# @param: Un string (separado por comas ",") con los MIME Types que acepta/quiere el cliente.
# @return: False si no hay error 406, True si si hay error.
def Check406Error(mime_types, type):
    type = type[(type.rfind('.') + 1):]
    acceptable_types = []
    mime_types = mime_types.split(',')
    for element in mime_types:
        element = element.split(';')[0].replace('\r', '')
        acceptable_types.append(element.split('/')[1])
    if '*' in acceptable_types:
        return False
    return False if type in acceptable_types else True


# @definition: Evento que se activa cuando el servidor recibe una peticion de un GET.
# @param: Diccionario con los headers
# @return: String con la informacion que el servidor le va a retornar al cliente.
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
    data_return = CreaterHeaderReturn("HTTP/1.1 200 OK\r\n", url)

    if url == '/' or url == '/index.html':
        entity_body = open("index.html", 'r')
        data_return += str(entity_body.read())
        entity_body.close()
    else:
        # Ignoramos las peticiones por el favicon.ico que hace el navegador
        if url[1:] != "favicon.ico":
            entity_body = open(url[1:], 'r')
            data_return += str(entity_body.read())
            entity_body.close()

    print "--- Salgo del GET"
    return data_return


# @definition: Evento que se activa cuando el servidor recibe una peticion de un POST.
# @param: Diccionario con los headers
# @return: String con la informacion que el servidor le va a retornar al cliente.
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
    data_return = CreaterHeaderReturn("HTTP/1.1 200 OK\r\n", url)

    user_info = data.replace('+', ' ').split('&')
    user_name = str(user_info[0].split('=')[1] + " " + user_info[1].split('=')[1])
    fin = open("user_welcome.html", 'r')
    data_return += str(fin.read()) % (user_name.encode('utf-8'))
    fin.close()

    print "--- Salgo del POST"
    return data_return


# @definition: Evento que se activa cuando el servidor recibe una peticion de un HEAD.
# @param: Diccionario con los headers
# @return: String con la informacion que el servidor le va a retornar al cliente.
def Head(dic_headers):
    print "--- Entro al HEAD"
    # El [:-1] es para quitarle el "\r" ya que molesta para la bitacora
    server = dic_headers["Host:"][:-1] if "Host:" in dic_headers else " "
    referer = dic_headers["Referer:"][:-1] if "Referer:" in dic_headers else " "
    timestamp = time.strftime("%c")
    data_url = dic_headers["HEAD"].split(" ")[0]
    url = data_url.split("?")[0]
    data = data_url.split("?")[1] if len(data_url.split("?")) > 1 else " "
    WriteLog("HEAD" + ',' + timestamp + ',' + server + ',' + referer + ',' + url + ',' + data + '\n')
    data_return = CreaterHeaderReturn("HTTP/1.1 200 OK\r\n", url)

    print "--- Salgo del HEAD"

    return data_return


# @definition: Metodo que analiza los encabezados que recibe el servidor y ejecuta la peticion que corresponda.
# @params: Int con el numero de hilo, String con la informacion de los encabezados a como los envia el navegador, Socket de la conexion entrante
def ProcessData(thread_number, data, input_conection):
    print "----- Soy el hilo {} -----".format(thread_number)
    print "Datos del header:"
    print data

    data_return = ""
    first_header = data.split('\n')[0]
    url = first_header.split(' ')[1]
    if url != '/' and Check404Error(url[1:]):
        # Hay error 404, retornar error de codigo 404 y la pagina de error
        data_return = CreaterHeaderReturn("HTTP/1.1 404 Not Found\r\n", "/404.html")
        entity_body = open("404.html", 'r')
        data_return += str(entity_body.read())
        entity_body.close()
    else:
        dic_headers = DicData(data)
        if Check406Error(dic_headers["Accept:"], url[1:]):
            # Hay error 406, retornar error de codigo 406.
            data_return = CreaterHeaderReturn("HTTP/1.1 406 Not Acceptable\r\n", "/406.html")
            entity_body = open("406.html", 'r')
            data_return += str(entity_body.read())
            entity_body.close()
        else:
            # No hubo errores.
            operation = data.split('\n')[0].split(' ')[0]  # Identifica el tipo de operacion y la ejecuta

            if (operation == 'GET'):
                data_return = Get(dic_headers)
            elif (operation == 'POST'):
                data_return = Post(dic_headers)
            elif (operation == 'HEAD'):
                data_return = Head(dic_headers)

    # Le envia la info al navegador y cierra la conexion
    input_conection.send(data_return)
    time.sleep(1)
    input_conection.close()


# @definition: Metodo que "levanta" el servidor  y lo deja ejecutando infinitamente.
def OpenServer():
    server_port = int(
        input('Ingrese el puerto de escucha del servidor: '))  # Puerto de escucha del servidor, se lo pide al usuario
    print 'El servidor esta corriendo en \"localhost:'+str(server_port)+'\"...'

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
            # print("ERROR: no se pudo establecer conexion con el socket")
            pass
    sock_input.close()


# ----- Programa principal-----

OpenServer()
