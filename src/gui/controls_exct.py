from tkinter import Frame, Label, Entry, Button, StringVar, BooleanVar, OptionMenu, Checkbutton
import tkinter
import numpy as np
import logic.geometry as geometry

class ControlExctPanel(Frame):
        
    LP : float = 0.2
    
    def __init__(self, master, update_plot_callback):
        super().__init__(master)
        self.update_plot_callback = update_plot_callback
        
        self.current_var = StringVar(value="1.0")
        self.excitation_type_var = StringVar(value="rlc")
        self.kd_var = StringVar(value="0.0")
        
        self.create_widgets()
        self.update_plot()

    def create_widgets(self):
        Label(self, text="Current I:").grid(row=0, column=0)
        self.current_entry = Entry(self, textvariable=self.current_var)
        self.current_entry.grid(row=0, column=1)
        self.current_entry.bind("<KeyRelease>", self.on_change)

        Label(self, text="Excitation Type:").grid(row=1, column=0)
        self.excitation_type_menu = OptionMenu(self, self.excitation_type_var, "rlc", "real", command=self.on_change)
        self.excitation_type_menu.grid(row=1, column=1)

        Label(self, text="Kd Coefficient:").grid(row=2, column=0)
        self.kd_entry = Entry(self, textvariable=self.kd_var)
        self.kd_entry.grid(row=2, column=1)
        self.kd_entry.bind("<KeyRelease>", self.on_change)
        
                
    def on_change(self, event=None):            
        self.update_plot()
                
    def update_plot(self):
        
        g = geometry.sample_input(
            XA = [ self.float_(s.strip()) for s in self.geom_var[0*3+0].get().split(",")  ], 
            YA = [ self.float_(s.strip()) for s in self.geom_var[0*3+1].get().split(",")  ], 
            ZA = [ self.float_(s.strip()) for s in self.geom_var[0*3+2].get().split(",")  ], 
            XB = [ self.float_(s.strip()) for s in self.geom_var[1*3+0].get().split(",")  ], 
            YB = [ self.float_(s.strip()) for s in self.geom_var[1*3+1].get().split(",")  ], 
            ZB = [ self.float_(s.strip()) for s in self.geom_var[1*3+2].get().split(",")  ], 
            XC = [ self.float_(s.strip()) for s in self.geom_var[2*3+0].get().split(",")  ], 
            YC = [ self.float_(s.strip()) for s in self.geom_var[2*3+1].get().split(",")  ], 
            ZC = [ self.float_(s.strip()) for s in self.geom_var[2*3+2].get().split(",")  ], 
            )
        self.update_plot_callback(g)