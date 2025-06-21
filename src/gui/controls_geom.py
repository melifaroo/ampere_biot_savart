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
    GEOM_VAR_NAME : Final = 'GEOM_MAIN'
    FELD_VAR_NAME : Final = 'GEOM_FELD'
    FORC_VAR_NAME : Final = 'SGMT_FORC'
    RADI_VAR_NAME: Final =  'SGMT_RADI'
    SAME_VAR_NAME : Final = 'SAME_GEOM'
    PDST_VAR_NAME : Final = 'POLE_DIST'
    PCNT_VAR_NAME: Final = 'PHASE_CNT'
    CONN_VAR_NAME: Final = 'POLE_CONN'
    
    AUTO_SRCE_VAR_NAME: Final = 'AUTO_SRCE'
    AUTO_SPLT_VAR_NAME: Final = 'AUTO_SPLT'
    AUTO_SHRT_VAR_NAME: Final = 'AUTO_SHRT'
    AUTO_SCON_VAR_NAME: Final = 'AUTO_SCON'
    AUTO_ECON_VAR_NAME: Final = 'AUTO_ECON'
    FORC_CONN_VAR_NAME: Final = 'FORC_CONN'
    RADI_CONN_VAR_NAME: Final = 'RADI_CONN'
    
    GEOM_SRCE_VAR_NAME: Final = 'GEOM_SRCE'
    GEOM_SPLT_VAR_NAME: Final = 'GEOM_SPLT'
    GEOM_SHRT_VAR_NAME: Final = 'GEOM_SHRT'
    
    GEOM_SCON_VAR_NAME: Final = 'GEOM_SCON'
    GEOM_ECON_VAR_NAME: Final = 'GEOM_ECON'
            
    AUTO_SROL_VAR_NAME: Final = 'AUTO_SROL'
    AUTO_EROL_VAR_NAME: Final = 'AUTO_EROL'
     
    
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
        f.write( '\n'.join([ '\n'.join([ ''.join([self.GEOM_VAR_NAME,sub,'ABC'[i],sub,'XYZ'[j],' = [', self.geom_main_var[i*3+j].get(), ']']) for j in range(3)                                    ]) for i in range(3)  ]) ); f.write( '\n' )
        f.write( '\n'.join([ '\n'.join([ ''.join([self.FELD_VAR_NAME,sub,'ABC'[i],sub,'XYZ'[j],' = [', self.geom_feld_var[i*3+j].get(), ']']) for j in range(3)                                    ]) for i in range(3)  ]) ); f.write( '\n' )
        f.write( '\n'.join([ '\n'.join([ ''.join([self.FORC_VAR_NAME,sub,'ABC'[i],sub,'%d' % j,' = [', self.sgmt_forc_var[i*M+j].get(), ']']) for j in range(M) if self.forc_list_var[i*M+j].get() ]) for i in range(3)  ]) ); f.write( '\n' )
        f.write(             '\n'.join([ ''.join([self.RADI_VAR_NAME,sub,'ABC'[i],sub,         ' = [', self.sgmt_radi_var[i]    .get(), ']'])                                                         for i in range(3)  ]) ); f.write( '\n' )
        f.write( ''.join([self.PDST_VAR_NAME,     ' = ',           self.pdst_var.get() ]) );                  f.write( '\n' )
        f.write( ''.join([self.PCNT_VAR_NAME,     ' = ',           self.pcnt_var.get() ]) );                  f.write( '\n' )
        f.write( ''.join([self.SAME_VAR_NAME,     ' = ', 'True' if self.same_var.get()      else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.CONN_VAR_NAME,     ' = ', 'True' if self.auto_conn_var.get() else 'False']) ); f.write( '\n' )
        
        
        f.write( ''.join([self.AUTO_SRCE_VAR_NAME,' = ', 'True' if self.auto_srce_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.AUTO_SPLT_VAR_NAME,' = ', 'True' if self.auto_splt_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.AUTO_SHRT_VAR_NAME,' = ', 'True' if self.auto_shrt_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.AUTO_SCON_VAR_NAME,' = ', 'True' if self.auto_scon_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.AUTO_ECON_VAR_NAME,' = ', 'True' if self.auto_econ_var.get() else 'False']) ); f.write( '\n' )
        f.write( ''.join([self.FORC_CONN_VAR_NAME,' = ', 'True' if self.forc_conn_var.get() else 'False']) ); f.write( '\n' )        
        f.write( ''.join([self.RADI_CONN_VAR_NAME,' = ',           self.radi_conn_var.get() ]) );             f.write( '\n' )
        
        f.write( ''.join([self.GEOM_SRCE_VAR_NAME,' = [', ',\t'.join( [ self.geom_srce_var[0*3+j].get() for j in range(3)] ) , ']'] ) ) ; f.write( '\n' )  
        f.write( ''.join([self.GEOM_SPLT_VAR_NAME,' = [', ',\t'.join( [ self.geom_splt_var[0*3+j].get() for j in range(3)] ) , ']'] ) ) ; f.write( '\n' )  
        f.write( ''.join([self.GEOM_SHRT_VAR_NAME,' = [', ',\t'.join( [ self.geom_shrt_var[0*3+j].get() for j in range(3)] ) , ']'] ) ) ; f.write( '\n' )         
        
        f.write( '\n'.join([ '\n'.join([ ''.join([self.GEOM_SCON_VAR_NAME,sub,'ABCS'[i],sub,'XYZ'[j],' = [', self.geom_scon_var[i*3+j].get(), ']']) for j in range(3) ]) for i in range(4)  ]) ); f.write( '\n' ) 
        f.write( '\n'.join([ '\n'.join([ ''.join([self.GEOM_ECON_VAR_NAME,sub, 'ABC'[i],sub,'XYZ'[j],' = [', self.geom_econ_var[i*3+j].get(), ']']) for j in range(3) ]) for i in range(3)  ]) ); f.write( '\n' ) 
                
        f.write( ''.join([self.AUTO_SROL_VAR_NAME,' = [', ',\t'.join( [ self.auto_srol_var[i].get() for i in range(4) ] ) , ']'] ) ) ; f.write( '\n' )       
        f.write( ''.join([self.AUTO_EROL_VAR_NAME,' = [', ',\t'.join( [ self.auto_erol_var[i].get() for i in range(3) ] ) , ']'] ) ) ; f.write( '\n' )       
        
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
                
        #defaults:
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
        M = self.MAX_FORCE_PER_PHASE
        sub = self.SUBFIELD_SEPARATOR        
                       
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
                                
                            if (nam == self.GEOM_VAR_NAME):
                                self.geom_main_var[i*3+j].set(val)
                            elif (nam == self.FELD_VAR_NAME):
                                self.geom_feld_var[i*3+j].set(val)
                            elif (nam == self.FORC_VAR_NAME):
                                self.sgmt_forc_var[i*M+j].set(val)
                                if forc_segs_var == None:
                                    forc_segs_var = [BooleanVar(value = False) for i in range(M*3)]
                                forc_segs_var[i*M+j].set(True)
                            elif (nam == self.RADI_VAR_NAME):
                                self.sgmt_radi_var[i].set(val)
                                
                            elif (nam == self.GEOM_SCON_VAR_NAME):
                                self.geom_scon_var[i*3+j].set(val)
                            elif (nam == self.GEOM_ECON_VAR_NAME):
                                self.geom_econ_var[i*3+j].set(val)  
                        else:           
                            if (key == self.GEOM_SRCE_VAR_NAME):
                                for i, v in enumerate(val.split(',\t')):
                                    self.geom_srce_var[i].set(v.strip())
                            elif (key == self.GEOM_SPLT_VAR_NAME):
                                for i, v in enumerate(val.split(',\t')):
                                    self.geom_splt_var[i].set(v.strip())
                            elif (key == self.GEOM_SHRT_VAR_NAME):
                                for i, v in enumerate(val.split(',\t')):
                                    self.geom_shrt_var[i].set(v.strip())
                            elif (key == self.AUTO_SROL_VAR_NAME):
                                for i, v in enumerate(val.split(',\t')):
                                    self.auto_srol_var[i].set(v.strip())
                            elif (key == self.AUTO_EROL_VAR_NAME):
                                for i, v in enumerate(val.split(',\t')):
                                    self.auto_erol_var[i].set(v.strip())                                         
                            elif (key == self.PDST_VAR_NAME):
                                self.pdst_var.set(val)
                            elif (key == self.PCNT_VAR_NAME):
                                self.pcnt_var.set(val)
                            elif (key == self.RADI_CONN_VAR_NAME):
                                self.radi_conn_var.set(val)
                            elif (key == self.SAME_VAR_NAME):
                                self.same_var.set(val=='True')
                            elif (key == self.CONN_VAR_NAME):
                                self.auto_conn_var.set(val=='True')
                            elif (key == self.AUTO_SRCE_VAR_NAME):
                                self.auto_srce_var.set(val=='True')
                            elif (key == self.AUTO_SPLT_VAR_NAME):
                                self.auto_splt_var.set(val=='True')
                            elif (key == self.AUTO_SHRT_VAR_NAME):
                                self.auto_shrt_var.set(val=='True')
                            elif (key == self.AUTO_SCON_VAR_NAME):
                                self.auto_scon_var.set(val=='True')
                            elif (key == self.AUTO_ECON_VAR_NAME):
                                self.auto_econ_var.set(val=='True')
                            elif (key == self.FORC_CONN_VAR_NAME):
                                self.forc_conn_var.set(val=='True')
            if not forc_segs_var==None:                                          
                for i in range(3):                               
                    for j in range(M):                            
                        self.forc_list_var[i*M+j].set(forc_segs_var[i*M+j].get())    
                        if not forc_segs_var[i*M+j].get():
                            XYZ = str_to_flt_arr(self.geom_main_var[i*3].get())
                            self.sgmt_forc_var[i*M+j].set( value= int_arr_to_str( [0]*(len(XYZ)-1) ) )    
                        
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
        
        NS  = [  length_str_arr(self.geom_main_var[k].get()) for k in range(3*3) ]
        NSX = [  length_str_arr(self.geom_scon_var[k].get()) for k in range(3*4) ]
        NGX = [  length_str_arr(self.geom_econ_var[k].get()) for k in range(3*3) ]

        N = "ABC".find(self.schema[0]) if (P == 3 and not self.schema == "ABC") else -1
        
        XYZABC = [ [0] for _ in range(3*3) ]
        for i in range(P):
            for j in range(3):
                XYZABC[i*3+j] = str_to_flt_arr(
                    ( ( ( (     self.geom_splt_var[0*3+j].get()   + ("," if NSX[3*3+j]>0 else "") + self.geom_scon_var[3*3+j].get() + ","  ) if i == N else "") +
                        (       self.geom_srce_var[0*3+j].get()       if N<0 or i == N else         self.geom_splt_var[0*3+j].get() ) 
                                                                  + ("," if NSX[i*3+j]>0 else "") + self.geom_scon_var[i*3+j].get() + "," ) if extra else "" ) +                     
                                self.geom_main_var[i*3+j].get() +                     
                    ( ( "," +   self.geom_econ_var[i*3+j].get()   + ("," if NGX[i*3+j]>0 else "") + self.geom_shrt_var[0*3+j].get()   ) if extra else "" ) 
                    )
                
        R = []       
        for i in range(P):
            R = R + str_to_flt_arr(
                ( ( (   ( ",".join( [ self.radi_conn_var.get() for _ in range(NSX[3*3+0]+1) ] ) + ","  ) if i == N else "") +
                    (   ( ",".join( [ self.radi_conn_var.get() for _ in range(NSX[i*3+0]+1) ] ) + ","  ) ) ) if extra else "" ) + 
                                      self.sgmt_radi_var[i] .get() +                                
                ( ( "," + ",".join( [ self.radi_conn_var.get() for _ in range(NGX[i*3+0]+1) ] ) ) if extra else "" )
                , 0.01)     
            
        NF = []
        for i in range(P):
            for j in range(M):
                if self.forc_list_var[i*M+j].get():     
                    NF1 = []           
                    for k in range(P):
                        if k == i:
                           NF1.extend( str_to_int_arr(                
                                ( ( (   ( ",".join( [ "0" for _ in range(NSX[3*3+0]+1) ] ) + ","  ) if k == N else "") +
                                    (   ( ",".join( [ "0" for _ in range(NSX[k*3+0]+1) ] ) + ","  ) ) ) if extra else "" ) +                   
                                                self.sgmt_forc_var[k*M+j].get() +    
                                ( ( "," + ",".join( [ "0" for _ in range(NGX[k*3+0]+1) ] ) ) if extra else "" ) ) ) 
                        else:
                           NF1.extend( [0]*( ( ( ( (NSX[3*3+0]+1) if k == N else 0 ) + (NSX[k*3+0]+1) ) if extra else 0 ) + (NS [k*3+0]-1) + ( (NGX[k*3+0]+1) if extra else 0 ) ) ) 
                    if (sum(NF1)>0):
                        NF.append(NF1)
            
        if (self.forc_conn_var.get() and extra):            
            NF1 = []       
            for k in range(P):
                NF1.extend( [0]*( ( ( (NSX[3*3+0]+1) if k == N else 0 ) if extra else 0 ) + ( (NSX[k*3+0]+1) if extra else 0 ) + (NS [k*3+0]-1) ) + [1]*( (NGX[k*3+0]+1) if extra else 0 ) ) 
            if any( nf1 == 1 for nf1 in NF1 ):
                NF.append(NF1)
            # NF1 = [] 
            # if N>0:
            #     for k in range(P):
            #             NF1.extend( [0]*( ( ( (NSX[3*3+0]+1) if k == N else 0 ) if extra else 0 ) ) + [1]*( (NSX[k*3+0]+1) if extra else 0 ) + [0]*( (NS [k*3+0]-1) + (NGX[k*3+0]+1) if extra else 0 ) ) 
            # if any( nf1 == 1 for nf1 in NF1 ):
            #     NF.append(NF1)
                 
        XYZ = [ [] for i in range(3) ]
        for j in range(3):
            for i in range(P):
                XYZ[j] = XYZ[j] + str_to_flt_arr(self.geom_feld_var[i*3+j].get())       
    
        return geometry.sample_input(
                XA = XYZABC[0*3+0], YA = XYZABC[0*3+1], ZA = XYZABC[0*3+2],    
                XB = XYZABC[1*3+0], YB = XYZABC[1*3+1], ZB = XYZABC[1*3+2],    
                XC = XYZABC[2*3+0], YC = XYZABC[2*3+1], ZC = XYZABC[2*3+2],               
                R = R, NF = NF, X = XYZ[0] , Y = XYZ[1] , Z = XYZ[2]                
                )     