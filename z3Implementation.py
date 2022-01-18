import sys
import algorithm3
from z3 import *
import numpy as np

"""Global Constants"""
CRITICALITY_READING = 20
UAVDISABLED = 2
LINE_OF_SEPARATION = "---------------------------------"
"""Define UAV to disable"""
def numberOfUAVDisabled():
    return UAVDISABLED
"""Driver Code"""
def main():
    data = algorithm3.main()
    print(LINE_OF_SEPARATION)
    """Z3 implementation"""
    print("FROM Z3 PROGRAM")
    print("Z3 implementation")
    
    print("2. Resilience")
    """Scenario where one or multiple UAV fail, so can the others complete the visits?"""
    totalDis, batteryLen = Reals ('totalDis batteryLen')
    s = Solver()
    """Empty equation"""
    s.add(batteryLen > totalDis)
    for elemZ3 in range(np.size(data['elements']['agent'])):
        s.push()    # start up stack
        s.add(totalDis == data['elements']['agent'][elemZ3].distanceTraveled, batteryLen == data['elements']['agent'][elemZ3].batteryLength)  #add variables
        s.check()   #check current constraint
        print(s)
        print(s.check())
        s.pop() #remove last stack

    print(LINE_OF_SEPARATION)
"""Calling Main function"""
if __name__=="__main__":
    main()