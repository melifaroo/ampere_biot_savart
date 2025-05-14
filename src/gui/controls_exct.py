from tkinter import Frame, Label, Entry, Button, StringVar, BooleanVar, OptionMenu, Checkbutton
from tkinter import ttk
from typing import Final
import numpy as np

import matplotlib.pyplot as plt
import logic.excitation as excitation
import logic.presentation as presentation
import logic.solution as solution
from utils.formats import str2flt, str2int, float_input_validate, positive_int_input_validate, nonneg_float_input_validate

class ControlExctPanel(Frame):
        
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
        
        self.duration_var = StringVar(value="20.0")
        
        self.discret_var = StringVar(value="20")
        
        self.current_var = StringVar(value="80.0")
        
        self.current_type_var = StringVar(value=self.CUR_TYPE_PEAK)
        
        self.excitation_type_var = StringVar(value=self.SRC_TYPE_RLC)
        
        self.k_natural_value_var = StringVar(value="0.0")
        
        self.k_override_var = BooleanVar(value=False)
        
        self.schema_var = StringVar(value = self.SCHEMA_A_BC)
        
        self.k_override_value_var = StringVar(value="0.0")
                        
        self.create_widgets()
        self.update()

    def create_widgets(self):
        Nph = self.app.control_geom_panel.geometry.getCircuitPhaseCount()
        
        Label(self, text="Duration T [ms]:").grid(row=0, column=0)
        self.duration_entry = Entry(self, textvariable=self.duration_var)
        self.duration_entry.bind("<KeyRelease>", self.on_change)
        self.duration_entry.config(validate="key", validatecommand=(self.register(nonneg_float_input_validate), '%P'))
        self.duration_entry.grid(row=0, column=1)
        
        Label(self, text="Diskret points:").grid(row=1, column=0)
        self.discret_entry = Entry(self, textvariable=self.discret_var)
        self.discret_entry.bind("<KeyRelease>", self.on_change)
        self.discret_entry.config(validate="key", validatecommand=(self.register(positive_int_input_validate), '%P'))
        self.discret_entry.grid(row=1, column=1)
        
        Label(self, text="Current I [kA]:").grid(row=2, column=0)
        self.current_entry = Entry(self, textvariable=self.current_var)
        self.current_entry.grid(row=2, column=1)
        self.current_entry.bind("<KeyRelease>", self.on_change)
        self.current_entry.config(validate="key", validatecommand=(self.register(nonneg_float_input_validate), '%P'))
        self.current_type_menu = OptionMenu(self, self.current_type_var, self.CUR_TYPE_PEAK, self.CUR_TYPE_RMS, command=self.on_change)
        self.current_type_menu.grid(row=2, column=2)

        Label(self, text="Excitation Type:").grid(row=3, column=0)
        self.excitation_type_menu = OptionMenu(self, self.excitation_type_var, self.SRC_TYPE_RLC, self.SRC_TYPE_GEN, command=self.on_change)
        self.excitation_type_menu.grid(row=3, column=1)

        state = "normal" if ( (self.excitation_type_var.get()==self.SRC_TYPE_RLC and Nph==3) ) else "disabled"
        self.schema_menu = ttk.Combobox(self, textvariable=self.schema_var, values= [self.SCHEMA_A_BC, self.SCHEMA_C_AB, self.SCHEMA_B_AC], state = state )
        self.schema_menu.bind("<<ComboboxSelected>>", self.on_change)
        self.schema_menu.grid(row=3, column=2)

        Label(self, text="Branches Asymm. Coef.:").grid(row=4, column=1)
        self.k_natural_value_entry = Entry(self, textvariable=self.k_natural_value_var, state="readonly" )
        self.k_natural_value_entry.grid(row=4, column=2)    
        
        self.k_override_entry = Checkbutton(self, text="Override Asymm. Coef.:", variable=self.k_override_var, state = state ,  command=self.on_change )         
        self.k_override_entry.grid(row=5, column=1)
        
        state = "normal" if ( (self.excitation_type_var.get()==self.SRC_TYPE_RLC and Nph==3 and self.k_override_var.get() ) ) else "disabled"
        self.k_override_value_entry = Entry(self, textvariable=self.k_override_value_var, state=state )
        self.k_override_value_entry.bind("<KeyRelease>", self.on_change)
        self.k_override_value_entry.config(validate="key", validatecommand=(self.register(float_input_validate), '%P'))
        self.k_override_value_entry.grid(row=5, column=2)    
                
        self.error_btn = Button(self, text="SOLVE", background="blue", command=self.solve)
        self.error_btn.grid(row=6, column=0, rowspan=3, columnspan=3)
                
    def on_change(self, event=None):            
        self.update_plot()
                
    def solve(self):
        self.update_plot()
        results = solution.solve(self.app.control_geom_panel.geometry, self.exitation)
        
        fig = plt.figure()#figsize=[screen_x/96, screen_y/96])#[height, height*((np.sqrt(5)-1.0)/2.0)] 
    
        Nph = self.app.control_geom_panel.geometry.getCircuitPhaseCount() 
        
        presentation.plotResults(results, fig, C = Nph)              
        
        # figManager.window.state('normal')# normal, iconic, withdrawn, or zoomed
        window = plt.get_current_fig_manager().window
        screen_x, screen_y = window.wm_maxsize()
        fig.set_size_inches([screen_x/fig.dpi, screen_y/fig.dpi-3]) 
        window.wm_geometry("+0+0")
        
        plt.show(block=False)

        
    def update(self):
        Nph = self.app.control_geom_panel.geometry.getCircuitPhaseCount()
        T = str2flt( self.duration_var.get() )
        N = str2int( self.discret_var.get() )
        I = str2flt( self.current_var.get() )
        current_type = "rms" if (self.current_type_var.get() == self.CUR_TYPE_RMS) else "peak"
        excitation_type = "gen" if (self.excitation_type_var.get() == self.SRC_TYPE_GEN) else "rlc"
        
        state = "normal" if Nph==3 else "disabled"
        self.schema_menu.config(state = state)
        
        peakPhaseNumber = 0 if self.schema_var.get()==self.SCHEMA_A_BC else (1 if self.schema_var.get()==self.SCHEMA_B_AC else 2)
        
        self.k_override_entry.config(state = state)
        
        asymK_override =  self.excitation_type_var.get()==self.SRC_TYPE_RLC and Nph==3 and self.k_override_var.get()  
        
        state = "normal" if asymK_override else "disabled"
        self.k_override_value_entry.config(state = state)
        
        asymK_value = str2flt(self.k_override_value_var.get()) if asymK_override else None
        
        self.exitation = excitation.build(T, N, I, type = excitation_type, current=current_type)
        
        solution.evalBranchCurrents(self.app.control_geom_panel.geometry, self.exitation, peakPhaseNumber = peakPhaseNumber , asymK_override = asymK_value)
        
        self.k_natural_value_var.set( "%6.2f" % self.exitation.asymK )
                
    def update_plot(self):
        self.update()
        self.update_plot_callback(self.exitation)
            

        
