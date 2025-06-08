import tkinter as tk
import numpy as np
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
from gui.app import Application
import logic.solution as solution
import logic.excitation as excitation
import logic.geometry as geometry
import logic.presentation as presentation
from numpy import log, pi, trapezoid, arcsinh

def demo_II():
    P = 1
    L = 1
    I = 10
    contour = geometry.sample_II(LP = P, L = L)    
    circuit = excitation.build(10, 21, I, type = "rlc", current ="peak")    
    results = solution.solve(contour, circuit)  
    
    fAx = (results.forces.Fx[0,11])
    fAy = (results.forces.Fy[0,11])
    fAz = (results.forces.Fz[0,11])
    fBx = (results.forces.Fx[1,11])  
    fBy = (results.forces.Fy[1,11])  
    fBz = (results.forces.Fz[1,11])   
    I = circuit.I.max()/1000    
    print("I[kA] = %5.0f | A||B" % ( I ))
    print("A:      (%5.1f, %5.1f, %5.1f)->(%5.1f, %5.1f, %5.1f)" % ( 0, 0, 0,  0, 0, L ))
    print("B:      (%5.1f, %5.1f, %5.1f)->(%5.1f, %5.1f, %5.1f)" % ( P, 0, 0,  P, 0, L ))  
    print("FA[N] = (%5.2f, %5.2f, %5.2f)" % ( fAx,  fAy, fAz  ))  
    print("FB[N] = (%5.2f, %5.2f, %5.2f)" % ( fBx,  fBy, fBz ))        
    presentation.plot(contour, circuit, results, Exit = True)      
    
    contour = geometry.sample_II_inf(LP = P, L = L)     
    results = solution.solve(contour, circuit)    
    fAx = (results.forces.Fx[0,11])
    fAy = (results.forces.Fy[0,11])
    fAz = (results.forces.Fz[0,11])
    fBx = (results.forces.Fx[1,11])  
    fBy = (results.forces.Fy[1,11])  
    fBz = (results.forces.Fz[1,11])      
    print("infinite")
    print("FA[N] = (%5.2f, %5.2f, %5.2f)" % ( fAx,  fAy, fAz  ))  
    print("FB[N] = (%5.2f, %5.2f, %5.2f)" % ( fBx,  fBy, fBz ))       
    presentation.plot(contour, circuit, results, Exit = False)      

def demo_X():
    L = 1
    Z = 1/2
    X = 1
    Y = 0
    contour = geometry.sample_X(X, Y, Z, L1 = L, L2 = L )    
    circuit = excitation.build(20, 21, 1, type = "rlc", current ="peak", Nph = 1)   
    results = solution.solve(contour, circuit, False)  
    fAx = (results.forces.Fx[0,11])
    fAy = (results.forces.Fy[0,11])
    fAz = (results.forces.Fz[0,11])
    fBx = (results.forces.Fx[1,11])  
    fBy = (results.forces.Fy[1,11])  
    fBz = (results.forces.Fz[1,11])  
    I = circuit.I.max()/1000
    print("I[kA] = %5.0f | AXB" % ( I ))
    print("A:      (%5.1f, %5.1f, %5.1f)->(%5.1f, %5.1f, %5.1f)" % ( 0, 0, Z,  0, L, Z ))
    print("B:      (%5.1f, %5.1f, %5.1f)->(%5.1f, %5.1f, %5.1f)" % ( X, Y, 0,  X, Y, L ))  
    print("FA[N] = (%5.2f, %5.2f, %5.2f)" % ( fAx,  fAy, fAz  ))  
    print("FB[N] = (%5.2f, %5.2f, %5.2f)" % ( fBx,  fBy, fBz ))    
    presentation.plot(contour, circuit, results, Exit = True)  
    
