#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#==============================================================================
# FPLGUI - GUI to set up flightplan for XPlane and IVAO with other useful functions
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
import os
import re

from math import radians, copysign
from warnings import warn
from urllib.request import urlopen
import webbrowser
import configparser as ConfigParser
from tkinter import Tk, Menu, Label, Entry, StringVar, OptionMenu, W, END, Toplevel, Button, Listbox, messagebox
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
# from tkinter.simpledialog import askstring
from tkinter.messagebox import showwarning, showinfo
from Fpl import Fpl
import avFormula


# chapter
class FPLGUI:

    def __init__(self):
        # Get database folder.
        self.srcDir = os.path.dirname(os.path.abspath(__file__))
        self.databaseDir = os.path.join(os.path.dirname(self.srcDir),'database')
        self.supportFilesDir = os.path.join(os.path.dirname(self.srcDir),'supportFiles')
        
        # check options for X-Plane directory
        ask4dir = False
        if os.path.isfile(os.path.join(self.databaseDir,'FPLGUI.cfg')):
            self.config = ConfigParser.RawConfigParser()
            self.config.read(os.path.join(self.databaseDir,'FPLGUI.cfg'))
            try:
                self.xPlaneDir = self.config.get('FPLGUI','XPLANEDIR')
            except ConfigParser.NoSectionError:
                ask4dir = True
            except ConfigParser.NoOptionError:
                ask4dir = True
        else:
            ask4dir = True
        
        # Show splash
        SPLASH_WIDTH = 350
        SPLASH_HEIGHT = 250
        splashWindow = Tk()
        splashWindow.title('FPLGUI')
        self.screenWidth = splashWindow.winfo_screenwidth() # width of the screen
        self.screenHeight = splashWindow.winfo_screenheight() # height of the screen
        x = round((self.screenWidth/2) - (SPLASH_WIDTH/2))
        y = round((self.screenHeight/2) - (SPLASH_HEIGHT/2))
        splashWindow.geometry('{}x{}+{}+{}'.format(SPLASH_WIDTH,SPLASH_HEIGHT,x,y))
        splashWindow.resizable(0, 0)
        splashWindow.iconbitmap(os.path.join(self.supportFilesDir,'FPLGUI.ico'))
        Label(splashWindow,text="Loading Navdata, Please wait.",justify='left',font=("Helvetica", 14)).place(relx=0.1,rely=0.1,anchor='nw')
        with open(os.path.join(self.supportFilesDir,'startupMessage.txt')) as startupFile:
            Label(splashWindow, text=startupFile.read(),justify='left',font=("Helvetica", 8)).place(relx=0.1, rely=0.4, anchor='nw')
        splashWindow.update()
        
        # let user select X-Plane dir and write options
        if ask4dir:
            time.sleep(3)
            self.xPlaneDir = askdirectory(mustexist=True,initialdir='C:\\',title='Select X Plane directory',parent=splashWindow).replace('/','\\')
            self.config = ConfigParser.RawConfigParser()
            self.config.add_section('FPLGUI')
            self.config.set('FPLGUI', 'XPLANEDIR', self.xPlaneDir)
            
            with open(os.path.join(self.databaseDir,'FPLGUI.cfg'),'w') as configFile:
                self.config.write(configFile)
        
        # Get navdata folder.
        if os.path.exists(os.path.join(self.xPlaneDir,'Custom Data','earth_fix.dat')) and \
           os.path.exists(os.path.join(self.xPlaneDir,'Custom Data','earth_nav.dat')) and \
           os.path.exists(os.path.join(self.xPlaneDir,'Custom Data','earth_awy.dat')) and \
           os.path.exists(os.path.join(self.xPlaneDir,'Custom Data','apt.csv')):
            self.navdataDir = os.path.join(self.xPlaneDir,'Custom Data')
        else:
            self.navdataDir = os.path.join(self.xPlaneDir,'Resources','default data')
        
        #inititalize Fpl-object
        self.fplPath = os.path.join(self.xPlaneDir,'Resources\\plugins\\X-IvAp Resources\\Flightplans')
        self.fpl = Fpl(self.fplPath)
        
        # Load Fixes
