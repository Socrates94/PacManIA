from Ghost import Ghost
class Dummy: pass
pc = Dummy()
pc.position = [200, 1, 200]
import pandas as pd
import numpy as np

MC = [
    [10,0,21,0,11,10,0,21,0,11],
    [24,0,25,21,23,23,21,25,0,22],
    [12,0,22,12,11,10,13,24,0,13],
    [0,0,0,10,23,23,11,0,0,0],
    [26,0,25,22,0,0,24,25,0,27],
    [0,0,0,24,0,0,22,0,0,0],
    [10,0,25,23,11,10,23,25,0,11],
    [12,11,24,21,23,23,21,22,10,13],
    [10,23,13,12,11,10,13,12,23,11],
    [12,0,0,0,23,23,0,0,0,13]
]
xMC = [0,30,71,114,156,199,242,286,328,358]
XPxToMC = np.full(359, -1, dtype=int)
for i,x in enumerate(xMC): XPxToMC[x] = i
yMC = [0,51,90,130,168,208,244,282,320,360]
YPxToMC = np.full(361, -1, dtype=int)
for i,y in enumerate(yMC): YPxToMC[y] = i

matrix = []

pinky = Ghost(matrix, MC, XPxToMC, YPxToMC, 378, 380, 2, 2)
# Simulating a movement of pacman to get pacman_dir
pc.position = [199, 1, 200] 
pinky.update2(pc.position, [pinky]) 
print("Pinky update complete without errors.")
