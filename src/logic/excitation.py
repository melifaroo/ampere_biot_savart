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
    
def build(TIME, T_SIZE : int, I, current = "peak", source_type = "gen", freq = 50, delta = 5, tau = None, tau_std = 45):
        
    tau_rlc_default = 27
    valid_types  = {"rlc", "gen"}
    if source_type not in valid_types:
        raise ValueError("error: Excitation.build - type must be one of %s." % valid_types)
    valid_currents  = {"rms", "peak"}
    if current not in valid_currents:
        raise ValueError("error: Excitation.build - type must be one of %s." % valid_types)
            
    omega = 2*pi*freq
    alpha = 0
    tau = (tau_std if source_type=="gen" else tau_rlc_default) if (tau == None) else tau
    phi = atan(omega*tau/1000)           
    phi_std = atan(omega*tau_std/1000)
    Kp = current_gen( (pi/2+phi_std)/omega, 1, omega, tau_std/1000, 0, phi_std)[0]
    Ip  = I if (current == "peak") else I*Kp
    Isc = I if (current ==  "rms") else I/Kp      
    I0 = Ip/( exp(-phi/omega*1000/tau)*sin(phi) )           
    T = np.linspace(0,TIME,T_SIZE)

    if  source_type == "rlc":
        I = current_rlc(T, I0, omega/1000, tau, delta)
    elif source_type == "gen":
        I = current_gen(T, Isc, omega/1000, tau, alpha, phi)
    else:
        raise ValueError("error: Excitation.build - type must be one of %s." % valid_types) 
    
    return Excitation(T, I*1000 )