#         self.fpl.getFixes(os.path.join(self.navdataDir,'earth_fix.dat'))
#         self.fpl.getNavaids(os.path.join(self.navdataDir,'earth_nav.dat'))
#         self.fpl.getAirports(os.path.join(self.navdataDir,'apt.csv'))
#         self.fpl.getAirways(os.path.join(self.navdataDir,'earth_awy.dat'))
        
        # Remove Splash.
        splashWindow.destroy()
        
        # Create main window
        self.master = Tk()
        self.master.title('FPLGUI')
        self.master.resizable(0, 0)
        
        ## menu ##
        menubar = Menu(self.master)
        
        filemenu = Menu(menubar,tearoff=0)
        filemenu.add_command(label="Clear",command=self.clear)
        filemenu.add_command(label="Send to XP",command=self.send)
        filemenu.add_separator()
        filemenu.add_command(label="Load",command=self.load)
        filemenu.add_command(label="Save",command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        acmenu = Menu(menubar,tearoff=0)
        acmenu.add_command(label="Load Template",command=self.acLoad)
        acmenu.add_command(label="Save Template",command=self.acSave)
        menubar.add_cascade(label="Aircraft", menu=acmenu)
        
        utilmenu = Menu(menubar,tearoff=0)
        utilmenu.add_command(label="Import Route",command=self.importRoute)
        utilmenu.add_separator()
        utilmenu.add_command(label="Simbrief",command=self.simbrief)
        utilmenu.add_command(label="Flightaware",command=self.flightaware)
        utilmenu.add_separator()
        utilmenu.add_command(label="Show at Skyvector",command=self.showSkyvector)
        utilmenu.add_command(label="Export to X-Plane",command=self.export2xp)
        utilmenu.add_command(label="Export to FF A320",command=self.export2FFA320)
        utilmenu.add_separator()
        utilmenu.add_command(label="Show FPL text",command=self.showFplText)
        utilmenu.add_separator()
        utilmenu.add_command(label="Options",command=self.options)
        menubar.add_cascade(label="Extras",menu=utilmenu)
        
        self.master.config(menu=menubar)
        
        ## row 0-1 ##
        ## send button
        self.b_send = Button(self.master, text = "Send", command=self.send)
        self.b_send.grid(row=0, column=0, rowspan = 2)
        
        ## callsign
        self.l_callsign = Label(self.master, text="7 a/c ident")
        self.l_callsign.grid(row=0, column=1)
        
        self.callsign = StringVar(self.master)
        self.e_callsign = Entry(self.master, textvariable=self.callsign)
        self.e_callsign.grid(row=1, column=1)
        self.callsign.trace_add('write', self.e_callsignCB)
        
        ## rules
        self.l_rules = Label(self.master, text="8 flight rules")
        self.l_rules.grid(row=0, column=2)
        
        self.rules = StringVar(self.master)
        self.rules.set("V")
        self.o_rules = OptionMenu(self.master, self.rules, "V", "I", "Y", "Z")
        self.o_rules.grid(row=1, column=2)
        
        
        ## flighttype
        self.l_flighttype = Label(self.master, text="  type of flight")
        self.l_flighttype.grid(row=0, column=3)
        
        self.flighttype = StringVar(self.master)
        self.flighttype.set("S")
        self.o_flighttype = OptionMenu(self.master, self.flighttype, "S", "N", "G", "M", "X")
        self.o_flighttype.grid(row=1, column=3)
        
        
        ## row 2-3 ##
        ## number
        self.l_number = Label(self.master, text="9 number")
        self.l_number.grid(row=2, column=0)
        
        self.number = StringVar(self.master)
        self.e_number = Entry(self.master, textvariable=self.number)
        self.e_number.grid(row=3, column=0)
        self.number.trace_add('write', self.e_numberCB)
        
        ## type of aircraft
        self.l_actype = Label(self.master, text="type of aircraft")
        self.l_actype.grid(row=2, column=1)
        
        self.actype = StringVar(self.master)
        self.e_actype = Entry(self.master, textvariable=self.actype)
        self.e_actype.grid(row=3, column=1)
        self.actype.trace_add('write', self.e_actypeCB)
        
        ## wakecat
        self.l_wakecat = Label(self.master, text="wake turb cat")
        self.l_wakecat.grid(row=2, column=2)
        
        self.wakecat = StringVar(self.master)
        self.wakecat.set("L")
        self.o_wakecat = OptionMenu(self.master, self.wakecat, "L", "M", "H", "J")
        self.o_wakecat.grid(row=3, column=2)
        
        ## equipment
        self.l_equipment = Label(self.master, text="10 equipment")
        self.l_equipment.grid(row=2, column=3)
        
        self.equipment = StringVar(self.master)
        self.e_equipment = Entry(self.master, textvariable=self.equipment)
        self.e_equipment.grid(row=3, column=3)
        self.equipment.trace_add('write', self.e_equipmentCB)
        
        ## equipment
        self.l_transponder = Label(self.master, text="transponder")
        self.l_transponder.grid(row=2, column=4)
        
        self.transponder = StringVar(self.master)
        self.e_transponder = Entry(self.master, textvariable=self.transponder)
        self.e_transponder.grid(row=3, column=4)
        self.transponder.trace_add('write', self.e_transponderCB)
        
        
        ## row 4-5 ##
        ## depicao
        self.l_depicao = Label(self.master, text="13 departure aerodrome")
        self.l_depicao.grid(row=4, column=0)
        
        self.depicao = StringVar(self.master)
        self.e_depicao = Entry(self.master, textvariable=self.depicao)
        self.e_depicao.grid(row=5, column=0)
        self.depicao.trace_add('write', self.e_depicaoCB)
        
        ## deptime
        self.l_deptime = Label(self.master, text="departure time")
        self.l_deptime.grid(row=4, column=1)
        
        self.deptime = StringVar(self.master)
        self.e_deptime = Entry(self.master, textvariable=self.deptime)
        self.e_deptime.grid(row=5, column=1)
        self.deptime.trace_add('write', self.e_deptimeCB)
        
        ## row 6-7 ##
        ## speed
        self.l_speed = Label(self.master, text="15 cruising speed")
        self.l_speed.grid(row=6, column=0, columnspan=2)
        
        self.speedtype = StringVar(self.master)
        self.speedtype.set("N")
        self.o_speedtype = OptionMenu(self.master, self.speedtype, "N", "M")
        self.o_speedtype.grid(row=7, column=0)
        
        self.speed = StringVar(self.master)
        self.e_speed = Entry(self.master, textvariable=self.speed)
        self.e_speed.grid(row=7, column=1)
        self.speed.trace_add('write', self.e_speedCB)
        
        ## level
        self.l_level = Label(self.master, text="flight altutude/level")
        self.l_level.grid(row=6, column=2, columnspan=2)
        
        self.leveltype = StringVar(self.master)
        self.leveltype.set("F")
        self.o_level = OptionMenu(self.master, self.leveltype, "F", "A", "VFR")
        self.o_level.grid(row=7, column=2)
        
        self.level = StringVar(self.master)
        self.e_level = Entry(self.master, textvariable=self.level)
        self.e_level.grid(row=7, column=3)
        self.level.trace_add('write', self.e_levelCB)
        
        
        ## row 8-9 ##
        ##route
        self.l_route = Label(self.master, text="    route")
        self.l_route.grid(row=8, column=0, sticky=W)
        
        self.route = StringVar(self.master)
        self.e_route = Entry(self.master, width=105, textvariable=self.route)
        self.e_route.grid(row=9, column=0, columnspan=5)
        self.route.trace_add('write', self.e_routeCB)
        
        ## row 10-11 ##
        ## destinationAP
        self.l_desticao = Label(self.master, text="13 destination aerodrome")
        self.l_desticao.grid(row=10, column=0)
        
        self.desticao = StringVar(self.master)
        self.e_desticao = Entry(self.master, textvariable=self.desticao)
        self.e_desticao.grid(row=11, column=0)
        self.desticao.trace_add('write', self.e_desticaoCB)
        
        ## duration
        self.l_eet = Label(self.master, text="EET")
        self.l_eet.grid(row=10, column=1)
        
        self.eet = StringVar(self.master)
        self.e_eet = Entry(self.master, textvariable=self.eet)
        self.e_eet.grid(row=11, column=1)
        self.eet.trace_add('write', self.e_eetCB)
        
        ## alternates
        self.l_alticao = Label(self.master, text="alternate")
        self.l_alticao.grid(row=10, column=2)
        
        self.alticao = StringVar(self.master)
        self.e_alticao = Entry(self.master, textvariable=self.alticao)
        self.e_alticao.grid(row=11, column=2)
        self.alticao.trace_add('write', self.e_alticaoCB)
        
        self.l_alt2icao = Label(self.master, text="2nd alternate")
        self.l_alt2icao.grid(row=10, column=3)
        
        self.alt2icao = StringVar(self.master)
        self.e_alt2icao = Entry(self.master, textvariable=self.alt2icao)
        self.e_alt2icao.grid(row=11, column=3)
        self.alt2icao.trace_add('write', self.e_alt2icaoCB)
        
        
        ## row 12-13 ##
        ##other
        self.l_other = Label(self.master, text="other")
        self.l_other.grid(row=12, column=0, sticky=W)
        
        self.other = StringVar(self.master)
        self.e_other = Entry(self.master, width=105, textvariable=self.other)
        self.e_other.grid(row=13, column=0, columnspan=5)
        self.other.trace_add('write', self.e_otherCB)
        
        
        ## row 14-15 ##
        ##endurance
        self.l_endurance = Label(self.master, text="19 endurance")
        self.l_endurance.grid(row=14, column=0)
        
        self.endurance = StringVar(self.master)
        self.e_endurance = Entry(self.master, textvariable=self.endurance)
        self.e_endurance.grid(row=15, column=0)
        self.endurance.trace_add('write', self.e_enduranceCB)
        
        ##persons
        self.l_pob = Label(self.master, text="persons on board")
        self.l_pob.grid(row=14, column=1)
        
        self.pob = StringVar(self.master)
        self.e_pob = Entry(self.master, textvariable=self.pob)
        self.e_pob.grid(row=15, column=1)
        self.pob.trace_add('write', self.e_pobCB)
        
        ##pic
        self.l_pic = Label(self.master, text="pilot in command")
        self.l_pic.grid(row=14, column=2)
        
        self.pic = StringVar(self.master)
        self.e_pic = Entry(self.master, width=40, textvariable=self.pic)
        self.e_pic.grid(row=15, column=2, columnspan=2)
        self.pic.trace_add('write', self.e_picCB)
        
        ## row 16 ##
        ##empty
        empty = Label(self.master, text="")
        empty.grid(row=16, column=0)
        
        self.updateContent()
        
        # Set master window options
        self.master.update()
        masterWidth = self.master.winfo_width()
        masterHeight = self.master.winfo_height()
        x = round((self.screenWidth/2) - (masterWidth/2))
        y = round((self.screenHeight/2) - (masterHeight/2))
        self.master.geometry('{}x{}+{}+{}'.format(masterWidth,masterHeight,x,y))
        self.master.title('FPLGUI')
        self.master.resizable(0, 0)
        self.master.iconbitmap(os.path.join(self.supportFilesDir,'FPLGUI.ico'))
        
        # Start master mainloop.
        self.master.mainloop()
        
    def updateContent(self):
        ## row 0-1 ##
        ## callsign
        self.e_callsign.delete(0, END)
        self.e_callsign.insert(0,self.fpl.callsign)
        
        ## rules    
        if self.fpl.rules:
            self.rules.set(self.fpl.rules)
        else:
            self.rules.set("V")
        
        ## flightType
        if self.fpl.flighttype:
            self.flighttype.set(self.fpl.flighttype)
        else:
            self.flighttype.set("S")
        
        
        ## row 2-3 ##
        ## number
        self.e_number.delete(0, END)
        self.e_number.insert(0,self.fpl.number)
        
        ## type of aircraft
        self.e_actype.delete(0, END)
        self.e_actype.insert(0,self.fpl.actype)
        
        ## wakecat
        if self.fpl.wakecat:
            self.wakecat.set(self.fpl.wakecat)
        else:
            self.wakecat.set("L")
        
        ## equipment
        self.e_equipment.delete(0, END)
        self.e_equipment.insert(0,self.fpl.equipment)
        
        ## equipment
        self.e_transponder.delete(0, END)
        self.e_transponder.insert(0,self.fpl.transponder)
        
        
        ## row 4-5 ##
        ## depicao
        self.e_depicao.delete(0, END)
        self.e_depicao.insert(0,self.fpl.depicao)
        
        ## deptime
        self.e_deptime.delete(0, END)
        self.e_deptime.insert(0,self.fpl.deptime)
        
        ## row 6-7 ##
        ## speed
        if self.fpl.speedtype:
            self.speedtype.set(self.fpl.speedtype)
        else:
            self.speedtype.set("N")
        
        self.e_speed.delete(0, END)
        self.e_speed.insert(0,self.fpl.speed)
        
        ## level
        if self.fpl.leveltype:
            self.leveltype.set(self.fpl.leveltype)
        else:
            self.leveltype.set("N")
        
        self.e_level.delete(0, END)
        self.e_level.insert(0,self.fpl.level)
        
        ## row 8-9 ##
        ##route
        self.e_route.delete(0, END)
        self.e_route.insert(0,self.fpl.route)
        
        ## row 10-11 ##
        ## destinationAP        
        self.e_desticao.delete(0, END)
        self.e_desticao.insert(0,self.fpl.desticao)
        
        ## eet        
        self.e_eet.delete(0, END)
        self.e_eet.insert(0,self.fpl.eet)
        
        ## alternates
        self.e_alticao.delete(0, END)
        self.e_alticao.insert(0,self.fpl.alticao)
        
        self.e_alt2icao.delete(0, END)
        self.e_alt2icao.insert(0,self.fpl.alt2icao)
        
        
        ## row 12-13 ##
        ##other
        self.e_other.delete(0, END)
        self.e_other.insert(0,self.fpl.other)
        
        
        ## row 14-15 ##
        ##endurance
        self.e_endurance.delete(0, END)
        self.e_endurance.insert(0,self.fpl.endurance)
        
        ##persons
        self.e_pob.delete(0, END)
        self.e_pob.insert(0,self.fpl.pob)
        
        ##pic
        self.e_pic.delete(0, END)
        self.e_pic.insert(0,self.fpl.pic)
    
    
    def updateFpl(self):
        self.fpl.callsign = self.e_callsign.get()
        self.fpl.pic = self.e_pic.get()
        self.fpl.speedtype = self.speedtype.get()
        self.fpl.pob = self.e_pob.get()
        self.fpl.endurance = self.e_endurance.get()
        self.fpl.other = self.e_other.get()
        self.fpl.alt2icao = self.e_alt2icao.get()
        self.fpl.alticao = self.e_alticao.get()
        self.fpl.eet = self.e_eet.get()
        self.fpl.desticao = self.e_desticao.get()
        self.fpl.route = self.e_route.get()
        self.fpl.level = self.e_level.get()
        self.fpl.leveltype = self.leveltype.get()
        self.fpl.speed = self.e_speed.get()
        self.fpl.deptime = self.e_deptime.get()
        self.fpl.depicao = self.e_depicao.get()
        self.fpl.transponder = self.e_transponder.get()
        self.fpl.equipment = self.e_equipment.get()
        self.fpl.wakecat = self.wakecat.get()
        self.fpl.actype = self.e_actype.get()
        self.fpl.number = self.e_number.get()
        self.fpl.flighttype = self.flighttype.get()
        self.fpl.rules = self.rules.get()
        
    
    def load(self):
        filepath = askopenfilename(filetypes=[("X-Plane Flightplan","*.fpl"),("All","*")],initialdir=self.fpl.path)
        self.fpl.load(filepath)
        self.updateContent()
    
    def save(self):
        self.updateFpl()
        filepath = asksaveasfilename(filetypes=[("X-Plane Flightplan","*.fpl"),("All","*")],initialdir=self.fpl.path)
        if filepath[-4:] != ".fpl":
            filepath += ".fpl"
        
        self.fpl.save(filepath)
        print("saved!")
        
    
    
    def send(self):
        self.updateFpl()
        self.fpl.save(self.fpl.path + "\\Default.fpl")
        
        if (len(self.fpl.route) + len(self.fpl.other)) > 255:
            showwarning("Too long entries",'"Route" and "Other" entries are too long ({}/255 characters combined)!\nThis will lead to disconnection in flight.\nTry to shorten these fields.'.format(len(self.fpl.route) + len(self.fpl.other)))
        print("generated!")
    
    
    def clear(self):
        self.e_callsign.delete(0, END)
        self.e_number.delete(0, END)
        self.e_actype.delete(0, END)
        self.e_equipment.delete(0, END)
        self.e_transponder.delete(0, END)
        self.e_depicao.delete(0, END)
        self.e_deptime.delete(0, END)
        self.e_speed.delete(0, END)
        self.e_level.delete(0, END)
        self.e_route.delete(0, END)
        self.e_desticao.delete(0, END)
        self.e_eet.delete(0, END)
        self.e_alticao.delete(0, END)
        self.e_alt2icao.delete(0, END)
        self.e_other.delete(0, END)
        self.e_endurance.delete(0, END)
        self.e_pob.delete(0, END)
        self.e_pic.delete(0, END)
    
    def options(self):
        self.optionsText = self.optionsFile.read()
        
        self.top = Toplevel(self.master)
        
        if len(self.routing) > 0:
            Label(self.top, text="X-Plane Path:").grid(row=0, column=0)
            
            self.tlEntryXpPath = Entry(self.top)
            self.tlEntryXpPath.grid(row=0, column=1)
            
            self.tlUpdateLabel = Label(self.top, text = "lastUpdated")
            self.tlUpdateLabel.grid(row=1, column=0)
            
            self.tlUpdateDbButton = Button(self.top,text="Update",command=self.updateRouteDbButtonCB,width=80)
            self.tlOkButton.grid(row=1, column=1)
            
            self.tlOkButton = Button(self.top,text="OK",command=self.optionsButtonOkCB,width=80)
            self.tlOkButton.grid(row=2, column=0)
            
            self.tlCancelButton = Button(self.top,text="OK",command=self.optionsButtonCancelCB,width=80)
            self.tlCancelButton.grid(row=2, column=1)
            
            self.master.wait_window(self.top)
        
    def updateRouteDbButtonCB(self):
#         dbUpdated = False
        downloadUrl = "https://www.ivao.de/scripts/php/cms/pfpx"
#         curDate = int(time.time())
#         lastUpdate = 0 #TODO: replace, when options implemented
#         timeDiff = curDate - lastUpdate
        timeDiff = 0

        if timeDiff > 864000:
            ivaoDatabase = urlopen(downloadUrl)
            database = ivaoDatabase.read()
#             lastUpdate = int(time.time())
#             dbUpdated = True
            
            DataFile = open(self.srcDir + r"\routeDatabase.txt",'w')
            DataFile.write(database)
            DataFile.close()
    
    def optionsButtonOkCB(self):
        self.top.destroy()
    
    def optionsButtonCancelCB(self):
        self.top.destroy()
    
    def simbrief(self):
        self.updateFpl()
        
        airline = ""
        fltnum = ""
        reg = ""
        selcal = ""
        
        ## airline, fltnum, reg from callsign
        reFind = re.search("[A-Z]{5}",self.fpl.callsign)
        if reFind:
            reg = reFind.group()
        else:
            reFindAirline = re.search("[A-Z]{3}(?=\w+)",self.fpl.callsign)
            reFindFltnum = re.search("(?<=[A-Z]{3})\w+",self.fpl.callsign)
            if reFindAirline and reFindFltnum:
                airline = reFindAirline.group()
                fltnum = reFindFltnum.group()
            else:
                print("invalid Callsign!")
            
        deph = self.fpl.deptime[0:1]
        depm = self.fpl.deptime[2:3]
        
        ## reg from REG/ or ask
        if not reg:
            reFind = re.search("(?<=REG/)[A-Z]{5}",self.fpl.other)
            if reFind:
                reg = reFind.group()
            else:
#                 reg = askstring("Registration", "Enter a/c registration:")
#                 if reg is None:
                    reg = ""
        
        ## airline from OPR/ or ask
        if not airline:
            reFind = re.search("(?<=OPR/)[A-Z]{3}",self.fpl.other)
            if reFind:
                airline = reFind.group()
            else:
#                 airline = askstring("Airline", "Enter airline ICAO:")
#                 if airline is None:
                    airline = ""
        
        ## selcal from SEL/ or ask
        reFind = re.search("(?<=SEL/)[A-S]{4}",self.fpl.other)
        if reFind:
            selcal = reFind.group()
        else:
#             selcal = askstring("Selcal", "Enter Selcal Code:")
#             if selcal is None:
                selcal = ""
        
        
        url = "https://www.simbrief.com/system/dispatch.php?airline={}&fltnum={}&type={}&orig={}&dest={}&deph={}&depm={}&reg={}&selcal={}&route={}&fl={}00".format(airline,
                                                                                                                                                                   fltnum,
                                                                                                                                                                   self.fpl.actype,
                                                                                                                                                                   self.fpl.depicao,
                                                                                                                                                                   self.fpl.desticao,
                                                                                                                                                                   deph,
                                                                                                                                                                   depm,
                                                                                                                                                                   reg,
                                                                                                                                                                   selcal,
                                                                                                                                                                   self.fpl.route,
                                                                                                                                                                   self.fpl.level)
        webbrowser.open(url,new=2)
    
    ## Display flights for departure and destination airport on flightaware.
    def flightaware(self):
        self.updateFpl()
        
        url = 'https://de.flightaware.com/live/findflight?origin={}&destination={}'.format(self.fpl.depicao,self.fpl.desticao)
        webbrowser.open(url,new=2)
    
    
    def importRoute(self):
        self.updateFpl()
        
        with open(self.databaseDir + r"\routeDatabase.txt") as dataFile:
            database = dataFile.read()
            
        self.fpl.desticao = self.fpl.desticao.upper()
        self.fpl.depicao = self.fpl.depicao.upper()
        
        patRte = re.compile(self.fpl.depicao + self.fpl.desticao + r"\d{2};.+\n")
        routes = patRte.findall(database)
        
        ## parse routes
        self.routing = []
        self.comment = []
        self.fl = []

        maxLenCom = 0

        for k in range(len(routes)):
            parts = re.split(";",routes[k])
            self.routing.append(parts[1])
            
            curComment = parts[2]
            #curComment = curComment[1:-2]
            curComment = re.split(",",curComment)
            
            curFL = curComment[0]
            curCommentList = curComment[1:]
            
            curComment = ""
            
            for l in curCommentList:
                curComment += l
            
            self.comment.append(curComment[1:-2])
            
            if len(curComment[1:-2]) > maxLenCom:
                maxLenCom = len(curComment[1:-2])
            
            self.fl.append(curFL)
        
        ## show window
        self.importRouteTop = Toplevel(self.master)
        
        if len(self.routing) > 0:
            Label(self.importRouteTop, text="Choose a Route").pack()
            
            self.importRouteListboxTl = Listbox(self.importRouteTop,width=180)
            self.importRouteListboxTl.pack()
            for k in range(len(self.routing)):
                self.importRouteListboxTl.insert(END, "{:11} {:50} {}".format(self.fl[k],self.comment[k],self.routing[k]))
            self.importRouteListboxTl.selection_set(0)
            
            self.tlOkButton = Button(self.importRouteTop,text="OK",command=self.routeListCB,width=80)
            self.tlOkButton.pack()
            
            self.master.wait_window(self.importRouteTop)
        else:
            Label(self.importRouteTop, text="No Routes found!").pack()
            self.tlOkButton = Button(self.importRouteTop,text="OK",command=self.importRouteTop.destroy,width=10)
            self.tlOkButton.pack()

    def export2FFA320(self):
        """
        Write the route to Flight Factor A320 Company Routes Database.
        Import to aircraft via the MCDU
        """
        self.updateFpl()
        #self.fpl.actype,self.fpl.depicao,self.fpl.desticao,deph,depm,reg,selcal,self.fpl.route,self.fpl.level
        fpl = self.fpl
        # check if ac type is A320
        if fpl.actype != 'A320':
            warn('A/C type is not A320!')
        
        # remove SID/STAR from route
        route = re.sub('[A-Z]{5}\d[A-Z]','',fpl.route).strip()
        
        # write route string
        routeString = 'RTE {}{} {} {} {} CI30 FL{}'.format(fpl.depicao,
                                                           fpl.desticao,
                                                           fpl.depicao,
                                                           route,
                                                           fpl.desticao,
                                                           fpl.level
                                                           )
        
        # find and open route database
        # check for duplicate and overwrite or append route
        coRoutePath = os.path.join(self.xPlaneDir,r'Aircraft\FlightFactorA320\data\corte.in')
        with open(coRoutePath,'r') as coRouteFile:
            lines = coRouteFile.readlines()
            written = False
            for k in range(len(lines)):
                if 'RTE {}{}'.format(fpl.depicao,fpl.desticao) in lines[k]:
                    lines[k] = '{}\n'.format(routeString)
                    written = True
                    break
            
            if not written:
                if lines[-1][-1] == '\n':
                    lines.append(routeString)
                else:
                    lines.append('\n{}'.format(routeString))
        
        # write new file
        with open(coRoutePath,'w') as coRouteFile:
            for k in lines:
                coRouteFile.write(k)
        
        # print success message
        print('exported (FF A320)!')
        
    def export2xp(self):
        self.updateFpl()
        
        # Get file path for export.
        fileCount = 0
        fmsFilePath = os.path.abspath(__file__)
        while os.path.isfile(fmsFilePath):
            fileCount += 1
            fmsFilePath = os.path.join(self.xPlaneDir,'Output','FMS plans','{}{}{:02}.fms'.format(self.fpl.depicao,self.fpl.desticao,fileCount))

        # Get coordinates of dep.
        curCoordinates = self.fpl.airports[self.fpl.depicao]
        
        # Get start altitude.
        curAltitude = int(self.fpl.level) * 100
        newAltitude = curAltitude
        
        # Remove SID/STAR from route and split in parts
        route = re.sub('[A-Z]{5}\d[A-Z]','',self.fpl.route).strip()
        route = route.split()
        
#         with open(fmsFilePath,'w') as fmsFile:
        # Write header and departure.
        fmsStr = ''
        
        # Process route.
        nWaypoints = 1
        curWaypoint = None
        curWaypointName = None
        lastWaypointName = None
        curAirway = None
        for rpId,rp in enumerate(route):
            if not(rpId % 2):
                # Waypoint
                
                # Split altitude from wp
                if '/' in rp:
                    wpSplit = rp.split('/')
                    curWaypointName = wpSplit[0]
                    altMatch = re.search('F\d+', wpSplit[1])
                    if altMatch is not None:
                        newAltitude = int(wpSplit[1][altMatch.start()+1:altMatch.end()]) * 100
                else:
                    curWaypointName = rp
                
                if curAirway is None:
                    # After DCT
                    curAltitude = newAltitude
                    
                    curWaypoint = self.fpl.waypoints[curWaypointName]
                    minDistance = 3.2 # slightly greater than pi
                    for wp in curWaypoint:
                        distance = avFormula.gcDistance(curCoordinates[0],curCoordinates[1],wp[0],wp[1])
                        if distance < minDistance:
                            minDistance = distance
                            nearWp = wp
                    fmsStr = '{}{} {} DRCT {} {} {}\n'.format(fmsStr,nearWp[2],curWaypointName,curAltitude,nearWp[0],nearWp[1])
                    nWaypoints += 1
                    
                else:
                    # After Airway
                    curAirwayParts = self.fpl.airways[curAirway].parts
                    curAirwayName = curAirway
                    curAirway = None
                    # Get part with both waypoints.
                    for pa in curAirwayParts:
                        if lastWaypointName in [k for m in pa for k in m] and curWaypointName in [n for o in pa for n in o]:
                            curAirway = pa
                            break
                    if curAirway is None:
                        print('One or both waypoints are no part of airway {}!'.format(curAirwayName))
                        raise(Exception,'Airway Error!')
                    
                    curWaypointId = None
                    lastWaypointId = None
                    for wpId,wp in enumerate(curAirway):
                        if curWaypointName in wp:
                            curWaypointId = wpId
                        elif lastWaypointName in wp:
                            lastWaypointId = wpId
                        if curWaypointId is not None and lastWaypointId is not None:
                            step = int(copysign(1,curWaypointId - lastWaypointId))
                            break
                    for wp in range(lastWaypointId+step,curWaypointId+step,step):
                        if curAirway[wp][0] == curWaypointName:
                            curAltitude = newAltitude
                        
                        fmsStr = '{}{} {} {} {} {} {}\n'.format(fmsStr,curAirway[wp][3],curAirway[wp][0],curAirwayName,curAltitude,curAirway[wp][1],curAirway[wp][2])
                        nWaypoints += 1
                        
                    curAirway = None
            elif rp != 'DCT':
                # Airway
                curAirway = rp
                lastWaypointName = curWaypointName
                
        curCoordinates = self.fpl.airports[self.fpl.desticao]
        fmsStr = '{}1 {} ADES 0.000000 {} {}'.format(fmsStr,self.fpl.desticao,curCoordinates[0],curCoordinates[1])
        nWaypoints += 1
        
        curCoordinates = self.fpl.airports[self.fpl.depicao]
        fmsStr = 'I\n1100 Version\nCYCLE {}\nADEP {}\nADES {}\nNUMENR {}\n1 {} ADEP 0.000000 {} {}\n{}'.format(self.fpl.cycleNumber,
                                                                                                               self.fpl.depicao,
                                                                                                               self.fpl.desticao,
                                                                                                               nWaypoints,
                                                                                                               self.fpl.depicao,
                                                                                                               curCoordinates[0],curCoordinates[1],
                                                                                                               fmsStr)
        
#         print(fmsStr)
        
        with open(fmsFilePath,'w') as fmsFile:
            fmsFile.write(fmsStr)
            
        print('fms file exported to XP!')
        
    def acLoad(self):
        
        self.updateFpl()
        
        self.getAcTemplates()
        
        # get the right template.
        if self.fpl.actype in self.acTemplates:
            template = self.acTemplates[self.fpl.actype]
            
            # Assign values to FPL.
            self.fpl.equipment = template[0]
            self.fpl.transponder = template[1]
            
            matchObj = re.search(r'PBN/\w+', self.fpl.other,flags=re.A)  # @UndefinedVariable
            if matchObj is not None:
                self.fpl.other = self.fpl.other.replace(self.fpl.other[matchObj.start():matchObj.end()], '')
            self.fpl.other = re.sub('  +',' ',self.fpl.other)
            self.fpl.other = self.fpl.other.strip()
            self.fpl.other = 'PBN/{} {}'.format(template[2],self.fpl.other)
            self.fpl.other = self.fpl.other.strip()
            
            self.fpl.wakecat = template[3]
            self.fpl.speed = template[4]
            self.fpl.pob = template[5]
            
            # Update Fields.
            self.updateContent()
            
        else:
            messagebox.showinfo("FPL", "No templates found for\naircraft {}!".format(self.fpl.actype))
                
    def acSave(self):
        # Preparations.
        self.updateFpl()
        self.getAcTemplates()
        
        # Check if template already exists and ask what to do.
        if self.fpl.actype in self.acTemplates:
            if messagebox.askyesno("Overwrite?","A template for the aircraft {} already exists.\nOverwrite?".format(self.fpl.actype)):
                self.acTemplates.pop(self.fpl.actype)
            else:
                return
        
        # Update Aircraft templates.
        self.acTemplates[self.fpl.actype] = [] 
        self.acTemplates[self.fpl.actype].append(self.fpl.equipment)
        self.acTemplates[self.fpl.actype].append(self.fpl.transponder)
        
        matchObj = re.search(r'PBN/\w+', self.fpl.other,flags=re.A)  # @UndefinedVariable
        if matchObj is not None:
            self.acTemplates[self.fpl.actype].append(self.fpl.other[matchObj.start():matchObj.end()].replace('PBN/',''))
        else:
            self.acTemplates[self.fpl.actype].append('')
        
        self.acTemplates[self.fpl.actype].append(self.fpl.wakecat)
        self.acTemplates[self.fpl.actype].append(self.fpl.speed)
        self.acTemplates[self.fpl.actype].append(self.fpl.pob)
        
        # Write the new list
        with open(os.path.join(self.databaseDir,'aircraft.csv'),'w') as acFile:
            acFile.write('ac;equip;transponder;PBN;wakeCat;speed;x;POB\n')
            for te in self.acTemplates:
                curTemplate = self.acTemplates[te]
                acFile.write('{};{};{};{};{};{};{}\n'.format(te,curTemplate[0],curTemplate[1],curTemplate[2],curTemplate[3],curTemplate[4],curTemplate[5]))
    
    def getAcTemplates(self):
        self.acTemplates = {}
        if not os.path.exists(os.path.join(self.databaseDir,'aircraft.csv')):
            open(os.path.join(self.databaseDir,'aircraft.csv'),'w').close()
        with open(os.path.join(self.databaseDir,'aircraft.csv')) as acFile:
            for lineNr,line in enumerate(acFile):
                if lineNr:
                    lineSplit = line.rstrip('\n').split(';')
                    self.acTemplates[lineSplit[0]] = [lineSplit[1],lineSplit[2],lineSplit[3],lineSplit[4],lineSplit[5],lineSplit[6]]
    
    
    
    def showSkyvector(self):
        # Calculate middle point.
        depCoordinates = self.fpl.airports[self.fpl.depicao]
        destCoordinates = self.fpl.airports[self.fpl.desticao]
        intermediatePoint = avFormula.gcIntermediatePoint(depCoordinates[0], depCoordinates[1], destCoordinates[0], destCoordinates[1])
        
        skyvectorUrl = 'http://skyvector.com/?ll={:9.6f},{:9.6f}&chart=304&zoom=6&fpl=%20{}%20{}%20{}'.format(intermediatePoint[0],
                                                                                                     intermediatePoint[1],
                                                                                                     self.fpl.depicao,
                                                                                                     self.fpl.route.replace(' ','%20'),
                                                                                                     self.fpl.desticao)
        webbrowser.open(skyvectorUrl,new=2)
        
        
    def showFplText(self):
        # Get Field contents.
        self.updateFpl()
        
        # Init string.
        fplString = '(FPL\n'
        
        # Complete string.
        fplString = '{}-{}-{}{}\n'.format(fplString,
                                          self.fpl.callsign,
                                          self.fpl.rules,
                                          self.fpl.flighttype)
        fplString = '{}-{}{}/{}-{}/{}\n'.format(fplString,
                                                self.fpl.number,
                                                self.fpl.actype,
                                                self.fpl.wakecat,
                                                self.fpl.equipment,
                                                self.fpl.transponder)
        fplString = '{}-{}{}\n'.format(fplString,
                                       self.fpl.depicao,
                                       self.fpl.deptime)
        fplString = '{}-N{:04}F{:03} {}\n'.format(fplString,
                                                  int(self.fpl.speed),
                                                  int(self.fpl.level),
                                                  self.fpl.route)
        fplString = '{}-{}{} {} {}\n'.format(fplString,
                                             self.fpl.desticao,
                                             self.fpl.eet,
                                             self.fpl.alticao,
                                             self.fpl.alt2icao)
        fplString = '{}-{})'.format(fplString,self.fpl.other)
        
        # Print string.
        print(fplString)
        
        # Copy to clipboard.
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(str(fplString))
        r.update()
        r.destroy()
        
        # Show in window.
        showinfo("Flightplan text", '{}\n\n(Copied to clipboard.)'.format(fplString))

        
    # Callbacks
    def routeListCB(self):
        selectedRoute = self.importRouteListboxTl.curselection()
        selectedRoute = selectedRoute[0]
        self.fpl.route = self.routing[selectedRoute]
        self.fpl.route = self.fpl.route[5:-5]
        self.importRouteTop.destroy()
        self.updateContent()
    
    def e_callsignCB(self,*args):  #@UnusedVariable
        string = self.callsign.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum():
                self.callsign.set(string[0:-1])
            else:
                self.callsign.set(self.callsign.get().upper())
        
    def e_numberCB(self,*args):  #@UnusedVariable
        string = self.number.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isdigit():
                self.number.set(string[0:-1])
        
    def e_actypeCB(self,*args):  #@UnusedVariable
        string = self.actype.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum() or len(string) > 4:
                self.actype.set(string[0:-1])
            else:
                self.actype.set(self.actype.get().upper())
        
    def e_equipmentCB(self,*args):  #@UnusedVariable
        string = self.equipment.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum():
                self.equipment.set(string[0:-1])
            else:
                self.equipment.set(self.equipment.get().upper())
        
    def e_transponderCB(self,*args):  #@UnusedVariable
        string = self.transponder.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum():
                self.transponder.set(string[0:-1])
            else:
                self.transponder.set(self.transponder.get().upper())
        
    def e_depicaoCB(self,*args):  #@UnusedVariable
        string = self.depicao.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum() or len(string) > 4:
                self.depicao.set(string[0:-1])
            else:
                self.depicao.set(self.depicao.get().upper())
        
    def e_deptimeCB(self,*args):  #@UnusedVariable
        string = self.deptime.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isdigit() or len(string) > 4:
                self.deptime.set(string[0:-1])
        
    def e_speedCB(self,*args):  #@UnusedVariable
        string = self.speed.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isdigit() or len(string) > 4:
                self.speed.set(string[0:-1])
        
    def e_levelCB(self,*args):  #@UnusedVariable
        string = self.level.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isdigit() or len(string) > 3:
                self.level.set(string[0:-1])
        
    def e_routeCB(self,*args):  #@UnusedVariable
        string = self.route.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum() and enteredChar != '/' and enteredChar != ' ':
                self.route.set(string[0:-1])
            else:
                self.route.set(self.route.get().upper())
        
    def e_desticaoCB(self,*args):  #@UnusedVariable
        string = self.desticao.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum() or len(string) > 4:
                self.desticao.set(string[0:-1])
            else:
                self.desticao.set(self.desticao.get().upper())
        
    def e_eetCB(self,*args):  #@UnusedVariable
        string = self.eet.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isdigit() or len(string) > 4:
                self.eet.set(string[0:-1])
        
    def e_alticaoCB(self,*args):  #@UnusedVariable
        string = self.alticao.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum() or len(string) > 4:
                self.alticao.set(string[0:-1])
            else:
                self.alticao.set(self.alticao.get().upper())
        
    def e_alt2icaoCB(self,*args):  #@UnusedVariable
        string = self.alt2icao.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum() or len(string) > 4:
                self.alt2icao.set(string[0:-1])
            else:
                self.alt2icao.set(self.alt2icao.get().upper())
        
    def e_otherCB(self,*args):  #@UnusedVariable
        string = self.other.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalnum() and enteredChar != '/' and enteredChar != ' ':
                self.other.set(string[0:-1])
            else:
                self.other.set(self.other.get().upper())
        
    def e_enduranceCB(self,*args):  #@UnusedVariable
        string = self.endurance.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isdigit() or len(string) > 4:
                self.endurance.set(string[0:-1])
        
    def e_pobCB(self,*args):  #@UnusedVariable
        string = self.pob.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isdigit():
                self.pob.set(string[0:-1])
        
    def e_picCB(self,*args):  #@UnusedVariable
        string = self.pic.get()
        if len(string):
            enteredChar = string[-1]
            if not enteredChar.isalpha() and enteredChar != ' ' and enteredChar != "'" and enteredChar != '-':
                self.pic.set(string[0:-1])

""" main """
if __name__ == '__main__':
    app = FPLGUI()
