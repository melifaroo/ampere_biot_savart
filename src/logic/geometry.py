import numpy as np
from dataclasses import dataclass

@dataclass
class Geometry:
    XS: float
    XE: float
    YS: float
    YE: float
    ZS: float
    ZE: float
    Nph: int
    NF: int
    NL: int
    X: float
    Y: float
    Z: float
    T: float
    I: float
    r: float = 0.02  # Default value
        
    def __init__(self, XS, XE, YS, YE, ZS, ZE, Nph, NF, X, Y, Z, NL=np.array([]), r=0.02):
        if not( (XS.shape==XE.shape) & 
                (YS.shape==YE.shape) & 
                (ZS.shape==ZE.shape) &
                (XS.shape==YS.shape) & 
                (XS.shape==ZS.shape) & 
                (XS.shape==Nph.shape) &
                (X.shape==Y.shape) & 
                (X.shape==Z.shape) ):
            exit('Exit on error: Geometry definition error - Input vectors dimensions must agree')     
        self.XS = XS #X coordinates of circuit segments start points
        self.XE = XE #X coordinates of circuit segments end points
        self.YS = YS #Y coordinates of circuit segments start points
        self.YE = YE #Y coordinates of circuit segments end points
        self.ZS = ZS #Z coordinates of circuit segments start points
        self.ZE = ZE #Z coordinates of circuit segments end points
        self.Nph = Nph #index of current branch for segments
        self.NF = NF #mask of segments for force output summation
        self.NL = NL
        self.X = X #X coordinates of field output points
        self.Y = Y #Y coordinates of field output points
        self.Z = Z #Z coordinates of field output points
        self.r = r #default radius of conductor using for corner approximation
        
    def getCircuitPhaseCount(self):
        return 1 + self.Nph.max() - self.Nph.min()
        
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
        
    
def sample_II_inf(L = 1, LP = 1, INF = 1e1, L0 = 1):
            
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_2_I) definition error - "L"(default=1) value should be greater than 0')     
                            
    if not( (LP>0) ):
        exit('Exit on error: Geometry(sample_2_I) definition error - "LP"(default=1) value should be greater than 0')     
            
    if not( (INF>L) ):
        exit('Exit on error: Geometry(sample_2_I) definition error - "INF"(default=10) value should be greater than "L"')     
            
    seg = 3;                

    X1 = np.array( [0]*seg + [+LP]*seg )
    X2 = X1

    Y1 = np.array( [0]*seg*2 )
    Y2 = Y1

    Z1 = [ -INF, -L/2, +L/2 ]
    Z1 = np.array(Z1 + Z1 )
    Z2 = [ -L/2, +L/2, INF ]
    Z2 = np.array(Z2 + Z2 )

    Nph = np.array([1]*seg + [2]*seg)-1   
    
    X = np.array([ 0,  LP])
    Y = np.array([ -L0 , -L0 ])
    Z = np.array([ 0 , 0 ])

    out = [0, 1, 0]
    NF = np.array([( out + [0]*seg ) , ( [0]*seg + out )   ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z)


def sample_II(L = 1, LP = 1, L0 = 1):
            
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_2_I) definition error - "L"(default=1) value should be greater than 0')     
                            
    if not( (LP>0) ):
        exit('Exit on error: Geometry(sample_2_I) definition error - "LP"(default=1) value should be greater than 0')     

    X1 = np.array( [0, LP] )
    X2 = np.array( [0, LP] )

    Y1 = np.array( [0, 0] )
    Y2 = np.array( [0, 0] )

    Z1 = np.array( [-L/2, -L/2] )
    Z2 = np.array( [ L/2,  L/2] )

    Nph = np.array([1, 2])-1       

    X = np.array([ 0,  LP])
    Y = np.array([ -L0 , -L0 ])
    Z = np.array([ 0 , 0 ])

    NF = np.array([[1,0], [0,1]])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z)

