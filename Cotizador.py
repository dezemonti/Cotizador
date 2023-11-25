from requests import Session
from lxml import html
from datetime import *
from tabulate import tabulate
from DBHelper import DBHelper

session= Session()

session.get("http://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda.asp")

Monedas=[
    {"nombre":"Peso Argentino","codigo":80,"codigoBCRA":"ARS","idmoneda":1},
    {"nombre":"Peso Chileno","codigo":11,"codigoBCRA":"CLP","idmoneda":2},
    {"nombre":"Real Brasilero","codigo":12,"codigoBCRA":"RS","idmoneda":3},
    {"nombre":"Dólar Estadounidense","codigo":2,"codigoBCRA":"USD","idmoneda":4}
]

dbHelper = DBHelper()

def historicoCotizaciones():
    print("*"*55)
    print("-"*15+"HISTÓRICO DE COTIZACIONES"+"-"*15)
    print("*"*55)

    req=input("¿Desea borrar la Base de Datos y obtener el Registro Histórico desde 2013 a la fecha? (S/N): ")
    if req == 'S':
        dbHelper.DBQuery("TRUNCATE FROM cotizaciones")
        dbHelper.commit()
        for moneda in Monedas:
            payload={
                "Fecha":"2013.1.1",
                "Moneda":moneda['codigo']
            }
            request=session.post(url="http://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda_2.asp", data=payload)

            tree = html.fromstring(request.text)
            filas= tree.xpath("//table/tr")
            for fila in filas:
                arrayCotizacion=[]
                arrayCotizacion.append({"fecha":fila[0].text.replace("\r","").replace("\n","")})
                arrayCotizacion.append({"id_monedas":moneda['idmoneda']})
                arrayCotizacion.append({"nombre":moneda['nombre']})
                arrayCotizacion.append({"valor_usd":fila[1].text.replace("\r","")})
                arrayCotizacion.append({"valor_peso":fila[2].text.replace("\r","")})
                dbHelper.DBQuery(dbHelper.constructorInsert("cotizaciones", arrayCotizacion))
                print("Insertado: "+str(fila[0].text.replace("\r","").replace("\n",""))+"   "+ moneda['nombre'])

        dbHelper.commit()
        from main import menu
        menu()
    else:
        from main import menu
        menu()

def actualizarCotizacionesALaFecha():
    print("*"*55)
    print("-"*16+"ACTUALIZAR COTIZACIONES"+"-"*16)
    print("*"*55)

    print("Para actualizar la Base de Datos, la misma debe contener registros...")
    query = input("¿Realizó la carga inicial desde el Histórico de Cotizaciones? (S/N): ")
    print("-"*55)
    if query == 'S':
        lastDate = dbHelper.DBQuery("SELECT fecha FROM cotizaciones ORDER BY id DESC LIMIT 1;")
        dbHelper.commit()
        print("La última cotización en Base de Datos es del "+lastDate[0]['fecha']+"")
        req=input("¿Quiere actualizar la Base de Datos al día de la fecha? (S/N): ")
        nextDate = date(int(lastDate[0]['fecha'][0:4]),int(lastDate[0]['fecha'][5:7]),int(lastDate[0]['fecha'][8:10])) + timedelta(days=1)
        nextDate = nextDate.strftime('%Y.%m.%d')
        if req == 'S':
            for moneda in Monedas:
                payload={
                    "Fecha":nextDate,
                    "Moneda":moneda['codigo']
                }
                request=session.post(url="http://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda_2.asp", data=payload)

                tree = html.fromstring(request.text)
                filas= tree.xpath("//table/tr")
                for fila in filas:
                    arrayCotizacion=[]
                    arrayCotizacion.append({"fecha":fila[0].text.replace("\r","").replace("\n","")})
                    arrayCotizacion.append({"id_monedas":moneda['idmoneda']})
                    arrayCotizacion.append({"nombre":moneda['nombre']})
                    arrayCotizacion.append({"valor_usd":fila[1].text})
                    arrayCotizacion.append({"valor_peso":fila[2].text})
                    dbHelper.DBQuery(dbHelper.constructorInsert("cotizaciones", arrayCotizacion))
                    print("Insertado: "+str(fila[0].text.replace("\r","").replace("\n",""))+"   "+ moneda['nombre'])

            dbHelper.commit()
            from main import menu
            menu()
        else:
            from main import menu
            menu()
    else:
        from main import menu
        menu()