def demo_L():
    L = 1
    I = 1
    contour = geometry.sample_L(L1=L, L2=L, r=0.02)    
    # contour.rotateZ()
    # # contour.mirriorZ()
    # contour.mirriorX()
    circuit = excitation.build(20, 21, 1, type = "const", current ="peak")   
    results = solution.solve(contour, circuit)  
      
    fAx = max(results.forces.Fx[0])
    fAy = max(results.forces.Fy[0])
    fAz = max(results.forces.Fz[0])
    fBx = max(results.forces.Fx[1])  
    fBy = max(results.forces.Fy[1])  
    fBz = max(results.forces.Fz[1])  
    I = circuit.current.max()/1000
    print("I[kA] = %5.0f | ALB" % ( I ))
    print("A:      (%5.1f, %5.1f, %5.1f)->(%5.1f, %5.1f, %5.1f)" % ( 0, L, 0,  0, 0, 0 ))
    print("B:      (%5.1f, %5.1f, %5.1f)->(%5.1f, %5.1f, %5.1f)" % ( 0, 0, 0,  0, L, 0 ))    
    print("FA[N] = (%5.2f, %5.2f, %5.2f)" % ( fAx,  fAy, fAz  ))  
    print("FB[N] = (%5.2f, %5.2f, %5.2f)" % ( fBx,  fBy, fBz ))            
    presentation.plot(contour, circuit, results, Exit = False)  
    
    # contour = geometry.sample_L_inf(L1=L, L2=L)    
    # circuit = exitation.build(10, 21, 1, I, type = "rlc", current ="peak")   
    # results = solution.solve(contour, circuit, False)    
 
    # fAx = (results.forces.Fx[0,11])
    # fAy = (results.forces.Fy[0,11])
    # fAz = (results.forces.Fz[0,11])
    # fBx = (results.forces.Fx[1,11])  
    # fBy = (results.forces.Fy[1,11])  
    # fBz = (results.forces.Fz[1,11])  
    # I = circuit.I.max()/1000
    # print("infinite")
    # print("FA[N] = (%5.2f, %5.2f, %5.2f)" % ( fAx,  fAy, fAz  ))  
    # print("FB[N] = (%5.2f, %5.2f, %5.2f)" % ( fBx,  fBy, fBz ))       
    # presentation.plot(contour, circuit, results, Exit = True)  

def demo_3I_K():
    contour = geometry.sample_3_I(L = 1, LP = 1, L0 = 1, INF = 1e1, r=0.02)
    circuit0 = excitation.build(20*1, 101*1, 1, type = "gen", current="peak")   
    
    
    print("%5s %5s %5s %5s %5s %5s %5s %5s" % ( "K", "IB/IC", "FA", "FB", "|BA|", "BAax", "|BB|", "BBax" ) )
    results0 = solution.solve(contour, circuit0)
    FA0 = abs(results0.forces.Fx[0,:]).max()
    FB0 = abs(results0.forces.Fx[1,:]).max()
    BAmg0 = abs(results0.fields.Bmag[0,:]).max()*1000
    BBmg0 = abs(results0.fields.Bmag[1,:]).max()*1000
    BAax0 = abs(results0.fields.Bax[0,:]).max()*1000
    BBax0 = abs(results0.fields.Bax[1,:]).max()*1000
    
    presentation.plot(contour, circuit0, results0)    
    
    circuit1 = excitation.build(20*1, 201*1, 1, type = "rlc", current="peak")   
    for K in np.array([0, 0.3]):
        circuit1.setK1ph([1, -0.5*(1 + K), -0.5*(1 - K)])
        results1 = solution.solve(contour, circuit1)
        FA1 = abs(results1.forces.Fx[0,:]).max()
        FB1 = abs(results1.forces.Fx[1,:]).max()
        BAmg1 = abs(results1.fields.Bmag[0,:]).max()*1000
        BBmg1 = abs(results1.fields.Bmag[1,:]).max()*1000
        BAax1 = abs(results1.fields.Bax[0,:]).max()*1000
        BBax1 = abs(results1.fields.Bax[1,:]).max()*1000
        
        print("%5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f" % ( K, (1+K)/(1-K), FA1/FA0, FB1/FB0, BAmg1/BAmg0,  BAax1/BAax0, BBmg1/BBmg0, BBax1/BBax0) )
        
        presentation.plot(contour, circuit1, results1)    
        
        

