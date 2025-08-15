import numpy as np
import mpmath
from numpy import log, arctan2, fill_diagonal
from logic.geometry import Geometry
from logic.excitation import Excitation
from dataclasses import dataclass

@dataclass
class Inductances:
    def __init__(self, L = np.array([])):
        self.L = L
        
@dataclass
class Forces:
    def __init__(self, Fx = np.array([]), Fy = np.array([]), Fz = np.array([]), N = np.array([])):
        self.Fx = Fx
        self.Fy = Fy
        self.Fz = Fz
        self.N = N
        
@dataclass
class Fields:
    def __init__(self, Bx = np.array([]), By = np.array([]), Bz = np.array([])):
        self.Bx = Bx
        self.By = By
        self.By = Bz
        self.Bax = By
        self.Btr = (Bx**2 + Bz**2)**0.5
        self.Bmag = (self.Bax**2 + self.Btr**2)**0.5
        
@dataclass
class Results:
    phases : int
    forces : Forces
    fields : Fields    
    times  : float
    inductances : Inductances    
    def __init__(self, times : float, fields = Fields(), forces = Forces(), inductances = Inductances()):
        self.times = times
        self.fields = fields
        self.forces = forces
        self.inductances = inductances
        
def solve(geometry : Geometry, excitation : Excitation):
       
    results = Results(
        excitation.T,
        biotsavart3d(geometry, excitation),
        ampere3d(geometry, excitation)
        )
        
    return results
            
def evalBranchCurrents(geometry: Geometry, excitation : Excitation , peakPhaseNumber = 0, asymK_override = None):
    
    N = geometry.getCircuitPhaseCount()
    
    
    if (N<3):         
        excitation.K = np.array([1, -1])[:N,np.newaxis]
    else:
        excitation.K = np.array([1, -0.5, -0.5])[:N,np.newaxis]   
        excitation.K = np.roll(excitation.K, peakPhaseNumber, axis=0) 
    
    inductances = neumann3d(geometry, excitation)         
     
    if (N==3):      
        i = np.delete(np.arange(3),np.where(excitation.K[:,0] == 1))
        j = i[::-1]
        
        if asymK_override==None:
            excitation.K[i,0] = np.sign(excitation.K[i,0])/(1 + inductances.L[i]/inductances.L[j])
        else:
            excitation.K[i[0],0] = -(1 + asymK_override)/2
            excitation.K[i[1],0] = -(1 - asymK_override)/2
        
        excitation.asymK = ( - inductances.L[i[0]] + inductances.L[j[0]])/(inductances.L[i[0]] + inductances.L[j[0]])
        
    if (excitation.current.ndim == 1):
        excitation.I = np.repeat(excitation.current[np.newaxis,:], repeats=N, axis=0) 
        excitation.I = np.multiply(excitation.I, excitation.K) 
        excitation.U = np.repeat(excitation.voltage[np.newaxis,:], repeats=N, axis=0) 
    elif (N<3):         
        excitation.I = np.repeat(excitation.current[0,:][np.newaxis,:], repeats=N, axis=0)
        excitation.I = np.multiply(excitation.I, excitation.K) 
        excitation.U = np.repeat(excitation.voltage[0,:][np.newaxis,:], repeats=N, axis=0)
    else:
        excitation.I = np.roll(excitation.current, 0, axis=0)
        excitation.U = np.roll(excitation.voltage, 0, axis=0)
        
    return inductances
 
def fun(y,a,c):
    return mpmath.ellippi(1-c**2/a**2, arctan2(y, c), 0) 
        
def biotsavart3d(geometry : Geometry, excitation : Excitation):
    [Bx, By, Bz] = _biotsavart3d(
        excitation.T, 
        excitation.I, 
        geometry.XS, 
        geometry.XE, 
        geometry.YS, 
        geometry.YE, 
        geometry.ZS,
        geometry.ZE, 
        geometry.Nph,
        geometry.X,
        geometry.Y,
        geometry.Z)
    return Fields(Bx, By, Bz)       
      
