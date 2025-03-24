from tkinter import Tk, Frame
from gui.controls import ControlPanel
from gui.plot import PlotArea

class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Current Control GUI")
        
        self.frame = Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        self.control_panel = ControlPanel(self.frame, self.update_plot)
        self.control_panel.pack()

        self.plot_area = PlotArea(self.frame)
        self.plot_area.pack()

    def update_plot(self):
        I = self.control_panel.current_I.get()
        excitation_type = self.control_panel.excitation_type.get()
        Kd = self.control_panel.Kd.get()
        # Call the plotting method with updated parameters
        self.plot_area.update_plot(I, excitation_type, Kd)

if __name__ == "__main__":
    root = Tk()
    app = Application(root)
    root.mainloop()