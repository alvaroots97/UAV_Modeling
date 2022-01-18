import math
import numpy as np
import json
import pandas as pd
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
        indexPOI.append(str(data['elements']['agent'][indexCounter].nameAgent))
        indexCounter = indexCounter +1
    for each in data['elements']['poi']:
        columnsAGENT.append(str(data['elements']['poi'][columnsCounter].namePoint))
        columnsCounter = columnsCounter +1
    df = pd.DataFrame(data, index = indexPOI, columns = columnsAGENT)
    #indexCounter = 0
    #columnsCounter = 0
    agentCounter = 0
    poiCounter = 0
    """Populate the dataframe with distances"""
    for i in data['elements']['agent']:
        for j in data['elements']['poi']:
            #df.at[agentCounter, str(""+indexPOI[poiCounter]+"")] = calculateDistance(data['elements']['agent'][agentCounter], data['elements']['poi']['poicounter'])
            df.iloc[[agentCounter],[poiCounter]] = calculateDistance(data['elements']['agent'][agentCounter], data['elements']['poi'][poiCounter])
            poiCounter = poiCounter +1
        poiCounter = 0
        agentCounter = agentCounter +1
    #agentCounter = 0
    #poiCounter = 0
    return df
"""Check how many Criticality values are positive"""
def checkCriticality(data):
    numPositives = 0
    counter = 0
    for each in data['elements']['poi']:
        if int(data['elements']['poi'][counter].criticality) > 0:
            numPositives = numPositives +1
        counter = counter +1
    counter = 0
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
    #editableData = data
    
    dataFrame = create_DF(data)
    print(dataFrame)
    print(dataFrame.min(axis=1))
    counting = 0
    for each in range(np.size(dataFrame.index)):
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting]].criticality) > 0: #updated [dataframde>0]
            assignPOI2Agent(dataFrame, data, counting)
            distanceTraveled(data, dataFrame, counting)
            assignNewCoordinates(data, dataFrame, counting)
            reduceCriticality(data, dataFrame, counting)
        else:
            pass  #assign an empty value in the route
        counting = counting + 1
    counting = 0
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    print(dataFrame)
    print(dataFrame.min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    dataFrame = create_DF(data)
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].closestsPOI)
    print(data['elements']['agent'][1].closestsPOI)
    print(data['elements']['agent'][2].closestsPOI)
    print("-----")
    for each in range(np.size(dataFrame.index)):
        #if dataFrame.min(axis=1).head().values[counting] == 0.0:
        #    dataFrame.iloc[counting][dataFrame.values.argmin(axis=1)[counting]] = math.nan
        #if int(data['elements']['poi'][dataFrame.values.argmin(axis=1)[counting]].criticality) <= 0:
        #    dataFrame.iloc[counting][dataFrame.values.argmin(axis=1)[counting]] = math.nan
        if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting]].criticality) > 0:
            assignPOI2Agent(dataFrame, data, counting)
            distanceTraveled(data, dataFrame, counting)
            assignNewCoordinates(data, dataFrame, counting)
            reduceCriticality(data, dataFrame, counting)
        else:
            pass
        counting = counting + 1
    counting = 0
    # for each in range(np.size(dataFrame.index)):
    #     if int(data['elements']['poi'][dataFrame[dataFrame>0].values.argmin(axis=1)[counting]].criticality) > 0:
    #         distanceTraveled(data, dataFrame, counting)
    #         assignNewCoordinates(data, dataFrame, counting)
    #         reduceCriticality(data, dataFrame, counting)
    #     else:
    #         pass
    #     counting = counting + 1
    # counting = 0
    print(dataFrame)
    print(dataFrame[dataFrame>0].min(axis=1))
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route)
    """ dataFrame = create_DF(data)
    print(np.size(dataFrame.index))
    counting = 0
    while checkCriticality(data) > 0:
        dataFrame = create_DF(data)
        #print(dataFrame)
        #print(dataFrame.min(axis=1))
        for each in range(np.size(dataFrame.index)):
            if int(data['elements']['poi'][dataFrame.values.argmin(axis=1)[counting]].criticality) <= 0:
               pass
            else:
               assignPOI2Agent(dataFrame, data, counting)
               distanceTraveled(data, dataFrame, counting)
               assignNewCoordinates(data, dataFrame, counting)
               reduceCriticality(data, dataFrame, counting)
            counting = counting + 1
        counting = 0
    print(data['elements']['agent'][0].route)
    print(data['elements']['agent'][1].route)
    print(data['elements']['agent'][2].route) """    
        
"""Calling Main function"""
if __name__=="__main__":
    main()

""" print(data['elements'])
    dataFrame = create_DF(data) #comment it out
    print(dataFrame) #testing
    print(dataFrame.min(axis=1)) #testing
    print(checkCriticality(data)) #testing
    assignPOI2Agent(dataFrame, data, 0) #testing
    assignNewCoordinates(data, dataFrame, 0) #testing
    distanceTraveled(data, dataFrame, 0) #testing
    reduceCriticality(data, dataFrame, 0) #testing
    print("Look at me")
    print(dataFrame.min(axis=1).head().values[0])
    
    dataFrame = create_DF(data)
    if dataFrame.min(axis=1).head().values[0] == 0.0:
        dataFrame.iloc[0][dataFrame.values.argmin(axis=1)[0]] = math.nan
    print(dataFrame)
    print(dataFrame.min(axis=1))
    print(checkCriticality(data)) #testing
    assignPOI2Agent(dataFrame, data, 0) #testing
    assignNewCoordinates(data, dataFrame, 0) #testing
    distanceTraveled(data, dataFrame, 0) #testing
    reduceCriticality(data, dataFrame, 0) #testing
    print(dataFrame.values.argmin(axis=1)[0]) 
    
    print("Testing second minimum value")
    print(dataFrame[dataFrame>0].min(axis=1)[0]) #value of distance
    print(dataFrame[dataFrame>0].values.argmin(axis=1)[0]) #index
    print(dataFrame[dataFrame>0].columns[dataFrame[dataFrame>0].values.argmin(axis=1)[0]]) #point
    print("next")
    #index first
    print(dataFrame[dataFrame>0].columns.get_loc(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[0])) #good one
    print(dataFrame[dataFrame>0].astype(float).idxmin(axis=1)[0]) #good one #point"""