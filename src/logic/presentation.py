import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from geometry import Geometry
from exitation import Exitation
from solution import Results

# def plotgeometry(g : Geometry):
    # plt.grid(True); plt.ylabel("ток [А]"); 
    # X0 = np.append(g.XS, g.XE[-1])
    # Y0 = np.append(g.YS, g.YE[-1])
    # Z0 = np.append(g.ZS, g.ZE[-1])
    # ax.plot( [g.XS, g.XE], [g.YS, g.YE], zs = [g.ZS, g.ZE])
    # plot3( LP*ones(1,seg+1), Y0, Z0, 'r.', 'MarkerSize', 20);
    # plot3( -0*ones(1,seg+1), Y0, Z0, 'b', 'LineWidth', 3);
    # plot3( -0*ones(1,seg+1), Y0, Z0, 'b.', 'MarkerSize', 20);
    # plot3(-LP*ones(1,seg+1), Y0, Z0, 'g', 'LineWidth', 3);
    # plot3(-LP*ones(1,seg+1), Y0, Z0, 'g.', 'MarkerSize', 20);
    # plot3([-LP, 0, LP], [0, 0 ,0], [0, 0 ,0], 'm.', 'MarkerSize', 50);
    # view([-1,1,1]);daspect([1 1 1]);

    # camup([0,1,0])


    # xlim([-LP, LP]); xlabel('X');
    # ylim([0, 1.5*max(Y0)]); ylabel('Y');
    # zlim([0, LX]);  zlabel('Z');
         
def plot(g : Geometry, e: Exitation, r: Results):    

    plt.figure() 
    
    M = r.fields.Bmag.shape[0]
       
       
    ax = plt.subplot(M+1, 2, 1, projection='3d')
        
    ax.plot( [g.XS, g.XE], [g.YS, g.YE], zs = [g.ZS, g.ZE])
    
    plt.subplot(M+1, 2, M+2); plt.xlim([0,e.T[-1]]); plt.grid(True); plt.ylabel("ток [А]");
    colors = ['r', 'b', 'g']; labels = ['A', 'B', 'C']
    for i in range(e.I.shape[0]):
        plt.plot(e.T, e.I[i,:] ,colors[i]+'-', linewidth=2.0)
    plt.legend(labels[0:e.I.shape[0]], loc = 'upper right')    
    
    #fields 
    colors = ['r', 'b', 'g']; labels = ['|B|','Bz','Bt']; titles = ['A', 'B', 'C']   
    for i in range(M):
        plt.subplot(M+1, 2, M+2+i); plt.xlim([0,e.T[-1]]); plt.grid(True); plt.title(titles[i]); plt.ylabel("поле [Тл]"); 
        plt.plot(e.T, r.fields.Bmag[i,:] ,colors[i]+'-', linewidth=2.0)
        plt.plot(e.T, r.fields.Bax[i,:] ,colors[i]+'--', linewidth=2.0)
        plt.plot(e.T, r.fields.Btr[i,:] ,colors[i]+':', linewidth=2.0)
        plt.legend(labels, loc = 'upper right')    
        
    plt.show()
    
    plt.figure() 
    
    M = r.forces.Fx.shape[0]
    
    plt.subplot(M+1, 2, 1); 
    
    
    plt.subplot(M+1, 2, M+2); plt.xlim([0,e.T[-1]]); plt.grid(True); plt.ylabel("ток [А]");
    colors = ['r', 'b', 'g']; labels = ['A', 'B', 'C']
    for i in range(e.I.shape[0]):
        plt.plot(e.T, e.I[i,:] ,colors[i]+'-', linewidth=2.0)
    plt.legend(labels[0:e.I.shape[0]], loc = 'upper right')    
    
    #forces 
    labels = ['x','y','z'];  
    for i in range(M):
        plt.subplot(M+1, 2, M+2+i); plt.xlim([0,e.T[-1]]); plt.grid(True); plt.ylabel("поле [Тл]"); 
        plt.plot(e.T, r.forces.Fx[i,:] ,'k-', linewidth=2.0)
        plt.plot(e.T, r.forces.Fy[i,:] ,'k--', linewidth=2.0)
        plt.plot(e.T, r.forces.Fz[i,:] ,'k:', linewidth=2.0)
        plt.legend(labels, loc = 'upper right')    
        
    plt.show()
