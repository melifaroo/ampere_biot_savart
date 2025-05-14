import numpy as np
from numpy import atan, sin, pi, exp
from dataclasses import dataclass

@dataclass  
class Excitation:
    current: float
    T: float
    I: float   
    K: float
    asymK : float = 0                           
        
    def __init__(self, T, I):
        if not( (T.shape==I.shape) ) and not( (T.shape[0]==I.shape[1]) ):
            exit('Exit on error: Exitation definition - Input vectors dimensions must agree')     
        self.T = T
        self.current = I

def current_gen(T, Isc, omega, tau, alpha, phi):    
    [j, t] = np.meshgrid([1,2,3], T, indexing='ij')
    return Isc*2**0.5*(sin( omega*t + alpha - phi - 2*pi/3 * (j - 1) ) - exp( -t / tau ) * sin( alpha - phi - 2*pi/3 * (j - 1) ) )
    
def current_rlc(t, I0, omega, tau, delta):
    return I0*exp(-(t-delta)/tau)*sin(omega*(t-delta))*(t>delta)
    
def build(TIME, T_SIZE : int, I , current = "rms", type = "const"):
        
    valid_types  = {"const", "rlc", "gen"}
    if type not in valid_types:
        raise ValueError("error: Excitation.build - type must be one of %s." % valid_types)
    valid_currents  = {"rms", "peak"}
    if current not in valid_currents:
        raise ValueError("error: Excitation.build - type must be one of %s." % valid_types)
        
    freq = 50
    tau = 45
    period = 1000/freq
    omega = 2*pi/period
    alpha = 0
    phi = atan(omega*tau)
    n = 1
        
    tau0 = 27
    period0 = 1000/freq
    omega0 = 2*pi/period0
    delta = 5
        
    if current == "rms":
        Isc = I
        Ip = current_gen( (pi/2+phi)/omega, Isc, omega, tau, alpha, phi)[0]
    elif current == "peak":
        Ip = I
        Isc = Ip / current_gen( (pi/2+phi)/omega, 1, omega, tau, alpha, phi)[0]
        
    t0 = atan(omega0*tau0)/omega0
    I0 = Ip/( exp(-t0/tau0)*sin(omega0*t0) )
           
    T = np.linspace(0,TIME,T_SIZE)

    if type == "const":
        I = T*0+I
    elif type == "rlc":
        I = current_rlc(T, I0, omega0, tau0, delta)
    elif type == "gen":
        I = current_gen(T, Isc, omega, tau, alpha, phi)
    else:
        raise ValueError("error: Excitation.build - type must be one of %s." % valid_types) 
    
    return Excitation(T, I*1000 )