import socket

# --------------Conexion entrante-----------------
# Creando el socket TCP/IP
sock_input = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enlace de socket y puerto conexion entrante
server_address = ('localhost', 1080)
sock_input.bind(server_address)

# Escuchando conexiones entrantes
sock_input.listen(10)
input_connection, client_address = sock_input.accept()

data_buffer = {}
data_size = 10000

while len(data_buffer) < data_size <= 10000:

    try:
        data = input_connection.recv(1000).decode()
        print(data)

    except:
        break

sock_input.close()
