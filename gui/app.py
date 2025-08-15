from tkinter import Tk, Frame
import tkinter as tk
from gui.controls_geom import ControlGeomPanel
from gui.controls_exct import ControlExctPanel
from gui.plot_geom import PlotGeomArea
from gui.plot_exct import PlotExctArea
from logic.geometry import Geometry
from logic.excitation import Excitation

import traceback

class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("AMPERE BIOT-SAVART NEUMANN")
        
        container = Frame(self.master)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight = 1)
        container.columnconfigure(0, weight = 1)
        
        self.plot_frame = Frame(container)        
        self.plot_geom_area = PlotGeomArea(self.plot_frame)        
        self.plot_exct_area = PlotExctArea(self.plot_frame)        
        self.ctrl_frame = Frame(container)  
        self.control_geom_panel = ControlGeomPanel(self.ctrl_frame, self, self.update_geom_plot)        
        self.control_exct_panel = ControlExctPanel(self.ctrl_frame, self, self.update_exct_plot)
        
        self.plot_frame.pack(side = tk.TOP, fill=tk.BOTH)
        self.plot_geom_area.pack(side = tk.LEFT, fill=tk.BOTH)
        self.plot_exct_area.pack(side = tk.RIGHT, fill=tk.BOTH, expand=True)
        self.ctrl_frame.pack(side = tk.BOTTOM, fill=tk.BOTH)        
        self.control_exct_panel.pack(side = tk.RIGHT, fill=tk.BOTH, expand=False)
        self.control_geom_panel.pack(side = tk.RIGHT, fill=tk.BOTH, expand=True)
                                
        self.control_geom_panel.update_plot()
        
    def save(self):
        self.control_geom_panel.save("work.geom.txt")
        self.control_exct_panel.save("work.exct.txt")

    def update_geom_plot(self, g : Geometry):

        # print("Update plot called: %s" % traceback.format_stack()[-1].splitlines()[0] )
        self.plot_geom_area.update_plot(g)
        
        
    def update_exct_plot(self, e : Excitation):

        # print("Update plot called: %s" % traceback.format_stack()[-1].splitlines()[0] )
        self.plot_exct_area.update_plot(e, self.control_geom_panel.geometry)
        
        