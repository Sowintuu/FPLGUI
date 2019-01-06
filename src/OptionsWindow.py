#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#==============================================================================
# OptionsWindow - Window to specify options of FPLGUI
# Copyright (C) 2018  Oliver Clemens
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.
#==============================================================================

import time
import datetime
import os
import re
import configparser as ConfigParser
from tkinter import Tk, Menu, Label, Entry, StringVar, IntVar, OptionMenu, W, END, Toplevel, Button, Listbox, Checkbutton
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from tkinter.messagebox import showwarning, showinfo

class OptionsWindow(object):
    
    
    def __init__(self,root,databaseDir,*optional):
        # Preparations.
        self.master = Toplevel(root)
        if not len(optional):
            self.master.title('FPLGUI: Options')
        else:
            self.master.title(optional[0])
        self.master.resizable(0, 0)
        self.master.grab_set()
        
        # Init variables
        self.xpUse = IntVar(self.master)
        self.xpUse.set(1)
        self.xPlaneDir = StringVar(self.master)
#         self.fsxUse = IntVar(self.master)
#         self.fsxUse.set(0)
#         self.fsxDir = StringVar(self.master)
        
        # Get current options.
        self.optionsFile = os.path.join(databaseDir,'FPLGUI.cfg')
        self.getCurrentOptions()
        
        # Set elements.
        #------------- PATHS -------------#
        # Row 0-1.
        self.l_xpUse = Label(self.master, text="Use XPlane")
        self.l_xpUse.grid(row=0, column=0)
        
        self.l_xpDir = Label(self.master, text="XPlane directory")
        self.l_xpDir.grid(row=0, column=1)
        
        self.c_xpUse = Checkbutton(self.master,
                                   variable=self.xpUse,
                                   command=self.c_xpUse_CB)
        self.c_xpUse.grid(row=1,column=0)
        
        self.e_xPlaneDir = Entry(self.master,textvariable=self.xPlaneDir,width=50)
        self.e_xPlaneDir.grid(row=1, column=1,columnspan=3)
#         self.e_xpDir.trace_add('write', self.e_callsignCB)
        
        self.b_xpDirBrowse = Button(self.master,text="Browse",command=self.b_xpDirBrowse_CB)
        self.b_xpDirBrowse.grid(row=1,column=4)
        
        # Row 2-3.
        self.l_fsxUse = Label(self.master, text="Use FSX",state='disabled')
        self.l_fsxUse.grid(row=2, column=0)
        
        self.l_fsxDir = Label(self.master, text="FSX directory",state='disabled')
        self.l_fsxDir.grid(row=2, column=1)
        
        self.c_fsxUse = Checkbutton(self.master,
#                                    variable=self.fsxUse,
#                                    command=self.c_fsxUse_CB,
                                   state='disabled')
        self.c_fsxUse.grid(row=3,column=0)
        
        self.e_fsxDir = Entry(self.master,
#                               textvariable=self.fsxDir,
                              width=50,
                              state='disabled')
        self.e_fsxDir.grid(row=3, column=1,columnspan=3)
#         self.e_xpDir.trace_add('write', self.e_callsignCB)
        
        self.b_xpDirBrowse = Button(self.master,
                                    text="Browse",
#                                     command=self.b_xpDirBrowse_CB,
                                    state='disabled')
        self.b_xpDirBrowse.grid(row=3,column=4)
        
        #------------- SIMBIREF -------------#
        # Row 4
        Label(self.master).grid(row=4,column=0)
        
        # Row 5
        Label(self.master, text="Simbiref").grid(row=5, column=0)
        
        # Row 6
        Label(self.master, text='OPF Layout').grid(row=6, column=0)
        
        self.opfFormat = StringVar(self.master)
#         self.opfFormat.set('LIDO')
        self.e_opfFormat = Entry(self.master,textvariable=self.opfFormat)#,width=50)
        self.e_opfFormat.grid(row=6, column=1)
        
        
        
        
        # Specify closing action.
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Make master window wait for closing.
        root.wait_window(self.master)
    
    def getCurrentOptions(self):
        if os.path.isfile(self.optionsFile):
            config = ConfigParser.RawConfigParser()
            config.read(self.optionsFile)
            
            # xPlaneDir
            try:
                self.xPlaneDir.set(config.get('FPLGUI', 'XPLANEDIR'))
            except ConfigParser.NoOptionError :
                self.xPlaneDir.set(None)
                
            # xpUse
            try:
                self.xpUse.set(int(config.get('FPLGUI','XPUSE')))
            except ConfigParser.NoOptionError:
                self.xpUse.set(1)
    
    def saveOptions(self):
        # Check options validity.
        if not re.match(r'[A-Za-z]:\\',self.xPlaneDir.get()):
            self.xPlaneDir.set(None)
        
        config = ConfigParser.RawConfigParser()
        
        # General
        config.add_section('FPLGUI')
        config.set('FPLGUI', 'XPLANEDIR', self.xPlaneDir.get())
        config.set('FPLGUI', 'XPUSE', self.xpUse.get())
        
        # Simbrief
        config.add_section('SIMBRIEF')
        config.set('SIMBRIEF', 'opfformat', self.opfFormat.get())
        
        with open(os.path.join(self.optionsFile),'w') as configFile:
            config.write(configFile)
    
    def c_xpUse_CB(self):
        pass
        
    def b_xpDirBrowse_CB(self):
        self.xPlaneDir.set(askdirectory(mustexist=True,initialdir='C:\\',title='Select X Plane directory',parent=self.master).replace('/','\\'))
        pass
    
    def on_closing(self):
        self.saveOptions()
        self.master.destroy()
    
if __name__ == '__main__':
    root = Tk()
    window = OptionsWindow(root,r'E:\gitserver\FPLGUI\database')

