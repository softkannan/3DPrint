#!/usr/bin/env python
"""

This module updates the fusion360 user parameter

"""
__author__ = "SoftK"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.0.1"

import os
import sys
import csv
import adsk.core
import adsk.fusion
import traceback
import io

class Fusion360UserParameters:

    def __init__(self):
        self.ui = None
        try:
            self.app = adsk.core.Application.get()
            self.ui  = self.app.userInterface
            self.design = self.app.activeProduct
            self.userParams = self.design.userParameters
        except:
            if self.ui:
                self.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def updateFusionUserParameters(self, name, value, units, comments):
        if self.userParams.itemByName(name) == None:
            self.__addNewUserParameter(name, value, units, comments)
        else:
            self.__updateUserParameter(name, value, units, comments)
    
    def __addNewUserParameter(self, name, value, units, comments):
        print("Add parameters: Name: " + name + ", Value: " + value + ", Units: " + units + ", Comments: " + comments)
        aUserValue = adsk.core.ValueInput.createByString(value)
        aUnits = self.design.unitsManager.defaultLengthUnits
        self.userParams.add(name, aUserValue, aUnits, comments)
    
    def __updateUserParameter(self, name, value, units, comments):
        print("Update parameters: Name: " + name + ", Value: " + value + ", Units: " + units + ", Comments: " + comments)
        aUserValue = adsk.core.ValueInput.createByString(value)
        aUnits = self.design.unitsManager.defaultLengthUnits
        self.userParams.itemByName(name).expression = value