def sample_X(X0, Y0, Z0, L1 = 1, L2 = 1 ):    
           
    X1 = np.array( [ 0  , X0 ]  )
    X2 = np.array( [ 0  , X0 ]  )

    Y1 = np.array( [ 0,  Y0  ] )
    Y2 = np.array( [ L1, Y0 ] )

    Z1 = np.array( [ Z0, 0 ] )
    Z2 = np.array( [ Z0, L2 ])

    Nph = np.array([1, 2])-1   

    X = np.array([])
    Y = np.array([])
    Z = np.array([])

    NF = np.array([ [1,0] , [0,1]  ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z)

def sample_L(L1 = 1, L2= 1, r=0.02):    
           
    X1 = np.array( [ 0, 0 ]  )
    X2 = np.array( [ 0, 0 ]  )

    Y1 = np.array( [ -L1, 0 ] )
    Y2 = np.array( [ 0,  0 ] )

    Z1 = np.array( [ 0, 0 ] )
    Z2 = np.array( [ 0, L2 ])

    Nph = np.array([1, 2])-1   

    X = np.array([])
    Y = np.array([])
    Z = np.array([])

    NF = np.array([ [1,0] , [0,1]  ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z, r=0.02)

def sample_L_inf(L1 = 1, L2= 1, INF = 10):    
    
    if not( (L1>0) ):
        exit('Exit on error: Geometry(sample_1_L) definition error - "L"(default=1) value should be greater than 0')  
    if not( (L2>0) ):
        exit('Exit on error: Geometry(sample_1_L) definition error - "L"(default=1) value should be greater than 0')     
                            
    if not( (INF>max(L1,L2)) ):
        exit('Exit on error: Geometry(sample_1_L) definition error - "INF"(default=10) value should be greater than "L"')     
    
    X1 = np.array( [ 0, 0, 0, 0]  )
    X2 = np.array( [ 0, 0, 0, 0]  )

    Y1 = np.array( [-INF, -L1, 0, 0] )
    Y2 = np.array( [0,   0,  0, 0 ] )

    Z1 = np.array( [0,  0, 0 , 0] )
    Z2 = np.array( [0, 0, L2 , INF])

    Nph = np.array([1, 1, 2, 2])-1   

    X = np.array([])
    Y = np.array([])
    Z = np.array([])

    NF = np.array([ [0, 1, 0, 0 ] , [0, 0, 1, 0]  ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z)

def sample_L_inf_2(L = 1, sect=1/8, INF = 10):
    
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_1_L_var2) definition error - "L"(default=1) value should be greater than 0')     
                            
    if not( (INF>L) ):
        exit('Exit on error: Geometry(sample_1_L_var2) definition error - "INF"(default=10) value should be greater than "L"')     
    
    if not( (sect<1) & (sect>0) ):
        exit('Exit on error: Geometry(sample_1_L_var2) definition error - "sect"(default=1/8) value should be less than 1 and greater than 0')     
    

    X1 = np.array( [ 0, 0, 0, 0, 0, 0]  )
    X2 = X1

    Y1 = np.array( [0, 0, 0, 0, L*sect, L] )
    Y2 = np.array( [0, 0, 0, L*sect, L, INF] )

    Z1 = np.array( [INF,  L, L*sect, 0, 0, 0])
    Z2 = np.array( [L, L*sect, 0, 0, 0, 0  ])

    Nph = np.array([1, 1, 1, 1, 1, 1])-1   

    X = np.array([])
    Y = np.array([])
    Z = np.array([])

    NF = np.array([ [0, 1, 0, 0, 0, 0 ] ,
                    [0, 0, 1, 0, 0, 0 ] , 
                    [0, 0, 0, 1, 0, 0 ] , 
                    [0, 0, 0, 0, 1, 0 ]  ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z)

def sample_1_O(L = 1, A = 1, B = 10):
    
    X1 = np.array( [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  )
    X2 = X1

    Y1 = np.array( [-A/2, -A/2, -A/2 , -A/2+L, A/2-L, A/2, A/2, A/2, A/2, A/2, A/2-L, -A/2+L, -A/2, -A/2] )
    Y2 = np.array( [-A/2, -A/2 , -A/2+L, A/2-L, A/2, A/2, A/2, A/2, A/2, A/2-L, -A/2+L, -A/2, -A/2, -A/2] )

    Z1 = np.array( [0, -A/2+L, -A/2, -A/2, -A/2, -A/2, -A/2 + L, 0, A/2 - L, A/2, A/2, A/2, A/2, A/2 -L])
    Z2 = np.array( [-A/2+L, -A/2, -A/2, -A/2, -A/2, -A/2 + L, 0, A/2 - L, A/2, A/2, A/2, A/2, A/2 -L, 0])

    Nph = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])-1   

    X = np.array([])
    Y = np.array([])
    Z = np.array([])

    NF = np.array([ [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ] ,
                    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ] , 
                    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ] ,
                    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ] ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z)
 