def demo_rects():
        
    contour = geometry.sample_3_O(L=0.5, L3=0.5, LP=0.5, r=0.025 )
        
    circuit = excitation.build(10*1, 101*1, 72, type = "rlc", current="peak")    
        
    results = solution.solve(contour, circuit)
    
    presentation.plot(contour, circuit, results, False)    

    # print(circuit.inductances.L)
    
    # print(inductances.L[1]/inductances.L[2] )
    
    # print(1 /(1 + inductances.L[1]/inductances.L[2]) )
        
    # print( ( - inductances.L[1] + inductances.L[2])/(inductances.L[1] + inductances.L[2]) )
    
    # print ( (- circuit.K[1] + circuit.K[2])/ 1 )
    
    print ( circuit.asymK )
    print ( np.reshape(circuit.K,(1,3))[0] )
    print("%5s %5s %5s" % ( "IA_pk",  "IB_pk",  "IC_pk" ))
    print("%5.0f %5.0f %5.0f" % ( abs(circuit.I[0]).max()/1000, abs(circuit.I[1]).max()/1000, abs(circuit.I[2]).max()/1000 ))
          

    # results = solution.solve(contour, circuit, True)
    # presentation.plot(contour, circuit, results)
    # FA = abs(results.forces.Fx[0,:]).max()
    # FB = abs(results.forces.Fx[1,:]).max()
    # E = trapezoid( abs(circuit.I[1,:]*circuit.I[0,:]) + abs(circuit.I[1,:]*circuit.I[2,:]), circuit.T[:])*1e-6

    # print(results.inductances.L)
    
    # print(results.inductances.L[1]/results.inductances.L[2])
    
    # for i in range(6):
    #     K=(1.0 - i*0.1)
    #     contour.setK1ph([ 1, -1/(1+K), -1/(1+1/K) ])
    #     circuit = exitation.build(20, 101, 3, 10, type = "rlc", current="peak")    
    #     results = solution.solve(contour, circuit, False)
    #     if i==3:
    #         presentation.plot(contour, circuit, results)    
    #     fA = abs(results.forces.Fx[0,:]).max()
    #     fB = abs(results.forces.Fx[1,:]).max()  
    #     e = trapezoid( abs(circuit.I[:]*circuit.I[:]*0.5) + abs(circuit.I[:]*circuit.I[:]*0.25), circuit.T)*1e-6
    #     print("%5.0f %5.0f %5.3f %5.3f %5.3f %5.0f%% %5.0f%% %5.0f%%" % ( circuit.I[0].max(), circuit.I[1].min(), e*(1+0.85**2+0.75**2), fA , fB, e*(1+0.85**2+0.75**2)/E*100, fA/FA*100, fB/FB*100 ))
    
    # contour.setK1ph([ 1, -1, 0 ])
    # circuit = exitation.build(20, 101, 1, 72, type = "rlc", current="peak")    
    # results = solution.solve(contour, circuit, False)
    # presentation.plot(contour, circuit, results)    


