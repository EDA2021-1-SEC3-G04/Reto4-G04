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
import threading
import controller
from DISClib.ADT.graph import gr
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
assert cf


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
    "Req 1"
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
    "Req 2"
    pass


def optionFour(catalog):
    "Req 3"
    pass


def optionFive(catalog):
    "Req 4"
    pass


def optionSix(catalog):
    "Req 5"
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
        inputs = input('Seleccione una opción para cataloginuar\n>')
        if int(inputs[0]) == 1:
            print("Cargando información de los archivos ....")
            catalog = controller.loadData(connectionsfile, landingpointsfile, countriesfile)

            lps = lt.firstElement(mp.keySet(catalog["landingpoints"]))
            lp_info = mp.get(catalog["landingpoints"], lps)['value']['info']
            lp_infos = mp.get(catalog["landingpoints"], lps)['value']['lstcables']
            for x in lt.iterator(lp_infos):
                print(gr.getEdge(catalog['internet_graph'], lp_info['landing_point_id'],lp_info['landing_point_id']+'-'+x))


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
            
            optionFour(catalog)

        elif int(inputs[0]) == 5:
            optionFive(catalog)

        elif int(inputs[0]) == 6:
            optionSix(catalog)

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