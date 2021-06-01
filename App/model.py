﻿"""
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
from DISClib.ADT import queue as q
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.ADT.graph import gr
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.ADT import stack
from DISClib.Utils import error as error
from DISClib.Algorithms.Graphs import prim
import haversine as hs
import time

assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

def initCatalog():
    """
    landinpoints: mapa - key: solo el landinpoint con el id, value: info -> toda la info del landinpoints.csv, lstcables -> lista de todos los cabels que llegan a ese landpoint

    ? Landinpoint ID
    ? capitalCity + ' Land LP ' + country

    internet_graph: grafo (tipo de vertides: <lp>-<cables>, <capitalCity>-locales, arcos: peso - distancia harvesine)

    components: almacena info de componentes conectados

    paths: Estructura que almancena los caminos de costo minimo desde un ertice determinado a todos los otros vértices del grafo

    countries: mapa Key: Pais, Value: toda la info para cada pais de countries.csv, la

    cables: mapa, Key: cable_name, Value: info -> info de los cables (lenght, capacityTBS...), lstlandingpoints -> landinpoints que conecta ese cable
    """
    catalog = {"landing_points":None, "internet_graph":None, "components":None, "paths":None, "countries":None, "cables": None, 'lp_names': None}
    catalog['landingpoints'] = mp.newMap(numelements=14000, maptype='PROBING')
    catalog['lp_names'] = mp.newMap(numelements=14000, maptype='PROBING')
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

    origin_info = mp.get(catalog['landingpoints'], origin_lp)['value']['info']  # Usa el mapa de landingpoints
    dest_info = mp.get(catalog['landingpoints'], destination_lp)['value']['info']  # Usa el mapa de landingpoints

    distance = calcHaversine(origin_info['latitude'], origin_info['longitude'], dest_info['latitude'], dest_info['longitude'])  # Calcula distancia entre los dos puntos
    
    origin = formatVertex(origin_lp, cable)  # <LandingPoint>-<Cable>
    destination = formatVertex(destination_lp, cable)

    addCableInfo(catalog, connection)  # Agrega la info del cable al mapa

    # ! INFO AL GRAFO
    addLPVertex(catalog, origin)  # * Agrega un vertice tipo <LandingPoint>-<Cable>
    addLPVertex(catalog, destination)  # Agrega un vertice tipo <LandingPoint>-<Cable>
    # ! TODO: checkdistance -> distancia entre los dos puntos o  el length?
    # addCable(catalog, origin, destination, cable_length)
    addCable(catalog, origin, destination, distance)  # * Agrega un cable con peso de distnace
    addCable(catalog, destination, origin, distance)
    addCableLanding(catalog, origin_lp, cable)  # * Agrega a lista de cables para un landinpoint
    addCableLanding(catalog, destination_lp, cable)
    
    return catalog


def addLPVertex(catalog, landingPt_id):
    """Agrega un vertice al grafo"""
    try:
        if not gr.containsVertex(catalog['internet_graph'], landingPt_id):
            gr.insertVertex(catalog['internet_graph'], landingPt_id)
        return catalog
    except Exception as exp:
        error.reraise(exp, 'model:addVertex')
    

def addCable(catalog, origin, destination, distance):
    """Agrega un arco al grafo"""
    edge = gr.getEdge(catalog['internet_graph'], origin, destination)
    if edge is None:
        gr.addEdge(catalog['internet_graph'], origin, destination, distance)
    return catalog


def addCableLanding(catalog, landingPt, cable):
    """Añade un cable a la lista para cada landinpoint"""

    entry = mp.get(catalog['landingpoints'], landingPt)
    if entry is None:
        lstcables = mp.newMap(numelements=1000, maptype='CHAINING')
        new_entry = {'info': None, 'lstcables': lstcables}
        mp.put(lstcables, cable, -1)
        # lstcables = lt.newList(datastructure='ARRAY_LIST')
        # lt.addLast(lstcables, cable)
        mp.put(catalog['landingpoints'], landingPt, new_entry)
    else:
        info = entry['value']['info']
        lstcables = entry['value']['lstcables']
        if not mp.contains(lstcables, cable):
            mp.put(lstcables, cable, -1)
        # if not lt.isPresent(lstcables, cable):
        #     lt.addLast(lstcables, cable)
        new_entry = {'info': info, 'lstcables': lstcables}

    mp.put(catalog['landingpoints'], landingPt, new_entry)
    return catalog


def addLandingPointConnections(catalog):
    """Conexiones entre vertices de un landinpoint - Crea la red Local"""

    lstLandingPts = mp.keySet(catalog['landingpoints'])

    # Para cada Landinpoint en el mapa, saca su lista de de cables y crea un conexion cada combinacion de ese key y cable
    for key in lt.iterator(lstLandingPts):
        lstCables = mp.get(catalog['landingpoints'], key)['value']['lstcables']
        prevCable = None
        addLPVertex(catalog, key) # * Landinpoint central tipo '34982'
        for cable in lt.iterator(mp.keySet(lstCables)):
        # for cable in lt.iterator(lstCables):
            cable = key + '-' + cable
            if prevCable is not None:
                addCable(catalog, cable, prevCable, .1) # * Peso de estos cables = 100m = .1 km
                addCable(catalog, prevCable, cable, .1) 
            addCable(catalog, key, cable, .1) # * Connecta LP central con todos los otros sub LPs
            addCable(catalog, cable, key, .1)
            prevCable = cable
        createLocalCable(catalog, key, True) # 
        
    return catalog

def createLocalCable(catalog, landingpoint, cableType): 
    """
    Determina cual es el cable de ancho de manda minimo para un landinpoint
    Se llama para crear el cable de la red local de un landinpoint
    Se llama para crear el cable de una capital a los landinpoint correspondientes
    Cable type -> True - Red Local,  False - Conexión terrestre
    """
    if cableType: 
        landingPointId = landingpoint.split('-')[0]  
        local_cable_name = 'Local Cable-' + landingPointId
    else:
        landingPointId = landingpoint  
        local_cable_name = 'Land Cable-' + landingPointId

    cable_lst = mp.get(catalog['landingpoints'], landingPointId) # Saca la lista de cables de un LP (SOLO EL ID)

    # if cable_lst is not None:
    # * Determinar el bandwith minimo (usando los cables que llegan a UN landinpoint (usa el mapa))
    min_bandwith = 100000.00
    min_cable = ""
    for cable in lt.iterator(mp.keySet(cable_lst['value']['lstcables'])):
    # for cable in lt.iterator(cable_lst['value']['lstcables']):
        cable_info = mp.get(catalog['cables'], cable)['value']['info']
        current_bndw = float(cable_info['capacityTBPS'])
        current_cable = cable_info['cable_name']

        if current_bndw < min_bandwith:
            min_bandwith = current_bndw
            min_cable = current_cable
    
    # ! ESTO SOLO SE DEBERIA HACER CON LOS CABLES QUE CONECTAN LP ! 
    # * Agrega el nuevo cable al mapa de de cables.
    mp.put(cable_lst['value']['lstcables'], local_cable_name, -1)  # Agrega ese nuevo cable a la lista de cables de un landinpoint
    # lt.addLast(cable_lst['value']['lstcables'], local_cable_name) 
    addCableInfo(catalog, {'capacityTBPS': min_bandwith, 'cable_name': local_cable_name, 'origin': landingpoint, 'destination': landingpoint})  # Agrega el cable local al MAPA de cables


def addCableInfo(catalog, connection): 
    """
    Agrega un cable al mapa de cables
    """
    cable = connection['cable_name']
    entry = mp.get(catalog['cables'], cable)
    if entry is None:
        cable_lps = mp.newMap(numelements=100, maptype='CHAINING') # Landingpoints a lo que llega el cable
        mp.put(catalog['cables'], cable, {'info': connection, 'landingpoints': cable_lps})
    else: 
        cable_lps = entry['value']['landingpoints']
        new_entry = {'info': connection, 'landingpoints': cable_lps}
        mp.put(catalog['cables'], cable, new_entry)

    # Agrega landingpoints
    mp.put(cable_lps, connection['origin'], 0)
    mp.put(cable_lps, connection['destination'], 0)
    
    return catalog


# landingpoints.csv
def addLandingPoint(catalog, landingPointInfo):
    """
    Carga info de landinpoints.csv
    En el mapa de landinpoints, agrega o crea la entre
    Keys -> landinpoint_id ej. 19128
    Values -> info: info del archivo, lstcables: lista de los cables que llegan

    ! Tambien se llama al crear los cables terrestes
    """
    landingPoint = landingPointInfo['landing_point_id']
    landintPointName = landingPointInfo['name']
    entry = mp.get(catalog['landingpoints'], landingPoint)
    if entry is None:
        lstcables = mp.newMap(numelements=1000, maptype='CHAINING')
        # lstcables = lt.newList(datastructure='ARRAY_LIST')
        new_entry = {'info': landingPointInfo, 'lstcables': lstcables}
        mp.put(catalog['landingpoints'], landingPoint, new_entry)
        mp.put(catalog['lp_names'], landintPointName, landingPoint)
    else:
        if not ('Land' in landingPointInfo['name']):
            lstcables = entry['value']
            new_entry = {'info': landingPointInfo, 'lstcables': lstcables}
            mp.put(catalog['landingpoints'], landingPoint, new_entry)
        else:
            lstcables = entry['value']['lstcables']
            new_entry = {'info': landingPointInfo, 'lstcables': lstcables}
            mp.put(catalog['landingpoints'], landingPoint, new_entry)

    # ! Vertice Central de los landinpoints + Conecta a todos los subvertices
    
    return catalog


# countries.csv
def addCountry(catalog, countryInfo): 
    """Agrega la información de un pais al mapa 'countries', usando countries.csv"""
    country = countryInfo["CountryName"]
    if not(country == ''):
        mp.put(catalog["countries"], country, countryInfo)
        capital = countryInfo["CapitalName"]
        latitude = countryInfo["CapitalLatitude"]
        longitude = countryInfo["CapitalLongitude"]
        createLandCable(catalog, country, capital, latitude, longitude)  # * Crea canales de comunicación terrestres



def createLandCable(catalog, country, capitalCity, lat, lon):
    """
    Se crea   canales de comunicación terrestres al grafo
    --> Adiciona en la capital de cada pais
        -> Conectar a todos los landinpoints en el pais
        -> Si no hay en el pais, conectar el LP más cercano (UNO SUBMARINO - Id numerico)
    """
    
    if capitalCity == '':
        capitalCity = country + '--'

    addLPVertex(catalog, capitalCity)  # Agregar vertice de la capital

    addLandingPoint(catalog, {'landing_point_id': capitalCity, 'id': capitalCity + '-Land-LP-' + country, 'name': capitalCity + ' Land LP ' + country, 'latitude': lat, 'longitude': lon})  # Agrega la capital al mapa de vertices

    # * Conectar la capital a los LPs del pais
    lps_in_country = False 
    all_lps = mp.keySet(catalog['landingpoints']) 
    min_distance = 2490239403294
    closest_sub_lp = ""


    for landingPt in lt.iterator(all_lps):

        current_lp = mp.get(catalog['landingpoints'], landingPt)['value']
        distance = calcHaversine(current_lp['info']['latitude'], current_lp['info']['longitude'], lat, lon) # Distancia entre capital y el LP actual
        if landingPt != capitalCity and country in current_lp['info']['name']:
            # ! Carga CON LPs centrales
            addCable(catalog, landingPt, capitalCity, distance)
            addCable(catalog, capitalCity, landingPt, distance)
            createLocalCable(catalog, capitalCity, False)
            lst_cables = current_lp['lstcables']
            for cable in lt.iterator(mp.keySet(lst_cables)): 
            # for cable in lt.iterator(lst_cables): 
                # Conecta la capital tambien con los subvertices
                if not('Local Cable' in cable) and not('Land Cable' in cable): # ! Solo se conecta a cables submarinos
                    lps_in_country = True  # * Si hay landinpoints en el pais de la capital
                    vertexA = formatVertex(current_lp['info']['landing_point_id'], cable)
                    # TODO: Ver que distance poner
                    addCable(catalog, vertexA, capitalCity, distance) # Agrega arco entre el vertice del LP (<lp>-<cable> y la capita)
                    # createLocalCable(catalog, capitalCity, False) # ! Va a agregar el cable entre capital al mapa -> bandwith y revisar nomrbe
                    addCable(catalog, capitalCity, vertexA, distance)
                    # TODO: lo de "El ancho de banda del cable de conexión a cada landing point de una ciudad capital se determinará como el valor del menor ancho de banda que llegan al landing point submarino."
        else:
            # * Si no el landpoint no esta en el pais, ver si esta más cerca que el anterior
            if distance < min_distance: 
                min_distance = distance
                closest_sub_lp = current_lp['info']['landing_point_id']


    if (not lps_in_country):
        # * Se crea el cable de la capital al lp submarino más cercano (conecta el LP Central)
        # print(capitalCity, 'cercano', closest_sub_lp, 'disantcia', min_distance )
        if (not closest_sub_lp == ""): 
            # ! Carga CON LPs centrales
            addCable(catalog, closest_sub_lp, capitalCity, min_distance) 
            addCable(catalog, capitalCity, closest_sub_lp, min_distance) 
            createLocalCable(catalog, closest_sub_lp, False)

            # ! Carga SIN los LPs centrales
            # lst_cables = mp.get(catalog['landingpoints'], closest_sub_lp)['value']['lstcables']
            # for cable in lt.iterator(lst_cables):
            #     if ('Local Cable'  not in cable) and ('Land Cable' not in cable):
            #         addCable(catalog, closest_sub_lp+'-'+cable, capitalCity, min_distance)


        
def calcHaversine(lat1, lon1, lat2, lon2):
    loc_1 = (float(lat1), float(lon1))
    loc_2 = (float(lat2), float(lon2))
    return hs.haversine(loc_1, loc_2) 


def formatVertex(origin, cable):
    name = origin + '-' + cable
    return name

# Construccion de modelos

# Funciones para agregar informacion al catalogo
def calcConnectedComponents(catalog, lp1, lp2): 
    catalog['components'] = scc.KosarajuSCC(catalog['internet_graph'])
    num_clusters = scc.connectedComponents(catalog['components'])
    landpts_cluster = scc.stronglyConnected(catalog['components'], lp1, lp2)
    return num_clusters, landpts_cluster

# Funciones para creacion de datos

# Funciones de consulta


def getLandingPointId(catalog, lp): 
    lp_id = None
    lst_name = mp.keySet(catalog['lp_names'])
    notFound = True
    i = 1
    while notFound and i <= lt.size(lst_name): 
        key = lt.getElement(lst_name, i)
        if lp in key:
            notFound = False
            lp_id = mp.get(catalog['lp_names'], key)['value']
        i += 1

    return lp_id

# ==============================
# REQUERIMIENTO 2
# ==============================
def pointsInterconnection(catalog):
    lst_lps = mp.keySet(catalog['landingpoints'])
    lstmax_lp = lt.newList(datastructure='ARRAY_LIST')
    maxdeg = 0
    for landingpoint in lt.iterator(lst_lps):
        lst_cables = mp.get(catalog['landingpoints'], landingpoint)['value']['lstcables']
        degree = mp.size(lst_cables)
        # degree = lt.size(lst_cables)
        if (degree == maxdeg): 
            lt.addLast(lstmax_lp, landingpoint)
            #agregar el nuevo a la lista
        if(degree > maxdeg):
            lstmax_lp = lt.newList(datastructure='ARRAY_LIST') 
            lt.addLast(lstmax_lp, landingpoint)
            maxdeg = degree
            
        # print(landingpoint, 'current', degree, 'max', maxdeg)
        # print(lstmax_lp) #updetear el nuevo mayor
        # time.sleep(2)
    return lstmax_lp, maxdeg



# ==============================
# REQUERIMIENTO 3
# ==============================

def getCapitalCity(catalog, country):
    country_entry = mp.get(catalog['countries'], country)
    capital_city = None
    if country_entry is not None:
        capital_city = country_entry['value']['CapitalName']
    return capital_city

def minimumDistanceCountries(catalog, capital_1, capital_2): 
    catalog['paths'] =  djk.Dijkstra(catalog['internet_graph'], capital_1)
    print(catalog['paths'].keys())
    path_exists = djk.hasPathTo(catalog['paths'], capital_2)
    print(path_exists)
    # print(catalog['paths']['visited'])
    path = djk.pathTo(catalog['paths'], capital_2)
     
    return path


# ==============================
# REQUERIMIENTO 4
# ==============================
def findGraphMST(catalog): 
    # catalog['internet_graph']['directed'] = False # ? Prim solo sirve en grafos no dirigidos 
    print(catalog['internet_graph']['directed'])
    mst_structure = prim.PrimMST(catalog['internet_graph'])
    mst_structure = prim.edgesMST(catalog['internet_graph'], mst_structure)
    mst = mst_structure['mst']
    edgesTo = mst_structure['edgeTo']
    mst_weight = prim.weightMST(catalog['internet_graph'], mst_structure)


    # 'mst' has all the edges in the mest

    # edgesTo has how to get somewhere but you dont know that somewhere
    # for x in lt.iterator(mst): 
    #     print(x)
    # for y in lt.iterator(mp.keySet(edgesTo)):  
    #     print(mp.get(edgesTo, y))

    nodes = lt.size(mst)
    print('nodes v2', lt.size(edgesTo))
    print('first elements', lt.firstElement(mst))
    mst_graph = createMSTgraph(catalog, mst)
    
    longest_branch = longestBranch(mst_graph)

    return nodes,  mst_weight



def createMSTgraph(catalog, mst): 
    """Usa la lista del mst para crear el grafo correspondiente"""
    catalog['mst'] = gr.newGraph(datastructure='ADJ_LIST', directed=True, size=3600, comparefunction=cmpLandingPoints)
    for edge in lt.iterator(mst): 
        vertexA = edge['vertexA']
        vertexB = edge['vertexB']
        weight = edge['weight']
        if not gr.containsVertex(catalog['mst'], vertexA):
            gr.insertVertex(catalog['mst'], vertexA)
        if not gr.containsVertex(catalog['mst'], vertexB):
            gr.insertVertex(catalog['mst'], vertexB)

        edge = gr.getEdge(catalog['mst'], vertexA, vertexB)
        if edge is None:
            gr.addEdge(catalog['mst'], vertexA, vertexB, weight)
            # gr.addEdge(catalog['mst'], vertexB, vertexA, weight)
    print(lt.size(gr.vertices(catalog['mst'])))
    return catalog['mst']

def longestBranch(mst_graph): 
    roots = lt.newList(datastructure='ARRAY_LIST') #! cambiar a tad
    mst_vertices = gr.vertices(mst_graph)
    i = 0
    # * Finds all 'roots' of the MST  (Nodes with an indegree of 0)
    while i <= lt.size(mst_vertices): 
        vertex = lt.getElement(mst_vertices, i)
        indegree = gr.indegree(mst_graph, vertex)
        if indegree == 0: 
            lt.addLast(roots, vertex)
        i += 1
    print(roots)
    root = lt.firstElement(roots)

    


    


# ==============================
# REQUERIMIENTO 5
# ==============================
def failureOfLP(catalog, landingpoint):

    adjacents = gr.adjacents(catalog['internet_graph'], landingpoint)
    vert = lt.firstElement(adjacents)
    vert_adjs_ed = gr.adjacentEdges(catalog['internet_graph'], vert)
    vert_adjs = gr.adjacents(catalog['internet_graph'], vert)

    print(vert_adjs_ed)
    print(vert_adjs)

    # print(mp.get(catalog['landingpoints'], landingpoint)['value']['lstcables'])
    # input()
    # for vert in lt.iterator(adjacents): 
        
        # for cable in lt.iterator(cables): 
        #     if 'Land Cable' in cable:
        #         print(cable)


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


