import numpy as np
import matplotlib.pyplot as plt
from numpy import exp, sin, cos, pi, atan

class Struct:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def plot_force(m,n,p, data, lim, T):
    plt.subplot(m, n, p)
    plt.plot(time, data.f[:,0] ,'k-', linewidth=2.0)
    plt.plot(time, data.f[:,1] ,'k--', linewidth=2.0)
    plt.plot(time, data.f[:,2] ,'k:', linewidth=2.0)
    plt.xlim([-0,T])
    plt.ylim([-lim*1.1, lim*1.1])
    plt.legend(["A","B","C"], loc = 'upper right')
    plt.grid(True)

def plot_current(m,n,p, data, lim, T):
    plt.subplot(m, n, p)
    plt.plot(time, data.i1[:,0,0] ,'k-', linewidth=2.0)
    plt.plot(time, data.i1[:,1,0] ,'k--', linewidth=2.0)
    plt.plot(time, data.i1[:,2,0] ,'k:', linewidth=2.0)
    plt.ylim([-lim*1.1, lim*1.1])
    plt.xlim([-0,T])
    plt.legend(["A","B","C"], loc = 'upper right')
    plt.grid(True)

def plot_field(m,n,p, data, lim, T):
    plt.subplot(m, n, p)
    plt.plot(time, data.ba[:,0,0] ,'k-', linewidth=2.0)
    plt.plot(time, data.ba[:,1,0] ,'k--', linewidth=2.0)
    plt.ylim([-lim*1.1, lim*1.1])
    plt.xlim([-0,T])
    plt.legend(["A","B","C"], loc = 'upper right')
    plt.grid(True)

def current_gen(t, j, Isc, omega, tau, alpha, phi):
    return Isc*2**0.5*(sin( omega*t + alpha - phi - 2*pi/3 * (j - 1) ) - exp( -t / tau ) * sin( alpha - phi - 2*pi/3 * (j - 1) ) )

def current_rlc(t, k, I0, omega, tau, delta):
    return I0*exp(-(t-delta)/tau)*sin(omega*(t-delta))*k*(t>delta)

def force(i1, i2, x1, x2):
    f = 0.2*i1*i2/(x2-x1)
    f[np.isnan(f) | np.isinf(f)] = 0
    f = f.sum(axis=2) 
    return f

def field(i1, x1, z1, x0, z0):
    bt = 0.2*0.001*(i1/((x0-x1)**2+(z0-z1)**2)*(z0-z1))
    bt = bt.sum(axis=1) 
    bz = 0.2*0.001*(i1/((x0-x1)**2+(z0-z1)**2)*(x0-x1))
    bz = bz.sum(axis=1)
    ba = 0.2*0.001*(i1/((x0-x1)**2+(z0-z1)**2)*((x0-x1)**2+(z0-z1)**2)**0.5)
    ba = ba.sum(axis=1)
    return 0


T = 60
time = np.linspace(0,T,1+int(T/1))

Lp = 0.150

Kd = 0.25

Isc = 31.5
freq = 50
tau = 45
period = 1000/freq
omega = 2*pi/period
alpha = 0
phi = atan(omega*tau)

tau0 = 27
period0 = 1000/freq
omega0 = 2*pi/period0
delta = 5

n = np.linspace(1,5,3)
Ip = Isc*2**0.5*(1 + exp( -n * period / tau / 2 ) )
print(Ip)
Kmk = Ip / Isc
Fp = 0.2*Ip**2/Lp
print(Fp)
I0 = Ip[0]/exp(-period0/tau0/4)

j = np.linspace(1,3,3)
x = np.linspace(0,2*Lp,3)
k = np.array([1, -1, 0])#-0.5*(1+Kd), -0.5*(1-Kd) ])

[j1, t, j2] = np.meshgrid(j, time, j)
[k1, t, k2] = np.meshgrid(k, time, k)
[x1, t, x2] = np.meshgrid(x, time, x)

real =Struct()
real.i1 = current_gen(t, j1, Isc, omega, tau, alpha, phi)
real.i2 = current_gen(t, j2, Isc, omega, tau, alpha, phi)
real.f = force(real.i1, real.i2, x1, x2)
# real.b = field(real.i1, x1, z1, x0, z0)

rlc3 =Struct()
rlc3.i1 = current_rlc(t, k1, I0, omega0, tau0, delta)
rlc3.i2 = current_rlc(t, k2, I0, omega0, tau0, delta)
rlc3.f = force(rlc3.i1, rlc3.i2, x1, x2)

fig1 = plt.figure() 

plot_current(2,3,1, real, Ip[0], T)
plt.ylabel("ГЕНЕРАТОР")
plt.title("ток [A]")
plot_force(2,3,2, real, Fp[0], T)
plt.ylabel("сила [Н]")
plt.ylabel("индукция [Тл]")

plot_current(2,3,4, rlc3, Ip[0], T)
plt.title("КОНТУР")
plot_force(2,3,5, rlc3, Fp[0], T)

plt.show()
