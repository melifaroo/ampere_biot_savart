import numpy as np
import colorsys
import matplotlib as mpl
import matplotlib.colors as mcolors
mpl.rcParams['axes3d.mouserotationstyle'] = 'trackball' # , 'trackball', 'azel', 'sphere', or 'arcball'
    
import matplotlib.pyplot as plt
from numpy import log10
from logic.geometry import Geometry
from logic.excitation import Excitation
from logic.solution import Results

def change_lightness(color, lightness=0.5):    
    """"
    Set the lightness of a given color.    
   
    Returns:
        tuple: The adjusted RGB color as a tuple.
    """
    # Convert the color to RGB
    try:
        c = mcolors.cnames[color]  # Handle named colors like 'red'
    except KeyError:
        c = color  # Assume it's already a valid color
    rgb = mcolors.to_rgb(c)  # Convert to RGB

    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(*rgb)

    # Adjust the lightness
    l = max(0, min(1, lightness))  # Ensure lightness stays in [0, 1]

    # Convert HLS back to RGB
    adjusted_rgb = colorsys.hls_to_rgb(h, l, s)
    return adjusted_rgb



def plotCurrent(e : Excitation, ax : plt.axes.__class__, fig : plt.figure.__class__ = None):
    plt.xlim([0,e.T[-1]])
    plt.grid(True)
    colors = ['r', 'b', 'g']; labels = ['A', 'B', 'C']
    C = e.I.shape[0]

    for i in range(C):
        plt.plot(e.T, e.I[i,:]/1000 ,colors[i]+'-', linewidth=2.0)
            
    if not fig == None:
        renderer = fig.canvas.get_renderer()
        tick_widths = [
            label.get_window_extent(renderer).width for label in ax.get_yticklabels() if label.get_text()
        ]
        max_tick_width = max(tick_widths) if tick_widths else 0
        labelpad = -max_tick_width-10   # Convert from points to inches
    else:
        labelpad = 0
        
    plt.ylabel("ток [кА] ", loc="top", labelpad=labelpad)
    plt.legend(labels[0:C], loc = 'upper right') 

