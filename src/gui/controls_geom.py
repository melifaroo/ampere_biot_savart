from typing import Final
from tkinter import Frame, Label, Entry, Button, StringVar, BooleanVar, OptionMenu, Checkbutton, messagebox, filedialog
from tkinter import ttk 
import os.path

from utils.formats import str2flt, str2int, str_to_int_arr, str_to_flt_arr, float_array_input_validate, int_array_input_validate, nonzero_float_input_validate, flt_arr_to_str, int_arr_to_str

import numpy as np
import logic.geometry as geometry

class ControlGeomPanel(Frame):
    
    GEOM_ENTRY_WIDTH : Final[int] = 150
    
    MAX_FORCE_PER_PHASE : Final[int] = 6
    STATUS_OK : Final = "Geometry is OK!"
    STATUS_ERROR : Final = "Geometry contains errors!"
    GEOM_VAR_NAME : Final = 'GEOM'
    FLD_VAR_NAME : Final = 'FLD'
    FORC_VAR_NAME : Final = 'FORC'
    RADIUS_VAR_NAME: Final = 'RAD'
    SAME_VAR_NAME : Final = 'SamePolesGeom'
    POLEDIST_VAR_NAME : Final = 'LP'
    PHASE_COUNT_VAR_NAME: Final = 'PhaseCount'
    
    error_message = ""
    status = STATUS_OK
            
    def __init__(self, master, app, update_plot_callback):
        super().__init__(master)
        self.app = app
        self.update_plot_callback = update_plot_callback
        
        self.init()
        self.load()                
        self.create()
        self.update()

    def create(self):
        
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        
        Label(self, text="Phase Count:").grid(row=0, column=0)
        self.phase_count_menu = OptionMenu(self, self.phase_count_var, "1", "2", "3", command=self.on_change)
        self.phase_count_menu.grid(row=0, column=1)
        
        self.same_check = Checkbutton(self, variable=self.same_var, text="Same geometry of all phases",  command=self.update_plot)
        self.same_check.grid(row=0, column = 2,  sticky="W"  )
                
                
        Label(self, text="Pole Distance [m]:").grid(row=0, column=3)
        self.poledist_entry = Entry(self, textvariable=self.poledist_var, justify="left")
        self.poledist_entry.grid(row=0, column=4)
        self.poledist_entry.bind("<KeyRelease>", self.on_change)
        self.poledist_entry.config(validate="key", validatecommand=(self.register(nonzero_float_input_validate), '%P'))
        
        self.error_btn = Button(self, text="LOAD", command=self.load_file)
        self.error_btn.grid(row=0, column=5)
        
        self.error_btn = Button(self, text="SAVE", command=self.save_file)
        self.error_btn.grid(row=0, column=6)
        
        self.error_btn = Button(self, text="OK", background="green", command=self.show_errors)
        self.error_btn.grid(row=0, column=7)
       
        self.geom_entry = [None]*3*3
        self.forc_entry = [None]*3*M
        self.fld_entry = [None]*3*3
        self.radius_entry = [None]*3
        self.forc_segs_entry = [None]*3*M
                        
        self.tabControl = ttk.Notebook(self)         
        self.tabControl.grid(row = 1, column = 0, columnspan = 8)
        
        for i in range(3):
            
            tab = Frame(self.tabControl) 
            self.tabControl.add(tab, text = "ABC"[i]) 
            self.tabControl.tab(0, state = "normal" if i<str2int(self.phase_count_var.get()) else "disabled")
            Label( tab, text="geometry points (N):").grid(row = 0, column=1) 
            
            Label( tab, text="field points:").grid(row = 0, column=2) 
            
            Label( tab, text="segments (effective) radius:").grid(row = 4, column=1) 
            
            Label( tab, text= "r, [cm]" ).grid(row = 5, column=0)
            self.radius_entry[i] = Entry(tab, textvariable = self.radius_var[i], width=self.GEOM_ENTRY_WIDTH, font=("Consolas",10) , state = "disabled" if (self.same_var.get() and i>0) else "normal" ) 
            self.radius_entry[i].grid(row=5, column=1)
            self.radius_entry[i].bind("<FocusOut>",  lambda event, i=i: ( self.on_segments_radius_change(event, i) ) )
            self.radius_entry[i].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
            
            Label( tab, text= "segments (N-1) to compute force:" ).grid(row = 6, column=1)
            
            for j in range(M):
                self.forc_entry[i*M+j] = Entry(tab, textvariable = self.forc_var[i*M+j], width=self.GEOM_ENTRY_WIDTH, font=("Consolas",10) , state = "disabled" if ((self.same_var.get() and i>0) or not (self.forc_segs_var[i*M+j].get())) else "normal" ) 
                self.forc_entry[i*M+j].grid(row=7+j, column=1)
                self.forc_entry[i*M+j].bind("<FocusOut>",  lambda event, i=i, j=j: ( self.on_force_segments_change(event, i, j) ) )
                self.forc_entry[i*M+j].config(validate="key", validatecommand=(self.register(int_array_input_validate), '%P'))

                self.forc_segs_entry[i*M+j] = Checkbutton(tab, variable=self.forc_segs_var[i*M+j], state = "normal" if ( not (self.same_var.get() and i>0) ) else "disabled" ,  command=self.update_plot ) 
                self.forc_segs_entry[i*M+j].grid(row=7+j, column=0)
                
            for j in range(3):
                Label( tab, text= "XYZ"[j] + " [m]" ).grid(row = 1+j, column=0)
                
                self.geom_entry[i*3+j] = Entry(tab, textvariable = self.geom_var[i*3+j], width=self.GEOM_ENTRY_WIDTH, font=("Consolas",10) , state = "disabled" if (self.same_var.get() and i>0) else "normal" ) 
                self.geom_entry[i*3+j].grid(row=1+j, column=1)
                self.geom_entry[i*3+j].bind("<FocusOut>",  lambda event, i=i, j=j: ( self.on_geom_change(event, i, j) ) )
                self.geom_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
                
                self.fld_entry[i*3+j] = Entry(tab, textvariable = self.fld_var[i*3+j], width=15, font=("Consolas",10) , state = "disabled" if (self.same_var.get() and i>0) else "normal" ) 
                self.fld_entry[i*3+j].grid(row=1+j, column=2)
                self.fld_entry[i*3+j].bind("<FocusOut>",  lambda event, i=i, j=j: ( self.on_geom_change(event, i, j) ) )
                self.fld_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
                
                
    def update(self):        
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        N = str2int(self.phase_count_var.get())
        self.poledist_entry.config(state = "normal" if self.same_var.get() else "disabled")
        for i in range(3):
            self.tabControl.tab(i, state = "normal" if i<N else "disabled")
            
            if self.same_var.get():  
                RAD = np.array( str_to_flt_arr(self.radius_var[0].get()) )      
                self.radius_var[i].set( flt_arr_to_str(RAD) ) 
                
            for j in range(3):
                if self.same_var.get():                    
                    XYZ = np.array( str_to_flt_arr(self.geom_var[0*3+j].get()) )  + str2flt(self.poledist_var.get())*i*(j==0)       
                    self.geom_var[i*3+j].set( flt_arr_to_str(XYZ) )    
                    FLD = np.array( str_to_flt_arr(self.fld_var[0*3+j].get()) )  + str2flt(self.poledist_var.get())*i*(j==0)       
                    self.fld_var[i*3+j].set( flt_arr_to_str(FLD) )  
                    
                self.geom_entry[i*3+j].config( state = "disabled" if (self.same_var.get() and i>0) else "normal" )
                
            for j in range(M):
                if self.same_var.get():                                   
                    FRC = np.array( str_to_int_arr(self.forc_var[0*M+j].get()) )       
                    self.forc_var[i*M+j].set( int_arr_to_str(FRC) ) 
                    self.forc_segs_var[i*M+j].set(self.forc_segs_var[0*M+j].get())
                    
                self.forc_segs_entry[i*M+j].config(state = "normal" if ( not (self.same_var.get() and i>0) ) else "disabled")
                self.forc_entry[i*M+j].config(state = "disabled" if ((self.same_var.get() and i>0) or not (self.forc_segs_var[i*M+j].get())) else "normal")
        
        if self.check():
            self.geometry = geometry.sample_input(
                XA = str_to_flt_arr(self.geom_var[0*3+0].get()) , 
                YA = str_to_flt_arr(self.geom_var[0*3+1].get()) , 
                ZA = str_to_flt_arr(self.geom_var[0*3+2].get()) , 
                XB = str_to_flt_arr(self.geom_var[1*3+0].get()) if N>1 else [0] , 
                YB = str_to_flt_arr(self.geom_var[1*3+1].get()) if N>1 else [0] , 
                ZB = str_to_flt_arr(self.geom_var[1*3+2].get()) if N>1 else [0], 
                XC = str_to_flt_arr(self.geom_var[2*3+0].get()) if N>2 else [0] , 
                YC = str_to_flt_arr(self.geom_var[2*3+1].get()) if N>2 else [0] , 
                ZC = str_to_flt_arr(self.geom_var[2*3+2].get()) if N>2 else [0] ,                 
                RA = str_to_flt_arr(self.radius_var[0].get(), 0.01), 
                RB = str_to_flt_arr(self.radius_var[1].get(), 0.01) if N>1 else [] , 
                RC = str_to_flt_arr(self.radius_var[2].get(), 0.01) if N>2 else [] ,  
                NFA = [ str_to_int_arr(self.forc_var[0*M+i].get()) for i in range(M) if self.forc_segs_var[0*M+i].get() ],
                NFB = [ str_to_int_arr(self.forc_var[1*M+i].get()) for i in range(M) if self.forc_segs_var[1*M+i].get() ] if N>1 else [],
                NFC = [ str_to_int_arr(self.forc_var[2*M+i].get()) for i in range(M) if self.forc_segs_var[2*M+i].get() ] if N>2 else []  ,
                X = np.concatenate([
                    str_to_flt_arr(self.fld_var[0*3+0].get()) , 
                    str_to_flt_arr(self.fld_var[1*3+0].get()) if N>1 else [],
                    str_to_flt_arr(self.fld_var[2*3+0].get()) if N>2 else []]) ,
                Y = np.concatenate([
                    str_to_flt_arr(self.fld_var[0*3+1].get()) , 
                    str_to_flt_arr(self.fld_var[1*3+1].get()) if N>1 else [],
                    str_to_flt_arr(self.fld_var[2*3+1].get()) if N>2 else [] ]) , 
                Z = np.concatenate([
                    str_to_flt_arr(self.fld_var[0*3+2].get()) , 
                    str_to_flt_arr(self.fld_var[1*3+2].get()) if N>1 else [],
                    str_to_flt_arr(self.fld_var[2*3+2].get()) if N>2 else [] ]),
                
                )     
            return True
        else:
            return False         
                
    def update_plot(self):     
        if self.update():
            self.update_plot_callback(self.geometry)
            self.app.control_exct_panel.update_plot()
        else:
            self.update_plot_callback(None)
       
    def check(self):
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        P = str2int(self.phase_count_var.get())
        result = True
        self.error_message = ""
        
        for i in range(P):
            check1 = True
            check2 = True
            check3 = True
            
            N = -1
            NN = -1
            
            if (N==-1):
                N = len(self.radius_var[i].get().split(","))+1
                
            for j in range(M):            
                if (N==-1 and self.forc_segs_var[i*M+j].get() ):
                    N = len(self.forc_var[i*M+j].get().split(","))+1
                if not (len(self.forc_var[i*M+j].get().split(","))==N-1) and self.forc_segs_var[i*M+j].get() :
                    check1 = False   
                                     
            for j in range(3):
                if N==-1:            
                    N = len(self.geom_var[i*3+j].get().split(","))
                if NN==-1:            
                    NN = len(self.fld_var[i*3+j].get().split(","))
                if not (len(self.geom_var[i*3+j].get().split(","))==N):
                    check1 = False
                if not (len(self.fld_var[i*3+j].get().split(","))==NN):
                    check2 = False
               
            if (check1):
                X = np.array( str_to_flt_arr(self.geom_var[i*3+0].get()) )
                Y = np.array( str_to_flt_arr(self.geom_var[i*3+1].get()) )
                Z = np.array( str_to_flt_arr(self.geom_var[i*3+2].get()) )
                dX = np.diff(X)
                dY = np.diff(Y)
                dZ = np.diff(Z)
                dL = (dX**2 + dY**2 + dZ**2)**0.5
                dD = dL - abs(dX) - abs(dY) - abs(dZ)
                check3 =not ( any(dL == 0) or any( dD != 0) )
                
                    
            color1 = "pink" if not check1 else "white"
            color2 = "pink" if not check2 else "white"
            color3 = "pink" if not (check1 and check3) else "white"
            
            self.radius_entry[i].config(background = color1)
            for j in range(M):        
                self.forc_entry[i*M+j].config(background = color1)
            for j in range(3):    
                self.geom_entry[i*3+j].config(background = color3)
                self.fld_entry[i*3+j].config(background = color2)
                
            result = result*check1*check2*check3
            
        if not result:
            self.status = self.STATUS_ERROR
            self.error_message = "Dimension must agree!" if not (check1 and check2) else "Only segments along the axis (horizontal or vertical) allowed!"
            self.error_btn.config(text="ERROR", background="red")
        else:            
            self.status = self.STATUS_OK
            self.error_btn.config(text="OK", background="green")
            
        return result
    
    def save_file(self):        
        filename = filedialog.asksaveasfilename(
            title='Save as file', defaultextension="txt", initialdir=os.getcwd() )
        self.save(file = filename)
                
    def save(self, file = "work.geom.txt"):   
        self.update_plot() 
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        N = str2int( self.phase_count_var.get() )
        f = open(file, "w")
        f.write( '\n'.join([ '\n'.join([ ''.join([self.GEOM_VAR_NAME,'_','ABC'[i],'_','XYZ'[j],' = [', self.geom_var[i*3+j].get(), ']']) for j in range(3) ]) for i in range(N)  ]) ); f.write( '\n' )
        f.write( '\n'.join([ '\n'.join([ ''.join([self.FLD_VAR_NAME,'_','ABC'[i],'_','XYZ'[j],' = [', self.fld_var[i*3+j].get(), ']']) for j in range(3) ]) for i in range(N)  ]) ); f.write( '\n' )
        f.write( '\n'.join([ '\n'.join([ ''.join([self.FORC_VAR_NAME,'_','ABC'[i],'_', '%d' % j,' = [', self.forc_var[i*M+j].get(), ']']) for j in range(M) if self.forc_segs_var[i*M+j].get() ]) for i in range(N)  ]) ); f.write( '\n' )
        f.write( '\n'.join([ ''.join([self.RADIUS_VAR_NAME,'_','ABC'[i],'_',' = [', self.radius_var[i].get(), ']']) for i in range(N)  ]) ); f.write( '\n' )
        f.write( ''.join([self.POLEDIST_VAR_NAME, ' = ', self.poledist_var.get() ]) ); f.write( '\n' )
        f.write( ''.join([self.SAME_VAR_NAME,' = ', 'True' if self.same_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.PHASE_COUNT_VAR_NAME, ' = ', self.phase_count_var.get() ]) ); f.write( '\n' )
        f.close()
       
    def load_file(self):
        filename = filedialog.askopenfilename(
            title='Open a file', defaultextension="txt", initialdir=os.getcwd() )
        self.load(file = filename)
        self.update_plot() 
        
    def init(self):
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        
        self.phase_count_var = StringVar()        
        self.same_var = BooleanVar()        
        self.poledist_var = StringVar()     
        self.radius_var = [StringVar() for i in range(3) ]  
        self.forc_segs_var = [BooleanVar() for i in range(M*3)]        
        self.geom_var = [StringVar() for i in range(3*3) ]
        self.forc_var = [StringVar() for i in range(M*3) ]
        self.fld_var = [StringVar() for i in range(3*3) ]       
              
        
    def load(self, file = "work.geom.txt"):          
        
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        
        #defaults:
        self.phase_count_var.set(value="3")        
        self.same_var.set(value = True)        
        self.poledist_var.set(value="0.21")                            
        XYZ: float =[  
                [  0.0,  0.0,  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [ -0.5, -0.5, -0.5, 0.1, 0.1, 0.1, 0.4, 0.4, 0.5, 0.5, 0.5],
                [  1.0,  0.4,  0.3, 0.3, 0.1, 0.0, 0.0, 0.1, 0.1, 0.5, 1.0], 
            ] 
        RAD: float = [ 2, 2, 2, 2, 2, 2, 2, 2, 2, 2 ]
        FRC: int =   [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 0 ]        
        FLD: float = [ [0], [0], [0] ]        
        
        for i in range(3):
            temp = np.array(RAD) 
            self.radius_var[i].set (value= flt_arr_to_str( temp ) )    
            for j in range(3):
                temp = np.array(XYZ[0*3+j])  + str2flt(self.poledist_var.get())*i*(j==0)       
                self.geom_var[i*3+j].set (value= flt_arr_to_str( temp ) )                 
                temp = np.array(FLD[0*3+j])  + str2flt(self.poledist_var.get())*i*(j==0)          
                self.fld_var[i*3+j].set( value= flt_arr_to_str( temp ) )    
            for j in range(M):
                self.forc_segs_var[i*M+j].set(value = (j==0))
                self.forc_var[i*M+j].set(value= int_arr_to_str( FRC if self.forc_segs_var[i*M+j].get() else [0]*len(FRC)) )
        
        #try to load from file
        if os.path.exists(file):        
            forc_segs_var = [BooleanVar(value = False) for i in range(M*3)]
            with open(file) as f:
                for l in f:
                    (key, val) = tuple([ s.strip() for s in l.split('=') ])
                    val =  val.strip('[]') 
                    print(key, '=', val ) 
                    if key.find('_')>0:
                        (nam, phs, idx) = tuple([ s.strip() for s in key.split('_') ])
                        i = 'ABC'.find(phs)
                        try:
                            j = int(idx)
                        except ValueError:
                            j = 'XYZ'.find(idx)
                            
                        if (nam == self.GEOM_VAR_NAME):
                            self.geom_var[i*3+j].set(val)
                        elif (nam == self.FLD_VAR_NAME):
                            self.fld_var[i*3+j].set(val)
                        elif (nam == self.FORC_VAR_NAME):
                            self.forc_var[i*M+j].set(val)
                            forc_segs_var[i*M+j].set(True)
                        elif (nam == self.RADIUS_VAR_NAME):
                            self.radius_var[i].set(val)
                    else:                    
                        if (key == self.POLEDIST_VAR_NAME):
                            self.poledist_var.set(val)
                        elif (key == self.SAME_VAR_NAME):
                            self.same_var.set(val=='True')
                        elif (key == self.PHASE_COUNT_VAR_NAME):
                            self.phase_count_var.set(val)
            for i in range(3):
                for j in range(M):                            
                    self.forc_segs_var[i*M+j].set(forc_segs_var[i*M+j].get())    
                    if not forc_segs_var[i*M+j].get():
                        XYZ = str_to_flt_arr(self.geom_var[i*3].get())
                        self.forc_var[i*M+j].set( value= int_arr_to_str( [0]*(len(XYZ)-1) ) )    
                        
                
        
    def show_errors(self):       
        if self.status == self.STATUS_OK:
            messagebox.showinfo(self.STATUS_OK, "") 
        else:
            messagebox.showerror(self.STATUS_ERROR, self.error_message) 
        
    def on_change(self, event=None):            
        self.update_plot()
        
    def on_geom_change(self, event=None, i = 0, j = 0):     
        XYZ = str_to_flt_arr(self.geom_var[i*3+j].get())       
        self.geom_var[i*3+j].set( flt_arr_to_str(XYZ) )         
        self.update_plot()            
        
        
    def on_segments_radius_change(self, event=None, i =0 ):     
        rad = str_to_flt_arr(self.radius_var[i].get())       
        self.radius_var[i].set( flt_arr_to_str(rad) )         
        self.update_plot()            
            
    def on_force_segments_change(self, event=None, i = 0, j = 0):     
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        FRC = str_to_int_arr(self.forc_var[i*M+j].get())       
        self.forc_var[i*M+j].set( int_arr_to_str(FRC) )     
        self.update_plot()
                    
        