"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
 * 
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
import sys
import folium
import threading
import controller
from DISClib.ADT.graph import gr
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import stack
assert cf


import time

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al catalogrolador para ejecutar la
operación solicitada
"""

# ___________________________________________________
#  Variables
# ___________________________________________________
countriesfile = 'countries.csv'
connectionsfile = 'connections.csv'
landingpointsfile = 'landing_points.csv'

catalog = None

# ___________________________________________________
#  Menu principal
# ___________________________________________________
def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("1- Cargar información en el catálogo")
    print("2- Econtrar clústers (components conectados)")
    print("3- Econtar puntos de interconexión")
    print("4- Econtrar ruta minima entre paises")
    print("5- Identificar infraestructura crítica")
    print("6- Impacto de fallo en un landing point")
    print("0- SALIR")
    print("*******************************************")


def optionTwo(catalog, lp1, lp2):
    "Req 1 -SCCs"
    lp_id1 = controller.getLandingPointId(catalog, lp1)
    lp_id2 = controller.getLandingPointId(catalog, lp2)   
    if (lp_id1 is not None) and (lp_id2 is not None):
        print(lp_id1, lp_id2)
        ans = controller.calcConnectedComponents(catalog, lp_id1, lp_id2)
        print('El número de clusteres en la red es: ' + str(ans[0]))
        if ans[1]: 
            print(lp1, "y", lp2, "estan en el mismo cluster")
        else:
            print(lp1, "y", lp2, "NO estan en el mismo cluster")
    else:
        print('Alguno de los Landinpoint no es válido')
        

def optionThree(catalog):
    """Req 2 - mapa de lps"""
    ans = controller.pointsInterconnection(catalog)
    print(ans[0])
    print(ans[1])
    item_map = folium.Map(location=[25.557547, -24.568953], zoom_start=2)
    for landinpoint in lt.iterator(ans[0]):
        item = mp.get(catalog['landingpoints'], landinpoint)['value']['info']
        print('Nombre:', item['id'], '\tLugar:', item['name'], '\tIdentificador: ', item['landing_point_id'])
        tooltip = item['id']
        item_lat = float(item['latitude'])
        item_lon = float(item['longitude'])
        cables = mp.get(catalog['landingpoints'], landinpoint)['value']['lstcables']
        folium.Marker(location=[item_lat, item_lon], popup="<strong></strong>", tooltip=tooltip).add_to(item_map)
        for cable in lt.iterator(mp.keySet(cables)): 
            cable = cable.split('-')[1:][0]
            cable_info = mp.get(catalog['landingpoints'], cable)['value']['info']
            cable_lat = float(cable_info['latitude'])
            cable_lon = float(cable_info['longitude'])
            tooltip_2 = cable_info['name']
            folium.Marker(location=[cable_lat, cable_lon], popup="<strong></strong>", tooltip=tooltip_2, color='red').add_to(item_map)
            folium.PolyLine([(item_lat, item_lon), (cable_lat, cable_lon)],
                color='grey',
                weight=2,
                opacity=0.6).add_to(item_map)


        

    item_map.save('Req 2.html')    

    print('\nHay', ans[1], 'cables conectados a dicho(s) landingpoints')
    # print(lt.size(mp.get(catalog['landingpoints'], 'Sofia')['value']['lstcables']))
    # print(lt.size(mp.get(catalog['landingpoints'], '3221')['value']['lstcables']))
    # print(gr.adjacentEdges(catalog['internet_graph'], 'Sofia'))

    
    


def optionFour(catalog, country_1, country_2):
    "Req 3 - Dijkstra"
    capital_1 = controller.getCapitalCity(catalog, country_1)
    capital_2 = controller.getCapitalCity(catalog, country_2)
    # print(capital_1, capital_2)
    if (capital_1 is not None) and (capital_2 is not None):
        
        # a = gr.getEdge(catalog['internet_graph'],'5693-Colombia-Florida Subsea Fiber (CFX-1)', '3563-Colombia-Florida Subsea Fiber (CFX-1)' )
        # b = gr.getEdge(catalog['internet_graph'],'3563-Colombia-Florida Subsea Fiber (CFX-1)', '3563-GigNet-1')
        # c = gr.getEdge(catalog['internet_graph'],'3563-GigNet-1', '3842-GigNet-1')

        # print(a, '-->', b, '-->', c)

        # print(gr.getEdge(catalog['internet_graph'],'10398', '10398-SednaLink Fibre'))

        # ans = controller.minimumDistanceCountries(catalog, '5693', '3842')
        # ans = controller.minimumDistanceCountries(catalog, '10398', '10398-SednaLink Fibre')

        # ans = controller.minimumDistanceCountries(catalog, '5693', '5693-Colombia-Florida Subsea Fiber (CFX-1)')

        # ans = controller.minimumDistanceCountries(catalog, 'Bogota', '5693')
        path = controller.minimumDistanceCountries(catalog, capital_1, capital_2)
        if path is not None:
            print("\nPresione 'enter' para ver el siguente\n")
            total_dist = 0.0
            while not stack.isEmpty(path):
                edge = stack.pop(path)
                total_dist += edge['weight']
                print(edge['vertexA'] + "-->" + edge['vertexB'] + " costo: " + str(edge['weight']) + " km")
                input()
        else:
            print('No existe el camino entre', capital_1, 'y', capital_2)
            
        print('El costo total es de ', total_dist, 'km')
    else:
        print('Alguno de los paises no fue valido')


def optionFive(catalog):
    "Req 4"
    ans = controller.findGraphMST(catalog)
    print("El número de nodos conectados a la red de expansión mínima es: ", ans[0])
    print("El costo total (distancia en [km]) de la red de expansión mínima es: ", ans[1])
    print("La rama más larga que hace parte de la red de expansión mínima : ")
    print(ans[2])
    prevEdge = None
    while not stack.isEmpty(ans[2][0]):
        edge = stack.pop(ans[2][0])
        if prevEdge is not None: 
            print(prevEdge + "-->" + edge)
        prevEdge = edge

    print('Esta rama tiene', ans[2][1], 'arcos')
    

def optionSix(catalog, landingpoint):
    "Req 5"
    lp_id = controller.getLandingPointId(catalog, landingpoint)
    if lp_id is not None:
        ans = controller.failureOfLP(catalog, lp_id)
        print('Hay', lt.size(ans), 'paises afectados')
        for country in lt.iterator(ans): 
            print('Pais:', country['country'], '\t Distancia:', country['distance'], 'km')
    else:
        print('El landingpoint no es válido')
    pass


def optionSeven(catalog):
    "Req 6 - Bono"
    pass


def optionEight(catalog):
    "Req 7 - Bono"
    pass


def thread_cycle():
    while True:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n>')
        if int(inputs[0]) == 1:
            print("Cargando información de los archivos ....")
            catalog = controller.loadData(connectionsfile, landingpointsfile, countriesfile)

            lps = lt.firstElement(mp.keySet(catalog["landingpoints"]))
            lp_info = mp.get(catalog["landingpoints"], lps)['value']['info']
            lp_infos = mp.get(catalog["landingpoints"], lps)['value']['lstcables']
            
            print("Cantidad de Landing Points: ", mp.size(catalog["landingpoints"]))
            print("Cantidad de conexiones entre Landing Points: ", gr.numEdges(catalog["internet_graph"]))
            print("Cantidad de paises: ", mp.size(catalog["countries"]))

            lps = lt.firstElement(mp.keySet(catalog["landingpoints"]))
            lp_info = mp.get(catalog["landingpoints"], lps)['value']['info']
            print('Primer landingpoint')
            print("Landing point id: ", lp_info['landing_point_id'], "id: ", lp_info['id'],"name: ", lp_info['name'],"latitude: ", lp_info['latitude'],"Longitude: ", lp_info["longitude"])
    
            countries = lt.firstElement(mp.keySet(catalog["countries"]))
            country_info = mp.get(catalog["countries"], countries)['value']
            print('Primer pais')
            print('CountryName: ', country_info['CountryName'], "Population: ", country_info['Population'], "Internet users: ", country_info['Internet users'])

        elif int(inputs[0]) == 2:
            lp1 = input('Ingrese el nombre del primer landing point: ')
            lp2 = input('Ingrese el nombre del segundo landing point: ')

            optionTwo(catalog, lp1, lp2)

        elif int(inputs[0]) == 3:
            optionThree(catalog)
    

        elif int(inputs[0]) == 4:
            country_1 = input('Ingrese el primer país: ')
            country_2 = input('Ingrese el segundo país: ')
            
            optionFour(catalog, country_1, country_2)

        elif int(inputs[0]) == 5:
            optionFive(catalog)

        elif int(inputs[0]) == 6:
            landingpoint = input('Ingrese el landinpoint: ')
            optionSix(catalog, landingpoint)

        elif int(inputs[0]) == 7:
            optionSeven(catalog)
        
        elif int(inputs[0]) == 8:
            optionEight(catalog)

        else:
            sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()