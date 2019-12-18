from __future__ import print_function	# For Py2/3 compatibility
import eel
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 17:38:58 2019

@author: David Rosales
"""
import numpy as np
from neo4j import GraphDatabase
from sklearn.linear_model import LogisticRegression
#from sklearn import metrics
#import pandas as pd


#Cargar driver neo4j
#-----------------------------------------------------------------
print('Estableciendo conexión con base de datos...')
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "SISTGBI2019"))
#Inicializar variables
#-----------------------------------------------------------------
data_base = np.zeros(shape=(5040,12))
data_base = np.dtype('int64').type(data_base)
data = np.zeros(shape=(5030,17))
data = np.dtype('int64').type(data)
teams = np.zeros(shape=(20,8))
teams = np.dtype('int64').type(teams)

for i in range(20):
    teams[i][0] = i + 1
    
#Cargar los datos desde neo4j
#-----------------------------------------------------------------
def charge_database(tx):
    print('Cargando base de datos...')
    aux=0
    for record in tx.run("MATCH (p:Partido)"
                         "RETURN p.Local, p.Visitante, p.GolesLocal, p.GolesVisitante,"
                         "p.PosicionLocal, p.PosicionVisitante, p.TirosLocal,"
                         "p.TirosVisitante, p.ParadasLocal, p.ParadasVisitante, p.Resultado, p.Jornada"):
        data_base[aux]=[record["p.Local"],record["p.Visitante"],record["p.GolesLocal"],
          record["p.GolesVisitante"],record["p.PosicionLocal"],record["p.PosicionVisitante"],
          record["p.TirosLocal"],record["p.TirosVisitante"],record["p.ParadasLocal"],
          record["p.ParadasVisitante"],record["p.Resultado"],record["p.Jornada"]]
        aux=aux+1
        
    aux=0   
    
 
#Actualizar datos de neo4j
#-----------------------------------------------------------------  
def update_database(tx, id):
    tx.run("MATCH (n:Equipo { Identificador: $name })"
           "SET n.golesFavor=$golesFavor, n.golesContra=$golesContra,"
           "n.posicion=$posicion, n.tirosRealizados=$tirosRealizados,"
           "n.tirosRecibidos=$tirosRecibidos, n.paradasRealizadas=$paradasRealizadas,"
           "n.paradasRecibidas=$paradasRecibidas"
           , name=str(id), golesFavor=str(teams[id-1][1]), golesContra=str(teams[id-1][2]),
           posicion=str(teams[id-1][3]), tirosRealizados=str(teams[id-1][4]),
           tirosRecibidos=str(teams[id-1][5]), paradasRealizadas=str(teams[id-1][6]),
           paradasRecibidas=str(teams[id-1][7]))

    
#Sesion de conexion con nuestra base de datos
#-----------------------------------------------------------------
with driver.session() as session:
    session.read_transaction(charge_database)
    driver.close()


#Definir matriz de entrenamiento
#-----------------------------------------------------------------
    
for i in range(5040):
   #actualizar goles a favor del local
   teams[data_base[i][0]-1][1] = teams[data_base[i][0]-1][1] + data_base[i][2]
   #actualizar goles en contra del visitante
   teams[data_base[i][1]-1][2] = teams[data_base[i][1]-1][2] + data_base[i][2]
   #actualizar goles a favor del visitante
   teams[data_base[i][1]-1][1] = teams[data_base[i][1]-1][1] + data_base[i][3]
   #actualizar goles en contra del local
   teams[data_base[i][0]-1][2] = teams[data_base[i][0]-1][2] + data_base[i][3]
   #actualizar posicion del local
   teams[data_base[i][0]-1][3] = data_base[i][4]
   #actualizar posicion del visitante
   teams[data_base[i][1]-1][3] = data_base[i][5]
   #actualizar tiros realizados por el local
   teams[data_base[i][0]-1][4] = teams[data_base[i][0]-1][4] + data_base[i][6]
   #actualizar tiros recibidos por el visitante
   teams[data_base[i][1]-1][5] = teams[data_base[i][1]-1][5] + data_base[i][6]
   #actualizar tiros realizados por el visitante
   teams[data_base[i][1]-1][4] = teams[data_base[i][1]-1][4] + data_base[i][7]
   #actualizar tiros recibidos por el local
   teams[data_base[i][0]-1][5] = teams[data_base[i][0]-1][5] + data_base[i][7]
   #actualizar paradas realizadas por el local
   teams[data_base[i][0]-1][6] = teams[data_base[i][0]-1][6] + data_base[i][8]
   #actualizar paradas recibidas por el visitante
   teams[data_base[i][1]-1][7] = teams[data_base[i][1]-1][7] + data_base[i][8]
   #actualizar paradas realizadas por el visitante
   teams[data_base[i][1]-1][6] = teams[data_base[i][1]-1][6] + data_base[i][9]
   #actualizar paradas recibidas por el local
   teams[data_base[i][0]-1][7] = teams[data_base[i][0]-1][7] + data_base[i][9]
 
for i in range(5040):
    if i>9:
       #equipo local
       data[i-10][0] = data_base[i][0]
       #equipo visitante
       data[i-10][1] = data_base[i][1]
       #goles a favor local
       data[i-10][2] = teams[data_base[i][0]-1][1]
       #goles en contra del equipo local
       data[i-10][3] = teams[data_base[i][0]-1][2]
       #goles a favor visitante
       data[i-10][4] = teams[data_base[i][1]-1][1]
       #goles en contra del equipo visitante
       data[i-10][5] = teams[data_base[i][1]-1][2]
       #posicion del local
       data[i-10][6] = teams[data_base[i][0]-1][3]
       #posicion del visitante
       data[i-10][7] = teams[data_base[i][1]-1][3]
       #tiros a puerta del local
       data[i-10][8] = teams[data_base[i][0]-1][4]
       #tiros a puerta recibidos por el local
       data[i-10][9] = teams[data_base[i][0]-1][5]
       #tiros a puerta del visitante
       data[i-10][10] = teams[data_base[i][1]-1][4]
       #tiros a puerta recibidos por el visitante
       data[i-10][11] = teams[data_base[i][1]-1][5]
       #paradas del local
       data[i-10][12] = teams[data_base[i][0]-1][6]
       #paradas recibidas por el local
       data[i-10][13] = teams[data_base[i][0]-1][7]
       #paradas del visitante
       data[i-10][14] = teams[data_base[i][1]-1][6]
       #paradas recibidas por el visitante
       data[i-10][15] = teams[data_base[i][1]-1][7]
       #resultado
       data[i-10][16] = data_base[i][10]   


#Cargar driver neo4j
#-----------------------------------------------------------------
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "SISTGBI2019"))
#Sesion de conexion con nuestra base de datos
#-----------------------------------------------------------------
with driver.session() as session:
    print('Actualizando base de datos...')
    session.write_transaction(update_database, 1)
    session.write_transaction(update_database, 2)
    session.write_transaction(update_database, 3)
    session.write_transaction(update_database, 4)
    session.write_transaction(update_database, 5)
    session.write_transaction(update_database, 6)
    session.write_transaction(update_database, 7)
    session.write_transaction(update_database, 8)
    session.write_transaction(update_database, 9)
    session.write_transaction(update_database, 10)
    session.write_transaction(update_database, 11)
    session.write_transaction(update_database, 12)
    session.write_transaction(update_database, 13)
    session.write_transaction(update_database, 14)
    session.write_transaction(update_database, 15)
    session.write_transaction(update_database, 16)
    session.write_transaction(update_database, 17)
    session.write_transaction(update_database, 18)
    session.write_transaction(update_database, 19)
    session.write_transaction(update_database, 20)
    driver.close()




# CREA dataset TRAIN y TEST
#---------------------------------------------------------------------------------------------
print('Entrenando sistema...')
np.random.seed(123)
m_train    = np.random.rand(len(data)) < 0.8
data_train = data[m_train,]
data_test  = data[~m_train,]


# CLASE
#---------------------------------------------------------------------------------------------
clase_train = data_train[:,-1]
clase_test  = data_test[:,-1]


# MODELO
#---------------------------------------------------------------------------------------------
modelo_lr = LogisticRegression(solver='lbfgs', multi_class='auto', max_iter=999999)
modelo_lr.fit(X=data_train[:,:-1],y=clase_train)


# PREDICCION
#---------------------------------------------------------------------------------------------
predicion = modelo_lr.predict(data_test[:,:-1])


# METRICAS
#---------------------------------------------------------------------------------------------
#print(metrics.classification_report(y_true=clase_test, y_pred=predicion))
#print(pd.crosstab(data_test[:,-1], predicion, rownames=['REAL'], colnames=['PREDICCION']))






# Set web files folder
eel.init('web')
print('Iniciando aplicación web...')
    
@eel.expose # Expose this function to Javascript
def predict(a,b):
    # PREDICCION
    #---------------------------------------------------------------------------------------------
  
    local = int(a)
   
    visitante = int(b)
    
    pred = np.zeros(shape=(1,16))
    pred = np.dtype('int64').type(pred)
    
    #equipo local
    pred[0][0] = local
    #equipo visitante
    pred[0][1] = visitante
    #goles a favor local
    pred[0][2] = teams[local-1][1]
    #goles en contra del equipo local
    pred[0][3] = teams[local-1][2]
    #goles a favor visitante
    pred[0][4] = teams[visitante-1][1]
    #goles en contra del equipo visitante
    pred[0][5] = teams[visitante-1][2]
    #posicion del local
    pred[0][6] = teams[local-1][3]
    #posicion del visitante
    pred[0][7] = teams[visitante-1][3]
    #tiros a puerta del local
    pred[0][8] = teams[local-1][4]
    #tiros a puerta recibidos por el local
    pred[0][9] = teams[local-1][5]
    #tiros a puerta del visitante
    pred[0][10] = teams[visitante-1][4]
    #tiros a puerta recibidos por el visitante
    pred[0][11] = teams[visitante-1][5]
    #paradas del local
    pred[0][12] = teams[local-1][6]
    #paradas recibidas por el local
    pred[0][13] = teams[local-1][7]
    #paradas del visitante
    pred[0][14] = teams[visitante-1][6]
    #paradas recibidas por el visitante
    pred[0][15] = teams[visitante-1][7]
       
    
    miprediccion = modelo_lr.predict(pred)
    probabilidades_prediccion = modelo_lr.predict_proba(pred)

    prx= int(round(probabilidades_prediccion[0][0]*100))
    pr1= int(round(probabilidades_prediccion[0][1]*100))
    pr2= int(round(probabilidades_prediccion[0][2]*100))
    
    px= "Probabilidad de empate: " + str(prx) + "%"
    p1= "Probabilidad de victoria local: " + str(pr1) + "%"
    p2= "Probabilidad de victoria visitante: " + str(pr2) + "%"
    
    #print('')
    #print('Probabilidad de empate:')
    #print(probabilidades_prediccion[0][0])
    #print('')
    #print('Probabilidad de victoria local:')
    #print(probabilidades_prediccion[0][1])
    #print('')
    #print('Probabilidad de victoria visitante:')
    #print(probabilidades_prediccion[0][2])
    
    
    def swt(argument):#
        switcher = {
            0: "Empate",
            1: "Victoria Local",
            2: "Victoria Visitante"
        }
        return switcher.get(argument,"")
        
    m= swt(miprediccion[0])
    
    #print()
    #print('Resultado estimado:')
    #print()
    #print(m)
    eel.say_result_js(m, px, p1, p2)   # Call a Javascript function


eel.start('app.html')    # Start



