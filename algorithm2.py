import math
import numpy as np
import json
from numpy.core.fromnumeric import size
import pandas as pd
from z3 import *
# AGENT can be referred as drone
#Point Of Interest can be referred as poi or POI
"""Global Constants"""
CRITICALITY_READING = 20

"""Object Agent"""
class Agent:
    def __init__(self, name, x, y, distanceTraveled, batteryLength, poi):
        self.nameAgent = name
        self.x_coordinate = x
        self.y_coordinate = y
        self.distanceTraveled = distanceTraveled
        self.batteryLength = batteryLength
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
        return Agent(obj['name'], obj['x'], obj['y'], obj['distanceTraveled'], obj['batteryLength'], obj['assignedPOI'])
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
    print(indexPOI)
    print(columnsAGENT)
    """Populate the dataframe with distances"""
    for i in data['elements']['agent']:
        for j in data['elements']['poi']:
            #df.at[agentCounter, str(""+indexPOI[poiCounter]+"")] = calculateDistance(data['elements']['agent'][agentCounter], data['elements']['poi']['poicounter'])
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
    # counter = 0
    for i in data['elements']['poi']:
        if int(i.criticality) > 0:
            numPositives = numPositives +1
        #counter = counter +1
    # counter = 0
    print("Counter of criticality: ", checkCriticality)
    return numPositives
"""Assign a POI to the route of each Agent"""
def assignPOI2Agent(dataFrame, data, counter):
    #if dataFrame.min(axis=1).head().values[counter] == 0.0:
        #dataFrame.iloc[counter][dataFrame.values.argmin(axis=1)[counter]] = math.nan
    #    pass
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
"""Null the the value when the same POI is the closest to 2 or more Agents"""
def nullRepeatPoints():
    pass
"""Driver Code"""
def main():
    """Import JSON file"""
    f = open('sample3.json',)
    data = json.load(f, object_hook=object_decoder)
    f.close()
    print("LOOP STARTS")
    dataFrame = create_DF(data)
    print(dataFrame)
    print(dataFrame.min(axis=1))
  
    print(np.size(dataFrame.index))
    print(np.size(dataFrame.columns))
    print(dataFrame.min(axis=1)[0])
    print(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[0])
    print(dataFrame.min(axis=1).head().values[0])
    print(dataFrame[dataFrame>0].values.argmin(axis=1)[0])
    print(dataFrame.columns)
    print(dataFrame.index)
    print(dataFrame.index[0])
    """Removing duplicate values loop"""
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # END OF LOOP     
    
    for counter_i in range(np.size(dataFrame.index)):
        print("Criticality")
        print(counter_i, (data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counter_i]].criticality))
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counter_i]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counter_i)
            distanceTraveled(data, dataFrame, counter_i)
            assignNewCoordinates(data, dataFrame, counter_i)
            reduceCriticality(data, dataFrame, counter_i)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    print(dataFrame)
    print(dataFrame.min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    """Data before Dataframe Update"""
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
    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

    for colY in (range(np.size(dataFrame.columns))):
        for rowX in (range(np.size(dataFrame.index))):
            # New Line to NaN items with <=0 of criticality
            #if int(data['elements']['poi'][rowX].criticality) < CRITICALITY_READING:
            #    dataFrame.iat[rowX,colY] = math.nan
                #pass
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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > CRITICALITY_READING: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS
    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS
    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS
    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS
    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS
    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS
    
    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS

    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS

    print("LOOP STARTS")
    # ORIGINAL LOOP STARTS
    dataFrame = create_DF(data) #fix this
    """Removing duplicate values loop"""
    # start removing duplicates llop
    repeatedAgents = []
    repeatedValues = []
    repeatedIndexes = []

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
    # end of removing duplicates loop
    """Data after Dataframe Update"""
    print("Data after Dataframe Update")
    print("Agents")
    o1 = 0
    for o in data['elements']['agent']:
        print(data['elements']['agent'][o1].nameAgent, data['elements']['agent'][o1].x_coordinate, data['elements']['agent'][o1].y_coordinate, data['elements']['agent'][o1].distanceTraveled, data['elements']['agent'][o1].batteryLength, data['elements']['agent'][o1].closestPOI)
        o1 = o1 +1
    print("Points of Interest")
    p1 = 0
    for p in data['elements']['poi']:
        print(data['elements']['poi'][p1].namePoint, data['elements']['poi'][p1].x_coordinate, data['elements']['poi'][p1].y_coordinate, data['elements']['poi'][p1].closestAgent, data['elements']['poi'][p1].criticality)
        p1 = p1 + 1
    print("End of printing")

    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    #counting = 0
    for counting_j in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting_j]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting_j)
            distanceTraveled(data, dataFrame, counting_j)
            assignNewCoordinates(data, dataFrame, counting_j)
            reduceCriticality(data, dataFrame, counting_j)
        else:
            pass  #assign an empty value in the route
        #counting = counting + 1
    #counting = 0
   
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    # ORIGINAL LOOP ENDS
    print("DISTANCE TRAVELED")
    print(data['elements']['agent'][0].distanceTraveled, data['elements']['agent'][0].batteryLength)
    print(data['elements']['agent'][1].distanceTraveled, data['elements']['agent'][1].batteryLength)
    print(data['elements']['agent'][2].distanceTraveled, data['elements']['agent'][2].batteryLength)
    """Z3 implementation"""
    print("Z3 implementation")
    """Z3 variables"""
    totalDis, batteryLen = Reals ('totalDis batteryLen')
    counterZ3 = 0
    s = Solver()
        
    """Empty equation"""
    s.add(batteryLen > totalDis)
    s.push()
    for elemZ3 in range(np.size(data['elements']['agent'])):
       
        #s.push()
        #s.add(totalDis == data['elements']['agent'][0].distanceTraveled, batteryLen == batteryLen == data['elements']['agent'][0].batteryLength)
        #print(s)
        #print(s.check())
        """Unsatisfacted Case"""
        s.pop()
        s.add(totalDis == data['elements']['agent'][counterZ3].distanceTraveled, batteryLen == data['elements']['agent'][counterZ3].batteryLength)
        #s.push()
        print(s)
        print(s.check())
        """Removing constrainst and creating new case"""
        counterZ3 = counterZ3 +1
    counterZ3 = 0
"""Calling Main function"""
if __name__=="__main__":
    main()

# might be useful code
#for repeated in (range(np.size(dataFrame.index))):
#        if repeated == (np.size(dataFrame.index)-2):
#            break
#        if dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[repeated] == dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[repeated+1]:
#            repeatedAgents.append(dataFrame.index[repeated])
#        if dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[repeated] == dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[repeated+2]:
#            repeatedAgents.append(dataFrame.index[repeated])