"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.ADT.graph import gr
from DISClib.Utils import error as error
import haversine as hs
assert cf



"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

def initCatalog():
    catalog = {"landing_points":None, "internet_graph":None, "components":None, "paths":None, "countries":None, "cables": None}
    catalog['landingpoints'] = mp.newMap(numelements=14000, maptype='PROBING')
    catalog["cables"] = mp.newMap(numelements=14000, maptype='PROBING')
    catalog["countries"] = mp.newMap(numelements=14000, maptype='PROBING')
    catalog['internet_graph'] = gr.newGraph(datastructure='ADJ_LIST', 
                                    directed=True, 
                                    size=14000, 
                                    comparefunction= cmpLandingPoints)
    return catalog


# connections.csv
def addConnections(catalog, connection):
    origin_lp = connection["origin"]
    destination_lp = connection["destination"]
    cable = connection["cable_name"]
    cable_length = connection["cable_length"]
    bandwidth = connection["capacityTBPS"]
    # TODO: checkdistance _ distancia entre dos puntos o length
    origin = formatVertex(origin_lp, cable)
    destination = formatVertex(destination_lp, cable)
    addCableInfo(catalog, connection)


    addLPVertex(catalog, origin)
    addLPVertex(catalog, destination)
    addCable(catalog, origin, destination, cable_length)
    addCableLanding(catalog, origin_lp, cable)
    addCableLanding(catalog, destination_lp, cable)
    
    return catalog


def addLPVertex(catalog, landingPt_id):
    try:
        if not gr.containsVertex(catalog['internet_graph'], landingPt_id):
            gr.insertVertex(catalog['internet_graph'], landingPt_id)
        return catalog
    except Exception as exp:
        error.reraise(exp, 'model:addstop')
    

def addCable(catalog, origin, destination, distance):
    edge = gr.getEdge(catalog['internet_graph'], origin, destination)
    if edge is None:
        gr.addEdge(catalog['internet_graph'], origin, destination, distance)
    return catalog


def addCableLanding(catalog, landingPt, cable):
    """Añade un cable a la lista para cada landinpoint"""
    entry = mp.get(catalog['landingpoints'], landingPt)
    if entry is None:
        lstcables = lt.newList(datastructure='ARRAY_LIST')
        lt.addLast(lstcables, cable)
        mp.put(catalog['landingpoints'], landingPt, lstcables)
    else:
        lstcables = entry['value']
        if not lt.isPresent(lstcables, cable):
            lt.addLast(lstcables, cable)
    return catalog


def addLandingPointConnections(catalog):
    """Conexiones entre vertices de un landinpoint"""
    lstLandingPts = mp.keySet(catalog['landingpoints'])
    for key in lt.iterator(lstLandingPts):
        lstCables = mp.get(catalog['landingpoints'], key)['value']
        prevCable = None
        for cable in lt.iterator(lstCables):
            cable = key + '-' + cable
            if prevCable is not None:
                addCable(catalog, cable, prevCable, 100)
            prevCable = cable
        createLocalCable(catalog, key)
    return catalog

def createLocalCable(catalog, landingpoint): 
    cable_lst = mp.get(catalog['landingpoints'], landingpoint)['value']
    
    min_bandwith = 100000.00
    min_cable = ""

    for cable in lt.iterator(cable_lst): 
        current_bndw = float(cable['capacityTBPS'])
        current_cable = cable['cable_name']

        if current_bndw < min_bandwith:
            min_bandwith = current_bndw
            min_cable = current_cable
    
    local_cable = landingpoint + '-LocalCable' 
    lt.addLast(cable_lst, local_cable)  
    mp.put(catalog['cables'], local_cable, {'capacityTBPS': min_bandwith})
    
    # sacar de mapa LPs la lista de cables
    # para cada cable, buscar su 'capacityTBPS' en el mapa de cables
    # ir viendo cual es menor
    # min_bandwith 
    # mp.put(mapa de los cables, 'LP-CableLocal', {'bandwith': min_bandwith})

