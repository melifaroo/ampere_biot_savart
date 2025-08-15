import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame
import logic.presentation as presentation
from logic.excitation import Excitation
from logic.geometry import Geometry
import traceback

class PlotExctArea(Frame):
    def __init__(self, master):
        super().__init__(master)  # Initialize as a Frame
        self.figure = plt.figure()
        grid = plt.GridSpec(nrows = 2, ncols = 2 , wspace=0.3, hspace=0.2, left=0.05, right=0.95, top=0.95, bottom = 0.05)
        self.axi = plt.subplot(grid[:,1])
        self.axu = plt.subplot(grid[0,0])
        self.axul = plt.subplot(grid[1,0])
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
      
    def update_plot(self, e : Excitation, g : Geometry):
        self.axi.cla()
        self.axu.cla()
        self.axul.cla()
        presentation.plotVoltagePhase(e, self.axu, self.figure)
        presentation.plotVoltageLinear(e, self.axul, self.figure)
        if not g is None:
            presentation.plotCurrent(e, self.axi, self.figure)
        self.canvas.draw()
        # print("Update plot completed: %s, axes %s, figure %s" % (  traceback.format_stack()[-1].splitlines()[0], self.ax  , self.figure  ))