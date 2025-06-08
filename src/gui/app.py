from tkinter import Tk, Frame
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
        
        self.frame = Frame(container)
        
        self.frame.grid()

        self.plot_geom_area = PlotGeomArea(self.frame)
        self.plot_geom_area.grid(row=0, column=0, columnspan=2)
        
        self.plot_exct_area = PlotExctArea(self.frame)
        self.plot_exct_area.grid(row=0, column=2, columnspan=2)
        
        self.control_geom_panel = ControlGeomPanel(self.frame, self, self.update_geom_plot)
        self.control_geom_panel.grid(row=1, column=0, columnspan=3)
                
        self.control_exct_panel = ControlExctPanel(self.frame, self, self.update_exct_plot)
        self.control_exct_panel.grid(row=1, column=3, columnspan=1)
        
        self.control_geom_panel.update_plot()
        
    def save(self):
        self.control_geom_panel.save("work.geom.txt")
        self.control_exct_panel.save("work.exct.txt")

    def update_geom_plot(self, g : Geometry):

        # print("Update plot called: %s" % traceback.format_stack()[-1].splitlines()[0] )
        self.plot_geom_area.update_plot(g)
        
        
    def update_exct_plot(self, e : Excitation):

        # print("Update plot called: %s" % traceback.format_stack()[-1].splitlines()[0] )
        if  hasattr(self.control_geom_panel, 'geometry'):
            self.plot_exct_area.update_plot(e, self.control_geom_panel.geometry)
        
        