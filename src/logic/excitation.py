import numpy as np
from numpy import atan, sin, pi, exp
from dataclasses import dataclass

@dataclass  
class Exitation:
    T: float
    I: float
    def __init__(self, T, I):
        if not( (T.shape[0]==I.shape[1]) ):
            exit('Exit on error: Exitation definition - Input vectors dimensions must agree')     
        self.T = T
        self.I = I
        
def current_gen(t, j, Isc, omega, tau, alpha, phi):
    N = j.shape[0]
    return Isc*2**0.5*(sin( omega*t + alpha - phi - 2*pi/N * (j - 1) ) - exp( -t / tau ) * sin( alpha - phi - 2*pi/N * (j - 1) ) )
    
def current_rlc(t, k, I0, omega, tau, delta):
    return I0*exp(-(t-delta)/tau)*sin(omega*(t-delta))*k*(t>delta)
    
def build(TIME, T_SIZE, NPhases, Isc, shape, Kd = 0):
    # Isc = 31.5
    freq = 50
    tau = 45
    period = 1000/freq
    omega = 2*pi/period
    alpha = 0
    phi = atan(omega*tau)
    n = 1
    Ip = Isc*2**0.5*(1 + exp( -n * period / tau / 2 ) )
    tau0 = 27
    period0 = 1000/freq
    omega0 = 2*pi/period0
    delta = 5
    I0 = Ip/exp(-period0/tau0/4)

    N = np.linspace(1,NPhases,NPhases)
    
    K = np.linspace(1,NPhases,NPhases)
    Kd = np.array([0, +1, -1])*Kd
    for i in range(1,NPhases):
        K[i] = 1/(NPhases-1)    
    K = K + K*Kd[0:NPhases]
    
    T = np.linspace(0,TIME,T_SIZE)

    [n, t] = np.meshgrid(N, T, indexing='ij')
    [k, t] = np.meshgrid(K, T, indexing='ij')
    if shape == "const":
        I = np.ones((NPhases, T_SIZE))*Ip
    elif shape == "rlc":
        I = current_rlc(t, k, I0, omega0, tau0, delta)
    elif shape == "gen":
        I = current_gen(t, n, Isc, omega, tau, alpha, phi)
    else:
        return 
    
    return Exitation(T, I)