def consultarCotizacionesPorFecha():
    print("*"*50)
    print("-"*9+"CONSULTAR COTIZACIONES POR FECHA"+"-"*9)
    print("*"*50)

    print("Tipos de Moneda")
    print("-"*50)
    print("[1] Peso Argentino (ARS)")
    print("[2] Peso Chileno (CLP)")
    print("[3] Real Brasilero (RS)")
    print("[4] Dólar Estadounidense (USD)")
    print("-"*50)
    tipoMoneda = input("Ingrese el tipo de moneda: ")
    fechaInicio = input("Ingrese la fecha (DD/MM/YYYY): ")

    fechaInicio = dbHelper.ArreglarFechaSQL(fechaInicio)

    rows=dbHelper.DBQuery("SELECT c.fecha,c.nombre,c.valor_usd,c.valor_peso FROM cotizaciones AS c JOIN monedas AS m WHERE c.fecha = '"+fechaInicio+"' AND c.id_monedas = "+tipoMoneda+" AND c.id_monedas = m.id;")
    dbHelper.commit()
    table = []
    table.append(["Fecha","Nombre","Valor USD","Valor PESOS"])
    if rows is None:
        print("No se obtuvo una respuesta de la Base de Datos.")
        req=input("¿Desea realizar una nueva consulta? (S/N): ")
        if req == 'S':
            consultarCotizacionesPorFecha()
        else:
            from main import menu
            menu()
    else:
        for row in rows:
            table.append([
                dbHelper.ArreglarFecha(row['fecha']),
                row['nombre'],
                row['valor_usd'],
                row['valor_peso']
            ])
    print(tabulate(table,headers='firstrow',tablefmt="fancy_grid"))
    print("-"*50)
    req=input("¿Desea realizar una nueva consulta? (S/N): ")
    if req == 'S':
        consultarCotizacionesPorFecha()
    else:
        from main import menu
        menu()

def consultarCotizacionesPorRangoFecha():
    print("*"*55)
    print("-"*7+"CONSULTAR COTIZACIONES POR RANGO DE FECHA"+"-"*7)
    print("*"*55)

    print("-"*20+"Tipos de Moneda"+"-"*20)
    print("-"*55)
    print("[1] Peso Argentino (ARS)")
    print("[2] Peso Chileno (CLP)")
    print("[3] Real Brasilero (RS)")
    print("[4] Dólar Estadounidense (USD)")
    print("-"*55)
    tipoMoneda = input("Ingrese el tipo de moneda: ")
    fechaInicio = input("Ingrese la fecha inicial (DD/MM/YYYY): ")
    fechaFinal = input("Ingrese la fecha final (DD/MM/YYYY): ")

    fechaInicio = dbHelper.ArreglarFechaSQL(fechaInicio)
    fechaFinal = dbHelper.ArreglarFechaSQL(fechaFinal)

    rows=dbHelper.DBQuery("SELECT c.fecha,c.nombre,c.valor_usd,c.valor_peso FROM cotizaciones AS c JOIN monedas AS m WHERE c.fecha BETWEEN '"+fechaInicio+"' AND '"+fechaFinal+"' AND c.id_monedas = "+tipoMoneda+" AND c.id_monedas = m.id;")
    dbHelper.commit()
    table = []
    table.append(["Fecha","Nombre","Valor USD","Valor PESOS"])
    if rows is None:
        print("No se obtuvo una respuesta de la Base de Datos.")
        req=input("¿Desea realizar una nueva consulta? (S/N): ")
        if req == 'S':
            consultarCotizacionesPorRangoFecha()
        else:
            from main import menu
            menu()
    else:
        for row in rows:
            table.append([
                dbHelper.ArreglarFecha(row['fecha']),
                row['nombre'],
                row['valor_usd'],
                row['valor_peso']
            ])
    print(tabulate(table,headers='firstrow',tablefmt="fancy_grid"))
    print("-"*50)
    req=input("¿Desea realizar una nueva consulta? (S/N): ")
    if req == 'S':
        consultarCotizacionesPorRangoFecha()
    else:
        from main import menu
        menu()

