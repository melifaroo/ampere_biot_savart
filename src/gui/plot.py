import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame

class PlotArea(Frame):
    def __init__(self, master):
        super().__init__(master)  # Initialize as a Frame
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update_plot(self, T, I, Bx, By, Bz, Fx, Fy, Fz):
        self.ax.clear()
        self.ax.plot(T, Bx, label='Bx')
        self.ax.plot(T, By, label='By')
        self.ax.plot(T, Bz, label='Bz')
        self.ax.set_title('Magnetic Field Components')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Magnetic Field (T)')
        self.ax.legend()
        self.canvas.draw()