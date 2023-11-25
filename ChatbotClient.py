import socket
import json
from tabulate import tabulate
from DBHelper import DBHelper

HOST = "127.0.0.1"
PORT = 2345

dbHelper = DBHelper()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    def consultarCotizacion():
            msg = input('Ingrese una fecha (DD/MM/YYYY) o escriba "V" para volver: ')
            if msg != '':
                if msg == 'V':
                    menuChatbotClient()
                else:
                    s.sendall(bytes(msg, encoding='ascii'))
                    data_bytes = s.recv(1024)
                    if data_bytes.decode('utf-8') == '404':
                        print("#"*30)
                        print(f'No se encontró respuesta.')
                        print("#"*30)
                        menuChatbotClient()
                    else:
                        data = json.loads(data_bytes.decode('utf-8'))
                        while data:
                            if isinstance(data,list):
                                if len(data) > 0:
                                    print(f'Cotización recibido!')
                                    print(f'ChatbotCotizaciones dice:')
                                    table = ["Fecha",dbHelper.ArreglarFecha(data[0]['fecha'])],["Nombre",data[0]['nombre']],["Valor USD",data[0]['valor_usd'].replace("\r","")],["Valor PESOS",data[0]['valor_peso'].replace("\r","")]
                                    print(tabulate(table,tablefmt="fancy_grid"))
                                    msg = input('Ingrese una fecha (DD/MM/YYYY) o escriba "V" para volver: ')
                                    if msg == 'V':
                                        menuChatbotClient()
                                        break
                                    else:
                                        s.sendall(bytes(msg, encoding='ascii'))
                                        data_bytes = s.recv(1024)
                                        if data_bytes.decode('utf-8') == '404':
                                            print("#"*30)
                                            print(f'No se encontró respuesta.')
                                            print("#"*30)
                                            menuChatbotClient()
                                            break
                                        else:
                                            data = json.loads(data_bytes.decode('utf-8'))
                            else:
                                print(f'Conexión con Servidor {HOST}:{PORT} finalizada.')
                                s.close()
                                break
            else:
                print("*"*30)
                print("Opción inválida!")
                print("*"*30)
                msg = input('Ingrese una fecha (DD/MM/YYYY): ')

    def menuChatbotClient():
        print("[1] Iniciar la consulta")
        print("[0] Salir")
        print("-"*30)
        opcion = int(input("Elija una opción: "))
        print("-"*30)

        while opcion != 0:
            if opcion == 1:
                consultarCotizacion()
                break
            else:
                print("Opción inválida!")
                print("#"*30)
                print("-"+"CONSULTA DE COTIZACIONES USD"+"-")
                print("#"*30)
                menuChatbotClient()
                print("-"*30)
                opcion = int(input("Elija una opción: "))
        
    print("*"*30)
    print(f'Conectado a {HOST}:{PORT}')
    print("#"*30)
    print("-"+"CONSULTA DE COTIZACIONES USD"+"-")
    print("#"*30)
    menuChatbotClient()
    print("Gracias por utilizar el programa!")
    print("-"*30)