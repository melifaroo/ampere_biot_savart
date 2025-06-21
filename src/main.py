import tkinter as tk
import warnings
warnings.filterwarnings("ignore")
from gui.app import Application
        
    
def main():   
   
    root = tk.Tk()
    app = Application(root)
    
    def on_closing():
        print("exit")
        app.save()
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

if __name__ == "__main__":
    main()