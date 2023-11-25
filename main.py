import Cotizador

def menu():
    print("*"*50)
    print("-"*13+"CONSULTA DE COTIZACIONES"+"-"*13)
    print("*"*50)
    print("[1] Histórico de Cotizaciones desde 2013")
    print("[2] Actualizar Cotizaciones a la fecha")
    print("[3] Consultar Cotizaciones por Fecha")
    print("[4] Consultar Cotizaciones por Rango de Fecha")
    print("[5] Consultar diferencia de Cotizaciones")
    print("[6] Chatbot de Cotizaciones (USD)")
    print("[0] Salir")
    print("-"*50)
    opcion = int(input("Elija una opción: "))
    print("-"*50)

    while opcion != 0:
        if opcion == 1:
            Cotizador.historicoCotizaciones()
            break
        if opcion == 2:
            Cotizador.actualizarCotizacionesALaFecha()
            break
        if opcion == 3:
            Cotizador.consultarCotizacionesPorFecha()
            break
        if opcion == 4:
            Cotizador.consultarCotizacionesPorRangoFecha()
            break
        if opcion == 5:
            Cotizador.consultarDiferenciaCotizaciones()
            break
        if opcion == 6:
            Cotizador.chatbotCotizaciones()
            break
        else:
            print("Opción inválida!")
            print("*"*50)
            print("-"*13+"CONSULTA DE COTIZACIONES"+"-"*13)
            print("*"*50)
            menu()
            print("-"*50)
            opcion = int(input("Elija una opción: "))

menu()
print("-"*50)
print("Gracias por utilizar el programa!")
print("-"*50)
exit()