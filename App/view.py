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
    print("2- Ecatalograr clústers (components conectados)")
    print("3- Ecatalograr puntos de interconexión")
    print("4- Ecatalograr ruta minima entre paises")
    print("5- Identificar infraestructura crítica")
    print("6- Impacto de fallo en un landing point")
    print("*******************************************")


def optionTwo(catalog):
    "Req 1"
    pass


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
        inputs = input('Seleccione una opción para cataloginuar\n')
        if int(inputs[0]) == 1:
            print("Cargando información de los archivos ....")
            catalog = controller.loadData(connectionsfile, landingpointsfile, countriesfile)
            # b = gr.vertices(catalog["internet_graph"])
            # a = gr.edges(catalog["internet_graph"])
            # for i in lt.iterator(b): 
            #     print(i)
            # for x in lt.iterator(a):
            #     print(x)

            # print(gr.numVertices(catalog["internet_graph"]))
            # print(mp.size(catalog["landingpoints"]))
            # print(mp.get(catalog["landingpoints"], '5901')['value'])
            # print(gr.numEdges(catalog["internet_graph"]))
            # print(gr.getEdge(catalog["internet_graph"], "10726-West African Cable System (WACS)", "4181-West African Cable System (WACS)"))
            # print(gr.getEdge(catalog["internet_graph"], "17027-GTMO-PR", "17027-GTMO-1"))
            
        elif int(inputs[0]) == 2:
            pass

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