def consultarDiferenciaCotizaciones():
    
    def convertirValorNulo(valor):
        return 0 if valor.startswith('-') else float(valor)
    
    def calcularPorcentaje(valor1,valor2):
        if valor1 == 0 or valor2 == 0:
            return 0
        return valor2/valor1
    
    print("*"*55)
    print("-"*10+"CONSULTAR DIFERENCIAS DE COTIZACION"+"-"*10)
    print("*"*55)

    print("-"*20+"Tipos de Moneda"+"-"*20)
    print("-"*55)
    print("[1] Peso Argentino (ARS)")
    print("[2] Peso Chileno (CLP)")
    print("[3] Real Brasilero (RS)")
    print("[4] Dólar Estadounidense (USD)")
    print("-"*55)
    tipoMoneda = input("Ingrese el tipo de moneda: ")
    fechaInicio = input("Ingrese la fecha Base (DD/MM/YYYY): ")
    fechaFinal = input("Ingrese la fecha A Comparar (DD/MM/YYYY): ")

    fechaInicio = dbHelper.ArreglarFechaSQL(fechaInicio)
    fechaFinal = dbHelper.ArreglarFechaSQL(fechaFinal)

    rows=dbHelper.DBQuery("SELECT c.fecha,c.nombre,c.valor_usd,c.valor_peso FROM cotizaciones AS c JOIN monedas AS m WHERE c.fecha = '"+fechaInicio+"' AND c.id_monedas = "+tipoMoneda+" AND c.id_monedas = m.id OR fecha = '"+fechaFinal+"' AND c.id_monedas = "+tipoMoneda+" AND c.id_monedas = m.id;")
    dbHelper.commit()

    tableUSD = []
    tableARS = []
    tableUSD.append(["Moneda","Fecha Base","Valor USD","Fecha Comparada","Valor USD","Diferencia (%)"])
    tableARS.append(["Moneda","Fecha Base","Valor PES","Fecha Comparada","Valor PES","Diferencia (%)"])

    if rows is None:
        print("No se obtuvo una respuesta de la Base de Datos.")
        req=input("¿Desea realizar una nueva consulta? (S/N): ")
        if req == 'S':
            consultarDiferenciaCotizaciones()
        else:
            from main import menu
            menu()
    else:
        if len(rows) == 2:
            valorUSD1 = convertirValorNulo(rows[0]['valor_usd'])
            valorARS1 = convertirValorNulo(rows[0]['valor_peso'])
            valorUSD2 = convertirValorNulo(rows[1]['valor_usd'])
            valorARS2 = convertirValorNulo(rows[1]['valor_peso'])
            difPercentUSD = calcularPorcentaje(valorUSD1,valorUSD2)
            difPercentARS = calcularPorcentaje(valorARS1,valorARS2)
            tableUSD.append([
                rows[0]['nombre'],
                dbHelper.ArreglarFecha(rows[0]['fecha']),
                rows[0]['valor_usd'],
                dbHelper.ArreglarFecha(rows[1]['fecha']),
                rows[1]['valor_usd'],
                difPercentUSD
            ])
            tableARS.append([
                rows[1]['nombre'],
                dbHelper.ArreglarFecha(rows[0]['fecha']),
                rows[0]['valor_peso'],
                dbHelper.ArreglarFecha(rows[1]['fecha']),
                rows[1]['valor_peso'],
                difPercentARS
            ])
            print(tabulate(tableUSD,headers='firstrow',tablefmt="fancy_grid"))
            print("+"*50)
            print(tabulate(tableARS,headers='firstrow',tablefmt="fancy_grid"))
            print("-"*50)
            req=input("¿Desea realizar una nueva consulta? (S/N): ")
            if req == 'S':
                consultarDiferenciaCotizaciones()
            else:
                from main import menu
                menu()
        else:
            print("No se obtuvo una respuesta de la Base de Datos.")
            req=input("¿Desea realizar una nueva consulta? (S/N): ")
            if req == 'S':
                consultarDiferenciaCotizaciones()
            else:
                from main import menu
                menu()

def chatbotCotizaciones():
    print(f'Servidor iniciado. Ejecute un Cliente de Chatbot...')
    import ChatbotServer