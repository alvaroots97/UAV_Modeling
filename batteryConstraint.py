from z3 import *

totalDis, batteryLen = Reals ('totalDis batteryLen')
s = Solver()
"""Variables"""
print(s)
s.add(totalDis > batteryLen)
"""Empty equation"""
print(s)
print(s.check())
"""Unsatisfacted Case"""
s.push()
s.add(totalDis == 900, batteryLen == 1000)
print(s)
print(s.check())
"""Removing constrainst and creating new case"""
s.pop()
s.add(totalDis == 1000, batteryLen == 800)
print(s)
print(s.check())
