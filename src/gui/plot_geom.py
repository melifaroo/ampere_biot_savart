import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame
import logic.presentation as presentation
from logic.geometry import Geometry
import traceback

class PlotGeomArea(Frame):
    def __init__(self, master):
        super().__init__(master)  # Initialize as a Frame
        self.figure = plt.figure()
        self.ax = plt.subplot(projection='3d')
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update_plot(self, g : Geometry):
        self.ax.cla()
        if not g is None:
            presentation.plotGeometry(g, self.ax)
        self.canvas.draw()
        # print("Update plot completed: %s, axes %s, figure %s" % (  traceback.format_stack()[-1].splitlines()[0], self.ax  , self.figure  ))