def _biotsavart3d(T, I, XS, XE, YS, YE, ZS, ZE, N3ph, X, Y, Z):
    if not( (XS.shape==XE.shape) & (YS.shape==YE.shape) & (ZS.shape==ZE.shape) &
            (XS.shape==YS.shape) & (XS.shape==ZS.shape) & (XS.shape==N3ph.shape) &
            (X.shape==Y.shape) & (X.shape==Z.shape) ):
        exit('Exit on error: biotsavart3d - Input vectors dimensions must agree')     
    
    [x, _, x1] = np.meshgrid(X, T, XS, indexing='ij')
    [x, _, x2] = np.meshgrid(X, T, XE, indexing='ij')
    [y, _, y1] = np.meshgrid(Y, T, YS, indexing='ij')
    [y, _, y2] = np.meshgrid(Y, T, YE, indexing='ij')
    [z, _, z1] = np.meshgrid(Z, T, ZS, indexing='ij')
    [z, _, z2] = np.meshgrid(Z, T, ZE, indexing='ij')
    [_, nt, nc] = np.meshgrid(X, np.linspace(1, T.shape[0], T.shape[0])-1, N3ph, indexing='ij')
      
    i = I[nc.astype(int), nt.astype(int)]
    
    # Bx = 1e-7*i*(0
    #         + (x1==x2)*(y1==y2)*(z1!=z2)*( y-y1 )/( (x-x1)**2+(y-y1)**2 )*(
    #             + (z-z2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5 
    #             - (z-z1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5
    #         )            
    #         + (x1!=x2)*(y1==y2)*(z1==z2)*( 0 )
    #         - (x1==x2)*(y1!=y2)*(z1==z2)*( z-z1 )/( (z-z1)**2+(x-x1)**2 )*(
    #             + (y-y2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5 
    #             - (y-y1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5
    #         )
    #     )
        
    # By = 1e-7*i*(0
    #         - (x1==x2)*(y1==y2)*(z1!=z2)*( x-x1 )/( (x-x1)**2+(y-y1)**2 )*(
    #             + (z-z2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5 
    #             - (z-z1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5
    #         )
    #         + (x1!=x2)*(y1==y2)*(z1==z2)*( z-z1 )/( (y-y1)**2+(z-z1)**2 )*(
    #             + (x-x2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5 
    #             - (x-x1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5
    #         )            
    #         - (x1==x2)*(y1!=y2)*(z1==z2)*( 0 )
    #     )
        
    # Bz = 1e-7*i*(0
    #         + (x1==x2)*(y1==y2)*(z1!=z2)*( 0 )
    #         - (x1!=x2)*(y1==y2)*(z1==z2)*( y-y1 )/( (y-y1)**2+(z-z1)**2 )*(
    #             + (x-x2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5 
    #             - (x-x1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5
    #         )
    #         + (x1==x2)*(y1!=y2)*(z1==z2)*( x-x1 )/( (z-z1)**2+(x-x1)**2 )*(
    #             + (y-y2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5 
    #             - (y-y1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5
    #         )     
    #     )
    
    Bx1 = +1* (x1==x2)*(y1==y2)*(z1!=z2)*( y-y1 )/( (x-x1)**2+(y-y1)**2 )*(z-z2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5; Bx1[np.isnan(Bx1)] = 0
    Bx2 = -1* (x1==x2)*(y1==y2)*(z1!=z2)*( y-y1 )/( (x-x1)**2+(y-y1)**2 )*(z-z1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5; Bx2[np.isnan(Bx2)] = 0   
    Bx3 = -1* (x1==x2)*(y1!=y2)*(z1==z2)*( z-z1 )/( (z-z1)**2+(x-x1)**2 )*(y-y2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5; Bx3[np.isnan(Bx3)] = 0
    Bx4 = +1* (x1==x2)*(y1!=y2)*(z1==z2)*( z-z1 )/( (z-z1)**2+(x-x1)**2 )*(y-y1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5; Bx4[np.isnan(Bx4)] = 0
    Bx = 1e-7*i*(Bx1 + Bx2 + Bx3 + Bx4)
        
    By1 = -1* (x1==x2)*(y1==y2)*(z1!=z2)*( x-x1 )/( (x-x1)**2+(y-y1)**2 )*(z-z2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5; By1[np.isnan(By1)] = 0
    By2 = +1* (x1==x2)*(y1==y2)*(z1!=z2)*( x-x1 )/( (x-x1)**2+(y-y1)**2 )*(z-z1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5; By2[np.isnan(By2)] = 0
    By3 = +1* (x1!=x2)*(y1==y2)*(z1==z2)*( z-z1 )/( (y-y1)**2+(z-z1)**2 )*(x-x2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5; By3[np.isnan(By3)] = 0
    By4 = -1* (x1!=x2)*(y1==y2)*(z1==z2)*( z-z1 )/( (y-y1)**2+(z-z1)**2 )*(x-x1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5; By4[np.isnan(By4)] = 0
    By = 1e-7*i*(By1 + By2 + By3 + By4)
                
    Bz1 = -1* (x1!=x2)*(y1==y2)*(z1==z2)*( y-y1 )/( (y-y1)**2+(z-z1)**2 )*(x-x2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5; Bz1[np.isnan(Bz1)] = 0
    Bz2 = +1* (x1!=x2)*(y1==y2)*(z1==z2)*( y-y1 )/( (y-y1)**2+(z-z1)**2 )*(x-x1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5; Bz2[np.isnan(Bz2)] = 0
    Bz3 = +1* (x1==x2)*(y1!=y2)*(z1==z2)*( x-x1 )/( (z-z1)**2+(x-x1)**2 )*(y-y2)/( (x-x2)**2+(y-y2)**2+(z-z2)**2 )**0.5; Bz3[np.isnan(Bz3)] = 0
    Bz4 = -1* (x1==x2)*(y1!=y2)*(z1==z2)*( x-x1 )/( (z-z1)**2+(x-x1)**2 )*(y-y1)/( (x-x1)**2+(y-y1)**2+(z-z1)**2 )**0.5; Bz4[np.isnan(Bz4)] = 0 
    Bz = 1e-7*i*(Bz1 + Bz2 + Bz3 + Bz4)


    Bx = np.sum(Bx, axis=2)
    By = np.sum(By, axis=2)
    Bz = np.sum(Bz, axis=2) 

    return Bx, By, Bz

def caf(A, X, r):
    return (A-X)*((A-X)!=0) + ( 1/2*r**2/( A + r*(A==0) ) )*((A-X)==0)*(A!=0) + r*((A-X)==0)*(A==0)

def ampere3d(geometry : Geometry, excitation : Excitation):
    [Fx, Fy, Fz, N] = _ampere3d(
        excitation.T, 
        excitation.I, 
        geometry.XS, 
        geometry.XE, 
        geometry.YS, 
        geometry.YE, 
        geometry.ZS,
        geometry.ZE,
        geometry.R,
        geometry.Nph,
        geometry.NF)
    return Forces(Fx, Fy, Fz, N)

def _ampere3d(T, I, XS, XE, YS, YE, ZS, ZE, R, N3ph, NF):
    if not( (XS.shape==XE.shape) & (YS.shape==YE.shape) & (ZS.shape==ZE.shape) &
        (XS.shape==YS.shape) & (XS.shape==ZS.shape) & (XS.shape==N3ph.shape)  ):
        exit('Exit on error: ampere3d - Input vectors dimensions must agree')     

    [xs_1, _, xs_2] = np.meshgrid(XS, T, XS, indexing='ij')
    [xe_1, _, xe_2] = np.meshgrid(XE, T, XE, indexing='ij')
    [ys_1, _, ys_2] = np.meshgrid(YS, T, YS, indexing='ij')
    [ye_1, _, ye_2] = np.meshgrid(YE, T, YE, indexing='ij')
    [zs_1, _, zs_2] = np.meshgrid(ZS, T, ZS, indexing='ij')
    [ze_1, _, ze_2] = np.meshgrid(ZE, T, ZE, indexing='ij')
    [ r_1, _,  r_2] = np.meshgrid(R , T, R , indexing='ij')
        
    [nc1, nt, nc2] = np.meshgrid(N3ph, np.linspace(1, T.shape[0], T.shape[0])-1, N3ph, indexing='ij')
      
    i_1 = I[nc1.astype(int), nt.astype(int)]
    i_2 = I[nc2.astype(int), nt.astype(int)]

    L1x = (xe_1-xs_1)
    L1y = (ye_1-ys_1)
    L1z = (ze_1-zs_1)
    L2x = (xe_2-xs_2)
    L2y = (ye_2-ys_2)
    L2z = (ze_2-zs_2)

    SEx = (xe_2-xs_1)
    SSx = (xs_2-xs_1)
    SSy = (ys_2-ys_1)
    ESy = (ys_2-ye_1)
    ESx = (xs_2-xe_1)
    EEx = (xe_2-xe_1)
    EEy = (ye_2-ye_1)
    SEy = (ye_2-ys_1)
    SEz = (ze_2-zs_1)
    EEz = (ze_2-ze_1)
    SSz = (zs_2-zs_1)
    ESz = (zs_2-ze_1)
    SS = ( SSx**2 + SSy**2 + SSz**2 )**(1/2)
    ES = ( ESx**2 + ESy**2 + ESz**2 )**(1/2)
    EE = ( EEx**2 + EEy**2 + EEz**2 )**(1/2)
    SE = ( SEx**2 + SEy**2 + SEz**2 )**(1/2)
                      
    condX = (L1x!=0)*(L2x!=0)*(L1y==0)*(L2y==0)*(L1z==0)*(L2z==0)#параллельные сегменты вдоль X  
    condY = (L1x==0)*(L2x==0)*(L1y!=0)*(L2y!=0)*(L1z==0)*(L2z==0)#параллельные сегменты вдоль Y  
    condZ = (L1x==0)*(L2x==0)*(L1y==0)*(L2y==0)*(L1z!=0)*(L2z!=0)#параллельные сегменты вдоль Z
    fx1 = + (SE-SS+ES-EE)*SSx*(condZ/( SSy**2 + SSx**2 ) + condY/( SSz**2 + SSx**2 ))
    fy1 = + (SE-SS+ES-EE)*SSy*(condZ/( SSy**2 + SSx**2 ) + condX/( SSz**2 + SSy**2 ))
    fz1 = + (SE-SS+ES-EE)*SSz*(condY/( SSz**2 + SSx**2 ) + condX/( SSz**2 + SSy**2 ))
   
    fx1[np.isnan(fx1)]=0
    fy1[np.isnan(fy1)]=0
    fz1[np.isnan(fz1)]=0
    fx1[np.isinf(fx1)]=0
    fy1[np.isinf(fy1)]=0
    fz1[np.isinf(fz1)]=0
    
    condXY = (L1x!=0)*(L1y==0)*(L1z==0)*   (L2x==0)*(L2y!=0)*(L2z==0) 
    condXZ = (L1x!=0)*(L1y==0)*(L1z==0)*   (L2x==0)*(L2y==0)*(L2z!=0) 
    condYX = (L1x==0)*(L1y!=0)*(L1z==0)*   (L2x!=0)*(L2y==0)*(L2z==0) 
    condYZ = (L1x==0)*(L1y!=0)*(L1z==0)*   (L2x==0)*(L2y==0)*(L2z!=0) 
    condZX = (L1x==0)*(L1y==0)*(L1z!=0)*   (L2x!=0)*(L2y==0)*(L2z==0) 
    condZY = (L1x==0)*(L1y==0)*(L1z!=0)*   (L2x==0)*(L2y!=0)*(L2z==0)  #скрещенные сегменты

    fx2 = (condZX+condYX)*( log( caf(SS,SSx,r_2) ) - log( caf(ES,ESx,r_2) ) - log( caf(SE,SEx,r_2) ) + log( caf(EE,EEx,r_2) )) 
    fy2 = (condXY+condZY)*( log( caf(SS,SSy,r_2) ) - log( caf(ES,ESy,r_2) ) - log( caf(SE,SEy,r_2) ) + log( caf(EE,EEy,r_2) )) 
    fz2 = (condYZ+condXZ)*( log( caf(SS,SSz,r_2) ) - log( caf(ES,ESz,r_2) ) - log( caf(SE,SEz,r_2) ) + log( caf(EE,EEz,r_2) ))

    fx2[np.isnan(fx2)]=0
    fy2[np.isnan(fy2)]=0
    fz2[np.isnan(fz2)]=0
    fx2[np.isinf(fx2)]=0
    fy2[np.isinf(fy2)]=0
    fz2[np.isinf(fz2)]=0

    fx = fx1 + fx2 
    fy = fy1 + fy2
    fz = fz1 + fz2 

    fx = fx*1e-7*i_2*i_1
    fy = fy*1e-7*i_2*i_1
    fz = fz*1e-7*i_2*i_1

    if len(NF)>0:
        [_, nc] = np.meshgrid(np.linspace(1,NF.shape[0],NF.shape[0])-1  ,N3ph, indexing='ij')
        nc = nc.reshape(NF.shape[0], N3ph.shape[0])    
        N = np.sum(nc*NF, axis=1)/np.sum(NF, axis=1)    
        N[np.where(np.sum(abs(nc*NF - N[:,np.newaxis]*NF), axis=1)>0)] = -1
    else:        
        N = np.array([])
        
    FX = []
    FY = []
    FZ = []
    for NF1 in NF:
                
        [nf1, nt, nf2] = np.meshgrid(NF1, np.linspace(1, T.shape[0], T.shape[0])-1, NF1, indexing='ij')
        FX1 = np.sum(fx*(1-nf2), axis=2)
        FY1 = np.sum(fy*(1-nf2), axis=2)
        FZ1 = np.sum(fz*(1-nf2), axis=2) 
       
        FX1 = np.sum((FX1*nf1[:,:,0]), axis=0)
        FY1 = np.sum((FY1*nf1[:,:,0]), axis=0)
        FZ1 = np.sum((FZ1*nf1[:,:,0]), axis=0)
        
        FX.append(FX1)
        FY.append(FY1)
        FZ.append(FZ1)
        
    
    FX = np.array(FX)
    FY = np.array(FY)
    FZ = np.array(FZ)
    
        
    # FX = np.sum(fx, axis=2)
    # FY = np.sum(fy, axis=2)
    # FZ = np.sum(fz, axis=2) 

    # if len(NF)>0:

    #     [nf, _] = np.meshgrid(NF, np.linspace(1, T.shape[0], T.shape[0])-1, indexing='ij')
    #     nf = nf.reshape(NF.shape[0], NF.shape[1], T.shape[0])
    #     [_, fx] = np.meshgrid(np.linspace(1,NF.shape[0],NF.shape[0])-1  ,FX, indexing='ij')
    #     fx = fx.reshape(NF.shape[0], FX.shape[0], T.shape[0])
    #     [_, fy] = np.meshgrid(np.linspace(1,NF.shape[0],NF.shape[0])-1  ,FY, indexing='ij')
    #     fy = fy.reshape(NF.shape[0], FY.shape[0], T.shape[0])
    #     [_, fz] = np.meshgrid(np.linspace(1,NF.shape[0],NF.shape[0])-1  ,FZ, indexing='ij')
    #     fz = fz.reshape(NF.shape[0], FZ.shape[0], T.shape[0])      
          
    #     [_, nc] = np.meshgrid(np.linspace(1,NF.shape[0],NF.shape[0])-1  ,N3ph, indexing='ij')
    #     nc = nc.reshape(NF.shape[0], N3ph.shape[0])
        
        
    #     N = np.sum(nc*NF, axis=1)/np.sum(NF, axis=1)    
    #     N[np.where(np.sum(abs(nc*NF - N[:,np.newaxis]*NF), axis=1)>0)] = -1
       
    #     FX = np.sum((fx*nf), axis=1)
    #     FY = np.sum((fy*nf), axis=1)
    #     FZ = np.sum((fz*nf), axis=1)
    # else:
    #     FX = np.array([])
    #     FY = np.array([])
    #     FZ = np.array([])
    #     N = np.array([])
        
    return FX, FY, FZ, N

def neumann3d(geometry : Geometry, excitation: Excitation):
    L = _neumann3d(
        excitation.K,
        geometry.XS, 
        geometry.XE, 
        geometry.YS, 
        geometry.YE, 
        geometry.ZS,
        geometry.ZE, 
        geometry.R,
        geometry.Nph,
        geometry.NL
        )
    return Inductances(L)

def _neumann3d(K, XS, XE, YS, YE, ZS, ZE, R, N3ph, NL):
    
    [xs_1, xs_2] = np.meshgrid(XS, XS, indexing='ij')
    [xe_1, xe_2] = np.meshgrid(XE, XE, indexing='ij')
    [ys_1, ys_2] = np.meshgrid(YS, YS, indexing='ij')
    [ye_1, ye_2] = np.meshgrid(YE, YE, indexing='ij')
    [zs_1, zs_2] = np.meshgrid(ZS, ZS, indexing='ij')
    [ze_1, ze_2] = np.meshgrid(ZE, ZE, indexing='ij')    
    [nc1, nc2] = np.meshgrid(N3ph, N3ph, indexing='ij')
    
    k1 = K[nc1.astype(int),0]
    k2 = K[nc2.astype(int),0]
    
    L1x = (xe_1-xs_1)
    L1y = (ye_1-ys_1)
    L1z = (ze_1-zs_1)
    L2x = (xe_2-xs_2)
    L2y = (ye_2-ys_2)
    L2z = (ze_2-zs_2)
    
    L = ( (XE-XS)**2 + (YE-YS)**2 + (ZE-ZS)**2 )**(1/2)
        
    SEx = (xe_2-xs_1)
    SEy = (ye_2-ys_1)
    SEz = (ze_2-zs_1)
    SSx = (xs_2-xs_1)
    SSy = (ys_2-ys_1)
    SSz = (zs_2-zs_1)
    ESx = (xs_2-xe_1)
    ESy = (ys_2-ye_1)
    ESz = (zs_2-ze_1)
    EEx = (xe_2-xe_1)
    EEy = (ye_2-ye_1)
    EEz = (ze_2-ze_1)
    
    Syz = ( SSz**2 + SSy**2 )**0.5
    Sxy = ( SSx**2 + SSy**2 )**0.5
    Szx = ( SSz**2 + SSx**2 )**0.5
    
    ESxyz = ( ESx**2 + Syz**2 )**0.5
    SSxyz = ( SSx**2 + Syz**2 )**0.5
    EExyz = ( EEx**2 + Syz**2 )**0.5
    SExyz = ( SEx**2 + Syz**2 )**0.5 
    ESyzx = ( ESy**2 + Szx**2 )**0.5
    SSyzx = ( SSy**2 + Szx**2 )**0.5 
    EEyzx = ( EEy**2 + Szx**2 )**0.5
    SEyzx = ( SEy**2 + Szx**2 )**0.5 
    ESzxy = ( ESz**2 + Sxy**2 )**0.5
    SSzxy = ( SSz**2 + Sxy**2 )**0.5
    EEzxy = ( EEz**2 + Sxy**2 )**0.5
    SEzxy = ( SEz**2 + Sxy**2 )**0.5 
    
    condX = (L1x!=0)*(L2x!=0)*(L1y==0)*(L2y==0)*(L1z==0)*(L2z==0)#параллельные сегменты вдоль X  
    condY = (L1x==0)*(L2x==0)*(L1y!=0)*(L2y!=0)*(L1z==0)*(L2z==0)#параллельные сегменты вдоль Y  
    condZ = (L1x==0)*(L2x==0)*(L1y==0)*(L2y==0)*(L1z!=0)*(L2z!=0)#параллельные сегменты вдоль Z
    
    Self = 2*1e-7*( L*log( 2*L/R ) - L*1 )
    Self[np.isinf(Self)]=0
    Self[np.isnan(Self)]=0
    
       
    mutualx = +np.sign(k1*k2)*1* 1e-7*condX*( + ESx*log( ESx + ESxyz ) - ESxyz
                                            - SSx*log( SSx + SSxyz ) + SSxyz
                                            - EEx*log( EEx + EExyz ) + EExyz
                                            + SEx*log( SEx + SExyz ) - SExyz )
                                
    mutualy = +np.sign(k1*k2)*1*  1e-7* condY*( + ESy*log( ESy + ESyzx ) - ESyzx
                                            - SSy*log( SSy + SSyzx ) + SSyzx
                                            - EEy*log( EEy + EEyzx ) + EEyzx
                                            + SEy*log( SEy + SEyzx ) - SEyzx ) 
                                
    mutualz = +np.sign(k1*k2)*1*  1e-7*condZ*(  + ESz*log( ESz + ESzxy ) - ESzxy
                                                - SSz*log( SSz + SSzxy ) + SSzxy
                                                - EEz*log( EEz + EEzxy ) + EEzxy
                                                + SEz*log( SEz + SEzxy ) - SEzxy ) 


    mutualx[np.isnan(mutualx)]=0
    mutualx[np.isinf(mutualx)]=0
    fill_diagonal(mutualx, 0)
    mutualy[np.isnan(mutualy)]=0
    mutualy[np.isinf(mutualy)]=0
    fill_diagonal(mutualy, 0)
    mutualz[np.isnan(mutualz)]=0
    mutualz[np.isinf(mutualz)]=0
    fill_diagonal(mutualz, 0)
    
    Mutual = np.sum(mutualx+mutualy+mutualz, axis=1)
    
    Inductance = Mutual + Self
    
    LS = np.sum((Self*NL), axis=1)
    
    L = np.sum((Inductance*NL), axis=1)
    
    return L
    
    