import numpy as np
from dataclasses import dataclass
from typing import Final

SUBFIELD_SEPARATOR : Final = '.'
GEOM_VAR_NAME : Final = 'WPNT'
FELD_VAR_NAME : Final = 'MPRB'
FORC_VAR_NAME : Final = 'FMSK'
RADI_VAR_NAME: Final =  'RADI'
SAME_VAR_NAME : Final = 'PSAM'
PDST_VAR_NAME : Final = 'PDST'
PCNT_VAR_NAME: Final = 'PCNT'
CONN_VAR_NAME: Final = 'PCON'
DEFAULT_SEGMENT_RADIUS: Final = 0.02

COND_LETTERS : Final = 'ABCS'

GND_VAR_NAME : Final = 'GNDP'
SRC_VAR_NAME : Final = 'SRCP'


@dataclass
class Geometry:
    XS: np.ndarray
    XE: np.ndarray
    YS: np.ndarray
    YE: np.ndarray
    ZS: np.ndarray
    ZE: np.ndarray
    NP: np.ndarray
    NF: np.ndarray
    NL: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    Z: np.ndarray
    # T: float
    # I: float
    R: np.ndarray
        
    def __init__(self, XS, XE, YS, YE, ZS, ZE, R, NP, NF, X, Y, Z, NL=np.array([])):
        if not( (XS.shape==XE.shape) & 
                (YS.shape==YE.shape) & 
                (ZS.shape==ZE.shape) &
                (XS.shape==YS.shape) & 
                (XS.shape==ZS.shape) & 
                (XS.shape==NP.shape) &
                (X.shape==Y.shape) & 
                (X.shape==Z.shape) ):
        # if not( (len(XS)==len(XE)) & 
        #         (len(YS)==len(YE))& 
        #         (len(ZS)==len(ZE)) &
        #         (len(XS)==len(YS)) & 
        #         (len(XS)==len(ZS)) & 
        #         (len(XS)==len(NP)) &
        #         (len(X)==len(Y)) & 
        #         (len(X)==len(Z)) ):
            exit('Exit on error: Geometry definition error - Input vectors dimensions must agree')     
        self.XS = XS #X coordinates of circuit segments start points
        self.XE = XE #X coordinates of circuit segments end points
        self.YS = YS #Y coordinates of circuit segments start points
        self.YE = YE #Y coordinates of circuit segments end points
        self.ZS = ZS #Z coordinates of circuit segments start points
        self.ZE = ZE #Z coordinates of circuit segments end points
        self.NP = NP #index of current branch for segments
        self.NF = NF #mask of segments for force output summation
        self.NL = NL
        self.X = X #X coordinates of field output points
        self.Y = Y #Y coordinates of field output points
        self.Z = Z #Z coordinates of field output points
        self.R = R #default radius of conductor using for corner approximation
        
    def getCircuitPhaseCount(self):
        return int(1 + self.NP.max() - self.NP.min())
        
    def rotateX(self):
        ys = -self.ZS
        ye = -self.ZE
        self.ZS = self.YS
        self.ZE = self.YE
        self.YS = ys
        self.YE = ye
                
    def rotateY(self):
        xs = +self.ZS
        xe = +self.ZE
        self.ZS = -self.XS
        self.ZE = -self.XE
        self.XS = xs
        self.XE = xe        
        
    def rotateZ(self):
        xs = -self.YS
        xe = -self.YE
        self.YS = self.XS
        self.YE = self.XE
        self.XS = xs
        self.XE = xe
            
    def mirriorZ(self):
        self.ZS = -self.ZS
        self.ZE = -self.ZE
                
    def mirriorX(self):
        self.XS = -self.XS
        self.XE = -self.XE        
        
    def mirriorY(self):
        self.YS = -self.YS
        self.YE = -self.YE
    
@dataclass
class WayPoints:
    X : list[float] # X coords array of way-points, size n
    Y : list[float] # Y coords array of way-points, size n
    Z : list[float] # Z coords array of way-points, size n
    def __init__(this, X = [], Y = [], Z = []):
        if not( (len(X)==len(Y)) & (len(Y)==len(Z)) ):
            exit('Exit on error: Geometry definition error - Input vectors dimensions must agree')
        this.X = X
        this.Y = Y
        this.Z = Z     

@dataclass
class Conductor(WayPoints):
    R : list[float] # radius of segments array, size n-1
    F : list[list[int]] # force masks, size (m, n-1)
    N : int # conductor phase index
    segs : int
    def __init__(this, X, Y, Z, N, F = [], R = []):    
        super().__init__(X, Y, Z)

        this.segs = len(X) - 1

        if isinstance(F, list):
            if len(F)>0 and any( [ len(f)!=this.segs for f in F ] ):
                exit('Exit on error: Geometry definition error - Input vectors dimensions must agree') 
        elif isinstance(F, int):
            F = [ [F]*this.segs ]
        else: F = []

        if isinstance(R, list):
            if len(R)==0:
                R = [DEFAULT_SEGMENT_RADIUS]*this.segs
            elif not len(R)==this.segs:
                exit('Exit on error: Geometry definition error - Input vectors dimensions must agree')
        elif isinstance(R, float):
            R = [R]*this.segs
        else: R = [DEFAULT_SEGMENT_RADIUS]*this.segs

        this.R = R
        this.F = F
        this.N = N
        
def fromConductorsWP( conductors : list[Conductor], field_points: WayPoints ):
    """

    """
    Sseg = slice(None, -1, +1)
    Eseg = slice(+1, None, +1)

    X = []
    Y = []
    Z = []
    X1 = []
    X2 = []
    Y1 = []
    Y2 = []
    Z1 = []
    Z2 = []
    R = []
    N = []
    all_segs = 0

    for conductor in conductors:
        X1  = np.append( X1, conductor.X[Sseg] )
        X2  = np.append( X2, conductor.X[Eseg] )
        Y1  = np.append( Y1, conductor.Y[Sseg] )
        Y2  = np.append( Y2, conductor.Y[Eseg] )
        Z1  = np.append( Z1, conductor.Z[Sseg] )
        Z2  = np.append( Z2, conductor.Z[Eseg] )
        R = np.append(R, conductor.R)
        N = np.append(N, [conductor.N]*conductor.segs)
        all_segs = all_segs + conductor.segs

    X  = np.array(field_points.X)
    Y  = np.array(field_points.Y)
    Z  = np.array(field_points.Z)
        
    NF = []
    pre_segs = 0
    for conductor in conductors:
        segs = conductor.segs
        for f in conductor.F:
            if len(NF)==0:
                NF =  [[0]*pre_segs + f + [0]*(all_segs-pre_segs-segs) ] 
            else:
                NF = np.vstack( ( NF, [[0]*pre_segs + f + [0]*(all_segs-pre_segs-segs) ] ) )
        pre_segs = pre_segs + segs

    NL = np.stack( (N==0, N==1, N==2) )
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, R, N, NF, X, Y, Z, NL)
