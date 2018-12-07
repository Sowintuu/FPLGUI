#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#==============================================================================
# Fpl - Class to describe a flightplan
# Copyright (C) 2018  Oliver Clemens
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#==============================================================================

import re
import configparser
import avFormula
from copy import deepcopy


class Fpl(object):
    
    def __init__(self,fplPath):
        self.path = fplPath
        self.load(self.path + "\\Default.fpl")
        self.waypoints = {}
        self.airways = {}
        self.airports = {}
    
    
    def load(self,path):
        
        config = configparser.RawConfigParser()
        config.read(path)
        
        self.callsign = config.get('FLIGHTPLAN', 'CALLSIGN')
        self.pic = config.get('FLIGHTPLAN', 'PIC')
        self.speedtype = config.get('FLIGHTPLAN', 'SPEEDTYPE')
        self.pob = config.get('FLIGHTPLAN', 'POB')
        self.endurance = config.get('FLIGHTPLAN', 'ENDURANCE')
        self.other = config.get('FLIGHTPLAN', 'OTHER')
        self.alt2icao = config.get('FLIGHTPLAN', 'ALT2ICAO')
        self.alticao = config.get('FLIGHTPLAN', 'ALTICAO')
        self.eet = config.get('FLIGHTPLAN', 'EET')
        self.desticao = config.get('FLIGHTPLAN', 'DESTICAO')
        self.route = config.get('FLIGHTPLAN', 'ROUTE')
        self.level = config.get('FLIGHTPLAN', 'LEVEL')
        self.leveltype = config.get('FLIGHTPLAN', 'LEVELTYPE')
        self.speed = config.get('FLIGHTPLAN', 'SPEED')
        self.deptime = config.get('FLIGHTPLAN', 'DEPTIME')
        self.depicao = config.get('FLIGHTPLAN', 'DEPICAO')
        self.transponder = config.get('FLIGHTPLAN', 'TRANSPONDER')
        self.equipment = config.get('FLIGHTPLAN', 'EQUIPMENT')
        self.wakecat = config.get('FLIGHTPLAN', 'WAKECAT')
        self.actype = config.get('FLIGHTPLAN', 'ACTYPE')
        self.number = config.get('FLIGHTPLAN', 'NUMBER')
        self.flighttype = config.get('FLIGHTPLAN', 'FLIGHTTYPE')
        self.rules = config.get('FLIGHTPLAN', 'RULES')
    
    
    def save(self,filepath):
        with open(filepath,'w') as fplFile:
            fplFile.write("[FLIGHTPLAN]\r\n")
            fplFile.write("CALLSIGN={}\r\n".format(self.callsign))
            fplFile.write("PIC={}\r\n".format(self.pic))
            fplFile.write("FMCROUTE={}\r\n".format(self.route))
            fplFile.write("LIVERY=\r\n")
            fplFile.write("AIRLINE=\r\n")
            fplFile.write("SPEEDTYPE={}\r\n".format(self.speedtype))
            fplFile.write("POB={}\r\n".format(self.pob))
            fplFile.write("ENDURANCE={}\r\n".format(self.endurance))
            fplFile.write("OTHER={}\r\n".format(self.other))
            fplFile.write("ALT2ICAO={}\r\n".format(self.alt2icao))
            fplFile.write("ALTICAO={}\r\n".format(self.alticao))
            fplFile.write("EET={}\r\n".format(self.eet))
            fplFile.write("DESTICAO={}\r\n".format(self.desticao))
            fplFile.write("ROUTE={}\r\n".format(self.route))
            fplFile.write("LEVEL={}\r\n".format(self.level))
            fplFile.write("LEVELTYPE={}\r\n".format(self.leveltype))
            fplFile.write("SPEED={}\r\n".format(self.speed))
            fplFile.write("DEPTIME={}\r\n".format(self.deptime))
            fplFile.write("DEPICAO={}\r\n".format(self.depicao))
            fplFile.write("TRANSPONDER={}\r\n".format(self.transponder))
            fplFile.write("EQUIPMENT={}\r\n".format(self.equipment))
            fplFile.write("WAKECAT={}\r\n".format(self.wakecat))
            fplFile.write("ACTYPE={}\r\n".format(self.actype))
            fplFile.write("NUMBER={}\r\n".format(self.number))
            fplFile.write("FLIGHTTYPE={}\r\n".format(self.flighttype))
            fplFile.write("RULES={}\r\n".format(self.rules))
    
    def getFixes(self,fixesFilePath):
        with open(fixesFilePath) as waypointsFile:
            for line in waypointsFile:
                lineSplit = re.split(' +',line.strip())
                if len(lineSplit) == 6:
                    newWaypoint = [float(lineSplit[0]),float(lineSplit[1]),11]
                    if lineSplit[2] not in self.waypoints:
                        self.waypoints.update({lineSplit[2]:[newWaypoint]})
                    else:
                        self.waypoints[lineSplit[2]].append(newWaypoint)
                elif len(lineSplit) > 1:
                    self.cycleNumber = re.findall('(?<=data cycle )\d{4}',line)[0]
    
    def getNavaids(self,navaidFilePath):
        with open(navaidFilePath) as navaidFile:
            for line in navaidFile:
                lineSplit = re.split(' +',line.strip())
                if lineSplit[0] in ['2','3','13']:
                    lineSplit[0] = lineSplit[0][-1]
                    newWaypoint = [float(lineSplit[1]),float(lineSplit[2]),int(lineSplit[0])]
                    if lineSplit[7] not in self.waypoints:
                        self.waypoints.update({lineSplit[7]:[newWaypoint]})
                    else:
                        self.waypoints[lineSplit[7]].append(newWaypoint)
    
    
    def getAirports(self,airportsFilePath):
        with open(airportsFilePath) as airportsFile:
            for line in airportsFile:
                lineSplit = re.split(',',line.strip())
                lat = re.split(' +',lineSplit[2].strip())
                lat = float(lat[1])
                lon = re.split(' +',lineSplit[3].strip())
                lon = float(lon[1])
                self.airports[lineSplit[0]] = [lat,lon]
                
        pass
    
    
    def getAirways(self,airwaysFilePath):
        with open(airwaysFilePath) as airwaysFile:
            for line in airwaysFile:
                lineSplit = re.split(' +',line.strip())
                if len(lineSplit) == 11:
                    # Get nearest fix pair.
                    fixes1 = deepcopy(self.waypoints[lineSplit[0]])
                    fixes2 = deepcopy(self.waypoints[lineSplit[3]])
                    nearest = [None,None]
                    distanceMin = 3.2 # Slightly greater than pi
                    
                    if len(fixes1) > 1 or len(fixes2) > 1:
                        for fi1id,fi1 in enumerate(fixes1):
                            if int(lineSplit[2]) != fi1[2]:
                                continue
                            for fi2id,fi2 in enumerate(fixes2):
                                if int(lineSplit[5]) != fi2[2]:
                                    continue
                                distance = avFormula.gcDistance(fi1[0],fi2[0],fi1[1],fi2[1])
                                if distance < distanceMin:
                                    nearest = [fi1id,fi2id]
                                    distanceMin = distance
                        
                    
                    else:
                        nearest = [0,0]
                        
                    
                    fix1 = fixes1[nearest[0]]
                    fix2 = fixes2[nearest[1]]
                    
                    # Add fix name to list
                    fix1.insert(0,lineSplit[0])
                    fix2.insert(0,lineSplit[3])
                    
                    
                    curAirways = lineSplit[10].split('-')
                    for aw in curAirways:
                        if aw not in self.airways:
                            self.airways[aw] = Airway(lineSplit[10])
                        self.airways[aw].update(fix1,fix2)
                        
    
