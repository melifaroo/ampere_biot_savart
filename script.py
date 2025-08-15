
import logic.geometry as geometry
import logic.excitation as excitation
import logic.presentation as presentation
import logic.solution as solution
import matplotlib as mpl
import matplotlib.pyplot as plt
from dataclasses import dataclass
import warnings
warnings.filterwarnings("ignore")
mpl.rcParams['axes3d.mouserotationstyle'] = 'trackball' # , 'trackball', 'azel', 'sphere', or 'arcball'

@dataclass
class vec3d:
    X : float
    Y : float
    Z : float
    def __init__(self):
        pass
    
@dataclass
class pole3:
    A : vec3d
    B : vec3d
    C : vec3d
    def __init__(self):
        self.A = vec3d()
        self.B = vec3d()
        self.C = vec3d()

T = 20.0
N  = 21
alpha    = 0.0
freq     = 60

I  = 80.0
current_type    = "peak"   # "rms" 

excitation_type = "rlc" # "gen"        
schema          = "ABC"

GEOM_MAIN = pole3()
GEOM_MAIN.A.X = [  0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00]
GEOM_MAIN.A.Y = [ -0.05,  -0.05,  -0.05,   0.10,   0.10,   0.10,   0.40,   0.40,   0.50,   0.50,   0.50]
GEOM_MAIN.A.Z = [  1.00,   0.40,   0.15,   0.15,   0.10,   0.00,   0.00,   0.10,   0.10,   0.50,   1.00]
segA = (len(GEOM_MAIN.A.X)-1) 
GEOM_MAIN.B.X = [  0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10]
GEOM_MAIN.B.Y = [ -0.05,  -0.05,  -0.05,   0.10,   0.10,   0.10,   0.40,   0.40,   0.50,   0.50,   0.50]
GEOM_MAIN.B.Z = [  1.00,   0.40,   0.15,   0.15,   0.10,   0.00,   0.00,   0.10,   0.10,   0.50,   1.00]
segB = (len(GEOM_MAIN.B.X)-1)
GEOM_MAIN.C.X = [  0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20]
GEOM_MAIN.C.Y = [ -0.05,  -0.05,  -0.05,   0.10,   0.10,   0.10,   0.40,   0.40,   0.50,   0.50,   0.50]
GEOM_MAIN.C.Z = [  1.00,   0.40,   0.15,   0.15,   0.10,   0.00,   0.00,   0.10,   0.10,   0.50,   1.00] 
segC = (len(GEOM_MAIN.C.X)-1)
GEOM_FELD = vec3d()
GEOM_FELD.X = [  0.00,  0.10,  0.20]
GEOM_FELD.Y = [ -0.05, -0.05, -0.05]
GEOM_FELD.Z = [  0.00,  0.00,  0.00]

force_segs = [                      [     0,      1,      1,      1,      1,      1,      1,      1,      1,      0] + [0]*(segB+segC),
                [0]*segA +          [     0,      1,      1,      1,      1,      1,      1,      1,      1,      0] + [0]*segC,
                [0]*(segA+segB) +   [     0,      1,      1,      1,      1,      1,      1,      1,      1,      0]]

R = [ 0.02 ]* ( segA + segB + segC )

geom = geometry.sample_input(
        XA = GEOM_MAIN.A.X, YA = GEOM_MAIN.A.Y, ZA = GEOM_MAIN.A.Z,  
        XB = GEOM_MAIN.B.X, YB = GEOM_MAIN.B.Y, ZB = GEOM_MAIN.B.Z,  
        XC = GEOM_MAIN.C.X, YC = GEOM_MAIN.C.Y, ZC = GEOM_MAIN.C.Z,             
        R = R, 
        NF = force_segs, 
        X = GEOM_FELD.X , Y = GEOM_FELD.Y , Z = GEOM_FELD.Z                
        )     


current = excitation.build(T, N, I, source_type = excitation_type, current=current_type, alpha=alpha/180*3.1415, freq=freq)

inductances = solution.evalBranchCurrents(geom, current, peakPhaseNumber = 1 , asymK_override = None)

figure = plt.figure()
grid = plt.GridSpec(nrows = 2, ncols = 4 , wspace=0.3, hspace=0.2, left=0.05, right=0.95, top=0.95, bottom = 0.05)

ax = plt.subplot(grid[:,0:2], projection='3d')
presentation.plotGeometry(geom, ax)
axi = plt.subplot(grid[:,3])
presentation.plotCurrent(current, axi, figure)
axu = plt.subplot(grid[0,2])
presentation.plotVoltagePhase(current, axu, figure)
axul = plt.subplot(grid[1,2])
presentation.plotVoltageLinear(current, axul, figure)
      
results = solution.solve(geom, current)  
presentation.plotResults(results, block = True) 
