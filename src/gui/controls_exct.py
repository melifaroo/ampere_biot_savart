from tkinter import Frame, Label, Entry, Button, StringVar, BooleanVar, OptionMenu, Checkbutton
from tkinter import ttk
import tkinter as tk
from typing import Final
import os.path

import matplotlib.pyplot as plt
import logic.excitation as excitation
import logic.presentation as presentation
import logic.solution as solution
from utils.formats import str_to_flt, str_to_int, float_input_validate, positive_int_input_validate, nonneg_float_input_validate, flt_arr_to_str

class ControlExctPanel(Frame):
        
    DURATION_VAR_NAME       : Final = 'Duration'
    DISCRET_VAR_NAME        : Final = 'Discret'
    CURRENT_VAR_NAME        : Final = 'Current'
    CURRENT_TYPE_VAR_NAME   : Final = 'Current_value_type'
    EXCT_TYPE_VAR_NAME      : Final = 'Source_type'
    K_OVERRIDE_VAL_VAR_NAME : Final = 'K_value_override'
    K_OVERRIDE_VAR_NAME     : Final = 'K_override'
    SCHEMA_VAR_NAME         : Final = 'Schema'
        
    MAX_FORCE_PER_PHASE : Final[int] = 6    
    
    CUR_TYPE_RMS : Final = "RMS"
    CUR_TYPE_PEAK : Final = "Peak"
    
    SCHEMA_A_BC : Final = "A(BC)"
    SCHEMA_B_AC : Final = "B(AC)"
    SCHEMA_C_AB : Final = "C(AB)"
    
    SRC_TYPE_RLC : Final = "RLC 1Ph Circuit"
    SRC_TYPE_GEN : Final = "3ph Generator"
    
    def __init__(self, master, app, update_plot_callback):
        super().__init__(master)
        self.app = app        
        self.update_plot_callback = update_plot_callback
        
        self.init()
        self.load()                
        self.create()
        self.update()
        self.app.control_geom_panel.schema = "ABC" if self.excitation_type_var.get() == self.SRC_TYPE_GEN else self.schema_var.get()   
        

    def create(self):
        if  hasattr(self.app.control_geom_panel, 'geometry'):
            geom = self.app.control_geom_panel.geometry
        if  not geom == None:
            Nph = geom.getCircuitPhaseCount()
        else:
            Nph = 1
                        
        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)              
        self.solve_btn = Button(panel, text="SOLVE", background="blue", command=self.solve)
        self.solve_btn.pack(expand=False, fill=tk.X)
                
        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)       
        Label(panel, text=" ").pack(side= tk.RIGHT)#.grid(row=1, column=0)
        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)     
        Label(panel, text=" ").pack(side= tk.RIGHT)#.grid(row=1, column=0)
          
        panel = Frame(self)           
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)               
        self.duration_entry = Entry(panel, textvariable=self.duration_var, validate="key", validatecommand=(self.register(nonneg_float_input_validate), '%P'))
        self.duration_entry.bind("<KeyRelease>", self.on_change)
        self.duration_entry.pack(side= tk.RIGHT, expand=False, fill=tk.X)#grid(row=1, column=1)
        Label(panel, text="Duration T [ms]:").pack(side= tk.RIGHT)#.grid(row=1, column=0)
        
        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)     
        self.discret_entry = Entry(panel, textvariable=self.discret_var)
        self.discret_entry.bind("<KeyRelease>", self.on_change)
        self.discret_entry.config(validate="key", validatecommand=(self.register(positive_int_input_validate), '%P'))
        self.discret_entry.pack(side=tk.RIGHT)#.grid(row=2, column=1)
        Label(panel, text="Diskret points:").pack(side=tk.RIGHT)#.grid(row=2, column=0)
        
        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)     
        self.current_type_menu = OptionMenu(panel, self.current_type_var, self.CUR_TYPE_PEAK, self.CUR_TYPE_RMS, command=self.on_change)
        self.current_entry = Entry(panel, textvariable=self.current_var)
        self.current_entry.bind("<KeyRelease>", self.on_change)
        self.current_entry.config(validate="key", validatecommand=(self.register(nonneg_float_input_validate), '%P'))        
        self.current_entry.pack(side=tk.RIGHT)#.grid(row=3, column=1)
        Label(panel, text="Current I [kA]:").pack(side=tk.RIGHT)#.grid(row=3, column=0)
        self.current_type_menu.pack(side=tk.RIGHT)#.grid(row=3, column=2)

        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)     
        state = "normal" if ( (self.excitation_type_var.get()==self.SRC_TYPE_RLC and Nph==3) ) else "disabled"
        self.excitation_type_menu = ttk.Combobox(panel, textvariable=self.excitation_type_var, width = 16, values= [self.SRC_TYPE_RLC, self.SRC_TYPE_GEN])
        self.excitation_type_menu.bind("<<ComboboxSelected>>", self.on_schema_change)
        self.excitation_type_menu.pack(side=tk.RIGHT)#.grid(row=4, column=1)
        Label(panel, text="Excitation Type:").pack(side=tk.RIGHT)#.grid(row=4, column=0)

        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)     
        self.schema_menu = ttk.Combobox(panel, textvariable=self.schema_var, width = 16, values= [self.SCHEMA_A_BC, self.SCHEMA_C_AB, self.SCHEMA_B_AC], state = state )
        self.schema_menu.bind("<<ComboboxSelected>>", self.on_schema_change)
        self.schema_menu.pack(side=tk.RIGHT)#.grid(row=4, column=2)
        Label(panel, text="Schema:").pack(side=tk.RIGHT)#.grid(row=4, column=0)
        
        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)     
        self.k_natural_value_entry = Entry(panel, textvariable=self.k_natural_value_var, state="readonly" )
        self.k_natural_value_entry.pack(side=tk.RIGHT)#.grid(row=5, column=2)  
        Label(panel, text="Branches Asymm. Coef.:").pack(side=tk.RIGHT)#.grid(row=5, column=1)  
        
        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)      
        state = "normal" if ( (self.excitation_type_var.get()==self.SRC_TYPE_RLC and Nph==3 and self.k_override_var.get() ) ) else "disabled"
        self.k_override_value_entry = Entry(panel, textvariable=self.k_override_value_var, state=state )
        self.k_override_value_entry.bind("<KeyRelease>", self.on_change)
        self.k_override_value_entry.config(validate="key", validatecommand=(self.register(float_input_validate), '%P'))
        self.k_override_entry = Checkbutton(panel, text="Override Asymm. Coef.:", variable=self.k_override_var, state = state ,  command=self.on_change )         
        self.k_override_value_entry.pack(side=tk.RIGHT)#.grid(row=6, column=2)   
        self.k_override_entry.pack(side=tk.RIGHT)#.grid(row=6, column=1)                
        
        panel = Frame(self)  
        panel.pack(side = tk.TOP, expand=False, fill=tk.X)     
        self.ind_entry = Entry(panel, textvariable=self.ind_var, state="readonly" )
        self.ind_entry.pack(side=tk.RIGHT)#.grid(row=7, column=2)    
        Label(panel, text="L [mkH] (A, B, C)").pack(side=tk.RIGHT)#.grid(row=7, column=1)
                
    def on_change(self, event=None):            
        self.update_plot()
        
    def on_schema_change(self, event=None):  
        self.app.control_geom_panel.schema = "ABC" if self.excitation_type_var.get() == self.SRC_TYPE_GEN else self.schema_var.get()   
        self.app.control_geom_panel.update_plot()
                
    def solve(self):        
        if  hasattr(self.app.control_geom_panel, 'geometry'):
            geom = self.app.control_geom_panel.geometry
        valid = self.app.control_geom_panel.valid
        if  valid and not geom == None:
            results = solution.solve(geom, self.exitation)  
            presentation.plotResults(results) 
        else:
            self.app.control_geom_panel.show_errors()
        
    def update(self):
        if  hasattr(self.app.control_geom_panel, 'geometry'):
            geom = self.app.control_geom_panel.geometry
        if  not geom == None:
            Nph = geom.getCircuitPhaseCount()
        else:
            Nph = 1
        T = str_to_flt( self.duration_var.get() )
        N = str_to_int( self.discret_var.get() )
        I = str_to_flt( self.current_var.get() )
        current_type = "rms" if (self.current_type_var.get() == self.CUR_TYPE_RMS) else "peak"
        excitation_type = "gen" if (self.excitation_type_var.get() == self.SRC_TYPE_GEN) else "rlc"
        
        state = "normal" if (Nph==3) else "disabled"
        self.schema_menu.config(state = state)
        
        peakPhaseNumber = 0 if self.schema_var.get()==self.SCHEMA_A_BC else (1 if self.schema_var.get()==self.SCHEMA_B_AC else 2)
        
        self.k_override_entry.config(state = state)
        
        asymK_override =  self.excitation_type_var.get()==self.SRC_TYPE_RLC and Nph==3 and self.k_override_var.get()  
        
        state = "normal" if asymK_override else "disabled"
        self.k_override_value_entry.config(state = state)
        
        asymK_value = str_to_flt(self.k_override_value_var.get()) if asymK_override else None
        
        self.exitation = excitation.build(T, N, I, source_type = excitation_type, current=current_type)
        
        if  not geom == None:
            inductances = solution.evalBranchCurrents(geom, self.exitation, peakPhaseNumber = peakPhaseNumber , asymK_override = asymK_value)
            self.ind_var.set(  flt_arr_to_str(inductances.L, 1e6) )
            
        self.k_natural_value_var.set( "%6.2f" % self.exitation.asymK )
        
                
    def update_plot(self):
        self.update()
        self.update_plot_callback(self.exitation)
        
    def save(self, file = "work.exct.txt"):   
        self.update_plot() 
        f = open(file, "w")
        f.write( ''.join([self.DURATION_VAR_NAME, ' = ', self.duration_var.get() ]) ); f.write( '\n' )
        f.write( ''.join([self.DISCRET_VAR_NAME, ' = ', self.discret_var.get() ]) ); f.write( '\n' )
        f.write( ''.join([self.CURRENT_VAR_NAME, ' = ', self.current_var.get() ]) ); f.write( '\n' )
        f.write( ''.join([self.CURRENT_TYPE_VAR_NAME, ' = ', self.current_type_var.get() ]) ); f.write( '\n' )
        f.write( ''.join([self.EXCT_TYPE_VAR_NAME, ' = ', self.excitation_type_var.get() ]) ); f.write( '\n' )
        f.write( ''.join([self.K_OVERRIDE_VAL_VAR_NAME, ' = ', self.k_override_value_var.get() ]) ); f.write( '\n' )
        f.write( ''.join([self.K_OVERRIDE_VAR_NAME, ' = ', 'True' if self.k_override_var.get() else 'False' ]) ); f.write( '\n' )
        f.write( ''.join([self.SCHEMA_VAR_NAME, ' = ', self.schema_var.get() ]) ); f.write( '\n' )
        f.close()
        
    def init(self):        
        self.duration_var = StringVar()        
        self.discret_var = StringVar()        
        self.current_var = StringVar()        
        self.current_type_var = StringVar()   
        self.excitation_type_var = StringVar()        
        self.k_natural_value_var = StringVar()       
        self.k_override_value_var = StringVar()      
        self.k_override_var = BooleanVar()        
        self.schema_var = StringVar()      
        self.ind_var = StringVar()        
                
    def load(self, file = "work.exct.txt"):
        
        self.duration_var.set(value="20.0")        
        self.discret_var.set(value="21")        
        self.current_var.set(value="80.0")        
        self.current_type_var.set(value=self.CUR_TYPE_PEAK)        
        self.excitation_type_var.set(value=self.SRC_TYPE_RLC)        
        self.k_natural_value_var.set(value="0.0")       
        self.k_override_value_var.set(value="0.0")      
        self.k_override_var.set(value=False)        
        self.schema_var.set(value = self.SCHEMA_A_BC)  
        self.ind_var.set(value="0.0,    0.0,    0.0")       
        
        if os.path.exists(file):  
            with open(file) as f:
                for l in f:
                    (key, val) = tuple([ s.strip() for s in l.split('=') ])
                    val =  val.strip('[]') 
                    print(key, '=', val )                     
                    if (key == self.DURATION_VAR_NAME):
                        self.duration_var.set(val)
                    elif (key == self.DISCRET_VAR_NAME):
                        self.discret_var.set(val)
                    elif (key == self.CURRENT_VAR_NAME):
                        self.current_var.set(val)
                    elif (key == self.CURRENT_TYPE_VAR_NAME):
                        self.current_type_var.set(val)
                    elif (key == self.EXCT_TYPE_VAR_NAME):
                        self.excitation_type_var.set(val)
                    elif (key == self.K_OVERRIDE_VAL_VAR_NAME):
                        self.k_override_value_var.set(val)
                    elif (key == self.K_OVERRIDE_VAR_NAME):
                        self.k_override_var.set(val == 'True')
                    elif (key == self.SCHEMA_VAR_NAME):
                        self.schema_var.set(val)
                           
            

        