class Airway(object):
    
    def __init__(self,name):#,nFixes):
        self.name = name
        self.parts = []
        
    def update(self,fix1,fix2):
        
        # Check parts if one or both fixed are alredy included and get their positions fix<n>Part.
        fix1Part = None
        fix2Part = None
        
        for paId,pa in enumerate(self.parts):
            if fix1 in pa:
                fix1Part = paId
                
            if fix2 in pa:
                fix2Part = paId
        paId = None
        pa = None
        
        # Sort the leg to a part or concat two parts. Several cases:
        # Case 1: Fixes in no part > Create new part.
        if fix1Part is None and fix2Part is None:
            self.parts.append([fix1,fix2])
            
        # Case 2: Only fix 2 included > append fix 1.
        elif fix1Part is None:
            fix2Ind = self.parts[fix2Part].index(fix2)
            if not fix2Ind:
                self.parts[fix2Part].insert(0, fix1)
            elif fix2Ind == (len(self.parts[fix2Part]) - 1):
                self.parts[fix2Part].append(fix1)
            else:
                raise(Exception,'Unexpected format cannot append to an intermediate fix')
            
        # Case 3: Only fix 1 included > append fix 2.
        elif fix2Part is None:
            fix1Ind = self.parts[fix1Part].index(fix1)
            if not fix1Ind:
                self.parts[fix1Part].insert(0, fix2)
            elif fix1Ind == (len(self.parts[fix1Part]) - 1):
                self.parts[fix1Part].append(fix2)
            else:
                raise(Exception,'Unexpected format cannot append to an intermediate fix')
        
        # Case 4: Both fixes included in different parts > Concat parts.
        elif fix1Part != fix2Part:
            fix1Ind = self.parts[fix1Part].index(fix1)
            fix2Ind = self.parts[fix2Part].index(fix2)
            
            if not fix1Ind:
                self.parts[fix1Part] = self.parts[fix1Part][::-1]
                
            if fix2Ind == (len(self.parts[fix2Part]) - 1):
                self.parts[fix2Part] = self.parts[fix2Part][::-1]
            
            self.parts.append(self.parts[fix1Part] + self.parts[fix2Part])
            self.parts.pop(fix1Part)
            if fix2Part > fix1Part:
                fix2Part -= 1
            self.parts.pop(fix2Part)