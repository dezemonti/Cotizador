import socket
import threading
import json
from DBHelper import DBHelper

dbHelper = DBHelper()
HOST = "127.0.0.1"
PORT = 2345

def startServer(HOST,PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(name=f'Usuario {addr}',target=client_thread, args=(conn,addr))
            print("#"*50)
            print(f'Se conectó {thread.name}')
            thread.start()
            exit()

def client_thread(conn, addr):
    clientThread = threading.current_thread().name
    try:
        print(f'Ejecutando Servidor. Esperando consulta del Usuario...')
        while True:
            data = conn.recv(1024).decode('utf-8')
            while data != '':
                if data == 'Volver':
                    conn.sendall(bytes(data,encoding='utf-8'))
                    break
                print(f'Consulta recibida!')
                print(f' {clientThread} consulta cotización USD en fecha:', data)
                data = dbHelper.ArreglarFechaSQL(data)
                resp = dbHelper.DBQuery("SELECT fecha, nombre, valor_usd, valor_peso FROM cotizaciones WHERE fecha = '"+data+"' AND id_monedas = 4;")
                dbHelper.commit()
                if len(resp) > 0:
                    resp_bytes = json.dumps(resp).encode('utf-8')
                    conn.sendall(resp_bytes)
                    print(f'Ejecutando Servidor. Esperando consulta del Usuario...')
                else:
                    errorMsg = '404'
                    conn.sendall(bytes(errorMsg,encoding='utf-8'))
                data = conn.recv(1024).decode('utf-8')
            print("*"*50)
            resp = input("¿Desea detener el servidor? (S/N): ")
            if resp == 'S':
                from main import menu
                menu()
            if resp == 'N':
                startServer(HOST,PORT)
    except Exception as e:
        print(f'Error cuando se manejaba el usuario: {e}')
    finally:
        print(f'Conexion con el Usuario ({addr[0]}:{addr[1]}) cerrada')
        conn.close()

startServer(HOST,PORT)