def sample_3_C(L = 1, L3 = 1, LP = 1, L0 = 1, INF = 1e1):
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "L"(default=1) value should be greater than 0')     
                           
    if not( (L3>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "L3"(default=1) value should be greater than 0')     
                            
    if not( (LP>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "LP"(default=1) value should be greater than 0')     
            
    if not( (INF>L) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "INF"(default=10) value should be greater than "L"')     

    seg = 5;                

    X1 = np.array( [-LP]*seg + [0]*seg + [+LP]*seg )
    X2 = X1

    Y1 = [ L3, L3, L3, 0, 0 ]
    Y1 = np.array(Y1 + Y1 + Y1)
    Y2 = [ L3, L3 , 0, 0, 0 ]
    Y2 = np.array(Y2 + Y2 + Y2)

    Z1 = [ +INF, L,  0, 0, L ]
    Z1 = np.array(Z1 + Z1 + Z1)
    Z2 = [ L,   0, 0, L, +INF ]
    Z2 = np.array(Z2 + Z2 + Z2)

    Nph = np.array([1]*seg + [2]*seg + [3]*seg)-1   

    X = np.array([-LP,  0, +LP])
    Y = np.array([-L0, -L0, -L0])
    Z = np.array([ 0,  0,  0])

    top = [0, 1, 0, 0, 0]
    pol = [0, 0, 1, 0, 0]
    bot = [0, 0, 0, 1, 0]
    NF = np.array([( top + [0]*seg*2 ) , ( pol + [0]*seg*2 ) ,( bot + [0]*seg*2 ) ,
                   ( [0]*seg + top + [0]*seg ) ,  ( [0]*seg + pol + [0]*seg ) , ( [0]*seg + bot + [0]*seg ) ,
                   ( [0]*seg*2 + top ), ( [0]*seg*2 + pol ), ( [0]*seg*2 + bot ),   ])
    
    top = [0, 1, 1, 1, 0]
    pol = [0, 1, 1, 1, 0]
    bot = [0, 1, 1, 1, 0]
    
    NL = np.array([( top + [0]*seg*2 ) , ( pol + [0]*seg*2 ) ,( bot + [0]*seg*2 ) ,
                   ( [0]*seg + top + [0]*seg ) ,  ( [0]*seg + pol + [0]*seg ) , ( [0]*seg + bot + [0]*seg ) ,
                   ( [0]*seg*2 + top ), ( [0]*seg*2 + pol ), ( [0]*seg*2 + bot ),   ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z, NL)

def sample_3_O(L = 1, L3 = 1, LP = 1, L0 = 1, r=0.02):
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "L"(default=1) value should be greater than 0')     
                           
    if not( (L3>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "L3"(default=1) value should be greater than 0')     
                            
    if not( (LP>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "LP"(default=1) value should be greater than 0')     
            
    seg = 4;                

    X1 = np.array( [-LP]*seg + [0]*seg + [+LP]*seg )
    X2 = X1

    Y1 = [ 0, L3, L3, 0]
    Y1 = np.array(Y1 + Y1 + Y1)
    Y2 = [ L3, L3 , 0, 0]
    Y2 = np.array(Y2 + Y2 + Y2)

    Z1 = [ L,  L, 0, 0 ]
    Z1 = np.array(Z1 + Z1 + Z1)
    Z2 = [ L,   0, 0, L ]
    Z2 = np.array(Z2 + Z2 + Z2)

    Nph = np.array([1]*seg + [2]*seg + [3]*seg)-1   

    X = np.array([-LP,  0, +LP])
    Y = np.array([-L0, -L0, -L0])
    Z = np.array([ 0,  0,  0])

    top = [0, 1, 0, 0]
    pol = [0, 0, 1, 0]
    bot = [0, 0, 0, 1]
    NF = np.array([( top + [0]*seg*2 ) , ( pol + [0]*seg*2 ) ,( bot + [0]*seg*2 ) ,
                   ( [0]*seg + top + [0]*seg ) ,  ( [0]*seg + pol + [0]*seg ) , ( [0]*seg + bot + [0]*seg ) ,
                   ( [0]*seg*2 + top ), ( [0]*seg*2 + pol ), ( [0]*seg*2 + bot ),   ])
    
    top = [1, 1, 1, 1]
    pol = [1, 1, 1, 1]
    bot = [1, 1, 1, 1]
    
    NL = np.array([( [1]*seg + [0]*seg*2 ) ,
                   ( [0]*seg + [1]*seg + [0]*seg ) ,
                   ( [0]*seg*2 + [1]*seg ) ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z, NL, r)

def sample_3_I(L = 1, LP = 1, L0 = 1, INF = 1e1, r=0.02):
    
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_3_I) definition error - "L"(default=1) value should be greater than 0')     
                            
    if not( (LP>0) ):
        exit('Exit on error: Geometry(sample_3_I) definition error - "LP"(default=1) value should be greater than 0')     
            
    if not( (INF>L) ):
        exit('Exit on error: Geometry(sample_3_I) definition error - "INF"(default=10) value should be greater than "L"')     
        
    seg = 3;                

    X1 = np.array( [-LP]*seg + [0]*seg + [+LP]*seg )
    X2 = X1

    Y1 = [ 0, 0, 0 ]
    Y1 = np.array(Y1 + Y1 + Y1)
    Y2 = [ 0, 0, 0 ]
    Y2 = np.array(Y2 + Y2 + Y2)

    Z1 = [ +INF, L/2,  -L/2 ]
    Z1 = np.array(Z1 + Z1 + Z1)
    Z2 = [ L/2,  -L/2, -INF ]
    Z2 = np.array(Z2 + Z2 + Z2)

    Nph = np.array([1]*seg + [2]*seg + [3]*seg)-1   

    X = np.array([-LP,  0, +LP])
    Y = np.array([-L0, -L0, -L0])
    Z = np.array([ 0,  0,  0])

    pol = [0, 1, 0]
    NF = np.array([(             pol + [0]*seg*2 ) ,
                   ( [0]*seg   + pol + [0]*seg ) ,
                   ( [0]*seg*2 + pol ) ])
    
    NL = np.array([(             pol + [0]*seg*2 ) ,
                   ( [0]*seg   + pol + [0]*seg ) ,
                   ( [0]*seg*2 + pol ) ])
    
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z, NL, r)


def sample_mono1(L = 1, D = 0.1, H = 0.3, LP = 0.150, L0 = 0.15, r=0.02):
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "L"(default=1) value should be greater than 0')     
                  
    if not( (LP>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "LP"(default=1) value should be greater than 0')     
    
    Y0 = [ 0,    0,   0,  H, L]
    Z0 = [ L,    H,   0,  0, 0] 
    Yac = [ D,    D,   D,  H, L]
    Zac = [ L,    H,   -D,  -D, -D] 
    seg = len(Y0)-1   
    polseg = [0, 1, 1, 0]
    
    Sseg = slice(None, -1, +1)
    Eseg = slice(+1, None, +1)
    Ssegr = slice(-1, 0, -1)
    Esegr = slice(-2, None, -1)
                
    X1  = np.array( [2*LP]*seg + [LP]*seg  + [0]*seg )
    X2  = np.array( [2*LP]*seg + [LP]*seg  + [0]*seg )
    Y1  = np.array( Yac[Sseg]   + Y0[Sseg] + Yac[Sseg] )
    Y2  = np.array( Yac[Eseg]   + Y0[Eseg] + Yac[Eseg] )
    Z1  = np.array( Zac[Sseg]   + Z0[Sseg] + Zac[Sseg] )
    Z2  = np.array( Zac[Eseg]   + Z0[Eseg] + Zac[Eseg] )
    Nph= np.array( [ 1]*seg   + [ 2]*seg  + [3]*seg ) 
    Nph = Nph-1

    X = np.array([2*LP, +LP, 0])
    Y = np.array([-L0-0.03, -L0-0.03, -L0-0.03])
    Z = np.array([ -D, -0, -D])

    NF = np.array([( polseg  + [0]*seg + [0]*seg  ) ,
                   ( [0]*seg  + polseg + [0]*seg  ) ,
                   ( [0]*seg  + [0]*seg + polseg  ) ,])
    
    NL = np.stack( (Nph==0, Nph==1, Nph==2))
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z, NL, r)


def sample_mono3(L = 1, L2 = 0.3, D = 0.1, H = 0.3, LP = 0.150, L0 = 0.15, r=0.02):
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "L"(default=1) value should be greater than 0')     
                  
    if not( (LP>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "LP"(default=1) value should be greater than 0')     
    
    Y0 = [ L,    0,   0,  H,  H, L]
    Z0 = [ L2,   L2,  0,  0, -D, -D] 
    Ya = Y0
    Za = [ L2-D,   L2-D,  -D,  -D, -2*D, -2*D] 
    Yc = Y0
    Zc = [ L2+D,   L2+D,  -D,  -D, -2*D, -2*D] 
    seg = len(Y0)-1   
    polseg = [0, 1, 1, 1, 0]
    
    Sseg = slice(None, -1, +1)
    Eseg = slice(+1, None, +1)
    Ssegr = slice(-1, 0, -1)
    Esegr = slice(-2, None, -1)
                
    X1  = np.array( [2*LP]*seg + [LP]*seg  + [0]*seg )
    X2  = np.array( [2*LP]*seg + [LP]*seg  + [0]*seg )
    Y1  = np.array( Ya[Sseg]   + Y0[Sseg] + Yc[Sseg] )
    Y2  = np.array( Ya[Eseg]   + Y0[Eseg] + Yc[Eseg] )
    Z1  = np.array( Za[Sseg]   + Z0[Sseg] + Zc[Sseg] )
    Z2  = np.array( Za[Eseg]   + Z0[Eseg] + Zc[Eseg] )
    Nph= np.array( [ 1]*seg   + [ 2]*seg  + [3]*seg ) 
    Nph = Nph-1

    X = np.array([2*LP, +LP, 0])
    Y = np.array([-L0-0.03, -L0-0.03, -L0-0.03])
    Z = np.array([ -D, -0, -D])

    NF = np.array([( polseg  + [0]*seg + [0]*seg  ) ,
                   ( [0]*seg  + polseg + [0]*seg  ) ,
                   ( [0]*seg  + [0]*seg + polseg  ) ,])
    
    NL = np.stack( (Nph==0, Nph==1, Nph==2))
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z, NL, r)

def sample_shell(L = 0.9, L1 = 0.7, L2 = 0.2, L3 = 0.3, L4 = 0.1, L5 = 0.3, L6  = 0.4, LZ = 1.3, LY = 1, LP = 0.210, L0 = 0.12, r=0.02):
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "L"(default=1) value should be greater than 0')     
                  
    if not( (LP>0) ):
        exit('Exit on error: Geometry(sample_3_C) definition error - "LP"(default=1) value should be greater than 0')     
    
    H = L5 + L6
    if (L2+L5<L1/2):  
        Y0 = [ 0,    0,                 0,  L5,  L5,     L5, L5+L3, L5+L3, H, H, H]
        Z0 = [ L+L2, L2+(L1/2-L2-L5),   L2, L2,   0,    -L4,   -L4,     0, 0, L1/2, L] 
        seg = len(Y0)-1   
        polseg = [1]*seg; polseg[0]=0; polseg[-1]=0  
    elif (L2+L5==L1/2):        
        Y0 = [ 0,    0,  L5,  L5,     L5, L5+L3, L5+L3, H, H, H]
        Z0 = [ L+L2,  L2, L2,   0,    -L4,   -L4,     0, 0, L1/2, L] 
        seg = len(Y0)-1   
        polseg = [1]*seg; polseg[0]=0; polseg[-1]=0  
    elif ((L2+L5>L1/2) and (L2<L1/2)):        
        Y0 = [ 0,     0,  L5-(L1/2-L2)  ,  L5,  L5,     L5, L5+L3, L5+L3, H, H, H]
        Z0 = [ L+L2,  L2, L2,               L2,   0,    -L4,   -L4,     0, 0, L1/2, L] 
        seg = len(Y0)-1   
        polseg = [1]*seg; polseg[0]=0; polseg[1]=0; polseg[-1]=0  
    elif ((L2==L1/2)):        
        Y0 = [ 0,     0,    L5,  L5,     L5, L5+L3, L5+L3, H, H, H]
        Z0 = [ L+L2,  L2,  L2,   0,    -L4,   -L4,     0, 0, L1/2, L] 
        seg = len(Y0)-1   
        polseg = [1]*seg; polseg[0]=0; polseg[1]=0; polseg[-1]=0  
    elif (L1/2<L2):
        Y0 = [ 0,     0,    L5,  L5, L5,     L5, L5+L3, L5+L3, H, H, H]
        Z0 = [ L+L2,  L2,  L2,   L1/2, 0,    -L4,   -L4,     0, 0, L1/2, L] 
        seg = len(Y0)-1   
        polseg = [1]*seg; polseg[0]=0; polseg[1]=0; polseg[2]=0; polseg[-1]=0  
    Sseg = slice(None, -1, +1)
    Eseg = slice(+1, None, +1)
    Ssegr = slice(-1, 0, -1)
    Esegr = slice(-2, None, -1)
            
    
    X1  = np.array( [2*LP]*seg + [LP]*seg  + [0]*seg )
    X2  = np.array( [2*LP]*seg + [LP]*seg  + [0]*seg )
    Y1  = np.array( Y0[Sseg]   + Y0[Sseg] + Y0[Sseg] )
    Y2  = np.array( Y0[Eseg]   + Y0[Eseg] + Y0[Eseg] )
    Z1  = np.array( Z0[Sseg]   + Z0[Sseg] + Z0[Sseg] )
    Z2  = np.array( Z0[Eseg]   + Z0[Eseg] + Z0[Eseg] )
    Nph= np.array( [ 1]*seg   + [ 2]*seg  + [3]*seg ) 
    Nph = Nph-1

    X = np.array([2*LP, +LP, 0])
    Y = np.array([L5-L0-0.03, L5-L0-0.03, L5-L0-0.03])
    Z = np.array([ -L4, -L4, -L4])

    NF = np.array([( polseg  + [0]*seg + [0]*seg  ) ,
                   ( [0]*seg  + polseg + [0]*seg  ) ,
                   ( [0]*seg  + [0]*seg + polseg  ) ,])
    
    NL = np.stack( (Nph==0, Nph==1, Nph==2))
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z, NL, r)

def sample_shell_rlcABC(L = 0.9, L1 = 0.7, L2 = 0.2, L3 = 0.3, L4 = 0.1, L5 = 0.3, L6  = 0.4, LZ = 1.3, LY = 1, LP = 0.210, L0 = 0.12, r=0.02):

    shell = sample_shell(L, L1, L2 , L3, L4, L5 , L6 , LZ, LY, LP, L0, r)

    H = L5 + L6
    #      inlet            outlet              inter
    Na  = [ 1]   + [ 1]   + [ 1]   + [ 1]   + [ 1]   + [ 2]    + [ 3] 
    Xa1 = [ 0]   + [2*LP] + [ 0]   + [ 0]   + [2*LP] + [ 0]    + [0 ] 
    Xa2 = [2*LP] + [2*LP] + [ 0]   + [ 0]   + [  LP] + [LP]    + [LP] 
    Ya1 = [ 0]   + [ 0]   + [ 0]   + [LY]   + [   H] + [ 0]    + [ H] 
    Ya2 = [ 0]   + [ 0]   + [LY]   + [LY]   + [   H] + [ 0]    + [ H] 
    Za1 = [LZ]   + [LZ]   + [L+L2] + [L+L2] + [   L] + [ L+L2] + [ L] 
    Za2 = [LZ]   + [L+L2] + [L+L2] + [LZ]   + [   L] + [ L+L2] + [ L]
    segA = len(Na)
        
    shell.XS = np.append( shell.XS , np.array(Xa1) )
    shell.XE = np.append( shell.XE , np.array(Xa2) )
    shell.YS = np.append( shell.YS , np.array(Ya1) )
    shell.YE = np.append( shell.YE , np.array(Ya2) )
    shell.ZS = np.append( shell.ZS , np.array(Za1) )
    shell.ZE = np.append( shell.ZE , np.array(Za2) )
    shell.Nph= np.append( shell.Nph , np.array(Na)-1 )

    shell.NF = np.stack( ( 
                          np.append( shell.NF[0,:], np.array([0]*segA) ), 
                          np.append( shell.NF[1,:], np.array([0]*segA) ), 
                          np.append( shell.NF[2,:], np.array([0]*segA)) ) )
    
    shell.NL = np.stack( (shell.Nph==0, shell.Nph==1, shell.Nph==2))
    
    return shell

def sample_shell_rlcCBA(L = 0.9, L1 = 0.7, L2 = 0.2, L3 = 0.3, L4 = 0.1, L5 = 0.3, L6  = 0.4, LZ = 1.3, LY = 1, LP = 0.210, L0 = 0.12, r=0.02):

    shell = sample_shell(L, L1, L2 , L3, L4, L5 , L6 , LZ, LY, LP, L0, r)
        
    H = L5 + L6
        #  inlet    outlet                      inter
    Na  = [ 3]      + [3]    + [ 3]    + [ 3]    + [ 1]   + [ 2]    + [ 3] 
    Xa1 = [ 0]      + [2*LP] + [ 2*LP] + [2*LP]  + [2*LP] + [2*LP]  + [0 ] 
    Xa2 = [ 0]      + [2*LP] + [ 2*LP] + [ 0]    + [  LP] + [1*LP]  + [LP] 
    Ya1 = [ 0]      + [ 0]   + [LY]    + [LY]    + [   H] + [ 0]    + [ H] 
    Ya2 = [ 0]      + [LY]   + [LY]    + [LY]    + [   H] + [ 0]    + [ H] 
    Za1 = [LZ]      + [L+L2] + [L+L2]  + [LZ]    + [   L] + [ L+L2] + [ L] 
    Za2 = [L+L2]    + [L+L2] + [LZ]    + [LZ]    + [   L] + [ L+L2] + [ L]
    segA = len(Na)
        
    shell.XS = np.append( shell.XS , np.array(Xa1) )
    shell.XE = np.append( shell.XE , np.array(Xa2) )
    shell.YS = np.append( shell.YS , np.array(Ya1) )
    shell.YE = np.append( shell.YE , np.array(Ya2) )
    shell.ZS = np.append( shell.ZS , np.array(Za1) )
    shell.ZE = np.append( shell.ZE , np.array(Za2) )
    shell.Nph= np.append( shell.Nph , np.array(Na)-1 )

    shell.NF = np.stack( ( 
                          np.append( shell.NF[0,:], np.array([0]*segA) ), 
                          np.append( shell.NF[1,:], np.array([0]*segA) ), 
                          np.append( shell.NF[2,:], np.array([0]*segA)) ) )
    
    shell.NL = np.stack( (shell.Nph==0, shell.Nph==1, shell.Nph==2))
    
    return shell


def sample_shell_3phInf(L = 0.9, L1 = 0.7, L2 = 0.2, L3 = 0.3, L4 = 0.1, L5 = 0.3, L6  = 0.4, LZ = 1.3, LY = 1, LP = 0.210, L0 = 0.12, r=0.02):

    shell = sample_shell(L, L1, L2 , L3, L4, L5 , L6 , LZ, LY, LP, L0, r)
        
    H = L5 + L6
        #  inlet    outlet                      inter
    Na  = [ 1]   + [ 1]   + [ 2]   + [ 2]   + [3]   + [ 3] 
    Xa1 = [2*LP] + [2*LP]   + [ LP]   + [ LP]   + [ 0]    + [0 ] 
    Xa2 = [2*LP] + [2*LP]   + [ LP]   + [ LP]   + [ 0]    + [0 ] 
    Ya1 = [ 0]   + [H]      + [ 0]   + [H]      + [ 0]   + [H]   
    Ya2 = [ 0]   + [H]      + [ 0]   + [H]      + [ 0]   + [H]  
    Za1 = [LZ]   + [L]      + [LZ]   + [L]      + [LZ]   + [L]
    Za2 = [L+L2] + [LZ]     + [L+L2] + [LZ]     + [L+L2] + [LZ]   
    segA = len(Na)
        
    shell.XS = np.append( shell.XS , np.array(Xa1) )
    shell.XE = np.append( shell.XE , np.array(Xa2) )
    shell.YS = np.append( shell.YS , np.array(Ya1) )
    shell.YE = np.append( shell.YE , np.array(Ya2) )
    shell.ZS = np.append( shell.ZS , np.array(Za1) )
    shell.ZE = np.append( shell.ZE , np.array(Za2) )
    shell.Nph= np.append( shell.Nph , np.array(Na)-1 )

    shell.NF = np.stack( ( 
                          np.append( shell.NF[0,:], np.array([0]*segA) ), 
                          np.append( shell.NF[1,:], np.array([0]*segA) ), 
                          np.append( shell.NF[2,:], np.array([0]*segA)) ) )
    
    shell.NL = np.stack( (shell.Nph==0, shell.Nph==1, shell.Nph==2))
    
    return shell



def sample_input(XA = [ 1,  1,  1,  1], YA = [ 0, 0, 1, 1], ZA = [ 1, 0, 0, 1], 
                 XB = [ 0,  0,  0,  0], YB = [ 0, 0, 1, 1], ZB = [ 1, 0, 0, 1], 
                 XC = [-1, -1, -1, -1], YC = [ 0, 0, 1, 1], ZC = [ 1, 0, 0, 1], 
                 NFA = [[0, 1, 0]], NFB = [[0, 1, 0]], NFC = [[0, 1, 0]], 
                 X = [ 1,  0, -1], Y = [-1, -1, -1], Z = [ 0,  0,  0]):

    if (not( (len(XA)==len(YA)) & (len(XA)==len(ZA)) ) or 
        not( (len(XB)==len(YB)) & (len(XB)==len(ZB)) ) or 
        not( (len(XC)==len(YC)) & (len(XC)==len(ZC)) ) or
        not( all( len(XA)==len(nFA)+1 for nFA in NFA) ) or
        not( all( len(XB)==len(nFB)+1 for nFB in NFB) ) or
        not( all( len(XC)==len(nFC)+1 for nFC in NFC) ) or
        not( ( len(X)==len(Y) ) & ( len(X)==len(Z) )  ) 
        ):
        raise ('Exit on error: Geometry definition error - Input vectors dimensions must agree')     
    
    segA = len(XA)-1   
    segB = len(XB)-1   
    segC = len(XC)-1   
    
    Sseg = slice(None, -1, +1)
    Eseg = slice(+1, None, +1)
    Ssegr = slice(-1, 0, -1)
    Esegr = slice(-2, None, -1)
                
    X1  = np.array( XA[Sseg] + XB[Sseg] + XC[Sseg] )
    X2  = np.array( XA[Eseg] + XB[Eseg] + XC[Eseg] )
    Y1  = np.array( YA[Sseg] + YB[Sseg] + YC[Sseg] )
    Y2  = np.array( YA[Eseg] + YB[Eseg] + YC[Eseg] )
    Z1  = np.array( ZA[Sseg] + ZB[Sseg] + ZC[Sseg] )
    Z2  = np.array( ZA[Eseg] + ZB[Eseg] + ZC[Eseg] )
    Nph= np.array( [ 1]*segA   + [ 2]*segB  + [3]*segC ) 
    Nph = Nph-1

    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)
    
    if len(NFA)>0:
        NF = np.concatenate([  NFA, [[0]*(segB+segC)]*len(NFA) if segB+segC>0 else [[]] ], 1) 
        
    if len(NFB)>0:        
        if len(NFA)>0:
            NF = np.concatenate([ NF, np.concatenate([[[0]*(segA)     ]*len(NFB),   NFB, [[0]*(segC)]*len(NFB) if segC>0 else [[]]     ], 1) ],0)
        else:
            NF = np.concatenate([[[0]*(segA)     ]*len(NFB),   NFB, [[0]*(segC)]*len(NFB) if segC>0 else [[]]     ], 1) 
      
    if len(NFC)>0: 
        if len(NFA)>0 or len(NFB)>0 :
            NF = np.concatenate([ NF, np.concatenate([[[0]*(segA+segB)]*len(NFC),   NFC  ], 1) ],0)
        else:
            NF = np.concatenate([[[0]*(segA+segB)]*len(NFC),   NFC  ], 1)
            
    NL = np.stack( (Nph==0, Nph==1, Nph==2))
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, Nph, NF, X, Y, Z, NL)