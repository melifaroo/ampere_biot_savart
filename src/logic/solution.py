import numpy as np
from numpy import log, atan, sin, pi, exp
from geometry import Geometry
from exitation import Exitation
from dataclasses import dataclass

@dataclass
class Forces:
    def __init__(self, Fx, Fy, Fz):
        self.Fx = Fx
        self.Fy = Fy
        self.Fz = Fz
        
@dataclass
class Fields:
    def __init__(self, Bx, By, Bz):
        self.Bx = Bx
        self.By = By
        self.By = Bz
        self.Bax = By
        self.Btr = (Bx**2 + Bz**2)**0.5
        self.Bmag = (self.Bax**2 + self.Btr**2)**0.5
        
@dataclass
class Results:
    forces : Forces
    fields : Fields        
    def __init__(self, fields, forces):
        self.fields = fields
        self.forces = forces
        
def solve(geometry : Geometry, exitation : Exitation):
    return Results(
        biotsavart3d(geometry, exitation),
        ampere3d(geometry, exitation)
        )
        
def biotsavart3d(geometry : Geometry, exitation : Exitation):
    [Bx, By, Bz] = _biotsavart3d(
        exitation.T, 
        exitation.I, 
        geometry.XS, 
        geometry.XE, 
        geometry.YS, 
        geometry.YE, 
        geometry.ZS,
        geometry.ZE, 
        geometry.NC,
        geometry.X,
        geometry.Y,
        geometry.Z)
    return Fields(Bx, By, Bz)       
      
