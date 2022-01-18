import math
import numpy as np
import json
import pandas as pd
from z3 import *
from z3Implementation import numberOfUAVDisabled
"""Global Constants"""
CRITICALITY_READING = 20
LINE_OF_SEPARATION = "---------------------------------"
"""Object Agent"""
class Agent:
    def __init__(self, name, x, y, distanceTraveled, batteryLength, batteryCharge, poi):
        self.nameAgent = name
        self.x_coordinate = x
        self.y_coordinate = y
        self.distanceTraveled = distanceTraveled
        self.batteryLength = batteryLength
        self.batteryCharge = batteryCharge
        self.closestPOI = poi
        self.route = []
    def distance_from_POI(self, distance):
        self.distance = distance
    def route_Agent(self, item):
        self.route.append(item)
        return self.route
"""Object Point of Interest"""
class PointOfInterest:
    def __init__(self, name, x, y, agent, criticality):
        self.namePoint = name
        self.x_coordinate = x
        self.y_coordinate = y
        self.closestAgent = agent
        self.criticality = criticality
"""Json Decoder"""
def object_decoder(obj):
    if '__type__' in obj and obj['__type__'] == 'drone':
        return Agent(obj['name'], obj['x'], obj['y'], obj['distanceTraveled'], obj['batteryLength'], obj['batteryCharge'], obj['assignedPOI'])
    if '__type__' in obj and obj['__type__'] == 'poi':
        return PointOfInterest(obj['name'], obj['x'], obj['y'], obj['assignedAgent'], obj['criticality'])
    return obj
"""Calculate the distance between 2 points"""
def calculateDistance(agent, poi):
    agentX = int(agent.x_coordinate)
    agentY = int(agent.y_coordinate)
    poiX = int(poi.x_coordinate)
    poiY = int(poi.y_coordinate)
    distance2points = np.round(math.sqrt(pow((agentX - poiX), 2) + pow((agentY - poiY), 2)), 2)
    return distance2points
"""Create a dataframe to store all distances"""
def create_DF(data):
    indexPOI = []
    columnsAGENT = []
    indexCounter = 0
    columnsCounter = 0
    for each in data['elements']['agent']:
        columnsAGENT.append(str(data['elements']['agent'][indexCounter].nameAgent))
        indexCounter = indexCounter +1
    for each in data['elements']['poi']:
        indexPOI.append(str(data['elements']['poi'][columnsCounter].namePoint))
        columnsCounter = columnsCounter +1
    df = pd.DataFrame(data, index = columnsAGENT, columns = indexPOI)
    indexCounter = 0
    columnsCounter = 0
    agentCounter = 0
    poiCounter = 0
    """Populate the dataframe with distances"""
    for i in data['elements']['agent']:
        for j in data['elements']['poi']:
            df.iloc[[agentCounter],[poiCounter]] = calculateDistance(data['elements']['agent'][agentCounter], data['elements']['poi'][poiCounter])
            poiCounter = poiCounter +1
        poiCounter = 0
        agentCounter = agentCounter +1
    agentCounter = 0
    poiCounter = 0
    return df
"""Check how many Criticality values are positive"""
def checkCriticality(data):
    numPositives = 0
    for i in data['elements']['poi']:
        if int(i.criticality) > 0:
            numPositives = numPositives +1
    print("Counter of criticality: ", checkCriticality)
    return numPositives
"""Assign a POI to the route of each Agent"""
def assignPOI2Agent(dataFrame, data, counter):
    data['elements']['agent'][counter].closestsPOI = dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter] #updated [dataframe>0]
    data['elements']['agent'][counter].route_Agent(data['elements']['agent'][counter].closestsPOI)
    print(data['elements']['agent'][counter].closestsPOI)
"""Calculate distance traveled"""
def distanceTraveled (data, dataFrame, counter):
    distance = float(dataFrame[dataFrame>0].min(axis=1).head().values[counter]) #updated [dataframe>0]
    data['elements']['agent'][counter].distanceTraveled =np.round(float(data['elements']['agent'][counter].distanceTraveled) + distance, 2)
    print(data['elements']['agent'][counter].distanceTraveled)