def demo_shell():
    contour = geometry.sample_shell_rlcABC(L = 0.9, L1 = 0.7, L2 = 0.2, L3 = 0.3, L4 = 0.1, L5 = 0.3, L6  = 0.4, LZ = 1.3, LY = 1, LP = 0.210, L0 = 0.12, r=0.02)
   
    circuit = excitation.build(10*1, 101*1, 72, type = "rlc", current="peak")    
    
    inductances = solution.neumann3d(contour)
    resistances = np.array([80e-6, 80e-6, 80e-6])
    circuit.setBranchImpedance(inductances, resistances)
    
    results = solution.solve(contour, circuit)
    results.inductances = inductances
    
    fA = abs(results.forces.Fx[0,:]).max()/10
    fB = abs(results.forces.Fx[1,:]).max()/10  
    fC = abs(results.forces.Fx[2,:]).max()/10
    e1 = trapezoid( abs(circuit.current[:]*circuit.current[:]*0.5) + abs(circuit.current[:]*circuit.current[:]*0.25), circuit.T*1e-3)*0.2*1e-6

    print("%5s %5s %5s %5s %5s %5s %5s" % ( "IA_pk",  "IB_pk",  "IC_pk", "E3", "FA_pk", "FB_pk", "FB_pk" ))
    print("%5.0f %5.0f %5.0f %5.3f %5.3f %5.3f %5.3f" % ( circuit.current.max()*circuit.K1ph[0]/1000, circuit.current.max()*circuit.K1ph[1]/1000, circuit.current.max()*circuit.K1ph[2]/1000, e1, fA , fB, fC ))
          
    presentation.plot(contour, circuit, results, Exit = True)  
    
    contour = geometry.sample_shell_3phInf(L = 0.9, L1 = 0.7, L2 = 0.2, L3 = 0.3, L4 = 0.1, L5 = 0.3, L6  = 0.4, LZ = 1.3, LY = 1, LP = 0.210, L0 = 0.12, r=0.02)
   
    circuit = excitation.build(60*1, 101*1, 72, type = "gen", current="peak")    
    results = solution.solve(contour, circuit)
    
    fA = abs(results.forces.Fx[0,:]).max()/10
    fB = abs(results.forces.Fx[1,:]).max()/10  
    fC = abs(results.forces.Fx[2,:]).max()/10
    e0 = trapezoid( abs(circuit.current[0,:]*circuit.current[1,:]) + abs(circuit.current[1,:]*circuit.current[2,:]), circuit.T*1e-3)*0.2*1e-6
    print("%5s %5s %5s %5s %5s %5s %5s" % ( "IA_pk",  "IB_pk",  "IC_pk", "E3", "FA_pk", "FB_pk", "FB_pk" ))
    print("%5.0f %5.0f %5.0f %5.3f %5.3f %5.3f %5.3f" % ( circuit.current.max()*circuit.K1ph[0]/1000, circuit.current.max()*circuit.K1ph[1]/1000, circuit.current.max()*circuit.K1ph[2]/1000, e0, fA , fB, fC ))
        
    K = e0/e1/(1)#+0.85**2+0.75**2)) 
    print("%5.1f" % K )
    
    presentation.plot(contour, circuit, results, Exit = False)  
    
  
def demo_shell_L1LP():
    print("\n")
    print("%8s %8s %8s %8s %8s %8s %8s %8s %8s %8s %8s  %8s %8s " % ( "LP" ,"L1" , "L2" , "Ipk A",  "Ipk B",  "Ipk C", "E", "F A", "F B", "|B| A", "B| A", "|B| B", "B| B",  ), sep="")
       
    for L2 in [0.2]: #, 0.15, 0.2, 0.3
        for LP in [0.15, 0.21, 0.275]:#
            L1 = 0.6#(0.6+0.7)*LP/0.21-0.6
            contour = geometry.sample_shell_3phInf(L = 0.9, L1 = L1, L2 = L2, L3 = 0.3, L4 = 0.1, L5 = 0.3, L6  = 0.4, LZ = 1.3, LY = 1, LP = LP, L0 = 0.12, r=0.02)
        
            circuit = excitation.build(20, 21, 72, type = "rlc", current="peak")    
            results = solution.solve(contour, circuit)
            
            fA = abs(results.forces.Fx[0,:]).max()/10
            fB = abs(results.forces.Fx[1,:]).max()/10  
            
            BA = abs(results.fields.Bmag[0,:]).max()*1000
            BB = abs(results.fields.Bmag[1,:]).max()*1000
            BAax = abs(results.fields.Bax[0,:]).max()*1000
            BBax = abs(results.fields.Bax[1,:]).max()*1000
            
            e0=0
            # e0 = trapezoid( abs(circuit.I[0,:]*circuit.I[1,:]) + abs(circuit.I[1,:]*circuit.I[2,:]), circuit.T*1e-3)*0.2*1e-6 
            
            print("%8.3f %8.3f %8.3f %8.0f %8.0f %8.0f %8.1f %8.1f %8.1f %8.1f %8.1f %8.1f %8.1f" % ( LP,L1,L2, circuit.current.max()*circuit.K1ph[0]/1000, circuit.current.max()*circuit.K1ph[1]/1000, circuit.current.max()*circuit.K1ph[2]/1000, e0, fA , fB, BA, BAax  , BB, BBax ))
                
        
            presentation.plot(contour, circuit, results, Exit = True)  