def addCableInfo(catalog, connection): 
    cable = connection['cable_name']
    entry = mp.get(catalog['cables'], cable)
    if entry is None:
        cable_lps = mp.newMap(numelements=100, maptype='CHAINING')
        mp.put(catalog['cables'], cable, {'info': connection, 'landingpoints': cable_lps})
    else: 
        cable_lps = entry['value']['landingpoints']
        new_entry = {'info': connection, 'landingpoints': cable_lps}
        mp.put(catalog['cables'], cable, new_entry)

    mp.put(cable_lps, connection['origin'], 0)
    mp.put(cable_lps, connection['destination'], 0)
    
    return catalog


# landingpoints.csv
def addLandingPoint(catalog, landingPointInfo):
    landingPoint = landingPointInfo['landing_point_id']
    entry = mp.get(catalog['landingpoints'], landingPoint)
    if entry is None:
        print('no estaba')
        lstcables = lt.newList()
        new_entry = {'info': landingPointInfo, 'lstcables': lstcables}
        mp.put(catalog['landingpoints'], landingPoint, new_entry)

    else:        
        lstcables = entry['value']
        new_entry = {'info': landingPointInfo, 'lstcables': lstcables}
        mp.put(catalog['landingpoints'], landingPoint, new_entry)
    return catalog


# countries.csv
def addCountry(catalog, countryInfo): 
    country = countryInfo["CountryName"]
    mp.put(catalog["countries"], country, countryInfo)
    capital = countryInfo["CapitalName"]
    latitude = countryInfo["CapitalLatitude"]
    longitude = countryInfo["CapitalLongitude"]
    createLandCable(catalog, country, capital,latitude, longitude)

# llamar a funcion createLandCable(catalogo, country, capital, latitude/longitud)

def createLandCable(catalog, country, capitalCity, lat, lon):
    
    addLPVertex(catalog, capitalCity)
    addLandingPoint(catalog, {'landing_point_id': capitalCity, 'id': country + '-localLP', 'name': country + ' local LP', 'latitude': lat, 'longitude': lon})

    # Conectar a cada LP del país
    lps_in_country = False
    all_lps = mp.keySet(catalog['landing_points'])
    min_distance = 2490239403294
    closest_sub_lp = ""
    for landingPt in lt.iterator(all_lps):
        current_lp = mp.get(catalog['landing_points'], landingPt)['value']
        if country in current_lp['info']['name']:
            lps_in_country = True
            lst_cables = current_lp['lstcables']
            for cable in lt.iterator(lst_cables): 
                vertexA = formatVertex(current_lp, cable)
                # TODO: Ver que distance poner
                addCable(catalog, vertexA, capitalCity, 100)
        else: 
            distance = calcHaversine(current_lp['info']['latitude'], current_lp['info']['longitude'], lat, lon)
            if distance < min_distance: 
                min_distance = distance
                closest_sub_lp = current_lp['info']['name']


    if not lps_in_country:
        print('no habia en el pais', min_distance, closest_sub_lp)
        # connect con capitalCity


def calcHaversine(lat1, lon1, lat2, lon2):
    loc_1 = (lat1, lon1)
    loc_2 = (lat2, lon2)
    return hs.haversine(loc_1, loc_2) 

    


def formatVertex(origin, cable):
    name = origin + '-' + cable
    return name

# Construccion de modelos

# Funciones para agregar informacion al catalogo

# Funciones para creacion de datos

# Funciones de consulta

# Funciones utilizadas para comparar elementos dentro de una lista
def cmpLandingPoints(lp, lp_dict):
    lp_code = lp_dict['key']
    if (lp == lp_code):
        return 0
    elif (lp > lp_code):
        return 1
    else:
        return -1

# Funciones de ordenamiento
