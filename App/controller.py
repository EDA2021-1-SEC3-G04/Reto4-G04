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
 """

import config as cf
import model
import csv


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""


# Inicialización del Catálogo de libros
def initCatalog():
    return model.initCatalog()


def loadData(connectionsfile, landingpointsfile, countriesfile): 
    catalog = initCatalog()
    loadLandingPoints(catalog, landingpointsfile)
    loadConnections(catalog, connectionsfile)
    loadCountries(catalog, countriesfile)
    return catalog

# Funciones para la carga de datos
def loadConnections(catalog, connectionsfile):
    connectionsfile = cf.data_dir + connectionsfile
    input_file = csv.DictReader(open(connectionsfile, encoding="utf-8-sig"),
                                delimiter=",")
    last_lp_cable = None
    for lp_cable in input_file:
        if last_lp_cable is not None:
            model.addConnections(catalog, lp_cable)
        last_lp_cable = lp_cable
    model.addLandingPointConnections(catalog)
    return catalog


def loadLandingPoints(catalog, landingpointsfile):
    landingpointsfile = cf.data_dir + landingpointsfile
    input_file = csv.DictReader(open(landingpointsfile, encoding="utf-8-sig"),
                                delimiter=",")
    for landingPoint in input_file:
        model.addLandingPoint(catalog, landingPoint)


def loadCountries(catalog, countriesfile):
    countriesfile = cf.data_dir + countriesfile
    input_file = csv.DictReader(open(countriesfile, encoding="utf-8-sig"),
                                delimiter=",")
    for country in input_file:
        model.addCountry(catalog, country)


# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo


def calcConnectedComponents(catalog, lp1, lp2):
    return model.calcConnectedComponents(catalog, lp1, lp2)

def getLandingPointId(catalog, lp): 
    return model.getLandingPointId(catalog, lp)

def pointsInterconnection(catalog):
    return model.pointsInterconnection(catalog)

def getCapitalCity(catalog, country):
    return model.getCapitalCity(catalog, country)

def minimumDistanceCountries(catalog, country_1, country_2): 
    return model.minimumDistanceCountries(catalog, country_1, country_2)

def findGraphMST(catalog):
    return model.findGraphMST(catalog)

def failureOfLP(catalog, landingpoint): 
    return model.failureOfLP(catalog, landingpoint)