def plotGeometry(g : Geometry, ax : plt.axes.__class__):
    colors = ['m', 'c', 'y']    
    for x0, y0, z0, nc in zip(g.X, g.Y, g.Z, np.arange(0, g.X.shape[0]) ):
        ax.plot([x0], [y0], [z0], marker='d', color=colors[nc%3])
        
    C = 1 + g.Nph.max()
    colors = ['r', 'b', 'g']
    i = 0
    for nf in g.NF:
        for x1, y1, z1, x2, y2, z2, nc, a in zip(g.XS, g.YS, g.ZS, g.XE, g.YE, g.ZE, g.Nph, nf):           
            if a:
                lightness=(1 + i%(g.NF.shape[0]//C))/(1 + g.NF.shape[0]//C); 
                color=change_lightness(colors[nc%3], lightness=lightness)
                ax.plot([x1, x2], [y1, y2], [z1, z2], color=color, linewidth=9)
        i=i+1
    
    for x1, y1, z1, x2, y2, z2, nc, ncprev, ncnext in zip(g.XS, g.YS, g.ZS, g.XE, g.YE, g.ZE, g.Nph, np.concatenate(([-1],g.Nph[:-1])), np.concatenate((g.Nph[1:],[g.Nph[-1]+1])) ):
        color=change_lightness(colors[nc%3], lightness=0.5)
        ax.plot([x1, x2], [y1, y2], [z1, z2], marker='o', color='k', linewidth=1, markersize = 3)
        size = ( np.diff(ax.get_xlim())**2 +  np.diff(ax.get_xlim())**2 +  np.diff(ax.get_xlim())**2)**0.5
        if(ncprev%C!=nc%C):
            ax.quiver(x1, y1, z1, (x2-x1), (y2-y1), (z2-z1), color=color, pivot="tail", normalize=True, length = size[0]/5)       
        if(ncnext%C!=nc%C):
            ax.quiver(x2, y2, z2, (x2-x1), (y2-y1), (z2-z1), color=color, pivot="tip", normalize=True, length = size[0]/5)
    
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.view_init( elev=20, azim=-60, vertical_axis="y"  )
    #ax.set_aspect('equal') 
  

def plotResults(r: Results, fig : plt.figure.__class__ = None, grid = None, C = 3, first_col = 0  ):    
    if not fig == None:
        renderer = fig.canvas.get_renderer()
            
    M = r.fields.Bmag.shape[0]    
    N = r.forces.Fx.shape[0]  
     
    if grid == None:    
        grid = plt.GridSpec(max(3, (M + C - 1) // C + (N + C - 1) // C ),2+C, wspace=0.3, hspace=0.2, left=0.05, right=0.95, top=0.95, bottom = 0.05)
                
    #fields 
    colors = ['m', 'c', 'y']
    labels = ['|B|','Bax','Btr']
    titles = ['A', 'B', 'C']   

    for i in range(M):
        ax = plt.subplot(grid[i%(M//C),first_col + i//(M//C)])
        plt.xlim([0, r.times[-1]])
        
        val_min = min( r.fields.Bax.min(), r.fields.Btr.min()  )*1000
        val_min_dig = np.ceil ( log10(abs(val_min)) )
        val_max = r.fields.Bmag.max()*1000
        val_max_dig = np.ceil ( log10(abs(val_max)) )
        ymin = np.floor( val_min/0.2 )*0.2
        ymax = np.ceil(  val_max/0.2 )*0.2
        
        plt.ylim([ymin, ymax]) 
        plt.grid(True)
        plt.title(titles[i])
        plt.plot(r.times, r.fields.Bmag[i,:]*1000 ,colors[i%3]+'-', linewidth=2.0)
        plt.plot(r.times, r.fields.Bax[i,:]*1000 ,colors[i%3]+'--', linewidth=2.0)
        plt.plot(r.times, r.fields.Btr[i,:]*1000 ,colors[i%3]+':', linewidth=2.0)
        

        tick_widths = [
            label.get_window_extent(renderer).width for label in ax.get_yticklabels() if label.get_text()
        ]
        max_tick_width = max(tick_widths) if tick_widths else 0
        labelpad = -max_tick_width-10   # Convert from points to inches

        
        plt.ylabel("поле [мТл] ", loc="top", labelpad=labelpad); 
        plt.legend(labels, loc = 'lower right')    
                      
    #forces 
    labels = ['x','y','z']    
    colors = ['r', 'b', 'g']       
    for i in range(N):
        j = (M + C - 1) // C + i%(N//C)
        c = i//(N//C)
        
        lightness=( i%(N//C)+1 )/(1 + N//C)
        color=change_lightness(colors[c%3], lightness=lightness)
        ax = plt.subplot(grid[j, 2 + c ])
        plt.xlim([0,r.times[-1]])
        
        ymin = np.floor( min( r.forces.Fx.min(), r.forces.Fy.min(), r.forces.Fz.min()  )*10 )/100
        ymax = np.ceil( max( r.forces.Fx.max(), r.forces.Fy.max(), r.forces.Fz.max()  )*10 )/100
        
        plt.ylim([ymin, ymax])
        
        plt.grid(True)
        plt.plot(r.times, r.forces.Fx[i,:]/10 ,'-', linewidth=2.0, color=color)
        plt.plot(r.times, r.forces.Fy[i,:]/10 ,'--', linewidth=2.0, color=color)
        plt.plot(r.times, r.forces.Fz[i,:]/10 ,':', linewidth=2.0, color=color)
        
        tick_widths = [
            label.get_window_extent(renderer).width for label in ax.get_yticklabels() if label.get_text()
        ]
        max_tick_width = max(tick_widths) if tick_widths else 0
        labelpad = -max_tick_width-10   # Convert from points to inches
        
        plt.ylabel("сила [кгс] ", loc="top", labelpad=labelpad); 
        
        plt.legend(labels, loc = 'lower right')    
        
def plot(g : Geometry, e: Excitation, r: Results, Exit = True ):    

    fig = plt.figure()#figsize=[screen_x/96, screen_y/96])#[height, height*((np.sqrt(5)-1.0)/2.0)] 
    
    C = 1 + g.Nph.max()    
    
    M = r.fields.Bmag.shape[0]    
    N = r.forces.Fx.shape[0]       
    grid = plt.GridSpec(max(3, (M + C - 1) // C + (N + C - 1) // C ),2+C, wspace=0.3, hspace=0.2, left=0.05, right=0.95, top=0.95, bottom = 0.05)
            
    ax = plt.subplot(grid[0:-1,0:2], projection='3d')      
    plotGeometry(g, ax)
    
    ax = plt.subplot(grid[-1,0:2])
    plotCurrent(e, ax, fig)   
    
    plotResults(r, ax, fig, grid, C, 2 )              
    
    # figManager.window.state('normal')# normal, iconic, withdrawn, or zoomed
    window = plt.get_current_fig_manager().window
    screen_x, screen_y = window.wm_maxsize()
    fig.set_size_inches([screen_x/fig.dpi, screen_y/fig.dpi-3]) 
    window.wm_geometry("+0+0")
    
    plt.show(block=not Exit)

def plotetwas():
    fig = plt.figure()

    FA = [ 
        [0.96,	1.05,	1.09,	1.12,	1.16],
        [0.97,	1.07,	1.11,	1.14,	1.18],
        [0.99,	1.09,	1.13,	1.16,	1.20],
        [1.006,	1.11,	1.15,	1.18,	1.22],
        [1.025,	1.13,	1.17,	1.20,   1.23],
        [1.04,	1.14,	1.19,	1.22,	1.25],
        [1.05,	1.16,	1.21,	1.24,	1.27],
    ]
    FB = [ 
        [0.90,	0.99,	1.03,	1.06,	1.09],
        [0.94,	1.03,	1.06,	1.09,	1.13],
        [0.96,	1.06,	1.10,   1.13,	1.16],
        [0.98,	1.08,	1.13,	1.16,	1.19],
        [1.01,	1.11,	1.15,	1.19,	1.22],
        [1.035,	1.14,	1.18,	1.21,	1.25],
        [1.05,	1.16,	1.21,	1.24,	1.28]
    ]
    BA =[
        [1.00,	1.04,	1.06,	1.07,	1.09],
        [0.99,	1.03,	1.05,	1.065,	1.08],
        [0.98,	1.025,	1.045,	1.06,	1.075],
        [0.975,	1.02,	1.04,	1.055,	1.07],
        [0.97,	1.015,	1.033,	1.05,	1.06],
        [0.965,	1.01,	1.025,	1.04,	1.055],
        [0.955,	1.00,	1.02,	1.035,	1.05]        
    ]

    BB = [
        [0.97,	1.01,	1.03,	1.04,	1.05],
        [0.96,	1.00,	1.02,	1.03,	1.04],
        [0.95,	0.99,	1.01,	1.02,	1.03],
        [0.94,	0.98,	1.00,	1.01,	1.025],
        [0.93,	0.97,	0.99,	1.00,	1.02],
        [0.92,	0.96,	0.98,	0.99,	1.01],
        [0.91,	0.95,	0.97,	0.98,	1.00],
    ]
    BAax = [ 
        [0.985,	1.03,	1.05,	1.07,	1.08],
        [0.99,	1.04,	1.06,	1.08,	1.09],
        [1.00,	1.05,	1.07,	1.085,	1.10],
        [1.005,	1.055,	1.08,	1.09,	1.105],
        [1.01,	1.06,	1.08,	1.10,	1.11],
        [1.015,	1.065,	1.09,	1.10,	1.12],
        [1.02,	1.07,	1.09,	1.11,	1.13],
    ]

    BBax = [
        [0.92,	0.96,	0.98,	1.00,	1.01],
        [0.905,	0.95,	0.965,	0.98,	0.99],
        [0.89,	0.93,	0.95,	0.96,	0.98],
        [0.87,	0.915,	0.93,	0.95,	0.96],
        [0.86,	0.90,	0.92,	0.93,	0.94],
        [0.84,	0.88,	0.90,	0.91,	0.93],
        [0.83,	0.87,	0.89,	0.90,	0.91],
    ]
         
    grid = plt.GridSpec( 3 , 2, wspace=0.3, hspace=0.3, left=0.1, right=0.9, top=0.9, bottom = 0.1)

           
    plt.subplot(grid[0,0]); 
    plt.plot( [0, 8], [1, 1], color='red', linewidth=2.0); plt.xlim([1,7])
    # bp = plt.boxplot(FA);     for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']: plt.setp(bp[element], color="lightgray")
    data = FA    
    plt.plot( [2, 2], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [4, 4], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][0], data[6][0] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.plot( [1, 7], [ data[0][1], data[6][1] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][2], data[6][2] ], color='black', linewidth=2.0 , linestyle='-')
    plt.plot( [1, 7], [ data[0][3], data[6][3] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][4], data[6][4] ], color='blue', linewidth=1.0 , linestyle=':')
    
    plt.xticks([1,2,3,4,5,6,7], ["0", "5%", "10%", "15%", "20%", "25%", "30%"]); plt.grid(True); plt.title("А"); plt.ylim([0.9, 1.3]); plt.ylabel("Сила на полюс")
    
    plt.subplot(grid[0,1]); 
    plt.plot( [0, 8], [1, 1], color='red', linewidth=2.0); plt.xlim([1,7])
    # bp = plt.boxplot(FB);        for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']: plt.setp(bp[element], color="lightgray")
    data = FB
    plt.plot( [2, 2], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [4, 4], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][0], data[6][0] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.plot( [1, 7], [ data[0][1], data[6][1] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][2], data[6][2] ], color='black', linewidth=2.0 , linestyle='-')
    plt.plot( [1, 7], [ data[0][3], data[6][3] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][4], data[6][4] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.xticks([1,2,3,4,5,6,7], ["0", "5%", "10%", "15%", "20%", "25%", "30%"]); plt.grid(True); plt.title("B"); plt.ylim([0.9, 1.3])
    
    plt.subplot(grid[1,0]); 
    plt.plot( [0, 8], [1, 1], color='red', linewidth=2.0); plt.xlim([1,7])
    # bp = plt.boxplot(BA);     for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']: plt.setp(bp[element], color="lightgray")
    data = BA
    plt.plot( [2, 2], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [4, 4], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][0], data[6][0] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.plot( [1, 7], [ data[0][1], data[6][1] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][2], data[6][2] ], color='black', linewidth=2.0 , linestyle='-')
    plt.plot( [1, 7], [ data[0][3], data[6][3] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][4], data[6][4] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.xticks([1,2,3,4,5,6,7], ["0", "5%", "10%", "15%", "20%", "25%", "30%"]); plt.grid(True); plt.title("A"); plt.ylim([0.9, 1.1]); plt.ylabel("Поле в приводе")
    
    plt.subplot(grid[1,1]); 
    plt.plot( [0, 8], [1, 1], color='red', linewidth=2.0); plt.xlim([1,7])
    # bp = plt.boxplot(BB);     for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']: plt.setp(bp[element], color="lightgray")
    data = BB
    plt.plot( [2, 2], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [4, 4], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][0], data[6][0] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.plot( [1, 7], [ data[0][1], data[6][1] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][2], data[6][2] ], color='black', linewidth=2.0 , linestyle='-')
    plt.plot( [1, 7], [ data[0][3], data[6][3] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][4], data[6][4] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.xticks([1,2,3,4,5,6,7], ["0", "5%", "10%", "15%", "20%", "25%", "30%"]); plt.grid(True); plt.title("B"); plt.ylim([0.9, 1.1])
    
    plt.subplot(grid[2,0]); 
    plt.plot( [0, 8], [1, 1], color='red', linewidth=2.0); plt.xlim([1,7])
    # bp = plt.boxplot(BAax) ;     for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']: plt.setp(bp[element], color="lightgray")   
    data = BAax
    plt.plot( [2, 2], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [4, 4], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][0], data[6][0] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.plot( [1, 7], [ data[0][1], data[6][1] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][2], data[6][2] ], color='black', linewidth=2.0 , linestyle='-')
    plt.plot( [1, 7], [ data[0][3], data[6][3] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][4], data[6][4] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.xticks([1,2,3,4,5,6,7], ["0", "5%", "10%", "15%", "20%", "25%", "30%"]); plt.grid(True); plt.title("A"); plt.ylim([0.8, 1.2]); plt.ylabel("Осевое поле в приводе")
    
    plt.subplot(grid[2,1]); 
    plt.plot( [0, 8], [1, 1], color='red', linewidth=2.0); plt.xlim([1,7])
    # bp = plt.boxplot(BBax);     for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']: plt.setp(bp[element], color="g")
    data = BBax
    plt.plot( [2, 2], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [4, 4], [0.8, 1.3], color='red', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][0], data[6][0] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.plot( [1, 7], [ data[0][1], data[6][1] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][2], data[6][2] ], color='black', linewidth=2.0 , linestyle='-')
    plt.plot( [1, 7], [ data[0][3], data[6][3] ], color='blue', linewidth=1.0 , linestyle='--')
    plt.plot( [1, 7], [ data[0][4], data[6][4] ], color='blue', linewidth=1.0 , linestyle=':')
    plt.xticks([1,2,3,4,5,6,7], ["0", "5%", "10%", "15%", "20%", "25%", "30%"]); plt.grid(True); plt.title("B"); plt.ylim([0.8, 1.2])
    
    
    window = plt.get_current_fig_manager().window
    screen_x, screen_y = window.wm_maxsize()
    fig.set_size_inches([screen_x/fig.dpi, screen_y/fig.dpi-3]) 
    window.wm_geometry("+0+0")
    plt.show()