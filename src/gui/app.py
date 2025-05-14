from tkinter import Tk, Frame
from gui.controls_geom import ControlGeomPanel
from gui.controls_exct import ControlExctPanel
from gui.plot_geom import PlotGeomArea
from gui.plot_exct import PlotExctArea
from logic.geometry import Geometry
from logic.excitation import Excitation

class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Circuit geometry and current source")
        
        self.frame = Frame(self.master)
        self.frame.grid()

        self.plot_geom_area = PlotGeomArea(self.frame)
        self.plot_geom_area.grid(row=0, column=0)
        
        self.plot_exct_area = PlotExctArea(self.frame)
        self.plot_exct_area.grid(row=0, column=1)
        
        self.control_geom_panel = ControlGeomPanel(self.frame, self, self.update_geom_plot)
        self.control_geom_panel.grid(row=1, column=0)
                
        self.control_exct_panel = ControlExctPanel(self.frame, self, self.update_curr_plot)
        self.control_exct_panel.grid(row=1, column=1)
        
        self.control_geom_panel.update_plot()

    def update_geom_plot(self, g : Geometry):

        self.plot_geom_area.update_plot(g)
        print("Update plot called")
        
        
    def update_curr_plot(self, e : Excitation):

        self.plot_exct_area.update_plot(e, self.control_geom_panel.geometry)
        print("Update plot called")
        

if __name__ == "__main__":
    root = Tk()
    app = Application(root)
    root.mainloop()