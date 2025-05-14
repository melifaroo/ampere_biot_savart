from tkinter import Frame, Label, Entry, Button, StringVar, OptionMenu

class ControlPanel(Frame):
    def __init__(self, master, update_plot_callback):
        super().__init__(master)
        self.update_plot_callback = update_plot_callback
        
        self.current_var = StringVar(value="1.0")
        self.excitation_type_var = StringVar(value="rlc")
        self.kd_var = StringVar(value="0.0")
        
        self.create_widgets()

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

        self.plot_button = Button(self, text="Update Plot", command=self.update_plot)
        self.plot_button.grid(row=3, columnspan=2)

    def on_change(self, event=None):
        self.update_plot()

    def update_plot(self):
        current = float(self.current_var.get())
        excitation_type = self.excitation_type_var.get()
        kd = float(self.kd_var.get())
        self.update_plot_callback(current, excitation_type, kd)