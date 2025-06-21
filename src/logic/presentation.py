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



def annot_abs_max(x, f, ax: plt.Axes ):
    (xmax, xmin) = ax.get_xlim()
    (ymax, ymin) = ax.get_ylim()
    C = f.shape[0]
    xa = np.zeros(C)
    ya = np.zeros(C)
    
    for i in range(C):
        y = f[i,:]
        xa[i] = x[np.argmax(abs(y))]
        ya[i] = y[np.argmax(abs(y))]
    imax =  np.argmax(ya)
    imin =  np.argmin(ya)
    mid = abs(ya[i]-ya[imax])<abs(ya[i]-ya[imin])
    for i in range(C):
        text= "{:.3f}| t = {:.3f}".format(ya[i], xa[i])
        fc = mcolors.to_rgba('white')
        fc = fc[:-1] + (0.7,)
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=60")
        kw = dict(xycoords='data',
                textcoords='offset points',
                arrowprops=arrowprops, 
                bbox=bbox_props, 
                ha="right" if i==imin else ( "left" if i==imax else ( "right" if mid else "left" ) ),
                va="bottom" if i==imin else ( "top" if i==imax else ( "bottom" if mid else "top" ) ),
                xytext=(  15 * (-1 if i==imin else ( 1 if i==imax else ( -1 if mid else 1 ) ) )  , 15*(-1 if i==imin else ( 1 if i==imax else ( -1 if mid else 1 ) ) ) ) )
        ax.annotate(text, xy=(xa[i], ya[i]),  **kw )
    
def plotCurrent(e : Excitation, ax : plt.Axes, fig : plt.Figure = None):
    ax.set_xlim([0,e.T[-1]])
    ax.grid(True)
    colors = ['r', 'b', 'g']; labels = ['A', 'B', 'C']
    C = e.I.shape[0]

    for i in range(C):
        ax.plot(e.T, e.I[i,:]/1000 ,colors[i]+'-', linewidth=2.0)
            
    if not fig == None:
        renderer = fig.canvas.get_renderer()
        tick_widths = [
            label.get_window_extent(renderer).width for label in ax.get_yticklabels() if label.get_text()
        ]
        max_tick_width = max(tick_widths) if tick_widths else 0
        labelpad = -max_tick_width-10   # Convert from points to inches
    else:
        labelpad = 0
        
    ax.set_ylabel("ток [кА] ", loc="top", labelpad=labelpad)
    ax.legend(labels[0:C], loc = 'upper right') 
    
    annot_abs_max(e.T, e.I/1000, ax)


def field_colors( M ):
    cmap = mpl.cm.get_cmap('Set1')
    return [ cmap(k) for k in range(M) ]

def force_colors( P, R ):
    cmap_name = ['Reds', 'Blues', 'Greens', 'Greys']
    cmap = mpl.cm.get_cmap(cmap_name[P])      
    return [ cmap(0.33 + 0.66/R/2 + 0.66/R*i ) for i in range(R) ]


def plotGeometry(g : Geometry, ax : plt.Axes):
    M = g.X.shape[0]
    colors = field_colors(M)    
    for x0, y0, z0, nc in zip(g.X, g.Y, g.Z, np.arange(0, M) ):
        ax.plot([x0], [y0], [z0], marker='d', color=colors[nc])
    
    C = 1
    if len(g.NF)>0:            
        [_, nc] = np.meshgrid(np.linspace(1,g.NF.shape[0], g.NF.shape[0])-1  ,g.Nph, indexing='ij')
        nc = nc.reshape(g.NF.shape[0], g.Nph.shape[0])
        N = np.sum(nc*g.NF, axis=1)/np.sum(g.NF, axis=1)    
        N[np.where(np.sum(abs(nc*g.NF - N[:,np.newaxis]*g.NF), axis=1)>0)] = -1
        
        C = int(max(N)-min(N)) + 1
        C0 = int(min(N))
                
        colors = [ force_colors( k+C0 , len(N[N==k+C0]) ) for k in range(C) ]
        
        for i in range(len(N)):        
            c = int(N[i])-C0
            r = int((N[:i]==N[i]).sum())        
            color = colors[c][r]
            for x1, y1, z1, x2, y2, z2, nc, a in zip(g.XS, g.YS, g.ZS, g.XE, g.YE, g.ZE, g.Nph, g.NF[i]):           
                if a:
                    ax.plot([x1, x2], [y1, y2], [z1, z2], color=color, linewidth=9)
    
    for x1, y1, z1, x2, y2, z2, nc, ncprev, ncnext in zip(g.XS, g.YS, g.ZS, g.XE, g.YE, g.ZE, g.Nph, np.concatenate(([-1],g.Nph[:-1])), np.concatenate((g.Nph[1:],[g.Nph[-1]+1])) ):
        color="rbg"[nc%3]
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
  

