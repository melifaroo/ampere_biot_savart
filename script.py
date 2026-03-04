
import logic.geometry as geometry
import logic.excitation as excitation
import logic.presentation as presentation
import logic.solution as solution
import matplotlib as mpl
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
mpl.rcParams['axes3d.mouserotationstyle'] = 'trackball' # , 'trackball', 'azel', 'sphere', or 'arcball'

T = 20.0
N  = 201
alpha    = 0.0
freq     = 60
I  = 80.0
current_type    = "peak"   # "rms" 
excitation_type = "rlc" # "gen"        
schema          = "ABC"

conductors = []
conductors.append( geometry.Conductor(
        [  0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00],
        [ -0.05,  -0.05,  -0.05,   0.10,   0.10,   0.10,   0.40,   0.40,   0.50,   0.50,   0.50],
        [  1.00,   0.40,   0.15,   0.15,   0.10,   0.00,   0.00,   0.10,   0.10,   0.50,   1.00],
        0,
        [[     0,      1,      1,      1,      1,      1,      1,      1,      1,      0]],
        0.02
))
conductors.append( geometry.Conductor(
        [  0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10,   0.10],
        [ -0.05,  -0.05,  -0.05,   0.10,   0.10,   0.10,   0.40,   0.40,   0.50,   0.50,   0.50],
        [  1.00,   0.40,   0.15,   0.15,   0.10,   0.00,   0.00,   0.10,   0.10,   0.50,   1.00],
        1,
        [[     0,      1,      1,      1,      1,      1,      1,      1,      1,      0]],
        0.02
))

conductors.append( geometry.Conductor(
        [  0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20,   0.20],
        [ -0.05,  -0.05,  -0.05,   0.10,   0.10,   0.10,   0.40,   0.40,   0.50,   0.50,   0.50],
        [  1.00,   0.40,   0.15,   0.15,   0.10,   0.00,   0.00,   0.10,   0.10,   0.50,   1.00],
        2,
        [[     0,      1,      1,      1,      1,      1,      1,      1,      1,      0]],
        0.02
))
filedPoints = geometry.WayPoints(
    [  0.00,  0.10,  0.20],
    [ -0.05, -0.05, -0.05],
    [  0.00,  0.00,  0.00]
)

geom = geometry.fromConductorsWP( conductors ,filedPoints )

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