def demo_ABC( contour: geometry.Geometry):
    circuit = excitation.build(20*1, 101*1, 72, type = "gen", current="peak")  
    
    for i in [0, 1, 2]: #, 0.15, 0.2, 0.3
        circuit.current = np.roll(circuit.current, i, axis=0)
        results = solution.solve(contour, circuit)
        
        fA = abs(results.forces.Fx[0,:]).max()/10
        fB = abs(results.forces.Fx[1,:]).max()/10  
        fC = abs(results.forces.Fx[2,:]).max()/10
        e0 = trapezoid( abs(circuit.current[0,:]*circuit.current[1,:]) + abs(circuit.current[1,:]*circuit.current[2,:]), circuit.T*1e-3)*0.2*1e-6
        print("%5s %5s %5s %5s %5s %5s %5s" % ( "IA_pk",  "IB_pk",  "IC_pk", "E3", "FA_pk", "FB_pk", "FB_pk" ))
        print("%5.0f %5.0f %5.0f %5.3f %5.3f %5.3f %5.3f" % ( circuit.current.max()*circuit.K1ph[0]/1000, circuit.current.max()*circuit.K1ph[1]/1000, circuit.current.max()*circuit.K1ph[2]/1000, e0, fA , fB, fC ))
                    
        presentation.plot(contour, circuit, results, Exit = True)  
        
    circuit = excitation.build(20*1, 101*1, 72, type = "rlc", current="peak")    
    for i in [0, 1, 2]: #, 0.15, 0.2, 0.3
                
        inductances = solution.neumann3d(contour)
        resistances = np.array([80e-6, 80e-6, 80e-6])
        circuit.setBranchImpedance(inductances, resistances)
        results = solution.solve(contour, circuit)
        
        fA = abs(results.forces.Fx[0,:]).max()/10
        fB = abs(results.forces.Fx[1,:]).max()/10  
        fC = abs(results.forces.Fx[2,:]).max()/10    
        e1 = trapezoid( abs(circuit.current[:]*circuit.current[:]*0.5) + abs(circuit.current[:]*circuit.current[:]*0.25), circuit.T*1e-3)*0.2*1e-6

        print("%5s %5s %5s %5s %5s %5s %5s" % ( "IA_pk",  "IB_pk",  "IC_pk", "E3", "FA_pk", "FB_pk", "FB_pk" ))
        print("%5.0f %5.0f %5.0f %5.3f %5.3f %5.3f %5.3f" % ( circuit.current.max()*circuit.K1ph[0]/1000, circuit.current.max()*circuit.K1ph[1]/1000, circuit.current.max()*circuit.K1ph[2]/1000, e1, fA , fB, fC ))
                    
        presentation.plot(contour, circuit, results, Exit = True)  
        contour.setK1ph(np.roll(circuit.K1ph, 1))