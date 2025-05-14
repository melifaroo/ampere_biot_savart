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
    NC: int
    NF: int
    X: float
    Y: float
    Z: float
    T: float
    I: float
    r: float = 0.1  # Default value
     
    @classmethod   
    def contour(Y0, Z0, out, Y, Z, N, LP=1, r=0.1, closed=False, INF=10):
        if not( (Y0.shape==Z0.shape) & 
                (Y.shape==Z.shape) ):
            exit('Exit on error: Geometry definition error - Input vectors dimensions must agree')     
        
        S = (Y0.shape[0]-1)
        nc = np.arange(1, N+1)
        
        [YS, _] = np.meshgrid( Y0[1:-2], nc )
        YS = YS.reshape(1, N*S)
        
        [YE, _] = np.meshgrid( Y0[2:-1], nc )
        YE = YE.reshape(1, N*S)
        
        [ZS, _] = np.meshgrid( Z0[1:-2], nc )
        ZS = ZS.reshape(1, N*S)
        
        [ZE, _] = np.meshgrid( Z0[2:-1], nc )
        ZE = ZE.reshape(1, N*S)
        
        [_, XS] = np.meshgrid( Z0[1:-2], (nc-1)*LP )
        XS = XS.reshape(1, N*S)
        
        [_, XE] = np.meshgrid( Z0[2:-1], (nc-1)*LP )
        XE = XE.reshape(1, N*S)
                
        [_, NC] = np.meshgrid( Z0[2:-1], nc-1 )
        
        NF = np.zeros((S, S))
        np.fill_diagonal(NF, 1)
              
        M = Z.shape[0]  
        
        [Z, _] = np.meshgrid( Z, nc )
        Z = Z.reshape(1, N*M)
        
        [Y, _] = np.meshgrid( Y, nc )
        Y = Y.reshape(1, N*M)
        
        [_, X] = np.meshgrid( np.arange(1, M+1), (nc-1)*LP )
        X = X.reshape(1, N*M)
                
        return Geometry(XS, XE, YS, YE, ZS, ZE, NC, NF, X, Y, Z, r)
        
    def __init__(self, XS, XE, YS, YE, ZS, ZE, NC, NF, X, Y, Z, r=0.1):
        if not( (XS.shape==XE.shape) & 
                (YS.shape==YE.shape) & 
                (ZS.shape==ZE.shape) &
                (XS.shape==YS.shape) & 
                (XS.shape==ZS.shape) & 
                (XS.shape==NC.shape) &
                (X.shape==Y.shape) & 
                (X.shape==Z.shape) ):
            exit('Exit on error: Geometry definition error - Input vectors dimensions must agree')     
        self.XS = XS #X coordinates of circuit segments start points
        self.XE = XE #X coordinates of circuit segments end points
        self.YS = YS #Y coordinates of circuit segments start points
        self.YE = YE #Y coordinates of circuit segments end points
        self.ZS = ZS #Z coordinates of circuit segments start points
        self.ZE = ZE #Z coordinates of circuit segments end points
        self.NC = NC #index of current branch for segments
        self.NF = NF #mask of segments for force output summation
        self.X = X #X coordinates of field output points
        self.Y = Y #Y coordinates of field output points
        self.Z = Z #Z coordinates of field output points
        self.r = r #default radius of conductor using for corner approximation
        
    
def sample_2_I(L = 1, LP = 1, INF = 1e3):
            
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

    Z1 = [ +INF, L/2, -L/2 ]
    Z1 = np.array(Z1 + Z1 )
    Z2 = [ L/2, -L/2, -INF ]
    Z2 = np.array(Z2 + Z2 )

    NC = np.array([1]*seg + [2]*seg)-1   

    X = np.array([ ])
    Y = np.array([ ])
    Z = np.array([ ])

    out = [0, 1, 0]
    NF = np.array([( out + [0]*seg ) , ( [0]*seg + out )   ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, NC, NF, X, Y, Z)

def sample_1_L(L = 1, INF = 10):    
    
    if not( (L>0) ):
        exit('Exit on error: Geometry(sample_1_L) definition error - "L"(default=1) value should be greater than 0')     
                            
    if not( (INF>L) ):
        exit('Exit on error: Geometry(sample_1_L) definition error - "INF"(default=10) value should be greater than "L"')     
    
    X1 = np.array( [ 0, 0, 0, 0]  )
    X2 = X1

    Y1 = np.array( [0, 0, 0, L] )
    Y2 = np.array( [0, 0, L, INF] )

    Z1 = np.array( [INF,  L, 0, 0])
    Z2 = np.array( [L, 0, 0, 0  ])

    NC = np.array([1, 1, 1, 1])-1   

    X = np.array([])
    Y = np.array([])
    Z = np.array([])

    NF = np.array([ [0, 1, 0, 0 ] , [0, 0, 1, 0]  ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, NC, NF, X, Y, Z)

def sample_1_L_var2(L = 1, sect=1/8, INF = 10):
    
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

    NC = np.array([1, 1, 1, 1, 1, 1])-1   

    X = np.array([])
    Y = np.array([])
    Z = np.array([])

    NF = np.array([ [0, 1, 0, 0, 0, 0 ] ,
                    [0, 0, 1, 0, 0, 0 ] , 
                    [0, 0, 0, 1, 0, 0 ] , 
                    [0, 0, 0, 0, 1, 0 ]  ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, NC, NF, X, Y, Z)

def sample_1_O(L = 1, A = 1, B = 10):
    
    X1 = np.array( [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  )
    X2 = X1

    Y1 = np.array( [-A/2, -A/2, -A/2 , -A/2+L, A/2-L, A/2, A/2, A/2, A/2, A/2, A/2-L, -A/2+L, -A/2, -A/2] )
    Y2 = np.array( [-A/2, -A/2 , -A/2+L, A/2-L, A/2, A/2, A/2, A/2, A/2, A/2-L, -A/2+L, -A/2, -A/2, -A/2] )

    Z1 = np.array( [0, -A/2+L, -A/2, -A/2, -A/2, -A/2, -A/2 + L, 0, A/2 - L, A/2, A/2, A/2, A/2, A/2 -L])
    Z2 = np.array( [-A/2+L, -A/2, -A/2, -A/2, -A/2, -A/2 + L, 0, A/2 - L, A/2, A/2, A/2, A/2, A/2 -L, 0])

    NC = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])-1   

    X = np.array([])
    Y = np.array([])
    Z = np.array([])

    NF = np.array([ [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ] ,
                    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ] , 
                    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ] ,
                    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ] ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, NC, NF, X, Y, Z)

def sample_3_C():
    INF = 1e6
    LP = 0.150
    L0 = 0.2
    L3 = 0.31
    L = 0.2
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

    NC = np.array([1]*seg + [2]*seg + [3]*seg)-1   

    X = np.array([-LP,  0, +LP])
    Y = np.array([-L0, -L0, -L0])
    Z = np.array([ 0,  0,  0])

    top = [0, 1, 0, 0, 0]
    pol = [0, 0, 1, 0, 0]
    bot = [0, 0, 0, 1, 0]
    NF = np.array([( top + [0]*seg*2 ) , ( [0]*seg + top + [0]*seg ) ,  ( [0]*seg*2 + top ),
                ( pol + [0]*seg*2 ) , ( [0]*seg + pol + [0]*seg ) ,  ( [0]*seg*2 + pol ), 
                ( bot + [0]*seg*2 ) , ( [0]*seg + bot + [0]*seg ) ,  ( [0]*seg*2 + bot ),   ])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, NC, NF, X, Y, Z)