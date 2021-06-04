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


from os import lstat
import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import queue as q
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import mergesort as mer
from DISClib.ADT.graph import gr
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import bfs
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
    catalog["capitals"] = mp.newMap(numelements=14000, maptype='PROBING')
    catalog['internet_graph'] = gr.newGraph(datastructure='ADJ_LIST', 
                                    directed=False, 
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

    # ! Añade info al grafo
    addLPVertex(catalog, origin)  # * Agrega un vertice tipo <LandingPoint>-<Cable>
    addLPVertex(catalog, destination)  # Agrega un vertice tipo <LandingPoint>-<Cable>
    # addCable(catalog, origin, destination, cable_length)
    addCable(catalog, origin, destination, distance)  # * Agrega un cable con peso de distance
    # addCable(catalog, destination, origin, distance)
    # ! Info adicional
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
                # addCable(catalog, prevCable, cable, .1) 
            addCable(catalog, key, cable, .1) # * Connecta LP central con todos los otros sub LPs
            # addCable(catalog, cable, key, .1)
            prevCable = cable
        createLocalCable(catalog, key, True) # 
        
    return catalog

def createLocalCable(catalog, landingpoint, cableType, dest=''): 
    """
    Determina cual es el cable de ancho de manda minimo para un landinpoint
    Se llama para crear el cable de la red local de un landinpoint
    Se llama para crear el cable de una capital a los landinpoint correspondientes
    Cable type -> True - Red Local,  False - Conexión terrestre
    """
    if cableType: 
        landingPointId = landingpoint.split('-')[0]  
        local_cable_name = 'Local Cable-' + landingPointId
        cable_lst = mp.get(catalog['landingpoints'], landingPointId)
    else:
        landingPointId = landingpoint  
        local_cable_name = 'Land Cable-' + dest 
        cable_lst = mp.get(catalog['landingpoints'], landingpoint)

     # Saca la lista de cables de un LP (SOLO EL ID)

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
    if cableType:
        mp.put(cable_lst['value']['lstcables'], local_cable_name, -1)  # Agrega ese nuevo cable a la lista de cables de un landinpoint
    else:
        mp.put(cable_lst['value']['lstcables'], local_cable_name, -1)
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
        mp.put(catalog['capitals'], capital, country)
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
            # addCable(catalog, capitalCity, landingPt, distance)
            lst_cables = current_lp['lstcables']
            for cable in lt.iterator(mp.keySet(lst_cables)): 
            # for cable in lt.iterator(lst_cables): 
                # Conecta la capital tambien con los subvertices
                if not('Local Cable' in cable) and not('Land Cable' in cable): # ! Solo se conecta a cables submarinos
                    lps_in_country = True  # * Si hay landinpoints en el pais de la capital
                    vertexA = formatVertex(current_lp['info']['landing_point_id'], cable)
                    addCable(catalog, vertexA, capitalCity, distance) # Agrega arco entre el vertice del LP (<lp>-<cable> y la capital)
                    createLocalCable(catalog, capitalCity, False, landingPt) 
                    createLocalCable(catalog, landingPt, False, capitalCity)
                    # addCable(catalog, capitalCity, vertexA, distance)
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
            # addCable(catalog, capitalCity, closest_sub_lp, min_distance) 
            createLocalCable(catalog, closest_sub_lp, False, capitalCity)

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

def getLandingPointId(catalog, lp): 
    """
    Dado un landinpoint (Ej. Redondo Beach) retorna el su identificador (id)
    Como el usuario solo da parte del nombre del landinpoint (Ej. Redondo Beach en verdad es Redondo Beach, CA, United States, toca usar la función de in para revisar que el string este dentro del nombre completo)

    ! Req 1 y 5
    """
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


def getCapitalCity(catalog, country):
    """Dado un pais, retorna su capital 

    ! Req 3
    """
    country_entry = mp.get(catalog['countries'], country)
    capital_city = None
    if country_entry is not None:
        capital_city = country_entry['value']['CapitalName']
    return capital_city

# ==============================
# REQUERIMIENTO 1
# ==============================
def calcConnectedComponents(catalog, lp1, lp2): 
    """
    Usa el algoritmo de Kosaraju Para calcular los componentes connectados del grafo.
    El numero de clusters (componenetes conectados)  y si dos lps estan fuertemente conectados (pertencecen al mismo cluster)
    """
    catalog['components'] = scc.KosarajuSCC(catalog['internet_graph'])
    num_clusters = scc.connectedComponents(catalog['components'])
    landpts_cluster = scc.stronglyConnected(catalog['components'], lp1, lp2)
    return num_clusters, landpts_cluster

# ==============================
# REQUERIMIENTO 2
# ==============================
def pointsInterconnection(catalog):
    """
    """
    lst_lps = mp.keySet(catalog['landingpoints'])
    lstmax_lp = lt.newList(datastructure='ARRAY_LIST')
    maxdeg = 0
    for landingpoint in lt.iterator(lst_lps):
        lst_cables = mp.get(catalog['landingpoints'], landingpoint)['value']['lstcables']
        degree = mp.size(lst_cables)
        if (degree == maxdeg): 
            lt.addLast(lstmax_lp, landingpoint)
        if(degree > maxdeg):
            lstmax_lp = lt.newList(datastructure='ARRAY_LIST') 
            lt.addLast(lstmax_lp, landingpoint)
            maxdeg = degree
            
    return lstmax_lp, maxdeg


# ==============================
# REQUERIMIENTO 3
# ==============================
def minimumDistanceCountries(catalog, capital_1, capital_2): 
    """
    Usa el algoritmo de Dijkstra para calcular los caminos mas baratos desde la capital 1
    Luego, con la estructura del Dijstra revisa si hay un camino entre la capital 1 y la capital 2
    """
    catalog['paths'] =  djk.Dijkstra(catalog['internet_graph'], capital_1)
    path_exists = djk.hasPathTo(catalog['paths'], capital_2)
    path = djk.pathTo(catalog['paths'], capital_2)
    return path


# ==============================
# REQUERIMIENTO 4
# ==============================
def findGraphMST(catalog): 
    """Usa Prim para crear el MST"""
    mst_structure = prim.PrimMST(catalog['internet_graph'])
    mst_structure = prim.edgesMST(catalog['internet_graph'], mst_structure)
    mst = mst_structure['mst']
    edgesTo = mst_structure['edgeTo']
    mst_weight = prim.weightMST(catalog['internet_graph'], mst_structure)

    nodes = lt.size(mst)
    mst_graph = createMSTgraph(catalog, mst)
    path = getMSTroots(catalog, mst_graph)

    return nodes, mst_weight, path


def createMSTgraph(catalog, mst): 
    """Usa la lista del MST dada por el prim para crear el grafo correspondiente"""
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
    return catalog['mst']

def getMSTroots(catalog, mst_graph):
    roots = lt.newList(datastructure='ARRAY_LIST') 
    mst_vertices = gr.vertices(mst_graph)
    i = 0
    # * Ecuentra todas las 'raices' del MST (nodos/vertices con un indegree de 0) 
    while i <= lt.size(mst_vertices): 
        vertex = lt.getElement(mst_vertices, i)
        indegree = gr.indegree(mst_graph, vertex)
        outdegree = gr.outdegree(mst_graph, vertex)
        if indegree == 0 and outdegree > 0: # Outdegree > 0 para asegurar que si se conecta con algo más
            lt.addLast(roots, vertex)
        i += 1

    longest_branch_dist = 0
    longest_branch_bfs = None
    # Por cada raiz que se econtro, calcula la rama más larga entre esta y una hoja. Guarda la rama más larga entre todas las rices.

    for root in lt.iterator(roots):
        info = longestBranch(catalog, mst_graph, root)
        if info[0] > longest_branch_dist: 
            longest_branch_dist = info[0]
            end_vertex = info[1]
            longest_branch_bfs = info[2]

    path = bfs.pathTo(longest_branch_bfs, end_vertex) # Camino entre la raiz y hoja de la rama más larga
    
    return path, longest_branch_dist

def longestBranch(catalog, mst_graph, root): 

    bfs_structure = bfs.BreadhtFisrtSearch(mst_graph, root)
    keySet = mp.keySet(bfs_structure['visited'])
    max_dist = 0
    end_vertex = None
    for vertex in lt.iterator(keySet):
        vertex_info = mp.get(bfs_structure['visited'], vertex)['value']
        dist_to = vertex_info['distTo']

        if dist_to > max_dist: 
            max_dist = dist_to
            end_vertex = vertex
    return max_dist, end_vertex, bfs_structure

# ==============================
# REQUERIMIENTO 5
# ==============================
def failureOfLP(catalog, landingpoint):

    lp_entry = mp.get(catalog['landingpoints'], landingpoint)
    lst_cities = lt.newList(datastructure='ARRAY_LIST')
    lst_lps = lt.newList(datastructure='ARRAY_LIST')
    if lp_entry is not None: 
        cables = lp_entry['value']['lstcables'] 
        for cable in lt.iterator(mp.keySet(cables)): # Cables adjacentes al LP por param (LP es solo el numero)
            if 'Land Cable' in cable: # Estos cables conectan a un lp con una ciudad (Capital del pais donde esta el LP que entra por param)
               lt.addLast(lst_cities, cable.split('-')[1:])
            elif not 'Local Cable' in cable: # Ver los cables adjacentes (que no forman parte de la red local)
                vertex = landingpoint + "-" + cable  # "Arma" los vertices tipo <LP>-<Cable> 
                adjacents = gr.adjacents(catalog['internet_graph'], vertex) # * Estos son los "verdaderos" adjs del LP
                for adj_vertex in lt.iterator(adjacents):
                    # Para cada adjacente que sea del tipo <LP>-<Cable>  y que ya no este en la lista de lps
                    if '-' in adj_vertex and not(lt.isPresent(lst_lps, adj_vertex.split('-')[:1])): 
                        lt.addLast(lst_lps, adj_vertex.split('-')[:1])  # Se guarda solo el # del LP
                                         
    lst_countries = locateLPs(catalog, lst_lps) # Donde esta cada LP adj

    for city in lt.iterator(lst_cities):  # Revisa la lista de ciudades (Se espera que solo haya una - capital de donde esta el LP)
        country = mp.get(catalog['capitals'], city[0])['value']
        if not lt.isPresent(lst_countries, country): # Añade a los paises si no esta todavia
            lt.addLast(lst_countries, city)

    lp_lat = mp.get(catalog['landingpoints'], landingpoint)['value']['info']['latitude']
    lp_lon = mp.get(catalog['landingpoints'], landingpoint)['value']['info']['longitude']

    pre_sort = lt.newList()
    for country in lt.iterator(lst_countries):
        # Para cada paiis adjacente, calcula la distancia entre su capital y el LP por param
        cc_lat = mp.get(catalog['countries'], country)['value']['CapitalLatitude']
        cc_lon = mp.get(catalog['countries'], country)['value']['CapitalLongitude']

        distance = calcHaversine(lp_lat, lp_lon, cc_lat, cc_lon)
        lt.addLast(pre_sort, {'country': country, 'distance': distance, 'CapitalLatitude': cc_lat, 'CapitalLongitude': cc_lon})

    # Ordena la lista final en orden descendente en cuanto a la distancia en km entre el LP y los piaises
    sorted_country = mer.sort(pre_sort, sortCountries)
    return sorted_country

def locateLPs(catalog, lst_lps): 
    lst_affected_countries = lt.newList(datastructure='ARRAY_LIST')
    # Para todos los LPs que son adj: 
    for lp in lt.iterator(lst_lps):
        lp = lp[0]
        notFound = True
        i = 1
        cables = mp.keySet(mp.get(catalog['landingpoints'], lp)['value']['lstcables'])
        # Busca los cables que sean 'Land Cable' (estos son los conecta un LP con la capital (si la hay))
        while notFound and i < lt.size(cables):
            cable = lt.getElement(cables, i)
            if 'Land Cable' in cable: 
                capital = cable.split('-')[1:][0]
                country = mp.get(catalog['capitals'], capital)['value']
                if not (lt.isPresent(lst_affected_countries, country)): 
                    lt.addLast(lst_affected_countries, country)
                notFound = False
                # Cuando ya la haya encontrado se acaba el ciclo
            i += 1
    return lst_affected_countries


# Funciones utilizadas para comparar elementos dentro de una lista
def cmpLandingPoints(lp, lp_dict):
    lp_code = lp_dict['key']
    if (lp == lp_code):
        return 0
    elif (lp > lp_code):
        return 1
    else:
        return -1

def sortCountries(country_1, country_2):
    """Funcion de comparación para ordenar las distancia en orden descendente"""
    dist_1 = country_1["distance"]
    dist_2 = country_2["distance"]
    return dist_1 > dist_2