def plotResults(res: Results):   
    #fields  
    M = res.fields.Bmag.shape[0]   
    if (M>0):
        fig = plt.figure()    
        renderer = fig.canvas.get_renderer()
        
        C = min(3, M)
        
        grid = plt.GridSpec( nrows = 1 + ( M - 1 )// C, ncols = C , wspace=0.3, hspace=0.2, left=0.05, right=0.95, top=0.95, bottom = 0.05)

        colors = field_colors(M)  
        
        labels = ['|B|','Bax','Btr']
        titles = ['A', 'B', 'C']   

        for i in range(M):
            ax = plt.subplot(grid[i//C, i%C])
            ax.set_xlim([0, res.times[-1]])
            
            val_min = min( res.fields.Bax.min(), res.fields.Btr.min()  )*1000
            val_min_dig = np.ceil ( log10(abs(val_min)) )
            val_max = res.fields.Bmag.max()*1000
            val_max_dig = np.ceil ( log10(abs(val_max)) )
            ymin = np.floor( val_min/0.2 )*0.2
            ymax = np.ceil(  val_max/0.2 )*0.2
            
            ax.set_ylim([ymin, ymax]) 
            ax.grid(True)
            ax.set_title(titles[i])
            ax.plot(res.times, res.fields.Bmag[i,:]*1000 ,'-', linewidth=2.0, color = colors[i])
            ax.plot(res.times, res.fields.Bax[i,:]*1000 ,'--', linewidth=2.0, color = colors[i])
            ax.plot(res.times, res.fields.Btr[i,:]*1000 ,':', linewidth=2.0, color = colors[i])
            

            tick_widths = [
                label.get_window_extent(renderer).width for label in ax.get_yticklabels() if label.get_text()
            ]
            max_tick_width = max(tick_widths) if tick_widths else 0
            labelpad = -max_tick_width-10   # Convert from points to inches
            
            ax.set_ylabel("поле [мТл] ", loc="top", labelpad=labelpad); 
            ax.legend(labels, loc = 'lower right')   
            
            annot_abs_max(res.times, np.vstack((res.fields.Bmag[i,:], res.fields.Bax[i,:], res.fields.Btr[i,:]))*1000, ax) 
            # annot_abs_max(res.times, [np.newaxis,:]*1000, ax) 
            # annot_abs_max(res.times, [np.newaxis,:]*1000, ax) 
            
        window = plt.get_current_fig_manager().window
        screen_x, screen_y = window.wm_maxsize()
        fig.set_size_inches([screen_x/2/fig.dpi, screen_y/2/fig.dpi]) 
        window.wm_geometry("+0+0")
                
        fig.show()
       
    #forces    
    
    M = res.forces.N.shape[0]  
    if (M>0): 
        fig = plt.figure()    
        renderer = fig.canvas.get_renderer()
        
        N = res.forces.N
        C = int(max(N)-min(N)) + 1
        C0 = int(min(N))
        R = max( [ len(N[N==k+C0]) for k in range(C) ]  )
        
        grid = plt.GridSpec( nrows = R, ncols = C , wspace=0.3, hspace=0.2, left=0.05, right=0.95, top=0.95, bottom = 0.05)
            
        colors = [ force_colors( k+C0 , len(N[N==k+C0]) ) for k in range(C) ]
                
        labels = ['x','y','z']    
            
        for i in range(len(N)):
            c = int(N[i])-C0
            r = int((N[:i]==N[i]).sum())
            
            color = colors[c][r]
            ax = plt.subplot(grid[ r, c ])
            ax.set_xlim([0,res.times[-1]])
            
            ymin = np.floor( min( res.forces.Fx.min(), res.forces.Fy.min(), res.forces.Fz.min()  )*10 )/100
            ymax = np.ceil( max( res.forces.Fx.max(), res.forces.Fy.max(), res.forces.Fz.max()  )*10 )/100
            
            ax.set_ylim([ymin, ymax])
            
            ax.grid(True)
            ax.plot(res.times, res.forces.Fx[i,:]/10 ,'-', linewidth=2.0, color=color)
            ax.plot(res.times, res.forces.Fy[i,:]/10 ,'--', linewidth=2.0, color=color)
            ax.plot(res.times, res.forces.Fz[i,:]/10 ,':', linewidth=2.0, color=color)
            
            tick_widths = [
                label.get_window_extent(renderer).width for label in ax.get_yticklabels() if label.get_text()
            ]
            max_tick_width = max(tick_widths) if tick_widths else 0
            labelpad = -max_tick_width-10   # Convert from points to inches
            
            ax.set_ylabel("сила [кгс] ", loc="top", labelpad=labelpad); 
            
            ax.legend(labels, loc = 'lower right')    
            
            annot_abs_max(res.times, np.vstack((res.forces.Fx[i,:], res.forces.Fy[i,:], res.forces.Fz[i,:]))/10, ax) 
            
        window = plt.get_current_fig_manager().window
        screen_x, screen_y = window.wm_maxsize()
        fig.set_size_inches([screen_x/2/fig.dpi, screen_y/2/fig.dpi]) 
        window.wm_geometry("+0+0")
            
        fig.show()
        
        