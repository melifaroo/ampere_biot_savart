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
    R: float
        
    def __init__(self, XS, XE, YS, YE, ZS, ZE, R, Nph, NF, X, Y, Z, NL=np.array([])):
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
        self.R = R #default radius of conductor using for corner approximation
        
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
    
    R = [r] * seg*3
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, R, Nph, NF, X, Y, Z, NL, r)


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
    
    R = [r] * seg*3
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, R, Nph, NF, X, Y, Z, NL, r)

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
    
    R = [r] * seg*3
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, R, Nph, NF, X, Y, Z, NL, r)

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
    shell.R= np.append( shell.R , [r]*segA )
    

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
    shell.R= np.append( shell.R , [r]*segA )

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
    shell.R= np.append( shell.R , [r]*segA )

    shell.NF = np.stack( ( 
                          np.append( shell.NF[0,:], np.array([0]*segA) ), 
                          np.append( shell.NF[1,:], np.array([0]*segA) ), 
                          np.append( shell.NF[2,:], np.array([0]*segA)) ) )
    
    shell.NL = np.stack( (shell.Nph==0, shell.Nph==1, shell.Nph==2))
    
    return shell



def sample_input(XA = [ 1,  1,  1,  1], YA = [ 0, 0, 1, 1], ZA = [ 1, 0, 0, 1], 
                 XB = [ 0,  0,  0,  0], YB = [ 0, 0, 1, 1], ZB = [ 1, 0, 0, 1], 
                 XC = [-1, -1, -1, -1], YC = [ 0, 0, 1, 1], ZC = [ 1, 0, 0, 1], 
                 R = [0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02], 
                 NF = [[0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0]],
                 X = [ 1,  0, -1], Y = [-1, -1, -1], Z = [ 0,  0,  0]):

    if (not(    (len(XA)==len(YA)) & (len(XA)==len(ZA)) ) or 
        not(    (len(XB)==len(YB)) & (len(XB)==len(ZB)) ) or 
        not(    (len(XC)==len(YC)) & (len(XC)==len(ZC)) ) or
        not( all(len(XA)-1+len(XB)-1+len(XC)-1==len(NF1) for NF1 in NF) ) or
        not(    (len(XA)-1+len(XB)-1+len(XC)-1==len(R) ) ) or
        not( ( len(X)==len(Y) ) & ( len(X)==len(Z) )  ) 
        ):
        raise Exception('Exit on error: Geometry definition error - Input vectors dimensions must agree')     
    
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
    Nph = np.array( [1]*segA + [2]*segB + [3]*segC ) - 1
    R   = np.array( R )
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)    
    NF = np.array(NF)  
    NL = np.stack( (Nph==0, Nph==1, Nph==2) )
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, R, Nph, NF, X, Y, Z, NL)