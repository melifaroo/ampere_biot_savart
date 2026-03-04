from typing import Final
from tkinter import  Spinbox, Frame, Label, Entry, Button, StringVar, BooleanVar, OptionMenu, Checkbutton, messagebox, filedialog
from tkinter import ttk 
import tkinter as tk
import os.path
import itertools

from utils.formats import length_str_arr, flt_to_str, str_to_flt, str_to_int, str_to_int_arr, str_to_flt_arr, float_array_input_validate, int_array_input_validate, nonzero_float_input_validate, flt_arr_to_str, int_arr_to_str

import numpy as np
import logic.geometry as geometry

class ControlGeomPanel(Frame):
        
    schema = "ABC"
    MAX_FORCE_PER_PHASE : Final[int] = 6
    STATUS_OK : Final = "Geometry is OK!"
    STATUS_ERROR : Final = "Geometry contains errors!"
    SUBFIELD_SEPARATOR : Final = '.'

    GEOM_MAIN_VN : Final = 'GEOM_MAIN'
    GEOM_FELD_VN : Final = 'GEOM_FELD'
    MASK_FORC_VN : Final = 'SGMT_FORC'
    MAIN_RADI_VN: Final =  'SGMT_RADI'
    POLS_SAME_VN : Final = 'SAME_GEOM'
    POLS_X_TR_VN : Final = 'POLE_DIST'
    POLS__CNT_VN: Final = 'PHASE_CNT'
    POLS_CONN_VN: Final = 'POLE_CONN'
    
    AUTO_SRCE_VN: Final = 'AUTO_SRCE'
    AUTO_SPLT_VN: Final = 'AUTO_SPLT'
    AUTO_NEUT_VN: Final = 'AUTO_SHRT'

    AUTO_SCON_VN: Final = 'AUTO_SCON'
    AUTO_NCON_VN: Final = 'AUTO_ECON'
    CONN_FORC_VN: Final = 'FORC_CONN'
    CONN_RADI_VN: Final = 'RADI_CONN'
    
    GEOM_SRCE_VN: Final = 'GEOM_SRCE'
    GEOM_SPLT_VN: Final = 'GEOM_SPLT'
    GEOM_NEUT_VN: Final = 'GEOM_SHRT'
    
    GEOM_SCON_VN: Final = 'GEOM_SCON'
    GEOM_NCON_VN: Final = 'GEOM_ECON'
            
    AUTO_SROL_VN: Final = 'AUTO_SROL'
    AUTO_EROL_VN: Final = 'AUTO_EROL'
     
    
    valid: bool = True
    
    error_message = ""
    status = STATUS_OK
            
    def __init__(self, master, app, update_plot_callback):
        super().__init__(master)
        self.app = app
        self.update_plot_callback = update_plot_callback
        
        self.init()
        self.load()                
        self.create()
        self.update()

    def create(self):
        
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        N = str_to_int(self.pcnt_var.get())
            
        panel = Frame(self)  
        panel.pack(side = tk.TOP, fill=tk.X, expand=False)
            
        self.error_btn = Button(panel, text="OK", width=10, background="green", command=self.show_errors)
        self.error_btn.pack(side= tk.RIGHT)
        
        Button(panel, text="LOAD", width=10, command=self.load_file).pack(side= tk.RIGHT)
        
        Button(panel, text="SAVE", width=10, command=self.save_file).pack(side= tk.RIGHT)        
        
        
        Label(panel, text="Phase Count:").pack(side= tk.LEFT)
        # .grid(row=0, column=3)
        self.pcnt_menu = OptionMenu(panel, self.pcnt_var, "1", "2", "3", command=self.on_change)
        self.pcnt_menu.pack(side= tk.LEFT)
        # self.phase_count_menu.grid(row=0, column=4)
        
        self.same_check = Checkbutton(panel, variable=self.same_var, text="Same geometry of all phases",  command=self.update_plot)
        self.same_check.pack(side= tk.LEFT)
        # self.same_check.grid(row=0, column = 5,  sticky="W"  )
                                
        Label(panel, text="Pole Distance [m]:").pack(side= tk.LEFT)
        # .grid(row=0, column=6)
        self.pdst_entry = Entry(panel, textvariable=self.pdst_var, justify="left")
        self.pdst_entry.pack(side= tk.LEFT)
        # self.poledist_entry.grid(row=0, column=7)
        self.pdst_entry.bind("<KeyRelease>", self.on_change)
        self.pdst_entry.config(validate="key", validatecommand=(self.register(nonzero_float_input_validate), '%P'))
        
        self.conn_check = Checkbutton(panel, variable=self.auto_conn_var, text="Phase connections",  command=self.update_plot)
        self.conn_check.pack(side= tk.LEFT)
        # self.jump_check.grid(row=0, column = 8,  sticky="W"  )
       
        self.conn_panel = [None]*4
        self.splt_panel = [None]*4
        self.srce_panel = [None]*4
        self.geom_main_entry = [None]*3*3
        self.list_forc_entry = [None]*3*M
        self.feld_entry = [None]*3*3
        self.radi_main_entry = [None]*3
        self.sgmt_forc_entry = [None]*3*M
        
        self.geom_scon_entry = [None]*3*4
        self.geom_econ_entry = [None]*3*4
        
        self.geom_splt_entry = [None]*3*4
        self.geom_srce_entry = [None]*3*4
        self.geom_shrt_entry = [None]*3*4
        
        self.auto_srol_entry = [None]*4
        self.auto_erol_entry = [None]*4
                        
        self.tabControl = ttk.Notebook(self)         
        self.tabControl.pack(side= tk.TOP, fill=tk.X, expand=True)
        
        for i in range(3):
            
            tab = Frame(self.tabControl) 
            self.tabControl.add(tab, text = "Phase" +"ABC"[i]) 
            self.tabControl.tab(0, state = "normal" if i<N else "disabled")
            
            Label( tab, text="geometry points (N):").pack(side = tk.TOP, expand=False, fill=tk.X)                 
            panel0 = Frame(tab)  
            panel0.pack(side = tk.TOP, expand=False, fill=tk.X)                
            for j in range(3):    
                panel = Frame(panel0)  
                panel.pack(side = tk.TOP, expand=True, fill=tk.X)       
                Label( panel, text= "XYZ"[j] + " [m]" ).pack(side = tk.LEFT) 
                self.geom_main_entry[i*3+j] = Entry(panel, textvariable = self.geom_main_var[i*3+j], font=("Consolas",10) , state = "disabled" if (self.same_var.get() and i>0) else "normal" ) 
                self.geom_main_entry[i*3+j].pack(side = tk.RIGHT, expand=True, fill = tk.X)
                self.geom_main_entry[i*3+j].bind("<FocusOut>",  lambda event, i=i, j=j: ( self.on_geom_change(event, i, j) ) )
                self.geom_main_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
                                
            Label( tab, text="segments (N-1) radius /effective/:").pack(side = tk.TOP, expand=False, fill=tk.X)            
            panel = Frame(tab)  
            panel.pack(side = tk.TOP, expand=True, fill=tk.X)    
            Label( panel, text= "r, [cm]" ).pack(side = tk.LEFT)
            self.radi_main_entry[i] = Entry(panel, textvariable = self.sgmt_radi_var[i], font=("Consolas",10) , state = "disabled" if (self.same_var.get() and i>0) else "normal" ) 
            self.radi_main_entry[i].pack(side = tk.RIGHT, expand=True, fill = tk.X)
            self.radi_main_entry[i].bind("<FocusOut>",  lambda event, i=i: ( self.on_segments_radius_change(event, i) ) )
            self.radi_main_entry[i].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
                
            Label( tab, text= "segments (N-1) to compute force:" ).pack(side = tk.TOP, expand=False, fill=tk.X)            
            panel0 = Frame(tab)  
            panel0.pack(side = tk.TOP, expand=False, fill=tk.X)
            for j in range(M):  
                panel = Frame(panel0)  
                panel.pack(side = tk.TOP, expand=True, fill=tk.X)                   
                self.sgmt_forc_entry[i*M+j] = Checkbutton(panel, variable=self.forc_list_var[i*M+j], state = "normal" if ( not (self.same_var.get() and i>0) ) else "disabled" ,  command=self.update_plot ) 
                self.sgmt_forc_entry[i*M+j].pack(side = tk.LEFT)           
                self.list_forc_entry[i*M+j] = Entry(panel, textvariable = self.sgmt_forc_var[i*M+j], font=("Consolas",10) , state = "disabled" if ((self.same_var.get() and i>0) or not (self.forc_list_var[i*M+j].get())) else "normal" ) 
                self.list_forc_entry[i*M+j].pack(side = tk.RIGHT, expand=True, fill = tk.X)
                self.list_forc_entry[i*M+j].bind("<FocusOut>",  lambda event, i=i, j=j: ( self.on_force_segments_change(event, i, j) ) )
                self.list_forc_entry[i*M+j].config(validate="key", validatecommand=(self.register(int_array_input_validate), '%P'))                 
                           
                             
            Label( tab, text="points to compute field:").pack(side = tk.TOP, expand=False, fill=tk.X)
            panel0 = Frame(tab)  
            panel0.pack(side = tk.TOP, expand=False, fill=tk.X)
            for j in range(3):
                panel = Frame(panel0)  
                panel.pack(side = tk.TOP, expand=True, fill=tk.X)
                Label( panel, text= "XYZ"[j] + " [m]" ).pack(side = tk.LEFT) 
                self.feld_entry[i*3+j] = Entry(panel, textvariable = self.geom_feld_var[i*3+j], width=15, font=("Consolas",10) , state = "disabled" if (self.same_var.get() and i>0) else "normal" ) 
                self.feld_entry[i*3+j].pack(side = tk.RIGHT, expand=True, fill = tk.X)
                self.feld_entry[i*3+j].bind("<FocusOut>",  lambda event, i=i, j=j: ( self.on_geom_change(event, i, j) ) )
                self.feld_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
               
        tab = Frame(self.tabControl) 
        self.tabControl.add(tab, text = "CONNECTORS") 
        self.tabControl.tab(3, state = "normal" if self.auto_conn_var.get() else "disabled")           
                   
        for i in range(4): 
            self.conn_panel[i] = Frame(tab)
            self.conn_panel[i].pack(side = tk.TOP, expand=False, fill=tk.X)
            panel = Frame(self.conn_panel[i])     
            panel.pack(side = tk.LEFT, expand=False, fill=tk.X)          
            if i == 0:
                Label(panel, text = " ").pack(side = tk.TOP, expand=True, fill=tk.X) 
                
            Label(panel, text = " ").pack(side = tk.TOP, expand=True, fill=tk.X) 
            for j in range(3):   
                Label(panel, text = "ABCS"[i] if (j==1) else " ").pack(side = tk.TOP, expand=True, fill=tk.X)     
           
            panel = Frame(self.conn_panel[i])       
            panel.pack(side = tk.LEFT, expand=False, fill=tk.X)     
            if i == 0:                
                Label(panel, text = " ").pack(side = tk.TOP, expand=True, fill=tk.X) 
            Label(panel, text = " ").pack(side = tk.TOP, expand=True, fill=tk.X)    
            for j in range(3):   
                Label(panel, text = "XYZ"[j] + " [m]").pack(side = tk.TOP, expand=True, fill=tk.X)     
        
            self.srce_panel[i] = Frame(self.conn_panel[i])  
            self.srce_panel[i].pack(side = tk.LEFT, expand=False, fill=tk.X)                  
            if i == 0:
                self.auto_source_entry = Checkbutton(self.srce_panel[i], variable=self.auto_srce_var, text = "auto source point",  command=self.update_plot ).pack(side = tk.TOP, expand=True, fill=tk.X)                
            
            Label(self.srce_panel[i], text = " ").pack(side = tk.TOP, expand=True, fill=tk.X) 
            for j in range(3):    
                self.geom_srce_entry[i*3+j] = Entry(self.srce_panel[i], textvariable = self.geom_srce_var[i*0+j] if i<3 else self.geom_splt_var[i*0+j], font=("Consolas",10) , state = "disabled" if (i>0 or self.auto_srce_var.get()) else "normal" ) 
                self.geom_srce_entry[i*3+j].pack(side = tk.TOP, expand=True, fill=tk.X)
                self.geom_srce_entry[i*3+j].bind("<FocusOut>",  lambda event, j=j: ( self.on_geom_source_change(event, j) ) )
                self.geom_srce_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
        
            self.splt_panel[i] = Frame(self.conn_panel[i])  
            self.splt_panel[i].pack(side = tk.LEFT, expand=False, fill=tk.X)    
            if i == 0:
                self.auto_split_entry = Checkbutton(self.splt_panel[i], variable=self.auto_splt_var, text = "auto split point",  command=self.update_plot ).pack(side = tk.TOP, expand=True, fill=tk.X)                
            
            Label(self.splt_panel[i], text = " ").pack(side = tk.TOP, expand=True, fill=tk.X) 
            for j in range(3):    
                self.geom_splt_entry[i*3+j] = Entry(self.splt_panel[i], textvariable = self.geom_splt_var[i*0+j] if i<N else None, font=("Consolas",10) , state = "disabled" if (i>0 or self.auto_srce_var.get()) else "normal" ) 
                self.geom_splt_entry[i*3+j].pack(side = tk.TOP, expand=True, fill=tk.X)
                self.geom_splt_entry[i*3+j].bind("<FocusOut>",  lambda event, j=j: ( self.on_geom_source_change(event, j) ) )
                self.geom_splt_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
            
            panel = Frame(self.conn_panel[i])  
            panel.pack(side = tk.LEFT, expand=True, fill=tk.X)                
            if i == 0:
                panel1 = Frame(panel)  
                panel1.pack(side = tk.TOP, expand=True, fill=tk.X)       
                self.auto_ext_ss_entry = Checkbutton(panel1, variable=self.auto_scon_var, text = "auto path",  command=self.update_plot )
                self.auto_ext_ss_entry.pack(side = tk.LEFT)              
               
            self.auto_srol_entry[i] = Spinbox(panel, textvariable=self.auto_srol_var[i], width=5 ,from_=0, to=5, increment=1, command = self.update_plot )
            self.auto_srol_entry[i].pack(side = tk.TOP, expand=True, fill=tk.X)          
            for j in range(3):    
                self.geom_scon_entry[i*3+j] = Entry(panel, textvariable = self.geom_scon_var[i*3+j], font=("Consolas",10) , state = "disabled" if (i>=N or self.auto_scon_var.get()) else "normal" ) 
                self.geom_scon_entry[i*3+j].pack(side = tk.TOP, expand=True, fill=tk.X)
                self.geom_scon_entry[i*3+j].bind("<FocusOut>",  lambda event, i=i, j=j: ( self.on_geom_ext_ss_change(event, i, j) ) )
                self.geom_scon_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
                
            panel = Frame(self.conn_panel[i])  
            panel.pack(side = tk.LEFT, expand=False, fill=tk.X)                
            if i == 0:                
                Label(panel, text = "start").pack(side = tk.TOP, expand=True, fill=tk.X)
                
            Label(panel, text = " ").pack(side = tk.TOP, expand=True, fill=tk.X) 
            for j in range(3):    
                entry = Entry(panel, textvariable = self.geom_main_var[i*3+j] if i<3 else self.geom_srce_var[i*0+j], font=("Consolas",10), width=8  , state = "disabled" ) 
                entry.bind('<Leave>', lambda event : (event.widget.xview_moveto(0)))
                entry.pack(side = tk.TOP, expand=True, fill=tk.X, anchor='e')
                
            panel = Frame(self.conn_panel[i])  
            panel.pack(side = tk.RIGHT, expand=False, fill=tk.X)               
            if i == 0:
                self.auto_ground_entry = Checkbutton(panel, variable=self.auto_shrt_var, text = "auto short point", command=self.update_plot ).pack(side = tk.TOP, expand=True, fill=tk.X)        
            
            Label(panel, text = " ").pack(side = tk.TOP, expand=True, fill=tk.X) 
            for j in range(3):    
                self.geom_shrt_entry[i*3+j] = Entry(panel, textvariable = self.geom_shrt_var[i*0+j] if i<3 else None, font=("Consolas",10) , state = "disabled" if (i>0 or self.auto_shrt_var.get()) else "normal" ) 
                self.geom_shrt_entry[i*3+j].pack(side = tk.TOP, expand=True, fill=tk.X)
                self.geom_shrt_entry[i*3+j].bind("<FocusOut>",  lambda event, j=j: ( self.on_geom_ground_change(event, j) ) )
                self.geom_shrt_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
        
            panel = Frame(self.conn_panel[i])  
            panel.pack(side = tk.RIGHT, expand=True, fill=tk.X)       
                
            if i == 0:
                panel1 = Frame(panel)  
                panel1.pack(side = tk.TOP, expand=True, fill=tk.X)   
                self.auto_ext_eg_entry = Checkbutton(panel1, variable=self.auto_econ_var, text = "auto path", command=self.update_plot )
                self.auto_ext_eg_entry.pack(side = tk.LEFT)
                
            self.auto_erol_entry[i] = Spinbox(panel, textvariable=self.auto_erol_var[i], width=5, from_=0, to=5, increment=1, command = self.update_plot)
            self.auto_erol_entry[i].pack(side = tk.TOP, expand=True, fill=tk.X)
            for j in range(3):    
                self.geom_econ_entry[i*3+j] = Entry(panel, textvariable = self.geom_econ_var[i*3+j], font=("Consolas",10) , state = "disabled" if (i>=N or self.auto_econ_var.get()) else "normal" ) 
                self.geom_econ_entry[i*3+j].pack(side = tk.TOP, expand=True, fill=tk.X)
                self.geom_econ_entry[i*3+j].bind("<FocusOut>",  lambda event, i=i, j=j: ( self.on_geom_ext_eg_change(event, i, j) ) )
                self.geom_econ_entry[i*3+j].config(validate="key", validatecommand=(self.register(float_array_input_validate), '%P'))
                    
            panel = Frame(self.conn_panel[i])  
            panel.pack(side = tk.RIGHT, expand=False, fill=tk.X)                
            if i == 0:                
                Label(panel, text = "end").pack(side = tk.TOP, expand=True, fill=tk.X) 
            
            Label(panel, text = " ").pack(side = tk.TOP, expand=True, fill=tk.X)     
            for j in range(3):    
                entry = Entry(panel, textvariable = self.geom_main_var[i*3+j] if i<3 else StringVar(), font=("Consolas",10), width=8 , state = "disabled" ) 
                entry.xview_moveto(1)
                entry.bind('<Leave>', lambda event : (event.widget.xview_moveto(1)))
                entry.pack(side = tk.TOP, expand=True, fill=tk.X, anchor='w')       
            
        panel = Frame(tab)
        panel.pack(side = tk.BOTTOM, expand=False, fill=tk.X)               
        Label(panel, text = "conn.segments radius /effective/, r [cm]:").pack(side = tk.LEFT) 
        entry = Entry(panel, textvariable = self.radi_conn_var, font=("Consolas",10), width=8  ) 
        entry.bind("<FocusOut>",  lambda : ( self.on_float_entry_change(entry) ) )                
        entry.pack(side = tk.LEFT)   
        check = Checkbutton(panel, variable=self.forc_conn_var, text = "compute force on connectors", command=self.update_plot )
        check.pack(side = tk.LEFT)      
    
                 
    def auto_var_update(self):        
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        P = str_to_int(self.pcnt_var.get())
        
        if self.same_var.get():  
            for i in range(3):            
                self.sgmt_radi_var[i].set( flt_arr_to_str( np.array( str_to_flt_arr(self.sgmt_radi_var[0].get()) ) ) )
                for j in range(3):     
                    self.geom_main_var[i*3+j].set( flt_arr_to_str( np.array( str_to_flt_arr(self.geom_main_var[0*3+j].get()) )  + str_to_flt(self.pdst_var.get())*i*(j==0) ) )          
                    self.geom_feld_var[i*3+j].set( flt_arr_to_str( np.array( str_to_flt_arr(self.geom_feld_var[0*3+j].get()) )  + str_to_flt(self.pdst_var.get())*i*(j==0)   ) )             
                for j in range(M):                
                    self.sgmt_forc_var[i*M+j].set( int_arr_to_str( np.array( str_to_int_arr(self.sgmt_forc_var[0*M+j].get()) ) ) ) 
                    self.forc_list_var[i*M+j].set(self.forc_list_var[0*M+j].get()) 
             
        if self.auto_conn_var.get():       
            if self.auto_shrt_var.get():
                for j in range(3):
                    self.geom_shrt_var[j].set( value = flt_to_str( sum( [ str_to_flt_arr(self.geom_main_var[i*3+j].get())[-1] for i in range(P) ] ) /P ) )    
                    
            if self.auto_econ_var.get(): 
                for i in range(3):    
                    XYZ = self.auto_path([ str_to_flt_arr(self.geom_main_var[i*3+j].get())[-1]  for j in range(3) ], 
                                        [ str_to_flt(self.geom_shrt_var[j].get())              for j in range(3) ], 
                                        int(self.auto_erol_var[i].get()) )               
                    for j in range(3):
                        self.geom_econ_var[i*3+j].set( flt_arr_to_str(XYZ[j::3]) )     
                    
            if (P == 3 and not self.schema == "ABC"):   
                N = "ABC".find(self.schema[0])
                if self.auto_splt_var.get():
                    for j in range(3):
                        self.geom_splt_var[j].set( value= flt_to_str( sum( [str_to_flt_arr(self.geom_main_var[i*3+j].get())[0] for i in range(P) if not i==N] ) / 2 ) )  
                        
                if self.auto_srce_var.get():
                    for j in range(3):
                        self.geom_srce_var[j].set( value= flt_to_str( str_to_flt_arr(self.geom_main_var[N*3+j].get())[0]/2 + str_to_flt_arr(self.geom_splt_var[j].get())[0]/2 ) )  
                
                if self.auto_scon_var.get(): 
                    for i in range(3):         
                        XYZ = self.auto_path( 
                                            [ str_to_flt(self.geom_srce_var[j].get() if i == N else self.geom_splt_var[j].get()) for j in range(3) ] , 
                                            [ str_to_flt_arr(self.geom_main_var[i*3+j].get())[0] for j in range(3) ], 
                                            int(self.auto_srol_var[i].get()) )                    
                        for j in range(3):
                            self.geom_scon_var[i*3+j].set( flt_arr_to_str(XYZ[j::3]) ) 
                    i = 3     
                    XYZ = self.auto_path( 
                                        [ str_to_flt(self.geom_splt_var[j].get()) for j in range(3) ], 
                                        [ str_to_flt(self.geom_srce_var[j].get()) for j in range(3) ], 
                                        int(self.auto_srol_var[i].get()) )             
                    for j in range(3):
                        self.geom_scon_var[i*3+j].set( flt_arr_to_str(XYZ[j::3]) )            
            else:
                N = 0
                if self.auto_srce_var.get():
                    for j in range(3):
                        self.geom_srce_var[j].set( value= flt_to_str( sum( [ str_to_flt_arr(self.geom_main_var[i*3+j].get())[0] for i in range(P) ] ) / P ) )  
                
                if self.auto_scon_var.get(): 
                    for i in range(3):          
                        XYZ = self.auto_path( 
                                            [ str_to_flt(self.geom_srce_var[j].get()) for j in range(3) ], 
                                            [ str_to_flt_arr(self.geom_main_var[i*3+j].get())[0] for j in range(3) ], 
                                            int(self.auto_srol_var[i].get()) )                    
                        for j in range(3):
                            self.geom_scon_var[i*3+j].set( flt_arr_to_str(XYZ[j::3]) )     

    def update(self):   
        self.auto_var_update()
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        P = str_to_int(self.pcnt_var.get())
        self.tabControl.tab(3, state = "normal" if self.auto_conn_var.get() else "disabled")
        self.pdst_entry.config(state = "normal" if self.same_var.get() else "disabled")
                
        if (P == 3 and not self.schema == "ABC"):                        
            N = "ABC".find(self.schema[0])
            for i in range(4):
                self.splt_panel[i].pack(after = self.srce_panel[i], side = tk.LEFT, expand=False, fill=tk.X)    
                self.conn_panel[i].pack(side = tk.TOP, expand=False, fill=tk.X)
                for j in range(3):
                    if i<3:
                        self.geom_srce_entry[i*3+j].config( textvariable = self.geom_srce_var[i*0+j] if i==N else StringVar() )
                        self.geom_splt_entry[i*3+j].config( textvariable = self.geom_splt_var[i*0+j] if not i==N else StringVar() )
                    else:
                        self.geom_srce_entry[i*3+j].config(state = "disabled" if self.auto_splt_var.get() else "normal")    
            self.conn_panel[3].pack(after = self.conn_panel[2], side = tk.TOP, expand=False, fill=tk.X)
        else:
            N = 0
            for i in range(3):
                self.splt_panel[i].pack_forget()
                for j in range(3):
                    self.geom_srce_entry[i*3+j].config( textvariable = self.geom_srce_var[i*0+j]  )
                    self.geom_splt_entry[i*3+j].config( textvariable =  StringVar() )
                if i<P:
                    self.conn_panel[i].pack(side = tk.TOP, expand=False, fill=tk.X)
                else:
                    self.conn_panel[i].pack_forget()     
            self.conn_panel[3].pack_forget()  
                
        for i in range(4):
            self.auto_srol_entry[i].config(state = "normal" if (self.auto_scon_var.get()) else "disabled" )
            self.auto_erol_entry[i].config(state = "normal" if (self.auto_econ_var.get()) else "disabled" )
            
        for i in range(3):
            self.tabControl.tab(i, state = "normal" if i<P else "disabled")                
            for j in range(3):                    
                self.geom_shrt_entry[i*3+j].config(state = "disabled" if (not i==N or self.auto_shrt_var.get()) else "normal" )
                self.geom_srce_entry[i*3+j].config(state = "disabled" if (not i==N or self.auto_srce_var.get()) else "normal")
                self.geom_econ_entry[i*3+j].config(state = "disabled" if (i>=P or self.auto_econ_var.get()) else "normal")
                self.geom_scon_entry[i*3+j].config(state = "disabled" if (i>=P or self.auto_scon_var.get()) else "normal")
                self.geom_main_entry[i*3+j].config(state = "disabled" if (self.same_var.get() and i>0) else "normal" )                
            for j in range(M):
                self.sgmt_forc_entry[i*M+j].config(state = "disabled" if (self.same_var.get() and i>0) else "normal")
                self.list_forc_entry[i*M+j].config(state = "disabled" if ((self.same_var.get() and i>0) or not (self.forc_list_var[i*M+j].get())) else "normal")

        ( self.valid, plotable ) = self.check()
        if (plotable):
            self.geometry = self.construct_geom()
        else:
            self.geometry = None
            
    def auto_path(self, SXYZ, EXYZ, roll):
        LXYZ = np.array([])
        DXYZ = np.array(EXYZ) - np.array(SXYZ)
        n = np.count_nonzero(DXYZ)
        if n>1:
            XYZ = np.array(SXYZ)
            IJK = np.arange(3)
            IJK = IJK[np.nonzero(DXYZ)]
            DXYZ = DXYZ[np.nonzero(DXYZ)]       
            idx = np.array(list(itertools.permutations(range(n))))            
            IJK = IJK[idx[roll%len(idx)]]
            DXYZ = DXYZ[idx[roll%len(idx)]]  
            for d,j in zip(DXYZ[:-1], IJK[:-1]):
                XYZ[j] = XYZ[j]+d
                LXYZ = np.append(LXYZ, XYZ)
        return LXYZ
                
    def update_plot(self):     
        self.update()
        self.update_plot_callback(self.geometry)
        self.app.control_exct_panel.update_plot()
       
    def check_directions(self, flt_arr):                
        dL2 = 0
        dD = 0
        for j in range(3):
            X = np.array( flt_arr[j] )
            dX = np.diff(X)
            dL2 = dL2 + dX**2
            dD = dD + abs(dX)
        return not ( any( ( dL2**0.5 - dD ) != 0) )
        
    def check(self):
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        P = str_to_int(self.pcnt_var.get())
        N = "ABC".find(self.schema[0]) if (P == 3 and not self.schema == "ABC") else -1
        result = True
        dimension = True
        direction = True
        self.error_message = ""
                
        for i in range(P):
            check1 = True
            check2 = True
            check3 = True
            check4 = True
            check5 = True
            check1_1 = True
            check3_1 = True
            check4_1 = True
            check5_1 = True
            
            N1 = -1
            N2 = -1
            N3 = -1
            N4 = -1
            N5 = -1
                            
            N1 = length_str_arr(self.sgmt_radi_var[i].get()) + 1 if N1==-1 else N1               
            for j in range(M):       
                N1 = length_str_arr(self.sgmt_forc_var[i*M+j].get()) + 1 if N1==-1 and self.forc_list_var[i*M+j].get() else N1
                check1 = check1 and ( length_str_arr(self.sgmt_forc_var[i*M+j].get())==N1-1 or not self.forc_list_var[i*M+j].get() )
                                   
            for j in range(3):               
                N1 = length_str_arr(self.geom_main_var[i*3+j].get()) if N1==-1 else N1
                N2 = length_str_arr(self.geom_feld_var[i*3+j].get()) if N2==-1 else N2
                N3 = length_str_arr(self.geom_econ_var[i*3+j].get()) if N3==-1 else N3
                N4 = length_str_arr(self.geom_scon_var[i*3+j].get()) if N4==-1 else N4   
                N5 = length_str_arr(self.geom_scon_var[3*3+j].get()) if N5==-1 else N5
                    
                check1 = check1 and ( length_str_arr(self.geom_main_var[i*3+j].get())==N1 )     
                check2 = check2 and ( length_str_arr(self.geom_feld_var[i*3+j].get())==N2 )
                check3 = check3 and ( length_str_arr(self.geom_econ_var[i*3+j].get())==N3 or not self.auto_conn_var.get() )
                check4 = check4 and ( length_str_arr(self.geom_scon_var[i*3+j].get())==N4 or not self.auto_conn_var.get() )
                check5 = check5 and ( length_str_arr(self.geom_scon_var[3*3+j].get())==N5 or not self.auto_conn_var.get() or not i == N )
               
            check1_1 = check1_1 and ( self.check_directions( [ str_to_flt_arr(self.geom_main_var[i*3+j].get()) for j in range(3) ] ) if check1 else True )
            check3_1 = check3_1 and ( self.check_directions( [ str_to_flt_arr(self.geom_main_var[i*3+j].get().split(",")[-1] + "," + self.geom_econ_var[i*3+j].get() + ("," if N3>0 else "") + self.geom_shrt_var[0*3+j].get() ) for j in range(3) ] ) if check3 and self.auto_conn_var.get() else True )
            check4_1 = check4_1 and ( self.check_directions( [ str_to_flt_arr( ( self.geom_srce_var[0*3+j].get() if N<0 or i == N else self.geom_splt_var[0*3+j].get() ) + ("," if N4>0 else "") + self.geom_scon_var[i*3+j].get() + "," + self.geom_main_var[i*3+j].get().split(",")[0]) for j in range(3) ] ) if check4 and self.auto_conn_var.get() else True )
            check5_1 = check5_1 and ( self.check_directions( [ str_to_flt_arr( self.geom_splt_var[0*3+j].get()   + ("," if N5>0 else "") + self.geom_scon_var[3*3+j].get() + "," + self.geom_srce_var[0*3+j].get() ) for j in range(3)] ) if check5 and self.auto_conn_var.get() and i == N else True )
                                    
            color1 = "pink" if not check1 else "white"
            color2 = "pink" if not check2 else "white"
            color3 = "pink" if not (check3 and check3_1) else "white"
            color4 = "pink" if not (check4 and check4_1) else "white"
            color5 = "pink" if not (check5 and check5_1) else "white"
            color0 = "pink" if not (check1 and check1_1) else "white"
            
            self.radi_main_entry[i].config(background = color1)
            for j in range(M):        
                self.list_forc_entry[i*M+j].config(background = color1)
            for j in range(3):    
                self.geom_main_entry[i*3+j].config(background = color0)
                self.feld_entry[i*3+j].config(background = color2)
                self.geom_econ_entry[i*3+j].config(background = color3)
                self.geom_scon_entry[i*3+j].config(background = color4)                
                if i == N:
                    self.geom_scon_entry[3*3+j].config(background = color5)
                
            dimension = dimension * check1*check2*check3*check4*check5
            direction = direction * check1_1*check3_1*check4_1*check5_1
            
        result = dimension*direction
        if not result:
            self.status = self.STATUS_ERROR
            self.error_message = ""
            self.error_message = self.error_message + \
                ( "\n Dimension must agree!" if not dimension else "") + \
                ( "\n Only segments along the axis (horizontal or vertical) allowed!" if not direction else "")
            
            self.error_btn.config(text="ERROR", background="red")
        else:            
            self.status = self.STATUS_OK
            self.error_btn.config(text="OK", background="green")
            
        return ( result, dimension )
    
    def save_file(self):        
        filename = filedialog.asksaveasfilename(
            title='Save as file', defaultextension="txt", initialdir=os.getcwd() )
        self.save(file = filename)
                
    def save(self, file = "work.geom.txt"):   
        self.update_plot() 
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        N = str_to_int( self.pcnt_var.get() )
        sub = self.SUBFIELD_SEPARATOR
        f = open(file, "w")
        f.write('\n'.join([ 
                    '\n'.join([ 
                        ''.join([self.GEOM_MAIN_VN,sub,'ABC'[i],sub,'XYZ'[j],' = [', self.geom_main_var[i*3+j].get(), ']'])
                    for j in range(3) ])
                for i in range(3)  ]) ); f.write( '\n' )
        f.write('\n'.join([
                    '\n'.join([
                        ''.join([self.GEOM_FELD_VN,sub,'ABC'[i],sub,'XYZ'[j],' = [', self.geom_feld_var[i*3+j].get(), ']'])
                    for j in range(3) ])
                for i in range(3)  ]) ); f.write( '\n' )
        f.write('\n'.join([
                    '\n'.join([
                        ''.join([self.MASK_FORC_VN,sub,'ABC'[i],sub,'%d' % j,' = [', self.sgmt_forc_var[i*M+j].get(), ']']) 
                    for j in range(M) if self.forc_list_var[i*M+j].get() ]) 
                for i in range(3)  ]) ); f.write( '\n' )
        f.write('\n'.join([
                        ''.join([self.MAIN_RADI_VN,sub,'ABC'[i],sub, ' = [', self.sgmt_radi_var[i].get(), ']']) 
                for i in range(3)  ]) ); f.write( '\n' )
        f.write( ''.join([self.POLS_X_TR_VN,     ' = ',           self.pdst_var.get() ]) );                  f.write( '\n' )
        f.write( ''.join([self.POLS__CNT_VN,     ' = ',           self.pcnt_var.get() ]) );                  f.write( '\n' )
        f.write( ''.join([self.POLS_SAME_VN,     ' = ', 'True' if self.same_var.get()      else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.POLS_CONN_VN,     ' = ', 'True' if self.auto_conn_var.get() else 'False']) ); f.write( '\n' )
                
        f.write( ''.join([self.AUTO_SRCE_VN,' = ', 'True' if self.auto_srce_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.AUTO_SPLT_VN,' = ', 'True' if self.auto_splt_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.AUTO_NEUT_VN,' = ', 'True' if self.auto_shrt_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.AUTO_SCON_VN,' = ', 'True' if self.auto_scon_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.AUTO_NCON_VN,' = ', 'True' if self.auto_econ_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.CONN_FORC_VN,' = ', 'True' if self.forc_conn_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.CONN_RADI_VN,' = ',           self.radi_conn_var.get() ]) );             f.write( '\n' )
        
        f.write( ''.join([self.GEOM_SRCE_VN,' = [', 
                    ',\t'.join( [ self.geom_srce_var[0*3+j].get() for j in range(3)] ) , ']'] ) ) ; f.write( '\n' )  
        f.write( ''.join([self.GEOM_SPLT_VN,' = [',
                    ',\t'.join( [ self.geom_splt_var[0*3+j].get() for j in range(3)] ) , ']'] ) ) ; f.write( '\n' )  
        f.write( ''.join([self.GEOM_NEUT_VN,' = [',
                    ',\t'.join( [ self.geom_shrt_var[0*3+j].get() for j in range(3)] ) , ']'] ) ) ; f.write( '\n' )         
        
        f.write('\n'.join([
                    '\n'.join([
                        ''.join([self.GEOM_SCON_VN,sub,'ABCS'[i],sub,'XYZ'[j],' = [', self.geom_scon_var[i*3+j].get(), ']'])
                    for j in range(3) ])
                for i in range(4)  ]) ); f.write( '\n' ) 
        f.write('\n'.join([
                    '\n'.join([
                        ''.join([self.GEOM_NCON_VN,sub, 'ABC'[i],sub,'XYZ'[j],' = [', self.geom_econ_var[i*3+j].get(), ']'])
                    for j in range(3) ])
                for i in range(3)  ]) ); f.write( '\n' ) 
                
        f.write( ''.join([self.AUTO_SROL_VN,' = [',
                    ',\t'.join( [ self.auto_srol_var[i].get() for i in range(4) ] ) , ']'] ) ) ; f.write( '\n' )       
        f.write( ''.join([self.AUTO_EROL_VN,' = [',
                    ',\t'.join( [ self.auto_erol_var[i].get() for i in range(3) ] ) , ']'] ) ) ; f.write( '\n' )       
        
        f.close()
       
    def load_file(self):
        filename = filedialog.askopenfilename(
            title='Open a file', defaultextension="txt", initialdir=os.getcwd() )
        self.load(file = filename)
        self.update_plot() 
        
    def init(self):
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
          
        self.forc_list_var = [BooleanVar() for i in range(M*3)]  
        self.sgmt_forc_var = [StringVar() for i in range(M*3) ]    
        self.sgmt_radi_var = [StringVar() for i in range(3) ]    
        self.geom_main_var = [StringVar() for i in range(3*3) ]
        self.geom_feld_var = [StringVar() for i in range(3*3) ]   
        self.geom_scon_var = [StringVar() for i in range(3*4) ]
        self.geom_econ_var = [StringVar() for i in range(3*4) ]
        self.geom_shrt_var = [StringVar() for i in range(3) ]
        self.geom_srce_var = [StringVar() for i in range(3) ]
        self.geom_splt_var = [StringVar() for i in range(3) ]
        self.auto_conn_var = BooleanVar(value = False)        
        self.pcnt_var = StringVar(value = '3')        
        self.same_var = BooleanVar(value = True)
        self.pdst_var = StringVar(value = '0.1')   
        self.auto_srce_var = BooleanVar(value = True)
        self.auto_shrt_var = BooleanVar(value = True)
        self.auto_splt_var = BooleanVar(value = True)
        self.auto_econ_var = BooleanVar(value = True)
        self.auto_scon_var = BooleanVar(value = True)
        self.auto_erol_var = [ StringVar() for i in range(4) ]
        self.auto_srol_var = [ StringVar() for i in range(4) ]        
        self.radi_conn_var = StringVar(value = '2')
        self.forc_conn_var = BooleanVar(value = True)
                
        #default sample geom:
        X: float = [  0.0,  0.0,  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]      
        Y: float = [ -0.5, -0.5, -0.5, 0.1, 0.1, 0.1, 0.4, 0.4, 0.5, 0.5, 0.5 ]   
        Z: float = [  1.0,  0.4,  0.3, 0.3, 0.1, 0.0, 0.0, 0.1, 0.1, 0.5, 1.0 ]                       
        self.sgmt_radi_var[0].set (value= flt_arr_to_str( [2]*(len(X)-1) ) )        
        self.geom_main_var[0*3+0].set( flt_arr_to_str( X ) )     
        self.geom_main_var[0*3+1].set( flt_arr_to_str( Y ) )     
        self.geom_main_var[0*3+2].set( flt_arr_to_str( Z ) )                 
        self.geom_feld_var[0*3+0].set( '0' )               
        self.geom_feld_var[0*3+1].set( '0' )               
        self.geom_feld_var[0*3+2].set( '0' )    
        self.forc_list_var[0*M+0].set( True)
        self.sgmt_forc_var[0*M+0].set( int_arr_to_str( [0] + [1]*(len(X)-3) + [0] ) )
              
        
    def load(self, file = "work.geom.txt"):       
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        sub = self.SUBFIELD_SEPARATOR        

        #default values, on case missing in file:
        self.auto_conn_var.set(value = False)        
        self.pcnt_var.set(value = '3')        
        self.same_var.set(value = True)
        self.pdst_var.set(value = '0.1')   
        self.auto_srce_var.set(value = True)
        self.auto_shrt_var.set(value = True)
        self.auto_splt_var.set(value = True)
        self.auto_econ_var.set(value = True)
        self.auto_scon_var.set(value = True)    
        self.radi_conn_var.set(value = '2')
        self.forc_conn_var.set(value = False)
                       
        #try to load from file
        if os.path.exists(file):        
            forc_segs_var = None
            with open(file) as f:
                for l in f:
                    if not l.strip()=="":
                        (key, val) = tuple([ s.strip() for s in l.split('=') ])
                        val =  val.strip('[]') 
                        print(key, '=', val ) 
                        if key.find(sub)>0:
                            (nam, phs, idx) = tuple([ s.strip() for s in key.split(sub) ])
                            i = 'ABCS'.find(phs)
                            try:
                                j = int(idx)
                            except ValueError:
                                j = 'XYZ'.find(idx)
                                
                            if (nam == self.GEOM_MAIN_VN):
                                self.geom_main_var[i*3+j].set(val)
                            elif (nam == self.GEOM_FELD_VN):
                                self.geom_feld_var[i*3+j].set(val)
                            elif (nam == self.MASK_FORC_VN):
                                self.sgmt_forc_var[i*M+j].set(val)
                                if forc_segs_var == None:
                                    forc_segs_var = [BooleanVar(value = False) for i in range(M*3)]
                                forc_segs_var[i*M+j].set(True)
                            elif (nam == self.MAIN_RADI_VN):
                                self.sgmt_radi_var[i].set(val)
                                
                            elif (nam == self.GEOM_SCON_VN):
                                self.geom_scon_var[i*3+j].set(val)
                            elif (nam == self.GEOM_NCON_VN):
                                self.geom_econ_var[i*3+j].set(val)  
                        else:           
                            if (key == self.GEOM_SRCE_VN):
                                for i, v in enumerate(val.split(',\t')):
                                    self.geom_srce_var[i].set(v.strip())
                            elif (key == self.GEOM_SPLT_VN):
                                for i, v in enumerate(val.split(',\t')):
                                    self.geom_splt_var[i].set(v.strip())
                            elif (key == self.GEOM_NEUT_VN):
                                for i, v in enumerate(val.split(',\t')):
                                    self.geom_shrt_var[i].set(v.strip())
                            elif (key == self.AUTO_SROL_VN):
                                for i, v in enumerate(val.split(',\t')):
                                    self.auto_srol_var[i].set(v.strip())
                            elif (key == self.AUTO_EROL_VN):
                                for i, v in enumerate(val.split(',\t')):
                                    self.auto_erol_var[i].set(v.strip())
                            elif (key == self.POLS_X_TR_VN):
                                self.pdst_var.set(val)
                            elif (key == self.POLS__CNT_VN):
                                self.pcnt_var.set(val)
                            elif (key == self.POLS_SAME_VN):
                                self.same_var.set(val=='True')
                            elif (key == self.POLS_CONN_VN):
                                self.auto_conn_var.set(val=='True')
                            elif (key == self.CONN_FORC_VN):
                                self.forc_conn_var.set(val=='True')
                            elif (key == self.CONN_RADI_VN):
                                self.radi_conn_var.set(val)
                            elif (key == self.AUTO_SRCE_VN):
                                self.auto_srce_var.set(val=='True')
                            elif (key == self.AUTO_SPLT_VN):
                                self.auto_splt_var.set(val=='True')
                            elif (key == self.AUTO_NEUT_VN):
                                self.auto_shrt_var.set(val=='True')
                            elif (key == self.AUTO_SCON_VN):
                                self.auto_scon_var.set(val=='True')
                            elif (key == self.AUTO_NCON_VN):
                                self.auto_econ_var.set(val=='True')
                                       
            for i in range(3):                               
                for j in range(M):    
                    if forc_segs_var==None: 
                        self.forc_list_var[i*M+j].set( False )
                        seg = len(self.geom_main_var[i*3+0].get().split(','))-1
                        self.sgmt_forc_var[i*M+j].set( int_arr_to_str( [0] + [1]*(seg-2) + [0] ) )  
                        
                    else:                         
                        self.forc_list_var[i*M+j].set(forc_segs_var[i*M+j].get())    
                        if not forc_segs_var[i*M+j].get():
                            seg = len(self.geom_main_var[i*3+0].get().split(','))-1
                            self.sgmt_forc_var[i*M+j].set( int_arr_to_str( [0]*seg ) )  
                            
                        
    def show_errors(self):       
        if self.status == self.STATUS_OK:
            messagebox.showinfo(self.STATUS_OK, "") 
        else:
            messagebox.showerror(self.STATUS_ERROR, self.error_message) 
        
    def on_change(self, event=None):            
        self.update_plot()
        
    def on_geom_change(self, event=None, i = 0, j = 0):     
        XYZ = str_to_flt_arr(self.geom_main_var[i*3+j].get())       
        self.geom_main_var[i*3+j].set( flt_arr_to_str(XYZ) )         
        self.update_plot()            
        
    def on_geom_ext_eg_change(self, event=None, i = 0, j = 0):     
        XYZ = str_to_flt_arr(self.geom_econ_var[i*3+j].get())       
        self.geom_econ_var[i*3+j].set( flt_arr_to_str(XYZ) )         
        self.update_plot()            
        
    def on_geom_ext_ss_change(self, event=None, i = 0, j = 0):     
        XYZ = str_to_flt_arr(self.geom_scon_var[i*3+j].get())       
        self.geom_scon_var[i*3+j].set( flt_arr_to_str(XYZ) )         
        self.update_plot()     
        
    def on_geom_ground_change(self, event=None, j = 0):     
        XYZ = str_to_flt(self.geom_shrt_var[0*3+j].get())       
        self.geom_shrt_var[0*3+j].set( flt_to_str(XYZ) )         
        self.update_plot()            
        
    def on_float_entry_change(self, entry : tk.Entry):     
        XYZ = str_to_flt(entry.get())       
        entry.set( flt_to_str(XYZ) )         
        self.update_plot()      
        
    def on_geom_source_change(self, event=None, j = 0):     
        XYZ = str_to_flt(self.geom_srce_var[0*3+j].get())       
        self.geom_srce_var[0*3+j].set( flt_to_str(XYZ) )         
        self.update_plot()         
                
    def on_segments_radius_change(self, event=None, i =0 ):     
        rad = str_to_flt_arr(self.sgmt_radi_var[i].get())       
        self.sgmt_radi_var[i].set( flt_arr_to_str(rad) )         
        self.update_plot()            
            
    def on_force_segments_change(self, event=None, i = 0, j = 0):     
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        FRC = str_to_int_arr(self.sgmt_forc_var[i*M+j].get())       
        self.sgmt_forc_var[i*M+j].set( int_arr_to_str(FRC) )     
        self.update_plot()
                    
    def construct_geom(self):
        M = ControlGeomPanel.MAX_FORCE_PER_PHASE
        P = str_to_int(self.pcnt_var.get())
        extra = self.auto_conn_var.get()
        N = "ABC".find(self.schema[0]) if (P == 3 and not self.schema == "ABC") else -1
        
        conductors = []
        for i in range(P):
            main = geometry.Conductor(
                str_to_flt_arr(self.geom_main_var[i*3+0].get()),
                str_to_flt_arr(self.geom_main_var[i*3+1].get()),
                str_to_flt_arr(self.geom_main_var[i*3+2].get()),
                i,
                [ str_to_int_arr(self.sgmt_forc_var[k*M+j].get()) for j in range(M) if self.forc_list_var[i*M+j].get() ],                
                str_to_flt_arr(self.sgmt_radi_var[i].get())
            )
            conductors.append(main)
            if extra:
                sX = [str_to_flt( self.geom_shrt_var[0*3+0].get() )]
                sY = [str_to_flt( self.geom_shrt_var[0*3+1].get() )]
                sZ = [str_to_flt( self.geom_shrt_var[0*3+2].get() )]

                phase_neut_conn = geometry.Conductor(
                    np.concatenate(( [main.X[-1]], str_to_flt_arr(self.geom_econ_var[i*3+0].get()), sX  )) ,
                    np.concatenate(( [main.Y[-1]], str_to_flt_arr(self.geom_econ_var[i*3+1].get()), sY  )) ,
                    np.concatenate(( [main.Z[-1]], str_to_flt_arr(self.geom_econ_var[i*3+2].get()), sZ  )) ,
                    i,
                    1 if self.forc_conn_var.get() else [],                
                    str_to_flt(self.radi_conn_var.get())
                ) 
                conductors.append(phase_neut_conn)
                
                sX = [str_to_flt( self.geom_srce_var[0*3+0].get() if N<0 or i == N else self.geom_splt_var[0*3+0].get() )]
                sY = [str_to_flt( self.geom_srce_var[0*3+1].get() if N<0 or i == N else self.geom_splt_var[0*3+1].get() )]
                sZ = [str_to_flt( self.geom_srce_var[0*3+2].get() if N<0 or i == N else self.geom_splt_var[0*3+2].get() )]
                sF = [] if N<0 or i == N else 1 if self.forc_conn_var.get() else []

                phase_srce_conn = geometry.Conductor(
                    np.concatenate(( sX, str_to_flt_arr(self.geom_scon_var[i*3+0].get()), [main.X[0]] )) ,
                    np.concatenate(( sY, str_to_flt_arr(self.geom_scon_var[i*3+1].get()), [main.Y[0]] )) ,
                    np.concatenate(( sZ, str_to_flt_arr(self.geom_scon_var[i*3+2].get()), [main.Z[0]] )) ,
                    i,
                    sF,                
                    str_to_flt(self.radi_conn_var.get())
                ) 
                conductors.append(phase_srce_conn)
                
                if i == N:
                    phase_srce_conn = geometry.Conductor(
                        np.concatenate(( 
                            [str_to_flt(self.geom_splt_var[0*3+0].get())], 
                            str_to_flt_arr(self.geom_scon_var[3*3+0].get()), 
                            [str_to_flt(self.geom_srce_var[0*3+0].get())] )) ,
                        np.concatenate(( 
                            [str_to_flt(self.geom_splt_var[0*3+1].get())], 
                            str_to_flt_arr(self.geom_scon_var[3*3+1].get()), 
                            [str_to_flt(self.geom_srce_var[0*3+1].get())] )) ,
                        np.concatenate(( 
                            [str_to_flt(self.geom_splt_var[0*3+2].get())], 
                            str_to_flt_arr(self.geom_scon_var[3*3+2].get()), 
                            [str_to_flt(self.geom_srce_var[0*3+2].get())] )) ,
                        i,
                        [],
                        str_to_flt(self.radi_conn_var.get())
                    ) 
                    conductors.append(phase_srce_conn)


        XYZ = [ [] for i in range(3) ]
        for j in range(3):
            for i in range(P):
                XYZ[j] = XYZ[j] + str_to_flt_arr(self.geom_feld_var[i*3+j].get())       


        filedPoints = geometry.WayPoints()
        for i in range(P):
            filedPoints.X = np.append( filedPoints.X, str_to_flt_arr(self.geom_feld_var[i*3+0].get())  )
            filedPoints.Y = np.append( filedPoints.Y, str_to_flt_arr(self.geom_feld_var[i*3+1].get())  )
            filedPoints.Z = np.append( filedPoints.Z, str_to_flt_arr(self.geom_feld_var[i*3+2].get())  )

        return geometry.fromConductorsWP( conductors ,filedPoints )