"""Assign new coordinates to each Agent"""
def assignNewCoordinates(data, dataFrame, counter):
    colAssign = dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter]) #updated [dataframe>0]
    valColAssign = "'"+str(colAssign)+"'"
    print(colAssign)
    data['elements']['agent'][counter].x_coordinate = data['elements']['poi'][colAssign].x_coordinate
    data['elements']['agent'][counter].y_coordinate = data['elements']['poi'][colAssign].y_coordinate
    print(data['elements']['agent'][counter].x_coordinate)
    print(data['elements']['agent'][counter].y_coordinate)
"""Reduce Criticality"""
def reduceCriticality (data, dataFrame, counter):
    data['elements']['poi'][dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter])].criticality = float(data['elements']['poi'][dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter])].criticality) - CRITICALITY_READING #updated [dataframe>0]
    print(data['elements']['poi'][dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter])].criticality)
"""Driver Code"""
def main():
    """Import JSON file"""
    f = open('sample3.json',)
    data = json.load(f, object_hook=object_decoder)
    f.close()

    print("Message from Z3")
    messageFromZ3 = numberOfUAVDisabled()
    print(messageFromZ3)

    for uav in data:
        if uav.index == messageFromZ3:
            del uav[messageFromZ3]


    for looping in range(5):
        print("LOOP STARTS")
        dataFrame = create_DF(data)
        print(dataFrame)
        print(dataFrame.min(axis=1))
        #1A STARTS
        """Removing duplicate values loop"""
        #If 2 or more UAV have the same POI, the smallest/closest will prevail
        repeatedAgents = []
        repeatedValues = []
        repeatedIndexes = []
        print("Columns")
        print(dataFrame.columns)
        for colY in (range(np.size(dataFrame.columns))):
            for rowX in (range(np.size(dataFrame.index))):
                if dataFrame.iat[rowX,colY] == dataFrame.min(axis=1)[rowX]:
                    repeatedAgents.append(dataFrame.index[rowX])
                    repeatedValues.append(dataFrame.min(axis=1)[rowX])
                    repeatedIndexes.append(rowX)
            for element in (range(np.size(repeatedAgents))):
                if repeatedValues[element] != min(repeatedValues):
                    dataFrame.iloc[[repeatedIndexes[element]],[colY]] = math.nan
                
            repeatedAgents = []
            repeatedValues = []
            repeatedIndexes = []
        #1A ENDS
        #1B STARTS
        for counter_i in range(np.size(dataFrame.index)):
            #print("criticality", data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counter_i]].criticality)
            #print(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter_i])
            #print(dataFrame.min(axis=1)[counter_i])
            #print(dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter_i]))
            if int(data['elements']['poi'][dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter_i])].criticality) < CRITICALITY_READING:
                dataFrame.iloc[[counter_i],[dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter_i])]] = math.nan
                #data['elements']['poi'][dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[counter_i])].criticality = math.nan
            #elif int(data['elements']['agent'][counter_i].batteryLength) == 0:
            assignPOI2Agent(dataFrame, data, counter_i)
            distanceTraveled(data, dataFrame, counter_i)
            assignNewCoordinates(data, dataFrame, counter_i)
            reduceCriticality(data, dataFrame, counter_i)
        #1B ENDS
        """Dataframe Information"""
        print("Data before Dataframe Update")
        print("Agents")
        n1 = 0
        for n in data['elements']['agent']:
            print(data['elements']['agent'][n1].nameAgent, data['elements']['agent'][n1].x_coordinate, data['elements']['agent'][n1].y_coordinate, data['elements']['agent'][n1].distanceTraveled, data['elements']['agent'][n1].batteryLength, data['elements']['agent'][n1].closestPOI)
            n1 = n1 + 1
        print("Points of Interest")
        m1 = 0
        for m in data['elements']['poi']:
            print(data['elements']['poi'][m1].namePoint, data['elements']['poi'][m1].x_coordinate, data['elements']['poi'][m1].y_coordinate, data['elements']['poi'][m1].closestAgent, data['elements']['poi'][m1].criticality)
            m1 = m1 + 1
        print("End of printing")
        print(data['elements']['agent'][0].route)
        print(data['elements']['agent'][1].route)
        print(data['elements']['agent'][2].route)
    return data
"""Calling Main function"""
if __name__=="__main__":
    main()