def _biotsavart3d(T, I, XS, XE, YS, YE, ZS, ZE, NC, X, Y, Z):
    if not( (XS.shape==XE.shape) & (YS.shape==YE.shape) & (ZS.shape==ZE.shape) &
            (XS.shape==YS.shape) & (XS.shape==ZS.shape) & (XS.shape==NC.shape) &
            (X.shape==Y.shape) & (X.shape==Z.shape) ):
        exit('Exit on error: biotsavart3d - Input vectors dimensions must agree')     
    
    [x, _, x1] = np.meshgrid(X, T, XS, indexing='ij')
    [x, _, x2] = np.meshgrid(X, T, XE, indexing='ij')
    [y, _, y1] = np.meshgrid(Y, T, YS, indexing='ij')
    [y, _, y2] = np.meshgrid(Y, T, YE, indexing='ij')
    [z, _, z1] = np.meshgrid(Z, T, ZS, indexing='ij')
    [z, _, z2] = np.meshgrid(Z, T, ZE, indexing='ij')
    [_, nt, nc] = np.meshgrid(X, np.linspace(1, T.shape[0], T.shape[0])-1, NC, indexing='ij')
    i = I[nc.astype(int), nt.astype(int)]

    lsq = ( (x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2 )
    rho = ( (x2-x1)*(x-x1)+(y2-y1)*(y-y1)+(z2-z1)*(z-z1) )/lsq
    x0 = x1*(1-rho) + x2*rho
    y0 = y1*(1-rho) + y2*rho
    z0 = z1*(1-rho) + z2*rho
    hsq = ( (x0-x)**2 + (y0-y)**2 + (z0-z)**2 )
    sina1 = np.sign(  rho)*( ( ((y0-y)*(z1-z)-(z0-z)*(y1-y))**2 + ((z0-z)*(x1-x)-(x0-x)*(z1-z))**2 + ((x0-x)*(y1-y)-(y0-y)*(x1-x))**2 ) / (hsq*( (x1-x)**2 + (y1-y)**2 + (z1-z)**2 )) )**0.5
    sina2 = np.sign(1-rho)*( ( ((y0-y)*(z2-z)-(z0-z)*(y2-y))**2 + ((z0-z)*(x2-x)-(x0-x)*(z2-z))**2 + ((x0-x)*(y2-y)-(y0-y)*(x2-x))**2 ) / (hsq*( (x2-x)**2 + (y2-y)**2 + (z2-z)**2 )) )**0.5
    
    Bx = ( (y2-y1)*(z-z0)-(z2-z1)*(y-y0) )*0.0001*i/hsq/lsq**0.5*(sina1+sina2) 
    Bx[np.isnan(Bx)] = 0
    By = ( (z2-z1)*(x-x0)-(x2-x1)*(z-z0) )*0.0001*i/hsq/lsq**0.5*(sina1+sina2)
    By[np.isnan(By)] = 0
    Bz = ( (x2-x1)*(y-y0)-(y2-y1)*(x-x0) )*0.0001*i/hsq/lsq**0.5*(sina1+sina2)
    Bz[np.isnan(Bz)] = 0

    Bx = np.sum(Bx, axis=2)
    By = np.sum(By, axis=2)
    Bz = np.sum(Bz, axis=2) 

    return Bx, By, Bz

def corner_approx(A, X, r):
    return (A-X)*((A-X)!=0) + 1/2*r**2/(A+r*(A==0))*((A-X)==0)*(A!=0) + 1/2*r*((A-X)==0)*(A==0)

def ampere3d(geometry : Geometry, exitation : Exitation):
    [Fx, Fy, Fz] = _ampere3d(
        exitation.T, 
        exitation.I, 
        geometry.XS, 
        geometry.XE, 
        geometry.YS, 
        geometry.YE, 
        geometry.ZS,
        geometry.ZE, 
        geometry.NC,
        geometry.NF,
        geometry.r)
    return Forces(Fx, Fy, Fz)

def _ampere3d(T, I, XS, XE, YS, YE, ZS, ZE, NC, NF, r=0.1):
    if not( (XS.shape==XE.shape) & (YS.shape==YE.shape) & (ZS.shape==ZE.shape) &
        (XS.shape==YS.shape) & (XS.shape==ZS.shape) & (XS.shape==NC.shape) ):
        exit('Exit on error: ampere3d - Input vectors dimensions must agree')     

    [xs_1, _, xs_2] = np.meshgrid(XS, T, XS, indexing='ij')
    [xe_1, _, xe_2] = np.meshgrid(XE, T, XE, indexing='ij')
    [ys_1, _, ys_2] = np.meshgrid(YS, T, YS, indexing='ij')
    [ye_1, _, ye_2] = np.meshgrid(YE, T, YE, indexing='ij')
    [zs_1, _, zs_2] = np.meshgrid(ZS, T, ZS, indexing='ij')
    [ze_1, _, ze_2] = np.meshgrid(ZE, T, ZE, indexing='ij')
        
    [nc1, nt, nc2] = np.meshgrid(NC, np.linspace(1, T.shape[0], T.shape[0])-1, NC, indexing='ij')
    
    i_1 = I[nc1.astype(int), nt.astype(int)]
    i_2 = I[nc2.astype(int), nt.astype(int)]

    L1x = (xe_1-xs_1)
    L1y = (ye_1-ys_1)
    L1z = (ze_1-zs_1)
    L2x = (xe_2-xs_2)
    L2y = (ye_2-ys_2)
    L2z = (ze_2-zs_2)

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
    SE = ( SEx**2 + SEy**2 + SEz**2 )**(1/2)
    SS = ( SSx**2 + SSy**2 + SSz**2 )**(1/2)
    ES = ( ESx**2 + ESy**2 + ESz**2 )**(1/2)
    EE = ( EEx**2 + EEy**2 + EEz**2 )**(1/2)
                      
    condX = (L1x!=0)*(L2x!=0)*(L1y==0)*(L2y==0)*(L1z==0)*(L2z==0)#параллельные сегменты вдоль X  
    condY = (L1x==0)*(L2x==0)*(L1y!=0)*(L2y!=0)*(L1z==0)*(L2z==0)#параллельные сегменты вдоль Y  
    condZ = (L1x==0)*(L2x==0)*(L1y==0)*(L2y==0)*(L1z!=0)*(L2z!=0)#параллельные сегменты вдоль Z
    fx1 = + 2*(SE-SS+ES-EE)*SSx*(condZ/( SSy**2 + SSx**2 )\
                                +condY/( SSz**2 + SSx**2 ))
    fy1 = + 2*(SE-SS+ES-EE)*SSy*(condZ/( SSy**2 + SSx**2 )\
                                +condX/( SSz**2 + SSy**2 ))
    fz1 = + 2*(SE-SS+ES-EE)*SSz*(condY/( SSz**2 + SSx**2 )\
                                +condX/( SSz**2 + SSy**2 ))
   
    fx1[np.isnan(fx1)]=0
    fy1[np.isnan(fy1)]=0
    fz1[np.isnan(fz1)]=0
    fx1[np.isinf(fx1)]=0
    fy1[np.isinf(fy1)]=0
    fz1[np.isinf(fz1)]=0
    
    cond =   ( (L1x!=0)*(L2x==0)*(L1y==0)*(L2y!=0)*(L1z==0)*(L2z==0) \
            + (L1x==0)*(L2x!=0)*(L1y!=0)*(L2y==0)*(L1z==0)*(L2z==0) \
            + (L1x!=0)*(L2x==0)*(L1y==0)*(L2y==0)*(L1z==0)*(L2z!=0) \
            + (L1x==0)*(L2x!=0)*(L1y==0)*(L2y==0)*(L1z!=0)*(L2z==0) \
            + (L1x==0)*(L2x==0)*(L1y!=0)*(L2y==0)*(L1z==0)*(L2z!=0) \
            + (L1x==0)*(L2x==0)*(L1y==0)*(L2y!=0)*(L1z!=0)*(L2z==0) ) #скрещенные сегменты

    SS_p_x = corner_approx(SS, +SSx, r)    
    SS_m_x = corner_approx(SS, -SSx, r)    
    ES_p_x = corner_approx(ES, +ESx, r)    
    ES_m_x = corner_approx(ES, -ESx, r)  
    SE_p_x = corner_approx(SE, +SEx, r)    
    SE_m_x = corner_approx(SE, -SEx, r)    
    EE_p_x = corner_approx(EE, +EEx, r)    
    EE_m_x = corner_approx(EE, -EEx, r)    
    
    SS_p_y = corner_approx(SS, +SSy, r)
    SS_m_y = corner_approx(SS, -SSy, r)
    ES_p_y = corner_approx(ES, +ESy, r)
    ES_m_y = corner_approx(ES, -ESy, r)
    SE_p_y = corner_approx(SE, +SEy, r)
    SE_m_y = corner_approx(SE, -SEy, r)
    EE_p_y = corner_approx(EE, +EEy, r)
    EE_m_y = corner_approx(EE, -EEy, r)

    # For the z components
    SS_p_z = corner_approx(SS, +SSz, r)
    SS_m_z = corner_approx(SS, -SSz, r)
    ES_p_z = corner_approx(ES, +ESz, r)
    ES_m_z = corner_approx(ES, -ESz, r)
    SE_p_z = corner_approx(SE, +SEz, r)
    SE_m_z = corner_approx(SE, -SEz, r)
    EE_p_z = corner_approx(EE, +EEz, r)
    EE_m_z = corner_approx(EE, -EEz, r)
    
    fx2 = (log(SS_p_x) + log(ES_m_x) + log(SE_m_x) + log(EE_p_x) - 
            log(SS_m_x) - log(ES_p_x) - log(SE_p_x) - log(EE_m_x)) * cond

    fy2 = (log(SS_p_y) + log(ES_m_y) + log(SE_m_y) + log(EE_p_y) - 
            log(SS_m_y) - log(ES_p_y) - log(SE_p_y) - log(EE_m_y)) * cond

    fz2 = (log(SS_p_z) + log(ES_m_z) + log(SE_m_z) + log(EE_p_z) - 
            log(SS_m_z) - log(ES_p_z) - log(SE_p_z) - log(EE_m_z)) * cond

    fx2[np.isnan(fx2)]=0
    fy2[np.isnan(fy2)]=0
    fz2[np.isnan(fz2)]=0
    fx2[np.isinf(fx2)]=0
    fy2[np.isinf(fy2)]=0
    fz2[np.isinf(fz2)]=0

    fx = fx1 + fx2 
    fy = fy1 + fy2
    fz = fz1 + fz2 

    fx = fx*0.05*i_2*i_1
    fy = fy*0.05*i_2*i_1
    fz = fz*0.05*i_2*i_1
        
    FX = np.sum(fx, axis=2)
    FY = np.sum(fy, axis=2)
    FZ = np.sum(fz, axis=2) 

    [nf, _] = np.meshgrid(NF, np.linspace(1, T.shape[0], T.shape[0])-1, indexing='ij')
    nf = nf.reshape(NF.shape[0], NF.shape[1], T.shape[0])
    [_, fx] = np.meshgrid(np.linspace(1,NF.shape[0],NF.shape[0])-1  ,FX, indexing='ij')
    fx = fx.reshape(NF.shape[0], FX.shape[0], T.shape[0])
    [_, fy] = np.meshgrid(np.linspace(1,NF.shape[0],NF.shape[0])-1  ,FY, indexing='ij')
    fy = fy.reshape(NF.shape[0], FY.shape[0], T.shape[0])
    [_, fz] = np.meshgrid(np.linspace(1,NF.shape[0],NF.shape[0])-1  ,FZ, indexing='ij')
    fz = fz.reshape(NF.shape[0], FZ.shape[0], T.shape[0])
    
    FX = np.sum((fx*nf), axis=1)
    FY = np.sum((fy*nf), axis=1)
    FZ = np.sum((fz*nf), axis=1)
        
    return FX, FY, FZ
